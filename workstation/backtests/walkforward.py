"""
Walk-Forward Analysis and Cross-Validation Framework
=====================================================
Provides robust backtesting methods:
- Walk-forward optimization (rolling window)
- Train/test cross-validation
- Parameter grid search
- Regime analysis
- Transaction cost sensitivity

Usage:
    from backtests.walkforward import WalkForwardAnalyzer, GridSearch, RegimeAnalyzer

    # Walk-forward
    wfa = WalkForwardAnalyzer(engine_class=BacktestEngine, ...)
    results = wfa.run(train_window=252*2, test_window=63*2, step=63)

    # Grid search
    gs = GridSearch(engine_class=BacktestEngine, ...)
    best_params, all_results = gs.search(param_grid)
"""

from __future__ import annotations

import warnings
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# ============================================================================
# Data Types
# ============================================================================


@dataclass
class WalkForwardResult:
    """Results from a single walk-forward iteration."""

    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime
    params: Dict[str, Any]
    train_metrics: Dict[str, float]
    test_metrics: Dict[str, float]
    equity_curve: pd.DataFrame
    trades: pd.DataFrame


@dataclass
class WalkForwardSummary:
    """Aggregated results from walk-forward analysis."""

    iterations: List[WalkForwardResult]

    # Aggregated metrics
    avg_train_sharpe: float = 0.0
    avg_test_sharpe: float = 0.0
    avg_test_return: float = 0.0
    avg_test_drawdown: float = 0.0
    hit_rate: float = 0.0  # % of iterations where test Sharpe > 0

    # Consistency metrics
    sharpe_consistency: float = 0.0  # std of test Sharpe across iterations
    return_consistency: float = 0.0  # std of test returns

    # Rolling equity
    combined_equity: pd.DataFrame = None

    def __post_init__(self):
        if not self.iterations:
            return

        test_sharpes = [
            it.test_metrics.get("sharpe_ratio", 0) for it in self.iterations
        ]
        test_returns = [
            it.test_metrics.get("annualized_return", 0) for it in self.iterations
        ]

        self.avg_train_sharpe = np.mean(
            [it.train_metrics.get("sharpe_ratio", 0) for it in self.iterations]
        )
        self.avg_test_sharpe = np.mean(test_sharpes)
        self.avg_test_return = np.mean(test_returns)
        self.avg_test_drawdown = np.mean(
            [it.test_metrics.get("max_drawdown", 0) for it in self.iterations]
        )
        self.hit_rate = np.mean([1 if s > 0 else 0 for s in test_sharpes])

        self.sharpe_consistency = np.std(test_sharpes) if test_sharpes else 0
        self.return_consistency = np.std(test_returns) if test_returns else 0

        # Combine equity curves
        if self.iterations:
            equity_frames = []
            for it in self.iterations:
                if it.equity_curve is not None and len(it.equity_curve) > 0:
                    eq = it.equity_curve.copy()
                    eq["iteration"] = len(equity_frames)
                    equity_frames.append(eq)
            if equity_frames:
                self.combined_equity = pd.concat(equity_frames, ignore_index=True)


@dataclass
class GridSearchResult:
    """Results from parameter grid search."""

    best_params: Dict[str, Any]
    best_score: float
    all_results: List[Dict[str, Any]]

    @property
    def results_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.all_results)


# ============================================================================
# Walk-Forward Analyzer
# ============================================================================


class WalkForwardAnalyzer:
    """
    Walk-forward optimization with rolling train/test windows.

    Key features:
    - Rolling window: train on past, test on future
    - Anchored window: train from start to point, test on next window
    - Walk-forward with re-optimization at each step

    Example:
        wfa = WalkForwardAnalyzer(
            engine_class=BacktestEngine,
            data_loader=load_data,  # function that returns DataFrame
            strategy_factory=create_strategy,
            metric='sharpe_ratio'  # metric to optimize
        )
        summary = wfa.run(
            train_window=252 * 2,  # 2 years train
            test_window=63,         # 3 months test
            step=21                  # roll forward 1 month
        )
    """

    def __init__(
        self,
        engine_class: Callable,
        data_loader: Callable[[str, str], pd.DataFrame],
        strategy_factory: Callable[[Dict], type],
        metric: str = "sharpe_ratio",
        param_space: Optional[Dict[str, List]] = None,
    ):
        """
        Args:
            engine_class: BacktestEngine class or similar
            data_loader: Function(start_date, end_date) -> DataFrame
            strategy_factory: Function(params) -> bt.Strategy class
            metric: Metric to optimize ('sharpe_ratio', 'calmar_ratio', 'total_return')
            param_space: Dict of param name -> list of values for optimization
        """
        self.engine_class = engine_class
        self.data_loader = data_loader
        self.strategy_factory = strategy_factory
        self.metric = metric
        self.param_space = param_space or {}

    def run(
        self,
        start_date: str,
        end_date: str,
        train_window: int,  # days
        test_window: int,  # days
        step: int = None,  # days to roll forward (default: test_window)
        optimize: bool = True,
    ) -> WalkForwardSummary:
        """
        Run walk-forward analysis.

        Args:
            start_date: Full data start (YYYY-MM-DD)
            end_date: Full data end (YYYY-MM-DD)
            train_window: Training period in trading days
            test_window: Testing period in trading days
            step: Roll forward step (default: test_window = non-overlapping)
            optimize: Whether to optimize params on train data

        Returns:
            WalkForwardSummary with aggregated results
        """
        # Load full dataset to get date range
        full_data = self.data_loader(start_date, end_date)
        if full_data.empty:
            raise ValueError(f"No data loaded for {start_date} to {end_date}")

        dates = pd.to_datetime(full_data.index).sort_values()
        if step is None:
            step = test_window

        iterations = []

        # Walk-forward windows
        train_start_idx = 0

        while True:
            train_start = dates[train_start_idx]
            train_end_idx = train_start_idx + train_window
            test_start_idx = train_end_idx
            test_end_idx = test_start_idx + test_window

            if test_end_idx >= len(dates):
                break

            train_end = dates[train_end_idx]
            test_start = dates[test_start_idx]
            test_end = dates[test_end_idx]

            # Skip if not enough test data
            if test_end_idx - test_start_idx < 20:
                train_start_idx += step
                continue

            # Load train/test data
            train_data = full_data.loc[train_start:train_end].copy()
            test_data = full_data.loc[test_start:test_end].copy()

            if (
                len(train_data) < train_window * 0.8
                or len(test_data) < test_window * 0.8
            ):
                train_start_idx += step
                continue

            # Optimize or use fixed params
            if optimize and self.param_space:
                best_params = self._optimize_params(train_data)
            else:
                best_params = {}

            # Run train backtest (for reference)
            train_metrics = self._run_backtest(train_data, best_params)

            # Run test backtest
            test_metrics, equity, trades = self._run_backtest(
                test_data, best_params, capture_equity=True
            )

            iterations.append(
                WalkForwardResult(
                    train_start=train_start,
                    train_end=train_end,
                    test_start=test_start,
                    test_end=test_end,
                    params=best_params,
                    train_metrics=train_metrics,
                    test_metrics=test_metrics,
                    equity_curve=equity,
                    trades=trades,
                )
            )

            train_start_idx += step

        return WalkForwardSummary(iterations=iterations)

    def _optimize_params(self, train_data: pd.DataFrame) -> Dict[str, Any]:
        """Find best params on training data."""
        from itertools import product

        best_score = -np.inf
        best_params = {}

        # Grid search over param space
        keys = list(self.param_space.keys())
        values = list(self.param_space.values())

        for combo in product(*values):
            params = dict(zip(keys, combo))
            try:
                metrics = self._run_backtest(train_data, params)
                score = metrics.get(self.metric, 0) or 0
                if score > best_score:
                    best_score = score
                    best_params = params
            except Exception:
                continue

        return best_params

    def _run_backtest(
        self, data: pd.DataFrame, params: Dict, capture_equity: bool = False
    ) -> Tuple[Dict[str, float], pd.DataFrame, pd.DataFrame]:
        """Run backtest and return metrics."""
        engine = self.engine_class(cash=100000, commission=0.001)

        # Prepare data
        df = data.copy()
        df["date"] = pd.to_datetime(df.index)
        df = df.reset_index(drop=True)
        df.columns = ["date", "open", "high", "low", "close", "volume"]

        from backend.backtest_engine import IBKRDataFeed

        data_feed = IBKRDataFeed(dataname=df)
        engine.add_data(data_feed, name="asset")

        # Add strategy
        strategy_class = self.strategy_factory(params)
        engine.add_strategy(strategy_class)

        # Run
        result = engine.run_backtest()

        metrics = {
            "sharpe_ratio": result.get("sharpe_ratio", 0) or 0,
            "total_return": result.get("total_return", 0) or 0,
            "annualized_return": result.get("annualized_return", 0)
            or result.get("total_return", 0)
            or 0,
            "max_drawdown": result.get("max_drawdown", 0) or 0,
            "sortino_ratio": result.get("sortino_ratio", 0) or 0,
            "calmar_ratio": result.get("calmar_ratio", 0) or 0,
            "win_rate": result.get("win_rate", 0) or 0,
            "total_trades": result.get("total_trades", 0) or 0,
        }

        equity = result.get("equity_curve") if capture_equity else None
        trades = result.get("trade_log", pd.DataFrame()) if capture_equity else None

        return metrics, equity, trades


# ============================================================================
# Grid Search Optimizer
# ============================================================================


class GridSearch:
    """
    Parameter grid search with cross-validation.

    Example:
        gs = GridSearch(
            engine_class=BacktestEngine,
            strategy_factory=create_momentum_strategy,
            data=price_data,
            metric='sharpe_ratio'
        )
        best_params, all_results = gs.search({
            'period': [10, 20, 30, 50],
            'threshold': [0.0, 0.01, 0.02]
        })
    """

    def __init__(
        self,
        engine_class: Callable,
        strategy_factory: Callable[[Dict], type],
        data: pd.DataFrame,
        metric: str = "sharpe_ratio",
        use_purged_cv: bool = True,
        signal_lookback: int = 0,
    ):
        """
        Args:
            engine_class: BacktestEngine class or similar.
            strategy_factory: Function(params) -> bt.Strategy class.
            data: Price DataFrame with DatetimeIndex.
            metric: Metric to optimise ('sharpe_ratio', 'calmar_ratio', ...).
            use_purged_cv: When True, use purged K-fold splits from
                ``backtests.stats.cross_validation``. This removes training
                observations whose signal lookback window overlaps with the
                test period, preventing label-leakage during param selection.
            signal_lookback: Approximate signal lookback in trading days.
                Used to purge training observations within ``signal_lookback``
                days before each test fold (approximates label_end_times when
                exact exit times are unavailable). Ignored when 0.
        """
        self.engine_class = engine_class
        self.strategy_factory = strategy_factory
        self.data = data
        self.metric = metric
        self.use_purged_cv = use_purged_cv
        self.signal_lookback = signal_lookback

    def search(
        self,
        param_grid: Dict[str, List],
        cv_folds: int = 5,
    ) -> GridSearchResult:
        """
        Run grid search over parameter combinations with time-series CV.

        Args:
            param_grid: Dict of param name -> list of values
            cv_folds: Number of expanding-window CV folds (default 5)

        Returns:
            GridSearchResult with best params and all results
        """
        from itertools import product

        keys = list(param_grid.keys())
        values = list(param_grid.values())

        # Build time-series CV splits (expanding window)
        splits = self._time_series_splits(cv_folds)

        all_results = []
        best_score = -np.inf
        best_params = {}

        for combo in product(*values):
            params = dict(zip(keys, combo))

            # Average score across CV folds
            fold_scores = []
            for train_data, test_data in splits:
                try:
                    metrics = self._run_backtest_on_data(params, test_data)
                    score = metrics.get(self.metric, 0) or 0
                    fold_scores.append(score)
                except Exception:
                    fold_scores.append(0)

            avg_score = np.mean(fold_scores) if fold_scores else 0
            std_score = np.std(fold_scores) if len(fold_scores) > 1 else 0

            result = {
                **params,
                "score": avg_score,
                "score_std": std_score,
                "n_folds": len(fold_scores),
            }
            all_results.append(result)

            if avg_score > best_score:
                best_score = avg_score
                best_params = params

        return GridSearchResult(
            best_params=best_params, best_score=best_score, all_results=all_results
        )

    def _time_series_splits(
        self, n_folds: int
    ) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """Build train/test splits, using purged K-fold when enabled.

        When ``use_purged_cv=True``, delegates to ``purged_kfold_split`` from
        ``backtests.stats.cross_validation`` with an optional lookback-based
        approximation of label end times. This removes training observations
        whose signal lookback window overlaps with the test period.

        When ``use_purged_cv=False``, falls back to simple expanding-window
        splits (legacy behaviour).
        """
        if self.use_purged_cv:
            return self._purged_splits(n_folds)
        return self._expanding_splits(n_folds)

    def _purged_splits(self, n_folds: int) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """Purged K-fold splits using backtests.stats.cross_validation."""
        from backtests.stats.cross_validation import purged_kfold_split

        dates = pd.to_datetime(self.data.index)

        # Approximate label_end_times: entry_date + signal_lookback trading days
        label_end_times: Optional[pd.Series] = None
        if self.signal_lookback > 0:
            # Map each date to its approximate outcome resolution date
            approx_ends = []
            for d in dates:
                loc = dates.get_loc(d)
                end_loc = min(loc + self.signal_lookback, len(dates) - 1)
                approx_ends.append(dates[end_loc])
            label_end_times = pd.Series(approx_ends, index=dates)

        idx_splits = purged_kfold_split(
            dates,
            n_splits=n_folds,
            embargo_pct=0.01,
            label_end_times=label_end_times,
        )

        splits = []
        for train_idx, test_idx in idx_splits:
            train_data = self.data.iloc[train_idx]
            test_data = self.data.iloc[test_idx]
            if len(test_data) >= 20:
                splits.append((train_data, test_data))
        return splits

    def _expanding_splits(
        self, n_folds: int
    ) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """Legacy expanding-window time-series splits (no purging).

        Each fold trains on data[:split_i] and tests on data[split_i:split_i+test_size].
        No data leakage: test always comes after train chronologically.
        """
        n = len(self.data)
        min_train = max(n // (n_folds + 1), 60)  # At least 60 rows for training
        test_size = (n - min_train) // n_folds

        splits = []
        for i in range(n_folds):
            train_end = min_train + i * test_size
            test_end = min(train_end + test_size, n)

            if train_end >= n or test_end <= train_end:
                break

            train_data = self.data.iloc[:train_end]
            test_data = self.data.iloc[train_end:test_end]

            if len(test_data) >= 20:  # Need minimum test data
                splits.append((train_data, test_data))

        return splits

    def _run_backtest(self, params: Dict) -> Dict[str, float]:
        """Run single backtest on full data (legacy, use _run_backtest_on_data)."""
        return self._run_backtest_on_data(params, self.data)

    def _run_backtest_on_data(
        self, params: Dict, data: pd.DataFrame
    ) -> Dict[str, float]:
        """Run single backtest on provided data slice."""
        engine = self.engine_class(cash=100000, commission=0.001)

        df = data.copy()
        df["date"] = pd.to_datetime(df.index)
        df = df.reset_index(drop=True)
        df.columns = ["date", "open", "high", "low", "close", "volume"]

        from backend.backtest_engine import IBKRDataFeed

        data_feed = IBKRDataFeed(dataname=df)
        engine.add_data(data_feed, name="asset")

        strategy_class = self.strategy_factory(params)
        engine.add_strategy(strategy_class)

        result = engine.run_backtest()

        return {
            "sharpe_ratio": result.get("sharpe_ratio", 0) or 0,
            "total_return": result.get("total_return", 0) or 0,
            "max_drawdown": result.get("max_drawdown", 0) or 0,
            "sortino_ratio": result.get("sortino_ratio", 0) or 0,
            "calmar_ratio": result.get("calmar_ratio", 0) or 0,
            "win_rate": result.get("win_rate", 0) or 0,
            "total_trades": result.get("total_trades", 0) or 0,
        }


# ============================================================================
# Regime Analysis
# ============================================================================


class RegimeAnalyzer:
    """
    Analyze strategy performance across market regimes.

    Regimes:
    - Bull/Bear (trend)
    - High/Low volatility
    - Up/Down market

    Example:
        ra = RegimeAnalyzer(strategy_result, market_data)
        regime_metrics = ra.analyze()
        ra.plot_regimes()
    """

    def __init__(
        self,
        strategy_result: Dict,
        market_data: pd.DataFrame,
    ):
        """
        Args:
            strategy_result: Backtest result dict with equity_curve
            market_data: Price data for regime detection
        """
        self.result = strategy_result
        self.market_data = market_data

        self.equity = strategy_result.get("equity_curve")
        if self.equity is not None and isinstance(self.equity, pd.DataFrame):
            if "date" in self.equity.columns:
                self.equity["date"] = pd.to_datetime(self.equity["date"])
                self.equity = self.equity.set_index("date")

    def detect_regimes(
        self,
        vol_lookback: int = 21,
        trend_lookback: int = 50,
    ) -> pd.DataFrame:
        """
        Detect market regimes.

        Returns DataFrame with regime labels:
        - regime: 'bull'|'bear' (based on trend)
        - vol_regime: 'high_vol'|'low_vol'
        """
        prices = (
            self.market_data["close"]
            if "close" in self.market_data.columns
            else self.market_data.iloc[:, 0]
        )

        # Trend regime: price vs SMA
        sma = prices.rolling(trend_lookback).mean()
        trend = (prices > sma).astype(int)  # 1 = bull, 0 = bear

        # Vol regime: rolling vol vs median
        returns = prices.pct_change()
        vol = returns.rolling(vol_lookback).std()
        vol_median = vol.rolling(252).median()
        vol_regime = (vol > vol_median).astype(int)  # 1 = high vol, 0 = low vol

        regimes = pd.DataFrame(
            {
                "trend": trend,
                "volatility": vol,
                "vol_regime": vol_regime,
            },
            index=prices.index,
        )

        return regimes

    def analyze(self) -> Dict[str, Dict[str, float]]:
        """
        Compute strategy metrics by regime.

        Returns:
            Dict of regime -> metrics
        """
        if self.equity is None:
            return {}

        regimes = self.detect_regimes()

        # Align equity with regimes
        common_idx = self.equity.index.intersection(regimes.index)
        equity = self.equity.loc[common_idx]
        regimes = regimes.loc[common_idx]

        # Returns by regime (copy to avoid mutating original)
        equity = equity.copy()
        equity["returns"] = equity["portfolio_value"].pct_change()

        results = {}

        # Trend regimes
        for regime_val, regime_name in [(1, "bull"), (0, "bear")]:
            mask = regimes["trend"] == regime_val
            rets = equity.loc[mask, "returns"].dropna()
            if len(rets) > 0:
                results[f"trend_{regime_name}"] = self._compute_metrics(rets)

        # Vol regimes
        for regime_val, regime_name in [(1, "high_vol"), (0, "low_vol")]:
            mask = regimes["vol_regime"] == regime_val
            rets = equity.loc[mask, "returns"].dropna()
            if len(rets) > 0:
                results[f"vol_{regime_name}"] = self._compute_metrics(rets)

        return results

    def _compute_metrics(
        self, returns: pd.Series, risk_free_rate: float = 0.0
    ) -> Dict[str, float]:
        """Compute metrics for a return series."""
        if len(returns) == 0:
            return {}

        total_return = (1 + returns).prod() - 1
        volatility = returns.std() * np.sqrt(252)
        excess_mean = returns.mean() - risk_free_rate / 252
        sharpe = excess_mean / returns.std() * np.sqrt(252) if returns.std() > 0 else 0

        # Drawdown
        cumulative = (1 + returns).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        max_dd = drawdown.min()

        return {
            "total_return": total_return,
            "annualized_return": (1 + total_return) ** (252 / len(returns)) - 1
            if len(returns) > 0
            else 0,
            "volatility": volatility,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd,
            "n_days": len(returns),
        }


# ============================================================================
# Transaction Cost Sensitivity
# ============================================================================


class CostSensitivityAnalyzer:
    """
    Analyze how strategy performance changes with transaction costs.

    Useful for understanding:
    - Break-even cost level
    - Cost robustness
    - Optimal rebalancing frequency
    """

    def __init__(
        self,
        engine_class: Callable,
        strategy_factory: Callable,
        data: pd.DataFrame,
    ):
        self.engine_class = engine_class
        self.strategy_factory = strategy_factory
        self.data = data

    def run(
        self,
        cost_levels: List[float] = None,
    ) -> pd.DataFrame:
        """
        Run backtest at different cost levels.

        Args:
            cost_levels: List of commission rates (0.001 = 0.1%)

        Returns:
            DataFrame with metrics at each cost level
        """
        if cost_levels is None:
            cost_levels = [0.0, 0.0005, 0.001, 0.002, 0.005, 0.01]  # 0 to 1%

        results = []

        for cost in cost_levels:
            metrics = self._run_backtest(cost)
            metrics["commission"] = cost
            metrics["commission_bps"] = cost * 10000
            results.append(metrics)

        return pd.DataFrame(results)

    def _run_backtest(self, commission: float) -> Dict[str, float]:
        """Run backtest with given commission."""
        engine = self.engine_class(cash=100000, commission=commission)

        df = self.data.copy()
        df["date"] = pd.to_datetime(df.index)
        df = df.reset_index(drop=True)
        df.columns = ["date", "open", "high", "low", "close", "volume"]

        from backend.backtest_engine import IBKRDataFeed

        data_feed = IBKRDataFeed(dataname=df)
        engine.add_data(data_feed, name="asset")

        strategy_class = self.strategy_factory({})
        engine.add_strategy(strategy_class)

        result = engine.run_backtest()

        return {
            "total_return": result.get("total_return", 0) or 0,
            "sharpe_ratio": result.get("sharpe_ratio", 0) or 0,
            "max_drawdown": result.get("max_drawdown", 0) or 0,
            "total_trades": result.get("total_trades", 0) or 0,
        }


# ============================================================================
# Export
# ============================================================================

__all__ = [
    "WalkForwardAnalyzer",
    "WalkForwardResult",
    "WalkForwardSummary",
    "GridSearch",
    "GridSearchResult",
    "RegimeAnalyzer",
    "CostSensitivityAnalyzer",
]
