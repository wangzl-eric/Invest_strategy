"""Cross-engine PnL equivalence tests (engine consolidation gate).

Proves the vectorized engine (``run_weights_backtest``), the native engine in
parity mode (``backtest_weights(cost_basis="target")``), and the independent
reference loop (``equivalence.reference_returns``) produce **identical** PnL on
the same strategies — to machine precision — while the native *realistic* mode
diverges only by the documented friction terms.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import alpha_research.backtests.runners.sector_rotation as sector_rotation
from alpha_research.backtests.equivalence import (
    assert_engines_agree,
    compare_engines,
    reference_returns,
)
from alpha_research.backtests.native import backtest_weights
from alpha_research.review.engine import run_weights_backtest

EXACT_TOL = 1e-9


# --------------------------------------------------------------------------
# Fixtures: a panel of prices + several strategy weight schedules
# --------------------------------------------------------------------------
@pytest.fixture
def prices() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    idx = pd.bdate_range("2019-01-01", periods=400)
    syms = ["AAA", "BBB", "CCC", "DDD"]
    data = 100 * np.cumprod(1 + rng.normal(0.0004, 0.011, (len(idx), 4)), axis=0)
    return pd.DataFrame(data, index=idx, columns=syms)


def _const(prices) -> pd.DataFrame:
    w = pd.DataFrame(np.nan, index=prices.index, columns=prices.columns)
    w.iloc[0] = [0.4, 0.3, 0.2, 0.1]
    return w


def _monthly(prices) -> pd.DataFrame:
    vectors = [
        [0.4, 0.3, 0.2, 0.1],
        [0.1, 0.4, 0.3, 0.2],
        [0.25, 0.25, 0.25, 0.25],
        [0.5, 0.0, 0.3, 0.2],
    ]
    w = pd.DataFrame(np.nan, index=prices.index, columns=prices.columns)
    rebal = pd.Series(prices.index).groupby(prices.index.to_period("M")).max().values
    for i, d in enumerate(rebal):
        w.loc[d] = vectors[i % len(vectors)]
    return w


def _long_short(prices) -> pd.DataFrame:
    w = pd.DataFrame(np.nan, index=prices.index, columns=prices.columns)
    rebal = pd.Series(prices.index).groupby(prices.index.to_period("M")).max().values
    for i, d in enumerate(rebal):
        w.loc[d] = [0.6, -0.4, 0.5, -0.3] if i % 2 == 0 else [-0.2, 0.5, -0.3, 0.4]
    return w


STRATEGIES = {"const": _const, "monthly": _monthly, "long_short": _long_short}


# --------------------------------------------------------------------------
# Exact agreement across engines
# --------------------------------------------------------------------------
class TestExactEquivalence:
    @pytest.mark.parametrize("strat", list(STRATEGIES))
    @pytest.mark.parametrize("cost_bps", [0.0, 5.0, 20.0])
    @pytest.mark.parametrize("shift_bars", [1, 2])
    def test_engines_agree(self, prices, strat, cost_bps, shift_bars):
        w = STRATEGIES[strat](prices)
        report = compare_engines(
            w, prices, cost_bps=cost_bps, shift_bars=shift_bars, tol=EXACT_TOL
        )
        assert report["exact_match"], report["exact_divergences"]
        assert report["max_exact_divergence"] < EXACT_TOL

    def test_native_parity_matches_vectorized_pnl(self, prices):
        w = _monthly(prices)
        nat = backtest_weights(
            w, prices, cost_bps=7.0, shift_bars=1, cost_basis="target"
        )
        vec = run_weights_backtest(w, prices, cost_bps=7.0, shift_bars=1)
        joined = pd.concat(
            [nat.daily_returns.rename("n"), vec.daily_returns.rename("v")], axis=1
        ).dropna()
        assert (joined["n"] - joined["v"]).abs().max() < EXACT_TOL
        # headline metrics match too
        assert nat.metrics["total_return"] == pytest.approx(
            vec.metrics["total_return"], abs=1e-9
        )
        assert nat.metrics["sharpe_ratio"] == pytest.approx(
            vec.metrics["sharpe_ratio"], abs=1e-9
        )

    def test_reference_equals_vectorized_exactly(self, prices):
        w = _monthly(prices)
        ref = reference_returns(w, prices, cost_bps=5.0, shift_bars=1)
        vec = run_weights_backtest(w, prices, cost_bps=5.0, shift_bars=1).daily_returns
        joined = pd.concat([ref.rename("r"), vec.rename("v")], axis=1).dropna()
        assert (joined["r"] - joined["v"]).abs().max() < EXACT_TOL

    def test_assert_engines_agree_returns_report(self, prices):
        report = assert_engines_agree(_const(prices), prices, cost_bps=5.0)
        assert report["exact_match"] is True


# --------------------------------------------------------------------------
# Realistic divergence is surfaced, not hidden
# --------------------------------------------------------------------------
class TestRealisticDivergence:
    def test_traded_matches_parity_when_cost_free(self, prices):
        report = compare_engines(_monthly(prices), prices, cost_bps=0.0, shift_bars=1)
        # cost-free, same-bar execution → realistic == parity to machine precision
        assert report["native_traded_vs_vectorized"] < 1e-9

    def test_traded_diverges_with_costs(self, prices):
        report = compare_engines(_monthly(prices), prices, cost_bps=20.0, shift_bars=1)
        # realistic charges drift-correction turnover → strictly larger divergence
        assert report["native_traded_vs_vectorized"] > 1e-6
        # but the exact engines still agree
        assert report["exact_match"]


# --------------------------------------------------------------------------
# Real strategy runner
# --------------------------------------------------------------------------
class TestRealStrategy:
    @pytest.fixture
    def sector_prices(self) -> pd.DataFrame:
        rng = np.random.default_rng(7)
        idx = pd.bdate_range("2018-01-01", periods=500)
        u = sector_rotation.SECTOR_ETFS
        data = 100 * np.cumprod(
            1 + rng.normal(0.0003, 0.011, (len(idx), len(u))), axis=0
        )
        return pd.DataFrame(data, index=idx, columns=u)

    def test_sector_rotation_engines_agree(self, sector_prices):
        w = sector_rotation.build_weights(
            sector_prices, None, sector_rotation.DEFAULT_PARAMS
        )
        report = compare_engines(w, sector_prices, cost_bps=5.0, shift_bars=1)
        assert report["exact_match"], report["exact_divergences"]
        assert report["max_exact_divergence"] < EXACT_TOL
        # the engines report the same Sharpe
        s_vec = report["summary"]["vectorized"]["sharpe"]
        s_par = report["summary"]["native_parity"]["sharpe"]
        assert s_vec == pytest.approx(s_par, abs=1e-9)


# --------------------------------------------------------------------------
# reference_returns edge cases
# --------------------------------------------------------------------------
class TestReferenceReturns:
    def test_no_overlap_raises(self, prices):
        bad = pd.DataFrame({"ZZZ": [0.5]}, index=pd.DatetimeIndex([prices.index[0]]))
        with pytest.raises(ValueError):
            reference_returns(bad, prices)

    def test_returns_series_named(self, prices):
        ref = reference_returns(_const(prices), prices, cost_bps=5.0, shift_bars=1)
        assert ref.name == "reference"
        assert len(ref) > 100
