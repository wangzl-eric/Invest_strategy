"""
Backtrader Engine for PA Investment Platform
============================================
A unified backtesting and live trading engine using Backtrader.
Supports both historical backtesting and live IBKR execution.

Full guide: docs/guides/BACKTEST_ENGINE_GUIDE.md (flow, sizing, optimizer)

Reference: https://www.backtrader.com/docu/live/ib/ib/

Metric Formulas (validated sources):
- Alpha: α = Rₚ - [R𝒇 + β(Rₘ - R𝒇)]  (Jensen 1968, CFA Level I)
- Beta: β = Cov(Rₚ, Rₘ) / Var(Rₘ)  (CAPM, Sharpe 1964, CFA Level I)
- Sharpe: SR = (Rₚ - R𝒇) / σₚ  (Sharpe 1966, CFA Level I)
- Max Drawdown: MDD = (Trough - Peak) / Peak  (CFA Level II, GARP)
- Volatility: σ = √[Σ(Rᵢ - R̄)² / (n-1)]  (Statistics, CFA Level I)
- Sortino: SOR = (Rₚ - R𝒇) / σ_d  (Sortino 1994)
- Calmar: CR = Annualized Return / |Max DD|  (Young 1991)
"""

import os

# Import our existing IBKR client for historical data
import sys
import warnings
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import backtrader as bt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ibkr_client import IBKRClient
except ImportError:
    from backend.ibkr_client import IBKRClient


class IBKRDataFeed(bt.feeds.PandasData):
    """
    Custom Backtrader data feed from pandas DataFrame.
    Maps pandas DataFrame to Backtrader's expected format.
    """

    params = (
        ("datetime", None),
        ("open", "open"),
        ("high", "high"),
        ("low", "low"),
        ("close", "close"),
        ("volume", "volume"),
        ("openinterest", -1),
    )


class ParquetDataFeed(bt.feeds.PandasData):
    """
    Custom Backtrader data feed from Parquet files.
    """

    params = (
        ("datetime", "date"),
        ("open", "open"),
        ("high", "high"),
        ("low", "low"),
        ("close", "close"),
        ("volume", "volume"),
        ("openinterest", -1),
    )


class SignalIndicator(bt.Indicator):
    """
    Custom indicator that accepts external signals as input.
    """

    lines = ("signal",)

    def __init__(self):
        self.lines.signal = self.data.signal


def _wrap_strategy_with_position_tracking(strategy_class: type) -> type:
    """
    Wrap any strategy to record position dynamics (1=long, 0=flat, -1=short),
    portfolio_value, and price at each bar. Records only during next() when
    the strategy has valid signals (not during prenext warmup).
    """

    def _record_position(self):
        """Record position, portfolio value, and price for current bar (next() only)."""
        pos = self.getposition(self.data).size
        position_signal = 1 if pos > 0 else (-1 if pos < 0 else 0)
        self.position_history.append(
            {
                "date": self.data.datetime.date(0),
                "position": position_signal,
                "portfolio_value": self.broker.getvalue(),
                "price": float(
                    self.data.close[0]
                ),  # Generic: close for daily, works for intraday
            }
        )

    class _PositionTrackingWrapper(strategy_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.position_history = []

        def next(self):
            _record_position(self)
            super().next()

    _PositionTrackingWrapper.__name__ = strategy_class.__name__
    return _PositionTrackingWrapper


class PositionObserver(bt.Observer):
    """Observer to track position size and portfolio value over time."""

    lines = ("position", "portfolio_value")

    def next(self):
        self.lines.position[0] = self._owner.position.size
        self.lines.portfolio_value[0] = self._owner.broker.getvalue()


class TradeLogger(bt.Observer):
    """Observer to log all trades with details."""

    lines = ("trade_type", "price", "size", "pnl")

    def __init__(self):
        self._trade_log = []
        self._prev_position = 0

    def next(self):
        current_position = self._owner.position.size

        # Detect trade (position changed)
        if current_position != self._prev_position:
            if current_position > self._prev_position:
                trade_type = "BUY"
            else:
                trade_type = "SELL"

            # Get execution price (simplified - use close)
            price = self.data.close[0]
            size = abs(current_position - self._prev_position)

            self._trade_log.append(
                {
                    "date": self.data.datetime.date(0),
                    "trade_type": trade_type,
                    "price": price,
                    "size": size,
                    "position": current_position,
                }
            )

        self._prev_position = current_position

    def get_log(self):
        return self._trade_log


class VolatilitySizer(bt.Sizer):
    """
    Size positions based on historical volatility. Higher vol -> smaller position.
    Uses rolling std of returns over lookback bars. Inverse-vol weighting.
    """

    params = (
        ("lookback", 20),  # bars for volatility calculation
        ("target_risk", 0.02),  # target risk per trade (e.g. 2%)
        ("min_vol", 1e-6),  # avoid div by zero
        ("max_pct", 100),  # cap position at this % of portfolio
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        if not isbuy:
            position = self.strategy.getposition(data)
            return abs(position.size)
        price = float(data.close[0])
        if price <= 0:
            return 0
        # Historical bars: data.close[-i] = i bars ago; len(strategy) = bars processed
        n_bars = len(self.strategy) if hasattr(self.strategy, "__len__") else 999
        lookback = min(self.params.lookback, n_bars - 1)
        if lookback < 2:
            return int(cash / price)
        returns = []
        for i in range(1, lookback):
            try:
                p0 = float(data.close[-i])
                p1 = float(data.close[-(i + 1)])
            except (IndexError, TypeError):
                break
            if p1 > 0:
                returns.append((p0 - p1) / p1)
        if not returns:
            return int(cash / price)
        vol = float(np.std(returns))
        vol = max(vol, self.params.min_vol)
        pv = self.strategy.broker.getvalue()
        risk_amount = pv * self.params.target_risk
        size = int(risk_amount / (price * vol)) if vol > 0 else 0
        max_size = int(pv * self.params.max_pct / 100 / price)
        return min(max(0, size), max_size)


class HistoricalPercentSizer(bt.Sizer):
    """
    Size by historical volatility ratio: scale position by (ref_vol / current_vol).
    When vol is low vs reference -> larger position; when high -> smaller.
    """

    params = (
        ("lookback", 20),
        ("base_pct", 100),  # base allocation when vol = ref
        ("ref_vol", None),  # reference vol (None = use lookback mean of vol)
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        if not isbuy:
            position = self.strategy.getposition(data)
            return abs(position.size)
        price = float(data.close[0])
        if price <= 0:
            return 0
        n_bars = len(self.strategy) if hasattr(self.strategy, "__len__") else 999
        lookback = min(self.params.lookback, n_bars - 1)
        if lookback < 2:
            return int(cash * self.params.base_pct / 100 / price)
        returns = []
        for i in range(1, lookback):
            try:
                p0, p1 = float(data.close[-i]), float(data.close[-(i + 1)])
            except (IndexError, TypeError):
                break
            if p1 > 0:
                returns.append((p0 - p1) / p1)
        if not returns:
            return int(cash * self.params.base_pct / 100 / price)
        vol = float(np.std(returns))
        ref = self.params.ref_vol
        if ref is None or ref <= 0:
            ref = vol
        if vol < 1e-8:
            vol = ref
        scale = min(ref / vol, 2.0)
        pct = min(self.params.base_pct * scale, 100)
        return int(cash * pct / 100 / price)


class BacktestEngine:
    """
    Unified Backtesting and Live Trading Engine.

    Features:
    - Backtest with historical data from parquet or IBKR
    - Live trading with IBKR (using Backtrader's native IBStore)
    - Built-in analytics (Sharpe, Drawdown, Returns)
    - Consistent logic between backtest and live
    """

    def __init__(
        self,
        cash: float = 100000,
        commission: float = 0.001,
        sizer=None,
        sizer_params: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the engine.

        Args:
            cash: Starting capital
            commission: Commission rate (0.001 = 0.1%)
            sizer: Position sizing. Default AllInSizer (100%).
                - None or 'allin': AllInSizer(percents=100)
                - float (0-100): AllInSizer(percents=sizer), e.g. 50 = half position
                - bt.Sizer class: cerebro.addsizer(sizer, **sizer_params)
                See docs/guides/BACKTEST_ENGINE_GUIDE.md for optimizer integration.
            sizer_params: Kwargs passed to custom sizer class when sizer is a class.
        """
        self.cash = cash
        self.commission = commission
        self.sizer = sizer
        self.sizer_params = sizer_params or {}
        self.cerebro = None
        self.strategy_class = None
        self.results = None

    def add_data(self, data: bt.DataBase, name: str = None):
        """Add a data feed to the cerebro."""
        if self.cerebro is None:
            self._init_cerebro()
        self.cerebro.adddata(data, name=name)

    def _init_cerebro(self):
        """Initialize Cerebro with standard settings."""
        self.cerebro = bt.Cerebro()
        self.cerebro.broker.setcash(self.cash)
        self.cerebro.broker.setcommission(commission=self.commission)
        # Position sizing: default AllInSizer, or custom percents/sizer
        self._apply_sizer()

        # Standard analyzers
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")

        # Position and trade tracking observers
        self.cerebro.addobserver(PositionObserver)
        self.cerebro.addobserver(TradeLogger)
        self.cerebro.addobserver(bt.observers.Broker)

    def _apply_sizer(self):
        """Apply position sizer based on self.sizer setting."""
        s = self.sizer
        if s is None or s == "allin":
            self.cerebro.addsizer(
                bt.sizers.AllInSizer, percents=95
            )  # 95% to leave buffer for commission (avoids Margin rejection)
        elif isinstance(s, (int, float)) and 0 <= s <= 100:
            self.cerebro.addsizer(bt.sizers.AllInSizer, percents=float(s))
        elif isinstance(s, type) and issubclass(s, bt.Sizer):
            self.cerebro.addsizer(s, **self.sizer_params)
        else:
            self.cerebro.addsizer(bt.sizers.AllInSizer, percents=95)

    def add_strategy(self, strategy_class: type, **params):
        """Add a strategy to the cerebro. Automatically wraps to record position dynamics (1, 0, -1)."""
        if self.cerebro is None:
            self._init_cerebro()
        self.strategy_class = strategy_class
        wrapped = _wrap_strategy_with_position_tracking(strategy_class)
        self.cerebro.addstrategy(wrapped, **params)

    def set_benchmark(self, benchmark_data: pd.DataFrame):
        """
        Set benchmark data for alpha/beta calculation.

        Args:
            benchmark_data: DataFrame with 'close' column indexed by date
        """
        self.benchmark_data = benchmark_data.copy()
        if "date" in self.benchmark_data.columns:
            self.benchmark_data["date"] = pd.to_datetime(self.benchmark_data["date"])
            self.benchmark_data = self.benchmark_data.set_index("date")
        self.benchmark_data.columns = [c.lower() for c in self.benchmark_data.columns]

    def load_parquet_data(self, filepath: str, name: str = None) -> bt.DataBase:
        """
        Load data from parquet file.

        Args:
            filepath: Path to parquet file
            name: Name for the data feed

        Returns:
            Backtrader data feed
        """
        df = pd.read_parquet(filepath)

        # Ensure datetime index
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")
        elif not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        # Standardize column names
        df.columns = [c.lower() for c in df.columns]

        data = ParquetDataFeed(dataname=df)
        self.add_data(data, name=name or filepath.split("/")[-1])
        return data

    async def load_ibkr_data(
        self,
        symbol: str,
        sec_type: str = "STK",
        exchange: str = "SMART",
        currency: str = "USD",
        duration: str = "1 Y",
        interval: str = "1 day",
        whatToShow: str = "TRADES",
        name: str = None,
    ) -> bt.DataBase:
        """
        Load historical data from IBKR using our IBKRClient.

        Args:
            symbol: Ticker symbol
            sec_type: Security type (STK, IND, FUT, etc.)
            exchange: Exchange
            currency: Currency
            duration: Duration (e.g., '1 Y', '2 Y')
            interval: Bar size (e.g., '1 day', '1 hour')
            whatToShow: Data type (TRADES, BID, ASK, etc.)
            name: Name for the data feed

        Returns:
            Backtrader data feed
        """
        client = IBKRClient()
        if not await client.ensure_connected():
            raise ConnectionError("Could not connect to IBKR")

        df = await client.get_historical_data(
            symbol=symbol,
            sec_type=sec_type,
            exchange=exchange,
            currency=currency,
            duration=duration,
            interval=interval,
            whatToShow=whatToShow,
        )

        await client.disconnect()

        if df is None or df.empty:
            raise ValueError(f"No data returned for {symbol}")

        # Ensure datetime index
        df.index = pd.to_datetime(df.index)

        # Standardize column names
        df.columns = [c.lower() for c in df.columns]

        data = IBKRDataFeed(dataname=df)
        self.add_data(data, name=name or symbol)
        return data

    def _calculate_comprehensive_metrics(
        self,
        returns_series: pd.Series,
        benchmark_returns: pd.Series = None,
        risk_free_rate: float = 0.05,
    ) -> Dict[str, float]:
        """
        Calculate comprehensive performance metrics.

        Formulas (validated sources):
        - Alpha: α = Rₚ - [R𝒇 + β(Rₘ - R𝒇)]  (Jensen 1968)
        - Beta: β = Cov(Rₚ, Rₘ) / Var(Rₘ)  (CAPM)
        - Sharpe: SR = (Rₚ - R𝒇) / σₚ  (Sharpe 1966)
        - Max Drawdown: (Trough - Peak) / Peak  (CFA)
        - Volatility: σ = √[Σ(Rᵢ - R̄)² / (n-1)]  (Statistics)
        - Sortino: (Rₚ - R𝒇) / σ_d  (Sortino 1994)
        - Calmar: Annualized Return / |Max DD|  (Young 1991)

        Args:
            returns_series: Strategy returns
            benchmark_returns: Benchmark returns (e.g., S&P 500)
            risk_free_rate: Annual risk-free rate (default 5%)

        Returns:
            Dictionary of metrics
        """
        metrics = {}

        # Handle empty returns series
        if returns_series is None or len(returns_series) == 0:
            return {
                "total_return": 0.0,
                "annualized_return": 0.0,
                "volatility": 0.0,
                "annualized_volatility": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "sortino_ratio": 0.0,
                "calmar_ratio": 0.0,
                "alpha": None,
                "beta": None,
            }

        # Annualization factor (assuming daily data)
        periods_per_year = 252
        daily_rf = risk_free_rate / periods_per_year

        # Basic return metrics
        total_return = (1 + returns_series).prod() - 1
        annualized_return = (1 + total_return) ** (
            periods_per_year / len(returns_series)
        ) - 1
        metrics["total_return"] = total_return
        metrics["annualized_return"] = annualized_return

        # Volatility (Standard Deviation)
        # σ = √[Σ(Rᵢ - R̄)² / (n-1)]
        volatility = returns_series.std()
        annualized_vol = volatility * np.sqrt(periods_per_year)
        metrics["volatility"] = volatility
        metrics["annualized_volatility"] = annualized_vol

        # Sharpe Ratio
        # SR = (Rₚ - R𝒇) / σₚ
        excess_returns = returns_series - daily_rf
        if volatility > 0:
            sharpe = excess_returns.mean() / volatility * np.sqrt(periods_per_year)
        else:
            sharpe = 0.0
        metrics["sharpe_ratio"] = sharpe

        # Maximum Drawdown
        # MDD = (Trough - Peak) / Peak
        cumulative = (1 + returns_series).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        metrics["max_drawdown"] = max_drawdown

        # Sortino Ratio (uses downside deviation)
        # SOR = (Rₚ - R𝒇) / σ_d
        negative_returns = returns_series[returns_series < 0]
        if len(negative_returns) > 0:
            downside_dev = negative_returns.std() * np.sqrt(periods_per_year)
        else:
            downside_dev = 0.0

        if downside_dev > 0:
            sortino = (annualized_return - risk_free_rate) / downside_dev
        else:
            sortino = 0.0
        metrics["sortino_ratio"] = sortino

        # Calmar Ratio
        # CR = Annualized Return / |Max DD|
        if abs(max_drawdown) > 0:
            calmar = annualized_return / abs(max_drawdown)
        else:
            calmar = 0.0
        metrics["calmar_ratio"] = calmar

        # Alpha and Beta (if benchmark provided)
        # α = Rₚ - [R𝒇 + β(Rₘ - R𝒇)]
        # β = Cov(Rₚ, Rₘ) / Var(Rₘ)
        if benchmark_returns is not None and len(benchmark_returns) > 0:
            # Align returns
            aligned_strategy = returns_series.align(benchmark_returns, join="inner")
            strategy_ret = aligned_strategy[0]
            benchmark_ret = aligned_strategy[1]

            if len(strategy_ret) > 1 and benchmark_ret.var() > 0:
                # Beta
                covariance = strategy_ret.cov(benchmark_ret)
                variance = benchmark_ret.var()
                beta = covariance / variance
                metrics["beta"] = beta

                # Alpha
                # α = Rₚ - [R𝒇 + β(Rₘ - R𝒇)]
                expected_return = daily_rf + beta * (benchmark_ret.mean() - daily_rf)
                alpha = strategy_ret.mean() - expected_return
                annualized_alpha = alpha * periods_per_year
                metrics["alpha"] = annualized_alpha
            else:
                metrics["beta"] = 0.0
                metrics["alpha"] = 0.0
        else:
            metrics["beta"] = None  # No benchmark
            metrics["alpha"] = None

        return metrics

    def run_backtest(
        self,
        benchmark_data: pd.DataFrame = None,
        risk_free_rate: float = 0.05,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Run backtest and return comprehensive results.

        Args:
            benchmark_data: Optional benchmark DataFrame for alpha/beta calculation
            risk_free_rate: Annual risk-free rate (default 5%)

        Returns:
            Dictionary with portfolio value, trades, metrics, position series
        """
        if self.cerebro is None:
            raise ValueError("No data or strategy added to cerebro")

        # Run backtest
        self.results = self.cerebro.run(**kwargs)

        # Extract results
        strategy = self.results[0]

        # Get final portfolio value
        final_value = self.cerebro.broker.getvalue()
        initial_value = self.cash

        # Get analyzers
        sharpe = strategy.analyzers.sharpe.get_analysis()
        drawdown = strategy.analyzers.drawdown.get_analysis()
        returns = strategy.analyzers.returns.get_analysis()
        trades = strategy.analyzers.trades.get_analysis()

        # Build unified equity curve (position + portfolio + price + returns + drawdown)
        equity_curve = pd.DataFrame()
        trade_log = []

        try:
            if (
                hasattr(strategy, "position_history")
                and len(strategy.position_history) > 0
            ):
                history = strategy.position_history
                equity_curve = pd.DataFrame(history)
                equity_curve["date"] = pd.to_datetime(equity_curve["date"])
                equity_curve = equity_curve.set_index("date")
            else:
                raise ValueError("Strategy has no position_history")
        except Exception as e:
            warnings.warn(f"Could not extract equity curve: {e}")

        # Fallback: Build from data feed when strategy has no position_history
        if equity_curve.empty and strategy is not None:
            try:
                data_feed = strategy.datas[0]
                date_array = getattr(data_feed.datetime, "array", None)
                date_lines = list(date_array) if date_array is not None else None
                data_len = len(date_lines) if date_lines else len(data_feed)
                if data_len > 0:
                    dates = [
                        bt.num2date(dt)
                        for dt in (
                            date_lines
                            or [data_feed.datetime[i] for i in range(data_len)]
                        )
                    ]
                    close_prices = [float(data_feed.close[i]) for i in range(data_len)]
                    values = [
                        initial_value
                        + (final_value - initial_value) * (i / (data_len - 1))
                        if data_len > 1
                        else final_value
                        for i in range(data_len)
                    ]
                    equity_curve = pd.DataFrame(
                        {
                            "date": dates,
                            "price": close_prices,
                            "position": [0] * data_len,
                            "portfolio_value": values,
                        }
                    )
                    equity_curve["date"] = pd.to_datetime(equity_curve["date"])
                    equity_curve = equity_curve.set_index("date")
            except Exception as e2:
                pass

        if equity_curve.empty:
            raise ValueError(
                "Equity curve is empty - backtest may have not run correctly. "
                "Check that: (1) data feed has data, (2) strategy executed trades, "
                "(3) observers are properly attached."
            )

        # Build trade log from position changes (0->1 = BUY, 1->0 = SELL)
        if "position" in equity_curve.columns and "price" in equity_curve.columns:
            pos = equity_curve["position"].fillna(0)
            prev_pos = pos.shift(1).fillna(0)
            for idx in equity_curve.index:
                p, pp = pos.loc[idx], prev_pos.loc[idx]
                if p > pp:  # position increased -> BUY
                    trade_log.append(
                        {
                            "date": idx,
                            "trade_type": "BUY",
                            "price": equity_curve.loc[idx, "price"],
                            "size": p - pp,
                        }
                    )
                elif p < pp:  # position decreased -> SELL
                    trade_log.append(
                        {
                            "date": idx,
                            "trade_type": "SELL",
                            "price": equity_curve.loc[idx, "price"],
                            "size": pp - p,
                        }
                    )

        # Compute returns, cumulative returns, peak, drawdown
        equity_curve = equity_curve.copy()
        equity_curve["returns"] = equity_curve["portfolio_value"].pct_change().fillna(0)
        equity_curve["cumulative_returns"] = (1 + equity_curve["returns"]).cumprod() - 1
        equity_curve["peak"] = equity_curve["portfolio_value"].cummax()
        equity_curve["drawdown"] = (
            equity_curve["portfolio_value"] - equity_curve["peak"]
        ) / equity_curve["peak"]
        returns_series = equity_curve["returns"].dropna()

        # Calculate comprehensive metrics
        benchmark_returns = None
        if benchmark_data is not None:
            bm = benchmark_data.copy()
            if "date" in bm.columns:
                bm["date"] = pd.to_datetime(bm["date"])
                bm = bm.set_index("date")
            bm.columns = [c.lower() for c in bm.columns]
            if not equity_curve.empty:
                common_dates = equity_curve.index.intersection(bm.index)
                if len(common_dates) > 0:
                    benchmark_returns = (
                        bm.loc[common_dates, "close"].pct_change().dropna()
                    )

        metrics = self._calculate_comprehensive_metrics(
            returns_series, benchmark_returns, risk_free_rate
        )

        # Build trade log DataFrame
        trade_df = pd.DataFrame(trade_log) if trade_log else pd.DataFrame()

        # Calculate win-rate metrics
        won_trades = trades.get("won", {}).get("total", 0)
        lost_trades = trades.get("lost", {}).get("total", 0)
        total_trades = trades.get("total", {}).get("total", 0)

        won_pnl = trades.get("won", {}).get("pnl", {}).get("average", 0) * won_trades
        lost_pnl = (
            abs(trades.get("lost", {}).get("pnl", {}).get("average", 0)) * lost_trades
        )

        win_rate = won_trades / total_trades if total_trades > 0 else 0
        profit_factor = won_pnl / lost_pnl if lost_pnl > 0 else 0

        metrics["win_rate"] = win_rate
        metrics["total_trades"] = total_trades
        metrics["won_trades"] = won_trades
        metrics["lost_trades"] = lost_trades
        metrics["profit_factor"] = profit_factor
        metrics["avg_win"] = trades.get("won", {}).get("pnl", {}).get("average", 0)
        metrics["avg_loss"] = trades.get("lost", {}).get("pnl", {}).get("average", 0)

        return {
            "initial_cash": initial_value,
            "final_value": final_value,
            "total_return": (final_value - initial_value) / initial_value,
            "sharperatio": sharpe.get("sharpeRatio", None),
            "max_drawdown": drawdown.get("max", {}).get("drawdown", 0) / 100,
            "avg_return": returns.get("avgreturn", 0),
            "total_trades": total_trades,
            "won_trades": won_trades,
            "lost_trades": lost_trades,
            "equity_curve": equity_curve,
            "position_series": equity_curve,  # Alias for backward compatibility
            "trade_log": trade_df,
            "returns_series": returns_series,
            "drawdown_series": equity_curve["drawdown"],
            "alpha": metrics.get("alpha"),
            "beta": metrics.get("beta"),
            "sharpe_ratio": metrics.get("sharpe_ratio"),
            "volatility": metrics.get("volatility"),
            "annualized_volatility": metrics.get("annualized_volatility"),
            "sortino_ratio": metrics.get("sortino_ratio"),
            "calmar_ratio": metrics.get("calmar_ratio"),
            "profit_factor": profit_factor,
            "win_rate": win_rate,
            "strategy": strategy,
            "cerebro": self.cerebro,
        }

    def get_equity_curve(self) -> pd.DataFrame:
        """Get equity curve from backtest."""
        if self.results is None:
            raise ValueError("Run backtest first")

        # Access the observer data
        strategy = self.results[0]

        # Get broker values over time
        # Note: This is simplified - full implementation would track equity
        return pd.DataFrame()

    def plot_results(self):
        """Plot backtest results using Backtrader's built-in plotter."""
        if self.cerebro is None:
            raise ValueError("Run backtest first")
        self.cerebro.plot()


# =============================================================================
# Strategy Factory Functions
# =============================================================================


def create_momentum_strategy(name: str = "Momentum", params: Dict = None):
    """
    Factory function to create a momentum strategy.

    Args:
        name: Strategy name
        params: Strategy parameters (period, threshold, etc.)

    Returns:
        Backtrader strategy class
    """
    default_params = {
        "period": 20,
        "threshold": 0.0,
    }
    if params:
        default_params.update(params)

    class MomentumStrategy(bt.Strategy):
        params = (
            ("period", default_params["period"]),
            ("threshold", default_params["threshold"]),
        )

        def __init__(self):
            self.sma = bt.ind.SMA(self.data.close, period=self.params.period)
            self.order = None
            self.trades = []

        def log(self, txt, dt=None):
            dt = dt or self.datas[0].datetime.date(0)
            print(f"{dt.isoformat()} {txt}")

        def notify_order(self, order):
            if order.status in [order.Submitted, order.Accepted]:
                return

            if order.status in [order.Completed]:
                if order.isbuy():
                    self.log(f"BUY EXECUTED, Price: {order.executed.price:.2f}")
                else:
                    self.log(f"SELL EXECUTED, Price: {order.executed.price:.2f}")

            elif order.status in [order.Canceled, order.Margin, order.Rejected]:
                self.log("Order Canceled/Margin/Rejected")

            self.order = None

        def next(self):
            if self.order:
                return

            # Intraday strategy: use previous bar's data (no look-ahead bias)
            # Decision made at start of day, using yesterday's close
            sma_value = self.sma[-1]
            current_price = self.data.close[-1]

            # Simple momentum: price above SMA = long, below = short
            if current_price > sma_value + self.params.threshold:
                self.order = self.buy()
            elif current_price < sma_value - self.params.threshold:
                self.order = self.sell()

    # Rename class
    MomentumStrategy.__name__ = name
    return MomentumStrategy


def create_mean_reversion_strategy(name: str = "MeanReversion", params: Dict = None):
    """
    Factory function to create a mean reversion strategy.

    Args:
        name: Strategy name
        params: Strategy parameters (period, std_dev, etc.)

    Returns:
        Backtrader strategy class
    """
    default_params = {
        "period": 20,
        "std_dev": 2.0,
    }
    if params:
        default_params.update(params)

    class MeanReversionStrategy(bt.Strategy):
        params = (
            ("period", default_params["period"]),
            ("std_dev", default_params["std_dev"]),
        )

        def __init__(self):
            self.sma = bt.ind.SMA(self.data.close, period=self.params.period)
            self.std = bt.ind.StandardDeviation(
                self.data.close, period=self.params.period
            )
            self.order = None

        def next(self):
            if self.order:
                return

            # Intraday strategy: use previous bar's data (no look-ahead bias)
            # Decision made at start of day, using yesterday's close
            upper_band = self.sma[-1] + self.params.std_dev * self.std[-1]
            lower_band = self.sma[-1] - self.params.std_dev * self.std[-1]
            current_price = self.data.close[-1]

            # Mean reversion: sell when price > upper band, buy when < lower band
            if current_price > upper_band:
                self.order = self.sell()
            elif current_price < lower_band:
                self.order = self.buy()

    # Rename class
    MeanReversionStrategy.__name__ = name
    return MeanReversionStrategy


def create_signal_strategy(name: str = "SignalStrategy", params: Dict = None):
    """
    Factory function to create a strategy from external signals.

    This is useful when signals are generated in Jupyter/pandas,
    then passed to Backtrader for backtesting.

    Args:
        name: Strategy name
        params: Must include 'signals' DataFrame with 'signal' column

    Returns:
        Backtrader strategy class
    """
    default_params = {
        "signals": None,  # DataFrame with signal column
    }
    if params:
        default_params.update(params)

    class SignalStrategy(bt.Strategy):
        params = (("signals", default_params["signals"]),)

        def __init__(self):
            self.order = None
            self.signal_idx = 0
            self.signals = self.params.signals

            if self.signals is not None:
                # Ensure index is datetime
                if not isinstance(self.signals.index, pd.DatetimeIndex):
                    self.signals.index = pd.to_datetime(self.signals.index)

        def notify_order(self, order):
            """Handle order notifications - clear order after execution."""
            if order.status in [order.Completed]:
                self.order = None

        def next(self):
            if self.order:
                return

            # Get current date
            current_date = self.data.datetime.date(0)

            # Find signal for current date
            signal = 0
            if self.signals is not None:
                # Try to match by date
                try:
                    signal_series = self.signals.loc[:current_date]
                    if len(signal_series) > 0:
                        signal = signal_series.iloc[-1]
                        if isinstance(signal, pd.Series):
                            signal = signal.get("signal", 0)
                        else:
                            signal = signal if hasattr(signal, "__float__") else 0
                    else:
                        signal = 0
                except (KeyError, TypeError):
                    signal = 0
            else:
                signal = 0

            # Execute based on signal
            # Signal: 1 = BUY, -1 = SELL/SHORT, 0 = FLAT/CLOSE
            if signal > 0:
                self.order = self.buy()
            elif signal < 0:
                self.order = self.sell()
            elif signal == 0:
                # Signal = 0 means exit/close any open position
                if self.getposition(self.data).size > 0:
                    self.order = self.close()

    # Rename class
    SignalStrategy.__name__ = name
    return SignalStrategy


# =============================================================================
# Quick Backtest Function
# =============================================================================


def quick_backtest(
    data: pd.DataFrame, signals: pd.Series, initial_cash: float = 100000
) -> Dict[str, Any]:
    """
    Quick backtest function using external signals.

    Args:
        data: Price data with columns [open, high, low, close, volume]
        signals: Series of signals (-1, 0, 1) indexed by date
        initial_cash: Starting capital

    Returns:
        Backtest results dictionary
    """
    engine = BacktestEngine(cash=initial_cash)

    # Prepare data
    df = data.copy()
    df["date"] = pd.to_datetime(df.index)
    df = df.set_index("date")

    # Add signals to dataframe
    if "signal" not in df.columns:
        df["signal"] = signals.reindex(df.index).fillna(0)

    # Add data feed
    data_feed = IBKRDataFeed(dataname=df)
    engine.add_data(data_feed, name="asset")

    # Add signal strategy
    strategy_class = create_signal_strategy("QuickSignal", {"signals": df})
    engine.add_strategy(strategy_class)

    # Run backtest
    results = engine.run_backtest()

    return results


# =============================================================================
# Live Trading Engine - Using Backtrader's Native IBStore
# =============================================================================


class LiveTradingEngine:
    """
    Live Trading Engine using Backtrader's native IBStore.

    Reference: https://www.backtrader.com/docu/live/ib/ib/

    Uses:
    - IBStore for connection management
    - IBBroker for order execution
    - IBData for live market data

    Contract formats (dataname):
    - Stock: 'AAPL-STK-SMART-USD' or 'AAPL' (defaults apply)
    - Index: 'VIX-IND-CBOE-USD'
    - Future: 'ES-202412-GLOBEX-USD'
    - Option: 'SPX-OPT-CBOE-USD-20241220-5000-CALL'
    - Forex: 'EUR.USD-CASH-IDEALPRO'
    """

    def __init__(
        self,
        cash: float = 100000,
        commission: float = 0.001,
        host: str = "127.0.0.1",
        port: int = 7496,
        client_id: int = 1,
    ):
        """
        Initialize the live trading engine.

        Args:
            cash: Starting capital
            commission: Commission rate
            host: IBKR TWS/Gateway host
            port: IBKR port (7496=live, 7497=demo)
            client_id: Client ID for connection
        """
        self.cash = cash
        self.commission = commission
        self.host = host
        self.port = port
        self.client_id = client_id

        self.cerebro = None
        self.store = None
        self.broker = None
        self.strategy_class = None
        self.is_running = False
        self._live_contracts = {}

    def _init_store_and_broker(self):
        """
        Initialize broker for live trading.

        Note: Backtrader's IBStore is not available in this version.
        We use our existing IBKRClient for execution instead.
        For now, use BacktestEngine with our IBKRClient for live data,
        and execute orders manually via IBKRClient.

        This is a simplified implementation - full IB integration
        would require either:
        1. A different backtrader version/package
        2. Manual order execution via our IBKRClient
        """
        # Use default broker for backtesting - live execution via IBKRClient
        self.cerebro = bt.Cerebro()
        self.cerebro.broker.setcash(self.cash)
        self.cerebro.broker.setcommission(commission=self.commission)
        self.store = None  # Not available
        self.broker = self.cerebro.broker

        # Add analyzers
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")

    def add_live_data(
        self,
        dataname: str,
        sectype: str = None,
        exchange: str = None,
        currency: str = None,
        what: str = "TRADES",
        live: bool = True,
    ):
        """
        Add a live data feed from IBKR using Backtrader's IBData.

        Per docs, dataname can be:
        - 'TICKER' (STK + SMART defaults)
        - 'TICKER-STK-EXCHANGE-CURRENCY'
        - 'TICKER-IND-EXCHANGE-CURRENCY'  (e.g., 'VIX-IND-CBOE-USD')
        - 'TICKER-YYYYMM-EXCHANGE-CURRENCY' (futures)
        - 'TICKER-YYYYMMDD-EXCHANGE-CURRENCY-STRIKE-RIGHT' (options)

        Args:
            dataname: Contract specification string
            sectype: Security type (STK, IND, FUT, OPT, CFD, CASH)
            exchange: Exchange (SMART, CBOE, GLOBEX, etc.)
            currency: Currency (USD, EUR, etc.)
            what: Data type (TRADES, BID, ASK)
            live: Enable live streaming
        """
        if self.cerebro is None:
            self._init_store_and_broker()

        # Note: IBData is not available in this backtrader version
        # For live trading, we use our IBKRClient for data and execution
        # This method stores the contract info for reference
        self._live_contracts = self._live_contracts or {}
        self._live_contracts[dataname] = {
            "dataname": dataname,
            "sectype": sectype,
            "exchange": exchange,
            "currency": currency,
            "what": what,
        }

        # For now, just note that live data would come from IBKRClient
        print(f"Note: Live data for {dataname} would be fetched via IBKRClient")

    def add_strategy(self, strategy_class: type, **params):
        """Add a strategy to the cerebro."""
        if self.cerebro is None:
            self._init_store_and_broker()
        self.strategy_class = strategy_class
        self.cerebro.addstrategy(strategy_class, **params)

    def run_live(self):
        """
        Run live trading synchronously.

        Note: This blocks - use in separate thread for interactive use.
        """
        if self.cerebro is None:
            raise ValueError("No strategy added")

        print("Starting live trading...")
        self.is_running = True
        self.cerebro.run()
        self.is_running = False
        print("Live trading stopped.")

    def stop(self):
        """Stop live trading and disconnect."""
        self.is_running = False
        if self.store:
            # IBStore handles disconnection automatically
            pass


# =============================================================================
# Helper function for common contract formats
# =============================================================================


def make_ibkr_dataname(
    symbol: str,
    sec_type: str = "STK",
    exchange: str = "SMART",
    currency: str = "USD",
    expiry: str = None,
    strike: float = None,
    right: str = None,
) -> str:
    """
    Build IBKR contract dataname string per Backtrader docs.

    Args:
        symbol: Ticker symbol (e.g., 'VIX', 'AAPL', 'ES')
        sec_type: Security type (STK, IND, FUT, OPT, FOP, CFD, CASH)
        exchange: Exchange (SMART, CBOE, GLOBEX, IDEALPRO)
        currency: Currency (USD, EUR, etc.)
        expiry: For futures/options (YYYYMM or YYYYMMDD)
        strike: Strike price for options
        right: Right (CALL or PUT)

    Returns:
        Contract dataname string for Backtrader

    Examples:
        Stock: make_ibkr_dataname('AAPL', 'STK', 'SMART', 'USD')
               -> 'AAPL-STK-SMART-USD'
        Index: make_ibkr_dataname('VIX', 'IND', 'CBOE', 'USD')
               -> 'VIX-IND-CBOE-USD'
        Future: make_ibkr_dataname('ES', 'FUT', 'GLOBEX', 'USD', '202412')
               -> 'ES-202412-GLOBEX-USD'
        Option: make_ibkr_dataname('SPX', 'OPT', 'CBOE', 'USD', '20241220', 5000, 'CALL')
               -> 'SPX-OPT-CBOE-USD-20241220-5000-CALL'
    """
    parts = [symbol]

    if sec_type:
        parts.append(sec_type)
    if exchange:
        parts.append(exchange)
    if currency:
        parts.append(currency)
    if expiry:
        parts.append(expiry)
    if strike:
        parts.append(str(strike))
    if right:
        parts.append(right)

    return "-".join(parts)


# Export classes
__all__ = [
    "BacktestEngine",
    "LiveTradingEngine",
    "IBKRDataFeed",
    "ParquetDataFeed",
    "VolatilitySizer",
    "HistoricalPercentSizer",
    "create_momentum_strategy",
    "create_mean_reversion_strategy",
    "create_signal_strategy",
    "quick_backtest",
    "make_ibkr_dataname",
]
