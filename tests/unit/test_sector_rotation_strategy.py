"""Tests for the sector rotation reference strategy (WP-1.6)."""
import numpy as np
import pandas as pd
import pytest

from alpha_research.backtests.runners.sector_rotation import (
    SECTOR_ETFS,
    build_weights,
    macro_tilt_scores,
)

FAST_PARAMS = {
    "mom_lookback": 60,
    "mom_skip": 10,
    "rs_lookback": 30,
    "macro_window": 20,
    "tilt_scale": 0.6,
    "max_weight": 0.20,
}


def _sector_prices(n=400, seed=11):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2022-01-03", periods=n)
    data = {
        t: 100.0 * np.cumprod(1 + rng.normal(0.0004, 0.012, n)) for t in SECTOR_ETFS
    }
    return pd.DataFrame(data, index=idx)


def _macro(index):
    """Synthetic PIT-aligned macro series: steepener, flat CPI, tight credit."""
    n = len(index)
    return {
        "T10Y2Y": pd.Series(np.linspace(-0.5, 1.0, n), index=index),
        "CPIAUCSL": pd.Series(300.0, index=index),
        "BAMLH0A0HYM2": pd.Series(np.linspace(5.0, 3.0, n), index=index),
    }


@pytest.mark.unit
class TestBuildWeights:
    def test_weights_contract_shape(self):
        px = _sector_prices()
        w = build_weights(px, _macro(px.index), FAST_PARAMS)
        assert isinstance(w, pd.DataFrame)
        assert isinstance(w.index, pd.DatetimeIndex)
        assert set(w.columns) == set(SECTOR_ETFS)

    def test_long_only_and_fully_invested(self):
        px = _sector_prices()
        w = build_weights(px, _macro(px.index), FAST_PARAMS)
        set_rows = w.dropna(how="all")
        assert len(set_rows) > 5  # monthly rebalances after warmup
        assert (set_rows.fillna(0) >= -1e-12).all().all()
        assert np.allclose(set_rows.sum(axis=1), 1.0, atol=1e-9)

    def test_max_weight_respected_before_renormalization_cap(self):
        px = _sector_prices()
        w = build_weights(px, _macro(px.index), FAST_PARAMS).dropna(how="all")
        # Post-normalization weights can exceed the raw cap only slightly when
        # total < 1; sanity bound at cap / min_total ~ 0.25
        assert w.max().max() <= 0.25 + 1e-9

    def test_no_lookahead_truncation_invariance(self):
        """Weights at date t must not change when future data is removed."""
        px = _sector_prices()
        macro = _macro(px.index)
        full = build_weights(px, macro, FAST_PARAMS)

        cutoff = px.index[300]
        px_trunc = px.loc[:cutoff]
        macro_trunc = {k: v.loc[:cutoff] for k, v in macro.items()}
        trunc = build_weights(px_trunc, macro_trunc, FAST_PARAMS)

        # Compare on rebalance rows present in both (skip the truncated
        # frame's final partial-month rebalance, which full data wouldn't have)
        full_rows = full.dropna(how="all")
        trunc_rows = trunc.dropna(how="all")
        common = full_rows.index.intersection(trunc_rows.index)
        assert len(common) >= 5
        pd.testing.assert_frame_equal(
            full_rows.loc[common], trunc_rows.loc[common], atol=1e-12, rtol=0
        )

    def test_runs_without_macro(self):
        px = _sector_prices()
        w = build_weights(px, None, FAST_PARAMS).dropna(how="all")
        assert np.allclose(w.sum(axis=1), 1.0, atol=1e-9)

    def test_default_params_used_when_missing(self):
        px = _sector_prices(n=600)
        w = build_weights(px, None, {})  # falls back to DEFAULT_PARAMS
        assert not w.dropna(how="all").empty


@pytest.mark.unit
class TestMacroTiltScores:
    def test_steepening_tilts_xlf_up_xlu_down(self):
        idx = pd.bdate_range("2023-01-02", periods=100)
        macro = {"T10Y2Y": pd.Series(np.linspace(-0.5, 1.0, 100), index=idx)}
        scores = macro_tilt_scores(macro, idx[-1], SECTOR_ETFS, window=20)
        assert scores["XLF"] > 0
        assert scores["XLU"] < 0
        assert scores["XLRE"] < 0
        assert scores.abs().max() == pytest.approx(1.0)

    def test_flattening_curve_does_not_fire(self):
        idx = pd.bdate_range("2023-01-02", periods=100)
        macro = {"T10Y2Y": pd.Series(np.linspace(1.0, -0.5, 100), index=idx)}
        scores = macro_tilt_scores(macro, idx[-1], SECTOR_ETFS, window=20)
        assert (scores == 0).all()

    def test_credit_widening_defensive_tilt(self):
        idx = pd.bdate_range("2023-01-02", periods=100)
        macro = {"BAMLH0A0HYM2": pd.Series(np.linspace(3.0, 6.0, 100), index=idx)}
        scores = macro_tilt_scores(macro, idx[-1], SECTOR_ETFS, window=20)
        assert scores["XLP"] > 0 and scores["XLV"] > 0
        assert scores["XLF"] < 0 and scores["XLY"] < 0

    def test_insufficient_history_is_neutral(self):
        idx = pd.bdate_range("2023-01-02", periods=10)
        macro = {"T10Y2Y": pd.Series(1.0, index=idx)}
        scores = macro_tilt_scores(macro, idx[-1], SECTOR_ETFS, window=20)
        assert (scores == 0).all()

    def test_cpi_needs_a_year_of_history(self):
        idx = pd.bdate_range("2023-01-02", periods=100)
        macro = {"CPIAUCSL": pd.Series(np.linspace(300, 320, 100), index=idx)}
        scores = macro_tilt_scores(macro, idx[-1], SECTOR_ETFS, window=20)
        assert (scores == 0).all()  # < 252 obs -> rule cannot evaluate
