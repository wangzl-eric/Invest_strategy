"""
Portfolio Builder: Connect Signals → Optimization → Backtest
=============================================================
A unified pipeline for multi-asset quantitative strategy development.

Usage:
    from backtests.builder import PortfolioBuilder

    builder = PortfolioBuilder()
    builder.set_universe(['SPY', 'TLT', 'GLD', 'UUP'])
    builder.set_signals(['momentum_60_21', 'mean_reversion'])
    builder.set_optimization('risk_parity')

    result = builder.run()
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd

# Ensure backtests is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class PortfolioConfig:
    """Configuration for portfolio construction."""

    # Universe
    universe: List[str] = field(default_factory=lambda: ["SPY", "TLT", "GLD"])

    # Signals to use
    signals: List[str] = field(default_factory=lambda: ["momentum_60_21"])

    # Optimization method
    optimization: str = (
        "mean_variance"  # mean_variance, risk_parity, black_litterman, equal_weight
    )

    # Risk parameters
    risk_aversion: float = 1.0
    max_weight: float = 0.30
    min_weight: float = -0.10
    target_gross: float = 1.0

    # Rebalancing
    rebalance_frequency: str = "monthly"  # daily, weekly, monthly
    turnover_penalty: float = 0.0

    # Backtest params
    initial_cash: float = 100000
    commission: float = 0.001


class PortfolioBuilder:
    """
    Unified portfolio construction pipeline.

    Flow:
    1. Load data for universe
    2. Compute signals for each asset
    3. Generate alpha (signal scores)
    4. Optimize weights
    5. Backtest and analyze
    """

    def __init__(self, config: Optional[PortfolioConfig] = None):
        self.config = config or PortfolioConfig()
        self.data: Dict[str, pd.DataFrame] = {}
        self.signals: Dict[str, pd.DataFrame] = {}
        self.weights: Optional[pd.Series] = None
        self.backtest_result: Optional[Dict] = None

    def load_data(
        self,
        data_loader: Callable[[str, str, str], pd.DataFrame],
        start_date: str,
        end_date: str,
        exchange: str = "XNYS",
        align_calendar: bool = True,
    ) -> "PortfolioBuilder":
        """
        Load price data for universe with optional trading-day alignment.

        Args:
            data_loader: Function(ticker, start, end) -> DataFrame
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            exchange: exchange_calendars exchange code for holiday filtering
                (default "XNYS" for NYSE).  Only used when align_calendar=True.
            align_calendar: When True (default), strip non-trading days from
                the combined price DataFrame using the exchange calendar.
                Prevents 1-3 day look-ahead artifacts from holiday rows.
        """
        print(f"Loading data for {self.config.universe}...")

        close_prices = {}
        for ticker in self.config.universe:
            try:
                df = data_loader(ticker, start_date, end_date)
                if df is not None and len(df) > 0:
                    close_prices[ticker] = df["close"]
                    self.data[ticker] = df
            except Exception as e:
                print(f"  Failed to load {ticker}: {e}")

        self.prices = pd.DataFrame(close_prices)

        # Strip non-trading days (holidays, weekends) to avoid look-ahead
        # artifacts from calendar gaps in resampled daily data.
        if align_calendar and not self.prices.empty:
            from backtests.calendar import align_to_trading_days

            n_before = len(self.prices)
            self.prices = align_to_trading_days(self.prices, exchange=exchange)
            n_dropped = n_before - len(self.prices)
            if n_dropped > 0:
                print(f"  Calendar alignment: dropped {n_dropped} non-trading rows")

        print(f"  Loaded {len(self.prices)} days of data")

        return self

    def compute_signals(
        self,
        signal_config: Optional[Dict[str, Dict]] = None,
    ) -> "PortfolioBuilder":
        """
        Compute signals for each asset.

        Args:
            signal_config: Dict of signal_name -> params
        """
        from backtests.strategies.signals import compute_signal_pandas, get_signal

        signal_config = signal_config or {}

        print(f"Computing signals: {self.config.signals}")

        for signal_name in self.config.signals:
            # Get signal class from registry
            signal_class = get_signal(signal_name)
            if signal_class is None:
                print(f"  Signal {signal_name} not found, skipping")
                continue

            # Compute signal using pandas (for non-Backtrader use)
            # Get params if any
            params = signal_config.get(signal_name, {})

            # Use the new compute_signal_pandas function
            sig = compute_signal_pandas(signal_class, self.prices, **params)
            self.signals[signal_name] = sig

        return self

    def generate_alpha(
        self,
        method: str = "mean",
    ) -> pd.Series:
        """
        Generate alpha scores from signals.

        Methods:
        - mean: Simple average of all signals
        - weighted: Weighted average
        - best: Use best performing signal
        """
        if not self.signals:
            raise ValueError("No signals computed. Call compute_signals() first.")

        if method == "mean":
            # Align signals
            aligned = []
            for sig_df in self.signals.values():
                if isinstance(sig_df, pd.DataFrame):
                    aligned.append(sig_df.mean(axis=1))
                else:
                    aligned.append(sig_df)

            alpha = pd.concat(aligned, axis=1).mean(axis=1)

        elif method == "best":
            # Use most recent signal value
            alphas = []
            for sig_df in self.signals.values():
                if isinstance(sig_df, pd.DataFrame):
                    alphas.append(sig_df.iloc[-1])
                else:
                    alphas.append(sig_df.iloc[-1])
            alpha = pd.concat(alphas)

        else:
            raise ValueError(f"Unknown alpha method: {method}")

        # Normalize to weights
        self.alpha = alpha.dropna()
        return self.alpha

    def optimize_weights(
        self,
        method: Optional[str] = None,
        as_of_date: Optional[str] = None,
    ) -> pd.Series:
        """
        Optimize portfolio weights.

        Methods:
        - mean_variance: Markowitz mean-variance
        - risk_parity: Equal risk contribution
        - equal_weight: 1/N allocation
        - black_litterman: Bayesian prior

        Args:
            method: Optimization method (default: self.config.optimization)
            as_of_date: Only use data up to this date for estimation (avoids look-ahead).
                        If None, uses all available data.
        """
        from portfolio.optimizer import OptimizationConfig, mean_variance_optimize
        from portfolio.risk import ledoit_wolf_cov

        method = method or self.config.optimization

        # Get returns for covariance estimation — only use data up to as_of_date
        prices = self.prices
        if as_of_date is not None:
            prices = prices.loc[:as_of_date]
        returns = prices.pct_change().dropna()

        if method == "equal_weight":
            common_assets = list(returns.columns)
            weights = pd.Series(1.0 / len(common_assets), index=common_assets)
            self.weights = weights.fillna(0)
            return self.weights

        # Generate alpha if not exists (needed for non-equal-weight methods)
        if not hasattr(self, "alpha"):
            self.generate_alpha()

        # Convert alpha to expected returns
        # Normalize alpha to annualized expected returns
        alpha_norm = (self.alpha - self.alpha.mean()) / self.alpha.std()
        expected_returns = alpha_norm * returns.std() * np.sqrt(252)  # Annualize

        # Handle missing assets
        common_assets = expected_returns.dropna().index.intersection(returns.columns)
        expected_returns = expected_returns[common_assets]

        if method == "mean_variance":
            cfg = OptimizationConfig(
                risk_aversion=self.config.risk_aversion,
                turnover_aversion=self.config.turnover_penalty,
                max_weight=self.config.max_weight,
                min_weight=self.config.min_weight,
                target_gross=self.config.target_gross,
            )
            cov = ledoit_wolf_cov(returns[common_assets])
            weights = mean_variance_optimize(
                expected_returns=expected_returns,
                cov=cov,
                cfg=cfg,
            )

        elif method == "risk_parity":
            weights = self._risk_parity_weights(returns[common_assets])

        else:
            raise ValueError(f"Unknown optimization method: {method}")

        self.weights = weights.fillna(0)
        return self.weights

    def _risk_parity_weights(self, returns: pd.DataFrame) -> pd.Series:
        """Compute risk parity weights using Ledoit-Wolf shrinkage covariance.

        Uses ledoit_wolf_cov() for consistency with the mean_variance path and
        to avoid instability when sample size is small relative to asset count.
        """
        from portfolio.risk import ledoit_wolf_cov

        cov = ledoit_wolf_cov(returns)
        vol = np.sqrt(np.diag(cov.values))

        # Inverse vol weights (simplified risk parity)
        inv_vol = 1.0 / np.where(vol > 0, vol, np.nan)
        inv_vol = np.nan_to_num(inv_vol, nan=0.0)
        total = inv_vol.sum()
        if total == 0:
            n = len(returns.columns)
            return pd.Series(1.0 / n, index=returns.columns)
        weights = inv_vol / total

        return pd.Series(weights, index=returns.columns)

    def _optimize_weights_as_of(
        self,
        as_of_date: str,
        common_assets: List[str],
    ) -> pd.Series:
        """Re-optimize portfolio weights using only data up to ``as_of_date``.

        This is the per-rebalance optimization called inside ``backtest()``
        to avoid static-weight look-ahead (blocker B3 in the PM advisory).

        The method mirrors ``optimize_weights()`` but does not mutate
        ``self.weights`` or ``self.alpha`` — it returns a new Series.

        Args:
            as_of_date: ISO date string (YYYY-MM-DD). Only prices up to and
                including this date are used for covariance estimation.
            common_assets: Asset subset to include in the result.

        Returns:
            pd.Series of portfolio weights indexed by asset name.
        """
        from portfolio.optimizer import OptimizationConfig, mean_variance_optimize
        from portfolio.risk import ledoit_wolf_cov

        method = self.config.optimization
        prices_to_date = self.prices.loc[:as_of_date, common_assets]
        returns_to_date = prices_to_date.pct_change().dropna()

        # Need at least 30 observations for a meaningful covariance estimate
        if len(returns_to_date) < 30:
            n = len(common_assets)
            return pd.Series(1.0 / n, index=common_assets)

        if method == "equal_weight":
            n = len(common_assets)
            return pd.Series(1.0 / n, index=common_assets)

        if method == "risk_parity":
            return self._risk_parity_weights(returns_to_date)

        # mean_variance — compute alpha from signals as-of this date
        alpha_as_of = self._alpha_as_of(as_of_date, common_assets, returns_to_date)
        if alpha_as_of is None:
            # Fall back to equal weight when alpha cannot be computed
            n = len(common_assets)
            return pd.Series(1.0 / n, index=common_assets)

        alpha_norm = (alpha_as_of - alpha_as_of.mean()) / (
            alpha_as_of.std() if alpha_as_of.std() > 0 else 1.0
        )
        expected_returns = alpha_norm * returns_to_date.std() * np.sqrt(252)
        expected_returns = expected_returns.dropna()

        if expected_returns.empty:
            n = len(common_assets)
            return pd.Series(1.0 / n, index=common_assets)

        cfg = OptimizationConfig(
            risk_aversion=self.config.risk_aversion,
            turnover_aversion=self.config.turnover_penalty,
            max_weight=self.config.max_weight,
            min_weight=self.config.min_weight,
            target_gross=self.config.target_gross,
        )
        cov = ledoit_wolf_cov(returns_to_date[expected_returns.index])
        try:
            return mean_variance_optimize(
                expected_returns=expected_returns,
                cov=cov,
                cfg=cfg,
            )
        except RuntimeError:
            n = len(common_assets)
            return pd.Series(1.0 / n, index=common_assets)

    def _alpha_as_of(
        self,
        as_of_date: str,
        common_assets: List[str],
        returns_to_date: "pd.DataFrame",
    ) -> "Optional[pd.Series]":
        """Compute per-asset alpha using signal values at ``as_of_date``.

        Returns None when no signals are configured or computable.
        """
        if not getattr(self, "signals", None):
            return None

        asset_alphas: Dict[str, float] = {}
        for asset in common_assets:
            asset_sig_values = []
            for sig_df in self.signals.values():
                col = asset if asset in sig_df.columns else None
                if col is None and isinstance(sig_df, pd.Series):
                    # Single-column signal stored as Series
                    val = (
                        float(sig_df.loc[:as_of_date].iloc[-1])
                        if len(sig_df.loc[:as_of_date]) > 0
                        else np.nan
                    )
                    asset_sig_values.append(val)
                elif col is not None:
                    val = (
                        float(sig_df.loc[:as_of_date, col].iloc[-1])
                        if len(sig_df.loc[:as_of_date]) > 0
                        else np.nan
                    )
                    asset_sig_values.append(val)
            if asset_sig_values:
                valid = [v for v in asset_sig_values if not np.isnan(v)]
                asset_alphas[asset] = float(np.mean(valid)) if valid else np.nan

        if not asset_alphas:
            return None

        return pd.Series(asset_alphas).reindex(common_assets)

    def backtest(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        cost_model: Optional[Any] = None,
        dynamic_reoptimize: bool = True,
    ) -> Dict[str, Any]:
        """
        Backtest the portfolio using computed signals and optimized weights.

        Uses a vectorized approach: at each rebalance point, weights are
        re-optimized using only the data available up to that date (no
        look-ahead bias). Transaction costs are applied via the CostModel
        hierarchy when a ``cost_model`` is provided.

        Args:
            start_date: Backtest start (YYYY-MM-DD). Defaults to 252 days in.
            end_date: Backtest end (YYYY-MM-DD). Defaults to last available.
            cost_model: A ``CostModel`` instance from ``backtests.costs``.
                When provided this replaces the flat ``config.commission``
                rate. When None, falls back to the flat rate.
            dynamic_reoptimize: If True (default), weights are re-optimized at
                every rebalance date using only data available up to that date.
                If False, the pre-computed ``self.weights`` are used throughout
                (faster but overstates weight stability).
        """
        if self.weights is None:
            self.optimize_weights()

        # Determine backtest period
        max_lookback = 252  # Default warmup
        if start_date is None:
            start_date = self.prices.index[min(max_lookback, len(self.prices) - 50)]
        if end_date is None:
            end_date = self.prices.index[-1]

        prices = self.prices.loc[start_date:end_date]
        returns = prices.pct_change().dropna()

        if len(returns) < 20:
            self.backtest_result = {}
            return {}

        # Determine rebalance dates
        rebal_freq = self.config.rebalance_frequency
        if rebal_freq == "daily":
            rebal_dates = returns.index
        elif rebal_freq == "weekly":
            rebal_dates = returns.resample("W-FRI").last().dropna().index
        else:  # monthly
            rebal_dates = returns.resample("M").last().dropna().index

        # Build weight matrix: at each date, what are the portfolio weights?
        # Seed from the pre-computed initial weights to get the asset list.
        common_assets = [a for a in self.weights.index if a in returns.columns]
        if not common_assets:
            self.backtest_result = {}
            return {}

        weight_matrix = pd.DataFrame(0.0, index=returns.index, columns=common_assets)

        current_weights = self.weights[common_assets].fillna(0)
        for date in returns.index:
            is_rebal = date in rebal_dates or date == returns.index[0]
            if is_rebal and dynamic_reoptimize:
                # Re-optimize using only data available up to this date.
                # This is the key fix for B3: weights are NOT static.
                as_of = str(date.date())
                try:
                    new_weights = self._optimize_weights_as_of(
                        as_of_date=as_of,
                        common_assets=common_assets,
                    )
                    current_weights = new_weights.reindex(common_assets).fillna(0)
                except Exception:
                    # Fall back to previous weights on optimization failure
                    pass
            weight_matrix.loc[date] = current_weights

        # Compute portfolio returns: sum of (weight * asset return) per day
        asset_returns = returns[common_assets]
        portfolio_returns = (weight_matrix * asset_returns).sum(axis=1)

        # Apply transaction costs at rebalance points using CostModel hierarchy
        # or fall back to flat commission rate when no cost_model is supplied.
        weight_changes = weight_matrix.diff().abs()
        # First row has NaN diff — treat as full turnover on day 1
        weight_changes.iloc[0] = weight_matrix.iloc[0].abs()
        total_turnover = weight_changes.sum(axis=1)

        if cost_model is not None:
            # CostModel.calculate_cost(quantity, price) — for a vectorized
            # path we use notional weight change as the "quantity" and 1.0 as
            # the "price" so cost is expressed as a fraction of portfolio value.
            cost_series = total_turnover.apply(
                lambda turnover: cost_model.calculate_cost(
                    quantity=float(turnover), price=1.0
                )
            )
            portfolio_returns = portfolio_returns - cost_series
        elif self.config.commission > 0:
            costs = total_turnover * self.config.commission
            portfolio_returns = portfolio_returns - costs

        # Compute equity curve
        cumulative = (1 + portfolio_returns).cumprod() * self.config.initial_cash
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak

        # Calculate metrics
        total_return = cumulative.iloc[-1] / self.config.initial_cash - 1
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe = (
            portfolio_returns.mean() / portfolio_returns.std() * np.sqrt(252)
            if portfolio_returns.std() > 0
            else 0
        )
        max_dd = drawdown.min()
        n_days = len(portfolio_returns)

        self.backtest_result = {
            "total_return": total_return,
            "annualized_return": (1 + total_return) ** (252 / n_days) - 1
            if n_days > 0
            else 0,
            "volatility": volatility,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd,
            "n_days": n_days,
            "weights": self.weights[common_assets].to_dict(),
            "equity_curve": pd.DataFrame(
                {
                    "date": cumulative.index,
                    "portfolio_value": cumulative.values,
                }
            ),
            "daily_returns": portfolio_returns,
        }
        return self.backtest_result

    def get_portfolio_metrics(self) -> Dict[str, float]:
        """Calculate portfolio-level metrics."""
        if not self.backtest_result:
            return {}

        # New vectorized backtest returns metrics directly
        return {
            k: v for k, v in self.backtest_result.items() if isinstance(v, (int, float))
        }

    def summary(self) -> pd.DataFrame:
        """Print portfolio summary."""
        print("\n" + "=" * 60)
        print("PORTFOLIO SUMMARY")
        print("=" * 60)

        print(f"\nUniverse: {self.config.universe}")
        print(f"Signals: {self.config.signals}")
        print(f"Optimization: {self.config.optimization}")

        print("\n--- Weights ---")
        if self.weights is not None:
            print(self.weights.sort_values(ascending=False).to_string())

        print("\n--- Performance ---")
        metrics = self.get_portfolio_metrics()
        for k, v in metrics.items():
            if isinstance(v, float):
                print(
                    f"  {k}: {v*100:.2f}%"
                    if "return" in k or "drawdown" in k
                    else f"  {k}: {v:.2f}"
                )

        print("=" * 60 + "\n")

        return self.weights


# ============================================================================
# Multi-Asset Strategy Examples
# ============================================================================


class MultiAssetStrategy:
    """
    Example multi-asset strategies that use the portfolio builder.
    """

    @staticmethod
    def trend_following(universe: List[str], start: str, end: str) -> PortfolioBuilder:
        """Trend-following strategy using momentum signals."""

        builder = PortfolioBuilder(
            PortfolioConfig(
                universe=universe,
                signals=["momentum_60_21"],
                optimization="mean_variance",
                risk_aversion=2.0,
            )
        )

        import yfinance as yf

        def loader(ticker, start, end):
            return yf.download(ticker, start=start, end=end, progress=False)

        builder.load_data(loader, start, end)
        builder.compute_signals()
        builder.optimize_weights()

        return builder

    @staticmethod
    def risk_parity_strategy(
        universe: List[str], start: str, end: str
    ) -> PortfolioBuilder:
        """Risk parity strategy."""

        builder = PortfolioBuilder(
            PortfolioConfig(
                universe=universe,
                signals=[],  # No signals, pure risk parity
                optimization="risk_parity",
            )
        )

        import yfinance as yf

        def loader(ticker, start, end):
            return yf.download(ticker, start=start, end=end, progress=False)

        builder.load_data(loader, start, end)
        builder.optimize_weights()

        return builder

    @staticmethod
    def blended_strategy(universe: List[str], start: str, end: str) -> PortfolioBuilder:
        """Blended momentum + risk parity strategy."""

        builder = PortfolioBuilder(
            PortfolioConfig(
                universe=universe,
                signals=["momentum_60_21", "mean_reversion"],
                optimization="mean_variance",
                risk_aversion=1.5,
                max_weight=0.25,
            )
        )

        import yfinance as yf

        def loader(ticker, start, end):
            return yf.download(ticker, start=start, end=end, progress=False)

        builder.load_data(loader, start, end)
        builder.compute_signals()
        builder.generate_alpha(method="mean")
        builder.optimize_weights()

        return builder


__all__ = [
    "PortfolioBuilder",
    "PortfolioConfig",
    "MultiAssetStrategy",
]
