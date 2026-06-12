"""Vectorized backtest engine for the weights contract.

Evaluates a target-weights DataFrame (the manifest entrypoint's output)
against close prices under an explicit execution convention. This is the
review pipeline's primary engine; the event-driven (Backtrader) layer is
validation-only (EXECUTION_PLAN.md, locked decision D7).

Execution model: weights computed from data up to bar *t* are shifted by
``shift_bars`` before earning returns, so the strategy function never needs
to (and must not) pre-shift its own output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

import numpy as np
import pandas as pd

TRADING_DAYS = 252


@dataclass
class BacktestResult:
    """Output of a weights-contract backtest."""

    daily_returns: pd.Series
    equity_curve: pd.DataFrame  # columns: date, portfolio_value
    weights: pd.DataFrame  # effective (post-shift) weights
    metrics: Dict[str, float] = field(default_factory=dict)


def run_weights_backtest(
    weights: pd.DataFrame,
    prices: pd.DataFrame,
    *,
    cost_bps: float = 5.0,
    shift_bars: int = 1,
    initial_cash: float = 100_000.0,
) -> BacktestResult:
    """Backtest target weights against close prices.

    Args:
        weights: DatetimeIndex x ticker target weights (NaN = no position).
        prices: DatetimeIndex x ticker close prices.
        cost_bps: Proportional cost charged on turnover (one-way, in bps).
        shift_bars: Execution-convention shift (1 = trade at close of the
            signal bar, 2 = conservative next-bar approximation). See
            ``ExecutionConvention.shift_bars``.
        initial_cash: Starting equity for the equity curve.

    Returns:
        BacktestResult with net daily returns, equity curve, effective
        weights, and summary metrics.
    """
    if shift_bars < 1:
        raise ValueError("shift_bars must be >= 1 (0 would be look-ahead)")
    if weights is None or weights.empty:
        raise ValueError("weights frame is empty")
    if not isinstance(weights.index, pd.DatetimeIndex):
        raise ValueError("weights must have a DatetimeIndex")

    common = [c for c in weights.columns if c in prices.columns]
    if not common:
        raise ValueError(
            "no overlap between weight columns and price columns "
            f"(weights: {list(weights.columns)[:5]}...)"
        )

    px = prices[common].sort_index()
    rets = px.pct_change()

    # Align weights to the price calendar: a target set on day t holds
    # (ffill) until the next target. Then apply the execution shift.
    w = weights[common].sort_index().reindex(px.index).ffill()
    w_eff = w.shift(shift_bars)

    # Drop warmup rows where no position exists yet
    valid = w_eff.notna().any(axis=1)
    w_eff = w_eff[valid].fillna(0.0)
    rets = rets.loc[w_eff.index]

    if len(w_eff) < 20:
        raise ValueError(
            f"only {len(w_eff)} usable bars after alignment — too short to review"
        )

    gross = (w_eff * rets).sum(axis=1)

    # Turnover: one-way sum of |weight changes|; day 1 = full entry.
    dw = w_eff.diff().abs()
    dw.iloc[0] = w_eff.iloc[0].abs()
    turnover = dw.sum(axis=1)
    costs = turnover * (cost_bps / 10_000.0)

    net = (gross - costs).astype(float)

    equity = (1.0 + net).cumprod() * initial_cash
    peak = equity.cummax()
    drawdown = (equity - peak) / peak

    n_days = len(net)
    vol = float(net.std() * np.sqrt(TRADING_DAYS))
    sharpe = (
        float(net.mean() / net.std() * np.sqrt(TRADING_DAYS)) if net.std() > 0 else 0.0
    )
    total_return = float(equity.iloc[-1] / initial_cash - 1.0)

    metrics = {
        "total_return": total_return,
        "annualized_return": float((1 + total_return) ** (TRADING_DAYS / n_days) - 1),
        "volatility": vol,
        "sharpe_ratio": sharpe,
        "max_drawdown": float(drawdown.min()),
        "annual_turnover": float(turnover.mean() * TRADING_DAYS),
        "cost_bps": float(cost_bps),
        "n_days": float(n_days),
    }

    equity_curve = pd.DataFrame(
        {"date": equity.index, "portfolio_value": equity.values}
    )
    return BacktestResult(
        daily_returns=net,
        equity_curve=equity_curve,
        weights=w_eff,
        metrics=metrics,
    )


def rebalance_dates(index: pd.DatetimeIndex, frequency: str) -> pd.DatetimeIndex:
    """Last trading day of each period in ``index`` for a rebalance frequency.

    Always uses actual index dates (never calendar period ends), so the
    result is directly usable as row labels.
    """
    if frequency == "daily":
        return index
    period = {"weekly": "W", "monthly": "M"}.get(frequency, frequency)
    s = index.to_series()
    last_per_period = s.groupby(index.to_period(period)).max()
    return pd.DatetimeIndex(last_per_period.values)


def equal_weight_baseline(
    prices: pd.DataFrame,
    *,
    rebalance: str = "monthly",
    cost_bps: float = 5.0,
    shift_bars: int = 1,
) -> BacktestResult:
    """Equal-weight buy-and-rebalance baseline over the same universe.

    Every reviewed strategy is compared against this naive alternative
    (lesson L6: always compare vs the simplest alternative).
    """
    px = prices.sort_index()
    rebal_dates = rebalance_dates(px.index, rebalance)

    n = px.shape[1]
    w = pd.DataFrame(np.nan, index=px.index, columns=px.columns)
    mask = px.index.isin(rebal_dates) | (px.index == px.index[0])
    w.loc[mask, :] = 1.0 / n
    return run_weights_backtest(w, px, cost_bps=cost_bps, shift_bars=shift_bars)


__all__ = ["BacktestResult", "run_weights_backtest", "equal_weight_baseline"]
