"""Tests for the vol-conditioned sector reversal strategy (Fire 2).

Offline / synthetic — no network, no FRED key. The look-ahead suite mirrors
``test_sector_rotation_strategy.py`` and extends it to carry the VIX panel through
truncation (implementation_plan §4 of
``research/strategies/vol_conditioned_reversal_2026-06-13_PENDING/``).
"""
import numpy as np
import pandas as pd
import pytest

from alpha_research.backtests.runners.vol_conditioned_reversal import (
    DEFAULT_PARAMS,
    SECTOR_ETFS,
    build_weights,
    vix_gate,
)

# Synthetic inception offsets (positions in the index) for the late-listed sectors.
XLRE_START = 200
XLC_START = 500

FAST_PARAMS = {
    "reversal_lookback": 5,
    "vix_lookback": 60,
    "vix_threshold_pct": 50,
    "construction": "long_short",
    "gross": 1.0,
    "max_weight": 0.20,
    "no_trade_band": 0.05,
    "n_legs_per_side": 0,
    "min_eligible": 5,
    "mom_neutralize": False,
}


def _sector_prices(n=900, seed=7):
    """Wide close frame over the 11 sectors with DYNAMIC inception (XLRE/XLC NaN
    before their synthetic listing dates) — exercises the eligibility path and the
    9 -> 10 -> 11 cross-section change."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2014-01-02", periods=n)
    data = {
        t: 100.0 * np.cumprod(1 + rng.normal(0.0003, 0.013, n)) for t in SECTOR_ETFS
    }
    px = pd.DataFrame(data, index=idx)
    px.loc[px.index[:XLRE_START], "XLRE"] = np.nan  # late inception
    px.loc[px.index[:XLC_START], "XLC"] = np.nan
    return px


def _vix(index, seed=3):
    """Synthetic PIT-aligned VIXCLS that crosses its own trailing-60 median both up
    and down, so both gate-ON and gate-OFF weeks occur (a constant VIX would make
    the gate test vacuous)."""
    n = len(index)
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    # two oscillations (period ~70 and ~210 days) + spikes + noise, floored at 9
    base = 18 + 7 * np.sin(t / 11.0) + 4 * np.sin(t / 33.0)
    spikes = np.where(rng.random(n) > 0.985, rng.uniform(10, 30, n), 0.0)
    vix = np.clip(base + rng.normal(0, 1.5, n) + spikes, 9.0, None)
    return {"VIXCLS": pd.Series(vix, index=index)}


def _active_rows(w):
    set_rows = w.dropna(how="all")
    gross = set_rows.abs().sum(axis=1)
    return set_rows[gross > 1e-9], set_rows[gross <= 1e-9]


@pytest.mark.unit
class TestBuildWeights:
    def test_weights_contract_shape(self):
        px = _sector_prices()
        w = build_weights(px, _vix(px.index), FAST_PARAMS)
        assert isinstance(w, pd.DataFrame)
        assert isinstance(w.index, pd.DatetimeIndex)
        assert set(w.columns) == set(SECTOR_ETFS)

    def test_dollar_neutral_capped_gross_one_on_active_weeks(self):
        px = _sector_prices()
        w = build_weights(px, _vix(px.index), FAST_PARAMS)
        active, flat = _active_rows(w)
        assert len(active) > 5  # the gate is active on a meaningful set of weeks
        assert len(flat) > 0  # ...and flat on others (duty cycle works)
        assert np.allclose(active.sum(axis=1), 0.0, atol=1e-8)  # dollar-neutral
        assert np.allclose(active.abs().sum(axis=1), 1.0, atol=1e-6)  # gross = 1.0
        assert active.abs().max().max() <= 0.20 + 1e-6  # per-name cap
        # at least one long and one short on every active week
        assert (active.gt(1e-12).sum(axis=1) >= 1).all()
        assert (active.lt(-1e-12).sum(axis=1) >= 1).all()

    def test_gate_off_weeks_are_exactly_flat(self):
        px = _sector_prices()
        w = build_weights(px, _vix(px.index), FAST_PARAMS)
        _, flat = _active_rows(w)
        assert len(flat) > 0
        assert (flat.fillna(0.0).abs() < 1e-12).all().all()

    def test_no_lookahead_truncation_invariance(self):
        """Weights at date t must not change when future price/VIX data is removed."""
        px = _sector_prices()
        macro = _vix(px.index)
        full = build_weights(px, macro, FAST_PARAMS)

        cutoff = px.index[640]
        px_trunc = px.loc[:cutoff]
        macro_trunc = {k: v.loc[:cutoff] for k, v in macro.items()}
        trunc = build_weights(px_trunc, macro_trunc, FAST_PARAMS)

        full_rows = full.dropna(how="all")
        trunc_rows = trunc.dropna(how="all")
        common = full_rows.index.intersection(trunc_rows.index)
        assert len(common) >= 10
        pd.testing.assert_frame_equal(
            full_rows.loc[common], trunc_rows.loc[common], atol=1e-9, rtol=0
        )

    def test_gate_is_truncation_invariant(self):
        px = _sector_prices()
        macro = _vix(px.index)
        full_gate = vix_gate(macro, px.index, 60, 50)
        cutoff = px.index[640]
        trunc_gate = vix_gate(
            {k: v.loc[:cutoff] for k, v in macro.items()}, px.index[:641], 60, 50
        )
        common = full_gate.index.intersection(trunc_gate.index)
        assert full_gate.loc[common].equals(trunc_gate.loc[common])

    def test_no_future_vix(self):
        """The gate at t uses no VIX observation dated after t."""
        px = _sector_prices()
        macro = _vix(px.index)
        full_gate = vix_gate(macro, px.index, 60, 50)
        t_pos = 700
        t = px.index[t_pos]
        masked = macro["VIXCLS"].copy()
        masked.iloc[t_pos + 1 :] = np.nan  # destroy all future VIX
        masked_gate = vix_gate({"VIXCLS": masked}, px.index, 60, 50)
        assert full_gate.loc[:t].equals(masked_gate.loc[:t])

    def test_warmup_fully_populated(self):
        """No weight row before a full trailing-60 VIX window exists (PM R6)."""
        px = _sector_prices()
        w = build_weights(px, _vix(px.index), FAST_PARAMS)
        set_rows = w.dropna(how="all")
        first_full_window = px.index[59]  # rolling(60, min_periods=60)
        assert set_rows.index.min() >= first_full_window

    def test_dynamic_universe_no_backfill(self):
        """Late-inception sectors carry no weight before their listing date."""
        px = _sector_prices()
        w = build_weights(px, _vix(px.index), FAST_PARAMS)
        xlre_date = px.index[XLRE_START]
        xlc_date = px.index[XLC_START]
        assert (w["XLRE"].loc[:xlre_date].fillna(0.0).abs() < 1e-12).all()
        assert (w["XLC"].loc[:xlc_date].fillna(0.0).abs() < 1e-12).all()
        # ...and they DO participate after inception (cross-section grows)
        assert w["XLC"].loc[xlc_date:].abs().sum() > 0

    def test_no_trade_band_reduces_turnover(self):
        px = _sector_prices()
        macro = _vix(px.index)
        w_band = build_weights(px, macro, {**FAST_PARAMS, "no_trade_band": 0.05})
        w_none = build_weights(px, macro, {**FAST_PARAMS, "no_trade_band": 0.0})
        turn_band = w_band.dropna(how="all").diff().abs().sum().sum()
        turn_none = w_none.dropna(how="all").diff().abs().sum().sum()
        assert turn_band <= turn_none + 1e-9

    def test_constant_vix_is_always_flat(self):
        """With a constant VIX, V(t) is never strictly above its own median -> flat."""
        px = _sector_prices()
        macro = {"VIXCLS": pd.Series(20.0, index=px.index)}
        w = build_weights(px, macro, FAST_PARAMS)
        active, flat = _active_rows(w)
        assert len(active) == 0

    def test_no_vix_means_no_trading(self):
        """Without the VIX series the gate is never ready -> nothing trades."""
        px = _sector_prices()
        w = build_weights(px, None, FAST_PARAMS)
        assert w.dropna(how="all").empty

    def test_default_params_used_when_missing(self):
        px = _sector_prices()
        w = build_weights(px, _vix(px.index), {})  # falls back to DEFAULT_PARAMS
        active, _ = _active_rows(w)
        assert len(active) > 0
        assert DEFAULT_PARAMS["reversal_lookback"] == 5

    def test_mom_neutralize_variant_runs(self):
        px = _sector_prices()
        w = build_weights(px, _vix(px.index), {**FAST_PARAMS, "mom_neutralize": True})
        active, _ = _active_rows(w)
        assert len(active) > 0
        assert np.allclose(active.sum(axis=1), 0.0, atol=1e-9)
