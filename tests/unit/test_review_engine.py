"""Tests for the weights-contract backtest engine (WP-1.4)."""
import numpy as np
import pandas as pd
import pytest

from alpha_research.review.engine import (
    equal_weight_baseline,
    rebalance_dates,
    run_weights_backtest,
)


def _prices(n=300, tickers=("AAA", "BBB"), seed=3, drift=0.0005):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2022-01-03", periods=n)
    return pd.DataFrame(
        {t: 100.0 * np.cumprod(1 + rng.normal(drift, 0.01, n)) for t in tickers},
        index=idx,
    )


@pytest.mark.unit
class TestRunWeightsBacktest:
    def test_zero_shift_rejected_as_lookahead(self):
        px = _prices()
        w = pd.DataFrame(0.5, index=px.index, columns=px.columns)
        with pytest.raises(ValueError, match="look-ahead"):
            run_weights_backtest(w, px, shift_bars=0)

    def test_known_answer_single_asset_no_costs(self):
        """100% in one asset, t_close execution: net return = next-day return."""
        px = _prices(tickers=("AAA",))
        w = pd.DataFrame(1.0, index=px.index, columns=["AAA"])
        res = run_weights_backtest(w, px, cost_bps=0.0, shift_bars=1)
        asset_rets = px["AAA"].pct_change()
        # After day-1 entry, daily returns equal the asset's returns
        aligned = res.daily_returns.iloc[1:]
        expected = asset_rets.loc[aligned.index]
        assert np.allclose(aligned.values, expected.values, atol=1e-12)

    def test_costs_reduce_returns(self):
        px = _prices()
        w = pd.DataFrame(np.nan, index=px.index, columns=px.columns)
        monthly = rebalance_dates(px.index, "monthly")
        rng = np.random.default_rng(0)
        for d in monthly:
            a = rng.uniform(0.2, 0.8)
            w.loc[d] = [a, 1 - a]
        free = run_weights_backtest(w, px, cost_bps=0.0)
        costly = run_weights_backtest(w, px, cost_bps=50.0)
        assert costly.metrics["total_return"] < free.metrics["total_return"]
        assert costly.metrics["cost_bps"] == 50.0

    def test_weights_ffill_between_rebalances(self):
        px = _prices()
        w = pd.DataFrame(np.nan, index=px.index, columns=px.columns)
        w.iloc[0] = [0.6, 0.4]
        res = run_weights_backtest(w, px, cost_bps=0.0)
        # Effective weights stay constant after entry (no further targets)
        assert np.allclose(res.weights.iloc[-1].values, [0.6, 0.4])

    def test_no_column_overlap_raises(self):
        px = _prices()
        w = pd.DataFrame(1.0, index=px.index, columns=["ZZZ"])
        with pytest.raises(ValueError, match="overlap"):
            run_weights_backtest(w, px)

    def test_too_short_raises(self):
        px = _prices(n=10)
        w = pd.DataFrame(0.5, index=px.index, columns=px.columns)
        with pytest.raises(ValueError, match="too short"):
            run_weights_backtest(w, px)

    def test_empty_weights_raise(self):
        px = _prices()
        with pytest.raises(ValueError, match="empty"):
            run_weights_backtest(pd.DataFrame(), px)

    def test_metrics_present_and_sane(self):
        px = _prices()
        w = pd.DataFrame(0.5, index=px.index, columns=px.columns)
        res = run_weights_backtest(w, px)
        for key in (
            "total_return",
            "annualized_return",
            "volatility",
            "sharpe_ratio",
            "max_drawdown",
            "annual_turnover",
            "n_days",
        ):
            assert key in res.metrics
        assert res.metrics["max_drawdown"] <= 0
        assert res.metrics["volatility"] >= 0


@pytest.mark.unit
class TestRebalanceDates:
    def test_monthly_picks_last_trading_day(self):
        idx = pd.bdate_range("2024-01-01", "2024-03-29")
        dates = rebalance_dates(idx, "monthly")
        assert pd.Timestamp("2024-01-31") in dates
        assert pd.Timestamp("2024-02-29") in dates
        assert len(dates) == 3
        assert all(d in idx for d in dates)

    def test_daily_is_identity(self):
        idx = pd.bdate_range("2024-01-01", periods=10)
        assert rebalance_dates(idx, "daily").equals(idx)

    def test_weekly(self):
        idx = pd.bdate_range("2024-01-01", "2024-01-31")
        dates = rebalance_dates(idx, "weekly")
        # last trading day of each ISO week, always members of the index
        assert all(d in idx for d in dates)
        assert len(dates) == 5


@pytest.mark.unit
def test_equal_weight_baseline_runs():
    px = _prices(tickers=("AAA", "BBB", "CCC"))
    res = equal_weight_baseline(px, rebalance="monthly", cost_bps=5.0)
    # Effective weights should hover near 1/3 per asset
    assert np.allclose(res.weights.iloc[-1].sum(), 1.0, atol=1e-9)
    assert res.metrics["n_days"] > 200
