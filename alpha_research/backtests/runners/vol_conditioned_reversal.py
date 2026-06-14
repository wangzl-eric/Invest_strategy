# 2026-06-14: Fire 2 implementation of the vol_conditioned_reversal proposal
# (alpha_research/research/strategies/vol_conditioned_reversal_2026-06-13_PENDING/).
# Owner-approved decisions: OWNER_DECISIONS_2026-06-14.md (GO fail-fast; D-COST
# approximate-first; D-HISTORY backfill ~1999; K4>K2 hard kill; VIXCLS/FRED PIT;
# n_trials=24 floor). SPEC source of truth: that folder's proposal.md + pm_review.md.
"""Vol-conditioned sector reversal (Phase 1 weights-contract strategy).

A **dollar-neutral cross-sectional 5-day reversal** across the liquid SPDR sector
ETFs — long the worst recent performers, short the best — that trades **only when
VIX is above its trailing 60-day median** (else the book is flat). Economic
mechanism: in high-volatility regimes, volatility-constrained intermediaries
withdraw liquidity and demand higher compensation to absorb uninformed sector-level
flow; the short-horizon reversal portfolio *is* that liquidity-provision return, and
the premium scales with the VIX (Nagel 2012, "Evaporating Liquidity"; Hameed,
Kang & Viswanathan 2010). This is a *cost-bound, not alpha-bound* strategy and a
structurally short-liquidity / short-vol carry trade — see the proposal's §5/§6.

Construction (proposal §2, pre-committed — do NOT tune without bumping ``n_trials``):

    1. r5_i(t) = close_i(t) / close_i(t-lookback) - 1          (5-day reversal score)
    2. z_i(t)  = cross-sectional z-score of r5 over eligible sectors
    3. s_i(t)  = -z_i(t)                                       (reversal tilt)
    4. gate    = V(t) > trailing rolling quantile of V (strictly backward, full
                 window); flat (all 0) when inactive
    5. weights = dollar-neutral (sum w = 0), capped (|w| <= max_weight),
                 gross-normalized (sum |w| = gross)            (50% long / 50% short)
    6. no-trade band: hold the prior book on names whose target moved <= band

**Look-ahead safety (weights contract).** Every quantity at date *t* uses only data
with timestamp <= *t*: the 5-day return looks back ``lookback`` bars; the VIX gate's
rolling quantile is strictly backward with a full ``min_periods`` window (never
centered); the VIX series itself is PIT-shifted upstream (publication lag) by the
review pipeline's macro loader. Weights are returned **unshifted** — the review
engine applies the execution-convention shift. This is what
``test_no_lookahead_truncation_invariance`` verifies.

Entrypoint (weights contract): :func:`build_weights`.
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd

# Dynamic membership (proposal §3) is enforced at runtime by eligibility (a sector
# enters only once it has real post-inception history); late inceptions (XLRE 2015,
# XLC 2018) are never backfilled. The full universe is listed here.
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

VIX_SERIES_ID = "VIXCLS"  # FRED VIX close; PIT-shifted upstream (D-VIX-SOURCE)

DEFAULT_PARAMS = {
    "reversal_lookback": 5,  # Lehmann/Nagel weekly horizon (literature, not tuned)
    "vix_lookback": 60,  # trailing strictly-backward median window
    "vix_threshold_pct": 50,  # gate active iff V(t) > this percentile of the window
    "construction": "long_short",  # dollar-neutral; sum(w)=0, gross normalized
    "gross": 1.0,  # 0.5 long / 0.5 short
    "max_weight": 0.20,  # per-name cap
    "no_trade_band": 0.05,  # turnover + $1-commission-floor control
    "n_legs_per_side": 0,  # 0 = full proportional-z tilt; >0 = tails-only variant
    "min_eligible": 5,  # below this cross-section -> flat
    "mom_neutralize": False,  # OFF baseline; ON is a declared, trial-counted variant
}


def _zscore_xs(s: pd.Series) -> pd.Series:
    """Cross-sectional z-score (NaN-safe; zero when dispersion is zero)."""
    std = s.std()
    if std is None or std == 0 or np.isnan(std):
        return pd.Series(0.0, index=s.index)
    return (s - s.mean()) / std


def _vix_series(
    macro: Optional[Dict[str, pd.Series]], index: pd.DatetimeIndex
) -> Optional[pd.Series]:
    """The PIT-shifted VIX series aligned (as-of ffill) to the price calendar."""
    if not macro or VIX_SERIES_ID not in macro or macro[VIX_SERIES_ID] is None:
        return None
    return macro[VIX_SERIES_ID].reindex(index).ffill()


def _gate_components(
    macro: Optional[Dict[str, pd.Series]],
    index: pd.DatetimeIndex,
    vix_lookback: int,
    vix_threshold_pct: float,
) -> "tuple[pd.Series, pd.Series]":
    """Return ``(active, ready)`` boolean series for the VIX regime gate.

    ``ready`` is True once a *full* trailing window exists (``min_periods`` =
    window) so the duty cycle is never biased by a partially-padded warmup (PM R6).
    ``active`` is True iff the VIX close strictly exceeds the trailing quantile,
    using only data <= *t* (strictly backward, never centered).
    """
    vix = _vix_series(macro, index)
    if vix is None:
        false = pd.Series(False, index=index)
        return false, false.copy()
    lb = max(2, int(round(vix_lookback)))
    q = float(vix_threshold_pct) / 100.0
    thresh = vix.rolling(lb, min_periods=lb).quantile(q)
    ready = thresh.notna() & vix.notna()
    active = (vix > thresh) & ready
    return active.fillna(False), ready.fillna(False)


def vix_gate(
    macro: Optional[Dict[str, pd.Series]],
    index: pd.DatetimeIndex,
    vix_lookback: int = 60,
    vix_threshold_pct: float = 50,
) -> pd.Series:
    """Boolean active-regime series (True = trade) — exposed for the look-ahead test.

    Strictly backward and full-window, so truncating future VIX cannot change the
    gate at any past date (``test_no_lookahead_truncation_invariance``).
    """
    active, _ = _gate_components(macro, index, vix_lookback, vix_threshold_pct)
    return active


def _neutralize_cap_normalize(raw: pd.Series, cap: float, gross: float) -> pd.Series:
    """Project a raw tilt onto {sum w = 0, |w_i| <= cap, sum|w| = gross}.

    Iterated clip -> gross-rescale -> re-demean converges for any feasible cap
    (cap >= gross / (2 * names_per_side)); for our config (gross 1.0, ~10 names,
    cap 0.20) it converges in a few steps. A degenerate, dispersion-free tilt maps
    to a flat (all-zero) book.
    """
    w = raw.astype(float) - float(raw.astype(float).mean())
    if float(w.abs().sum()) == 0.0:
        return w  # no cross-sectional dispersion -> flat
    for _ in range(64):
        w = w.clip(lower=-cap, upper=cap)
        total = float(w.abs().sum())
        if total == 0.0:
            return w
        w = w * (gross / total)  # scale to target gross (preserves zero mean)
        w = w - float(w.mean())  # restore dollar-neutrality
        if (
            float(w.abs().max()) <= cap + 1e-12
            and abs(float(w.abs().sum()) - gross) <= 1e-10
        ):
            break
    # Final op is a demean so dollar-neutrality is exact (removes hidden beta);
    # the cap holds to ~machine precision and gross to ~1e-8 on cap-binding weeks.
    w = w.clip(lower=-cap, upper=cap)
    return w - float(w.mean())


def build_weights(
    prices: pd.DataFrame,
    macro: Optional[Dict[str, pd.Series]],
    params: dict,
) -> pd.DataFrame:
    """Weights-contract entrypoint: weekly dollar-neutral VIX-gated reversal weights.

    Weights at each rebalance date use only data up to that date (the 5-day return
    looks back; the VIX gate is strictly backward; macro is PIT-shifted upstream).
    The review engine applies the execution-convention shift — **no pre-shifting
    here**. Rows are NaN before warmup (engine drops them), exactly 0.0 on
    gated-off weeks (explicit flat), and signed (long/short) on active weeks.
    """
    from alpha_research.review.engine import rebalance_dates

    p = {**DEFAULT_PARAMS, **(params or {})}
    lookback = max(1, int(round(p["reversal_lookback"])))
    vix_lb = max(2, int(round(p["vix_lookback"])))
    vix_pct = float(p["vix_threshold_pct"])
    cap = float(p["max_weight"])
    gross = float(p["gross"])
    band = float(p["no_trade_band"])
    n_legs = max(0, int(round(p["n_legs_per_side"])))
    min_elig = max(2, int(round(p["min_eligible"])))
    mom_neut = bool(p["mom_neutralize"])

    universe = [t for t in prices.columns if t in SECTOR_ETFS] or list(prices.columns)
    px = prices[universe].sort_index()

    # 5-day reversal score and (optional) 6-1 momentum — both backward-looking.
    r5 = px / px.shift(lookback) - 1.0
    mom = (px.shift(21) / px.shift(126) - 1.0) if mom_neut else None

    active, ready = _gate_components(macro, px.index, vix_lb, vix_pct)
    rebal = rebalance_dates(px.index, "weekly")

    weights = pd.DataFrame(np.nan, index=px.index, columns=universe)
    prev = pd.Series(0.0, index=universe)  # last emitted book (for the no-trade band)

    for d in rebal:
        # Eligibility: a sector enters only once r5 is real (>= lookback post-
        # inception bars); ineligible names get an explicit 0 (never a phantom slot).
        elig = [t for t in universe if bool(pd.notna(r5.loc[d, t]))]
        if not bool(ready.loc[d]) or len(elig) < min_elig:
            continue  # warmup incomplete -> leave NaN (engine warmup-drops the row)

        if not bool(active.loc[d]):
            weights.loc[d, universe] = 0.0  # gate OFF -> explicit flat, zero gross
            prev = pd.Series(0.0, index=universe)
            continue

        # Reversal tilt over the eligible cross-section.
        s = -_zscore_xs(r5.loc[d, elig])

        if mom_neut and mom is not None:
            mz = _zscore_xs(mom.loc[d, elig])
            denom = float((mz * mz).sum())
            if denom > 0:  # project s orthogonal to cross-sectional momentum
                s = s - (float((s * mz).sum()) / denom) * mz

        if n_legs > 0 and len(elig) > 2 * n_legs:  # tails-only variant
            ranked = s.sort_values()
            keep = list(ranked.index[:n_legs]) + list(ranked.index[-n_legs:])
            s = s.loc[keep]

        target = _neutralize_cap_normalize(s, cap, gross)  # exact neutral + gross

        # No-trade band vs the previously held book (full entry after a flat week,
        # since prev is then all-zero and every target leg breaches the band).
        prev_elig = prev.reindex(target.index).fillna(0.0)
        hold = (target - prev_elig).abs() <= band
        book = target.copy()
        book[hold] = prev_elig[hold]
        book = _neutralize_cap_normalize(book, cap, gross)  # re-normalize post-band

        weights.loc[d, universe] = 0.0
        weights.loc[d, list(book.index)] = book.reindex(book.index).values
        prev = pd.Series(0.0, index=universe)
        prev[list(book.index)] = book

    return weights


__all__ = ["build_weights", "vix_gate", "SECTOR_ETFS", "DEFAULT_PARAMS"]
