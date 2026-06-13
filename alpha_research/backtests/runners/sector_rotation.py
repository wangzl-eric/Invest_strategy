# 2026-06-12: Implementation of the sector_rotation_2026-03-13_conditional
# proposal under the Phase 1 weights contract (EXECUTION_PLAN.md WP-1.6).
"""Sector rotation via macro-linked momentum (Phase 1 reference strategy).

Implements `alpha_research/research/strategies/sector_rotation_2026-03-13_conditional/
proposal.md` with the PM's approval requirements closed:

- FRED inputs arrive PIT-shifted (publication lag) via the review pipeline's
  macro loader — the CPI look-ahead the PM flagged is structurally impossible.
- XLI added to the universe (was missing from ticker_universe.py).
- Regime rules below are pre-committed from the proposal text, not fitted.
- The review pipeline always benchmarks against the equal-weight baseline.

Composite alpha per sector (proposal weights):

    alpha = 0.5 * z(6-1 month momentum)
          + 0.3 * macro_tilt_score
          + 0.2 * z(3-month return)

Note on relative strength: the proposal specifies "3-month return vs SPY".
Cross-sectionally, z-scoring (r_i - r_SPY) equals z-scoring r_i because the
SPY term is constant across sectors — so the z-scored own return is used
directly and SPY stays a benchmark, not a universe member.

Pre-committed macro regime rules (from the proposal, applied on 63-day
changes of PIT-shifted series):

    T10Y2Y steepening       -> +XLF;        -XLRE, -XLU
    CPI YoY accelerating    -> +XLE, +XLB;  -XLY, -XLC
    HY OAS widening         -> +XLV, +XLP;  -XLF, -XLY

Entrypoint (weights contract): :func:`build_weights`.
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd

SECTOR_ETFS = [
    "XLK",
    "XLF",
    "XLE",
    "XLV",
    "XLC",
    "XLY",
    "XLP",
    "XLI",
    "XLB",
    "XLRE",
    "XLU",
]

DEFAULT_PARAMS = {
    "mom_lookback": 126,  # 6-month window
    "mom_skip": 21,  # skip most recent month (6-1 momentum)
    "rs_lookback": 63,  # 3-month relative strength
    "macro_window": 63,  # change window for regime rules
    "tilt_scale": 0.6,  # how far weights deviate from equal weight
    "max_weight": 0.20,  # per-sector cap
}

# rule -> (positive-tilt sectors, negative-tilt sectors)
_MACRO_RULES = {
    "T10Y2Y": (["XLF"], ["XLRE", "XLU"]),
    "CPIAUCSL": (["XLE", "XLB"], ["XLY", "XLC"]),
    "BAMLH0A0HYM2": (["XLV", "XLP"], ["XLF", "XLY"]),
}


def _zscore_xs(s: pd.Series) -> pd.Series:
    """Cross-sectional z-score (NaN-safe; zero when dispersion is zero)."""
    std = s.std()
    if std is None or std == 0 or np.isnan(std):
        return pd.Series(0.0, index=s.index)
    return (s - s.mean()) / std


def macro_tilt_scores(
    macro: Dict[str, pd.Series],
    as_of: pd.Timestamp,
    universe: list,
    window: int,
) -> pd.Series:
    """Pre-committed regime tilts as of a date, from PIT-shifted series.

    Each rule contributes +1 to its overweight sectors and -1 to its
    underweights when the trigger fires (63d change in the indicated
    direction); the sum is scaled to unit max-abs so the 0.30 composite
    weight is comparable to the z-scored signals.
    """
    scores = pd.Series(0.0, index=universe)
    for series_id, (overs, unders) in _MACRO_RULES.items():
        s = macro.get(series_id)
        if s is None:
            continue
        s = s.loc[:as_of].dropna()
        if len(s) < window + 1:
            continue
        if series_id == "CPIAUCSL":
            # YoY inflation acceleration (CPI is a monthly level series,
            # as-of ffilled to daily; 252 trading days ~ 1 year)
            if len(s) < 252 + window + 1:
                continue
            yoy = s / s.shift(252) - 1.0
            change = yoy.iloc[-1] - yoy.iloc[-1 - window]
        else:
            change = s.iloc[-1] - s.iloc[-1 - window]
        if pd.isna(change) or change <= 0:
            continue  # rule fires only on steepening / acceleration / widening
        for t in overs:
            if t in scores.index:
                scores[t] += 1.0
        for t in unders:
            if t in scores.index:
                scores[t] -= 1.0
    max_abs = scores.abs().max()
    return scores / max_abs if max_abs > 0 else scores


def build_weights(
    prices: pd.DataFrame,
    macro: Optional[Dict[str, pd.Series]],
    params: dict,
) -> pd.DataFrame:
    """Weights-contract entrypoint: monthly long-only sector weights.

    Weights at each rebalance date use only data up to that date (rolling
    windows look backward; macro series are PIT-shifted upstream). The
    review engine applies the execution shift — no pre-shifting here.
    """
    p = {**DEFAULT_PARAMS, **(params or {})}
    macro = macro or {}

    universe = [t for t in prices.columns if t in SECTOR_ETFS] or list(prices.columns)
    px = prices[universe].sort_index()

    mom_lb = int(p["mom_lookback"])
    skip = int(p["mom_skip"])
    rs_lb = int(p["rs_lookback"])

    # 6-1 momentum: P(t-skip) / P(t-mom_lb) - 1 — entirely backward-looking
    mom = px.shift(skip) / px.shift(mom_lb) - 1.0
    # 3-month return (see module docstring on SPY equivalence)
    rs = px / px.shift(rs_lb) - 1.0

    from alpha_research.review.engine import rebalance_dates

    rebal = rebalance_dates(px.index, "monthly")
    warmup = max(mom_lb, rs_lb) + 1
    rebal = [d for d in rebal if d >= px.index[min(warmup, len(px) - 1)]]

    weights = pd.DataFrame(np.nan, index=px.index, columns=universe)

    for d in rebal:
        # Eligibility: a sector enters only once it has full signal history
        # (handles late inceptions like XLC 2018 / XLRE 2015 — ineligible
        # sectors get an explicit 0, never a phantom equal-weight slot).
        eligible = mom.loc[d].notna() & rs.loc[d].notna()
        n_elig = int(eligible.sum())
        if n_elig < 3:
            continue
        elig_cols = [t for t in universe if eligible[t]]

        alpha = (
            0.5 * _zscore_xs(mom.loc[d, elig_cols])
            + 0.3 * macro_tilt_scores(macro, d, elig_cols, int(p["macro_window"]))
            + 0.2 * _zscore_xs(rs.loc[d, elig_cols])
        )
        # Long-only: tilt around equal weight, cap, renormalize
        raw = (1.0 / n_elig) * (1.0 + float(p["tilt_scale"]) * alpha.fillna(0.0))
        raw = raw.clip(lower=0.0, upper=float(p["max_weight"]))
        total = raw.sum()
        if total > 0:
            weights.loc[d] = 0.0
            weights.loc[d, elig_cols] = raw / total

    return weights


__all__ = ["build_weights", "macro_tilt_scores", "SECTOR_ETFS", "DEFAULT_PARAMS"]
