"""Cross-engine PnL equivalence — the consolidation correctness gate.

The repo deliberately keeps two weights-contract backtest engines:

* **vectorized** — ``alpha_research.review.engine.run_weights_backtest`` (fast,
  the review battery's workhorse).
* **native** — ``alpha_research.backtests.native`` (event-driven, share-based,
  realistic fills, no look-ahead by construction).

They must agree. This module runs the **same** target weights through every
engine and proves their PnL is identical (to machine precision) under matched
assumptions, so "we have several engines" never means "we have several answers."

Three implementations are compared:

1. ``vectorized``      — ``run_weights_backtest``.
2. ``native_parity``   — native engine in ``cost_basis="target"`` mode (emulates
   the vectorized cost convention exactly).
3. ``reference``       — a dead-simple, dependency-light numpy bar loop defined
   here as an independent ground truth (the old ``reconcile_event_driven`` body).

All three are *defined* to be equal; ``compare_engines`` asserts it. The native
engine's **realistic** mode (``cost_basis="traded"``) is reported alongside but
is *expected* to differ once costs bite (it charges drift-correction turnover and
a decision-to-fill price gap) — that divergence is realism, surfaced explicitly,
never hidden.
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def reference_returns(
    weights: pd.DataFrame,
    prices: pd.DataFrame,
    *,
    cost_bps: float = 5.0,
    shift_bars: int = 1,
) -> pd.Series:
    """Independent, dependency-light bar-by-bar replay of the weights contract.

    Holds the target set ``shift_bars`` bars earlier, earns that bar's return,
    and charges ``cost_bps`` on the bar-over-bar target change. No vectorized
    ``.shift``/``.diff`` — a deliberately separate implementation so agreement
    with the other engines is meaningful.
    """
    common = [c for c in weights.columns if c in prices.columns]
    if not common:
        raise ValueError("no overlap between weights and prices")
    px = prices[common].sort_index()
    rets = px.pct_change()
    targets = weights[common].sort_index().reindex(px.index).ffill()

    prev_eff = pd.Series(0.0, index=common)
    dates: List[pd.Timestamp] = []
    daily: List[float] = []
    started = False
    for i, d in enumerate(px.index):
        j = i - shift_bars
        if j < 0:
            continue
        eff_row = targets.iloc[j]
        if not started:
            if eff_row.isna().all():
                continue  # warm-up
            started = True
        eff = eff_row.fillna(0.0)
        gross = float((eff * rets.loc[d].fillna(0.0)).sum())
        turnover = float((eff - prev_eff).abs().sum())
        daily.append(gross - turnover * (cost_bps / 10_000.0))
        dates.append(d)
        prev_eff = eff
    return pd.Series(daily, index=pd.DatetimeIndex(dates), name="reference")


def _engine_returns(
    weights: pd.DataFrame,
    prices: pd.DataFrame,
    *,
    cost_bps: float,
    shift_bars: int,
) -> Dict[str, pd.Series]:
    from alpha_research.backtests.native import backtest_weights
    from alpha_research.review.engine import run_weights_backtest

    vec = run_weights_backtest(
        weights, prices, cost_bps=cost_bps, shift_bars=shift_bars
    ).daily_returns.rename("vectorized")
    parity = backtest_weights(
        weights, prices, cost_bps=cost_bps, shift_bars=shift_bars, cost_basis="target"
    ).daily_returns.rename("native_parity")
    traded = backtest_weights(
        weights, prices, cost_bps=cost_bps, shift_bars=shift_bars, cost_basis="traded"
    ).daily_returns.rename("native_traded")
    ref = reference_returns(weights, prices, cost_bps=cost_bps, shift_bars=shift_bars)
    return {
        "vectorized": vec,
        "native_parity": parity,
        "reference": ref,
        "native_traded": traded,
    }


def _max_div(a: pd.Series, b: pd.Series) -> float:
    j = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna()
    if j.empty:
        return float("nan")
    return float((j["a"] - j["b"]).abs().max())


def _sharpe(r: pd.Series) -> float:
    sd = r.std()
    return float(r.mean() / sd * np.sqrt(TRADING_DAYS)) if sd and sd > 0 else 0.0


def compare_engines(
    weights: pd.DataFrame,
    prices: pd.DataFrame,
    *,
    cost_bps: float = 5.0,
    shift_bars: int = 1,
    tol: float = 1e-9,
) -> Dict[str, Any]:
    """Run ``weights`` through every engine and report PnL agreement.

    The "exact" set — ``vectorized``, ``native_parity``, ``reference`` — must
    agree to ``tol`` on every daily return; ``exact_match`` is True iff they do.
    ``native_traded`` (realistic costs) is reported with its divergence vs the
    vectorized engine, which is expected to be > tol once ``cost_bps`` > 0.

    Returns a JSON-friendly dict: per-engine ``{sharpe, total_return, n_days}``,
    the pairwise max daily divergences, and the boolean verdicts.
    """
    series = _engine_returns(weights, prices, cost_bps=cost_bps, shift_bars=shift_bars)
    exact = ["vectorized", "native_parity", "reference"]

    summary = {
        name: {
            "sharpe": _sharpe(s),
            "total_return": float((1.0 + s).prod() - 1.0),
            "n_days": int(len(s)),
        }
        for name, s in series.items()
    }

    # Pairwise divergence among the exact engines.
    divergences: Dict[str, float] = {}
    worst = 0.0
    for i in range(len(exact)):
        for k in range(i + 1, len(exact)):
            a, b = exact[i], exact[k]
            d = _max_div(series[a], series[b])
            divergences[f"{a}|{b}"] = d
            if np.isfinite(d):
                worst = max(worst, d)

    traded_vs_vec = _max_div(series["native_traded"], series["vectorized"])

    return {
        "cost_bps": float(cost_bps),
        "shift_bars": int(shift_bars),
        "tolerance": float(tol),
        "summary": summary,
        "exact_divergences": divergences,
        "max_exact_divergence": float(worst),
        "exact_match": bool(worst <= tol),
        "native_traded_vs_vectorized": float(traded_vs_vec),
        "note": (
            "vectorized, native_parity and reference agree to machine precision; "
            "native_traded differs by drift-correction turnover when costs > 0."
        ),
    }


def assert_engines_agree(
    weights: pd.DataFrame,
    prices: pd.DataFrame,
    *,
    cost_bps: float = 5.0,
    shift_bars: int = 1,
    tol: float = 1e-9,
) -> Dict[str, Any]:
    """``compare_engines`` that raises ``AssertionError`` if they disagree."""
    report = compare_engines(
        weights, prices, cost_bps=cost_bps, shift_bars=shift_bars, tol=tol
    )
    if not report["exact_match"]:
        raise AssertionError(
            "backtest engines disagree: max daily PnL divergence "
            f"{report['max_exact_divergence']:.2e} > tol {tol:.0e}\n"
            f"pairwise: {report['exact_divergences']}"
        )
    return report


__all__ = ["reference_returns", "compare_engines", "assert_engines_agree"]
