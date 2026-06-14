# 2026-06-14: Independent event-driven reconciliation for the shared backtester.
# A second, explicit bar-by-bar implementation of the weights-contract backtest that
# cross-checks the vectorized engine (engine.run_weights_backtest). If the two agree,
# the vectorized result is corroborated; a divergence flags a shift/cost/look-ahead bug.
# Dependency-free (numpy/pandas) so it runs every review. The heavyweight Backtrader
# execution-sim adapter (backtests/event_driven/, D7) remains the path for fill/slippage
# realism; this is the always-on engine-agreement gate.
"""Event-driven cross-check of the vectorized weights-contract backtest."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def reconcile_event_driven(
    weights: pd.DataFrame,
    prices: pd.DataFrame,
    *,
    cost_bps: float = 5.0,
    shift_bars: int = 1,
) -> Dict[str, Any]:
    """Replay the weights as an explicit per-bar loop and compare to the vectorized engine.

    The loop holds the target set ``shift_bars`` bars earlier (the execution convention),
    earns that bar's return, and charges ``cost_bps`` on the bar-over-bar weight change —
    the same economics as ``run_weights_backtest`` but computed independently (no vectorized
    ``.shift``/``.diff``), so a mismatch localizes an engine bug.

    Returns a dict with both engines' Sharpe/total-return, the max per-day return
    divergence, and ``reconciled`` (True when the two agree to ~1e-9).
    """
    from alpha_research.review.engine import run_weights_backtest

    common = [c for c in weights.columns if c in prices.columns]
    if not common:
        return {"available": False, "reason": "no overlap between weights and prices"}

    px = prices[common].sort_index()
    rets = px.pct_change()
    targets = weights[common].sort_index().reindex(px.index).ffill()

    dates = px.index
    prev_eff = pd.Series(0.0, index=common)
    ed_dates, ed_daily = [], []
    started = False
    for i, d in enumerate(dates):
        j = i - shift_bars
        if j < 0:
            continue
        eff_row = targets.iloc[j]
        if not started:
            if eff_row.isna().all():
                continue  # warmup: no position yet (mirrors engine's `valid` mask)
            started = True
        eff = eff_row.fillna(0.0)
        gross = float((eff * rets.loc[d].fillna(0.0)).sum())
        turnover = float((eff - prev_eff).abs().sum())  # day 1: full entry (prev=0)
        ed_daily.append(gross - turnover * (cost_bps / 10_000.0))
        ed_dates.append(d)
        prev_eff = eff

    if len(ed_daily) < 2:
        return {"available": False, "reason": "too few bars after alignment"}

    ed = pd.Series(ed_daily, index=ed_dates)
    ed_sharpe = (
        float(ed.mean() / ed.std() * np.sqrt(TRADING_DAYS)) if ed.std() > 0 else 0.0
    )
    ed_total = float((1.0 + ed).prod() - 1.0)

    vec = run_weights_backtest(
        weights, prices, cost_bps=cost_bps, shift_bars=shift_bars
    )
    vec_r = vec.daily_returns

    aligned = pd.concat([ed.rename("ed"), vec_r.rename("vec")], axis=1).dropna()
    max_div = (
        float((aligned["ed"] - aligned["vec"]).abs().max())
        if len(aligned)
        else float("nan")
    )
    reconciled = bool(np.isfinite(max_div) and max_div < 1e-9)

    return {
        "available": True,
        "reconciled": reconciled,
        "max_daily_return_divergence": max_div,
        "n_bars_event_driven": int(len(ed)),
        "n_bars_vectorized": int(len(vec_r)),
        "event_driven": {"sharpe": ed_sharpe, "total_return": ed_total},
        "vectorized": {
            "sharpe": float(vec.metrics["sharpe_ratio"]),
            "total_return": float(vec.metrics["total_return"]),
        },
        "note": (
            "Independent bar-by-bar replay agrees with the vectorized engine."
            if reconciled
            else "DIVERGENCE — investigate engine shift/cost/look-ahead handling."
        ),
    }


__all__ = ["reconcile_event_driven"]
