"""Pluggable analyzers — the backtrader ``Analyzer`` pattern.

An ``Analyzer`` observes the finished return/equity stream and emits a dict of
statistics. The engine runs every registered analyzer and stores the merged
output under ``BacktestResult.analyzers[name]``. Keeping them as small, pure
functions of the return series (rather than wired into the loop) makes each one
independently testable and lets users add their own without touching the engine.

Built-ins:
  * ``ReturnsAnalyzer``   — total / annualised return, volatility, hit rate.
  * ``SharpeAnalyzer``    — annualised Sharpe and Sortino.
  * ``DrawdownAnalyzer``  — max drawdown depth and longest underwater run.
  * ``TradeAnalyzer``     — trade count, commission, slippage, turnover.
  * ``PerformanceAnalyzer`` — the full repo metric suite
    (``reporting.performance.compute_performance_metrics``), so the native
    engine produces the same QuantStats-grade ``performance.json`` payload.
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd

TRADING_DAYS = 252


class Analyzer:
    """Base analyzer. Override ``analyze`` and set a unique ``name``."""

    name: str = "analyzer"

    def analyze(self, ctx: "AnalysisInput") -> Dict[str, Any]:
        raise NotImplementedError


class AnalysisInput:
    """Bundle of finished-run series passed to every analyzer."""

    def __init__(
        self,
        *,
        returns: pd.Series,
        equity: pd.Series,
        turnover: pd.Series,
        trades: List[Any],
    ) -> None:
        self.returns = returns
        self.equity = equity
        self.turnover = turnover
        self.trades = trades


def _annualized_sharpe(returns: pd.Series) -> float:
    sd = returns.std()
    if sd == 0 or np.isnan(sd):
        return 0.0
    return float(returns.mean() / sd * np.sqrt(TRADING_DAYS))


class ReturnsAnalyzer(Analyzer):
    name = "returns"

    def analyze(self, ctx: AnalysisInput) -> Dict[str, Any]:
        r = ctx.returns
        n = len(r)
        total = float((1.0 + r).prod() - 1.0)
        ann = float((1.0 + total) ** (TRADING_DAYS / n) - 1.0) if n > 0 else 0.0
        return {
            "total_return": total,
            "annualized_return": ann,
            "volatility": float(r.std() * np.sqrt(TRADING_DAYS)),
            "hit_rate": float((r > 0).mean()) if n else 0.0,
            "n_days": int(n),
        }


class SharpeAnalyzer(Analyzer):
    """Annualised Sharpe and Sortino, excess of an annual risk-free rate."""

    name = "sharpe"

    def __init__(self, rf_annual: float = 0.0) -> None:
        self.rf_annual = float(rf_annual)

    def analyze(self, ctx: AnalysisInput) -> Dict[str, Any]:
        r = ctx.returns
        rf_daily = self.rf_annual / TRADING_DAYS
        excess = r - rf_daily
        sd = excess.std()
        sharpe = (
            float(excess.mean() / sd * np.sqrt(TRADING_DAYS))
            if sd and not np.isnan(sd)
            else 0.0
        )
        downside = excess[excess < 0]
        dd = downside.std()
        sortino = (
            float(excess.mean() / dd * np.sqrt(TRADING_DAYS))
            if dd and not np.isnan(dd)
            else 0.0
        )
        return {
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "rf_annual": self.rf_annual,
        }


class StatsAnalyzer(Analyzer):
    """Statistical-rigour battery, reusing ``backtests.stats.sharpe_tests``.

    Wires the native engine into the repo's existing multiple-testing machinery
    so an event-driven run produces the same significance evidence a reviewer
    expects: Probabilistic Sharpe (PSR), Deflated Sharpe (DSR, penalised by the
    number of declared trials), and a block-bootstrap Sharpe confidence interval.

    Args:
        n_trials: Number of strategy variations tried (feeds the DSR deflation).
            Declare this honestly — it is the multiple-testing correction.
        benchmark_sharpe: Null Sharpe the PSR is tested against (default 0).
    """

    name = "stats"

    def __init__(self, n_trials: int = 1, benchmark_sharpe: float = 0.0) -> None:
        self.n_trials = int(n_trials)
        self.benchmark_sharpe = float(benchmark_sharpe)

    def analyze(self, ctx: AnalysisInput) -> Dict[str, Any]:
        from alpha_research.backtests.stats.sharpe_tests import (
            deflated_sharpe_ratio,
            probabilistic_sharpe_ratio,
            sharpe_confidence_interval,
        )

        arr = ctx.returns.to_numpy()
        if len(arr) < 20:
            return {"available": False, "reason": "fewer than 20 returns"}
        ci_low, ci_point, ci_high = sharpe_confidence_interval(arr)
        return {
            "available": True,
            "psr": float(
                probabilistic_sharpe_ratio(arr, benchmark_sharpe=self.benchmark_sharpe)
            ),
            "dsr": float(deflated_sharpe_ratio(arr, n_trials=self.n_trials)),
            "n_trials": self.n_trials,
            "sharpe_ci_95": [float(ci_low), float(ci_high)],
            "sharpe_point": float(ci_point),
        }


class DrawdownAnalyzer(Analyzer):
    name = "drawdown"

    def analyze(self, ctx: AnalysisInput) -> Dict[str, Any]:
        equity = ctx.equity
        peak = equity.cummax()
        dd = (equity - peak) / peak
        underwater = (dd < -1e-12).to_numpy()
        longest = cur = 0
        for u in underwater:
            cur = cur + 1 if u else 0
            longest = max(longest, cur)
        return {
            "max_drawdown": float(dd.min()) if len(dd) else 0.0,
            "max_drawdown_days": int(longest),
        }


class TradeAnalyzer(Analyzer):
    name = "trades"

    def analyze(self, ctx: AnalysisInput) -> Dict[str, Any]:
        trades = ctx.trades
        commission = float(sum(getattr(t, "commission", 0.0) for t in trades))
        slippage = float(sum(getattr(t, "slippage", 0.0) for t in trades))
        return {
            "n_trades": int(len(trades)),
            "total_commission": commission,
            "total_slippage": slippage,
            "annual_turnover": float(ctx.turnover.mean() * TRADING_DAYS)
            if len(ctx.turnover)
            else 0.0,
        }


class PerformanceAnalyzer(Analyzer):
    """Full repo metric suite via ``compute_performance_metrics``."""

    name = "performance"

    def __init__(self, benchmark: pd.Series | None = None) -> None:
        self.benchmark = benchmark

    def analyze(self, ctx: AnalysisInput) -> Dict[str, Any]:
        from alpha_research.backtests.reporting.performance import (
            compute_performance_metrics,
        )

        return compute_performance_metrics(ctx.returns, benchmark=self.benchmark)


def default_analyzers() -> List[Analyzer]:
    return [ReturnsAnalyzer(), SharpeAnalyzer(), DrawdownAnalyzer(), TradeAnalyzer()]


__all__ = [
    "Analyzer",
    "AnalysisInput",
    "ReturnsAnalyzer",
    "SharpeAnalyzer",
    "DrawdownAnalyzer",
    "TradeAnalyzer",
    "PerformanceAnalyzer",
    "StatsAnalyzer",
    "default_analyzers",
]
