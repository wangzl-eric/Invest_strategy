"""Tests for the comprehensive performance metrics + event-driven reconciliation
(the shared backtester's enriched output layer, 2026-06-14)."""
import numpy as np
import pandas as pd
import pytest

from alpha_research.backtests.reporting.performance import (
    compute_performance_metrics,
    performance_headline,
)
from alpha_research.review.engine import run_weights_backtest
from alpha_research.review.validation import reconcile_event_driven


def _returns(n=600, mu=0.0005, sigma=0.01, seed=5):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    return pd.Series(rng.normal(mu, sigma, n), index=idx)


@pytest.mark.unit
class TestPerformanceMetrics:
    def test_all_groups_present(self):
        m = compute_performance_metrics(_returns())
        assert m["available"]
        for grp in ("window", "returns", "risk", "risk_adjusted", "periodic"):
            assert grp in m
        # spot-check the rich fields the user asked for
        assert "sortino" in m["risk_adjusted"]
        assert "calmar" in m["risk_adjusted"]
        assert "cagr" in m["returns"]
        assert "var_95_daily" in m["risk"]
        assert "tail_ratio" in m["risk"]
        assert "max_drawdown_days" in m["risk"]
        assert m["periodic"]["monthly_returns"]  # non-empty table

    def test_known_signs(self):
        # all-positive constant returns -> positive Sharpe, full win rate, no drawdown
        idx = pd.bdate_range("2021-01-01", periods=300)
        r = pd.Series(0.001, index=idx)
        m = compute_performance_metrics(r)
        assert m["returns"]["win_rate"] == 1.0
        assert m["risk"]["max_drawdown"] == 0.0
        assert m["risk_adjusted"]["sharpe"] > 0
        assert m["returns"]["total_return"] > 0

    def test_benchmark_block(self):
        r = _returns(seed=1)
        # benchmark correlated with r plus noise
        b = r * 0.8 + _returns(seed=2) * 0.5
        m = compute_performance_metrics(r, benchmark=b)
        vb = m["vs_benchmark"]
        assert vb["available"]
        for k in (
            "beta",
            "alpha_annualized",
            "correlation",
            "information_ratio",
            "up_capture",
        ):
            assert k in vb
        assert -2 < vb["beta"] < 5

    def test_short_series_unavailable(self):
        m = compute_performance_metrics(
            pd.Series([0.01], index=pd.bdate_range("2021-01-01", periods=1))
        )
        assert m["available"] is False

    def test_headline_subset(self):
        h = performance_headline(compute_performance_metrics(_returns()))
        assert set(["cagr", "sortino", "calmar", "tail_ratio", "win_rate"]).issubset(h)


def _weights_and_prices(n=400, seed=9):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2021-01-04", periods=n)
    tickers = ["AAA", "BBB", "CCC", "DDD"]
    px = pd.DataFrame(
        {t: 100 * np.cumprod(1 + rng.normal(0.0003, 0.012, n)) for t in tickers},
        index=idx,
    )
    # weekly long-only equal-weight target on the last trading day of each week
    w = pd.DataFrame(np.nan, index=idx, columns=tickers)
    rebal = idx.to_series().groupby(idx.to_period("W")).max().values
    w.loc[w.index.isin(rebal)] = 0.25
    return w, px


@pytest.mark.unit
class TestEngineReconciliation:
    @pytest.mark.parametrize("shift", [1, 2])
    def test_reconciles_with_vectorized_engine(self, shift):
        w, px = _weights_and_prices()
        rec = reconcile_event_driven(w, px, cost_bps=5.0, shift_bars=shift)
        assert rec["available"]
        assert rec["reconciled"], rec
        assert rec["max_daily_return_divergence"] < 1e-9
        # the independent loop should match the engine's Sharpe to ~6 dp
        vec = run_weights_backtest(w, px, cost_bps=5.0, shift_bars=shift)
        assert abs(rec["event_driven"]["sharpe"] - vec.metrics["sharpe_ratio"]) < 1e-6

    def test_dollar_neutral_long_short_reconciles(self):
        w, px = _weights_and_prices()
        # turn it into a L/S book: long AAA/BBB, short CCC/DDD
        w = w.copy()
        w[["CCC", "DDD"]] = -w[["CCC", "DDD"]]
        rec = reconcile_event_driven(w, px, cost_bps=8.0, shift_bars=2)
        assert rec["available"] and rec["reconciled"], rec
