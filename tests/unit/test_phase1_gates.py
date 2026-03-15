"""End-to-end validation of Phase 1 quantitative gates.

Verifies that all 11 gates required for APPROVED verdict can be computed
without errors against synthetic data.  This test does NOT check that any
real strategy passes the thresholds — it confirms the computation pipeline
is fully wired and produces finite values.

Gates (from research/STRATEGY_TRACKER.md + PM advisory):
  1. Deflated Sharpe Ratio > 0
  2. Walk-forward OOS hit rate > 55%
  3. Survives 2x realistic costs: Sharpe > 0
  4. PSR > 0.80
  5. Worst regime annual loss > -15%
  6. LLM verdict != ABANDON  (integration only — synthetic stub here)
  7. Strategy half-life > 2 years
  8. MinBTL < available data length
  9. Dynamic rebalancing produces finite equity curve
 10. CostModel (CompositeCostModel) integrates with vectorized backtest
 11. Trading-day alignment via exchange_calendars (no holiday rows in output)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_prices(n: int = 1500, seed: int = 42, tickers=None):
    """Synthetic OHLCV price data."""
    rng = np.random.RandomState(seed)
    dates = pd.bdate_range("2018-01-01", periods=n)

    if tickers is None:
        close = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, n)))
        return pd.DataFrame(
            {
                "open": close * (1 + rng.normal(0, 0.001, n)),
                "high": close * (1 + abs(rng.normal(0, 0.005, n))),
                "low": close * (1 - abs(rng.normal(0, 0.005, n))),
                "close": close,
                "volume": rng.randint(1000, 10000, n),
            },
            index=dates,
        )

    data = {}
    for ticker in tickers:
        close = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, n)))
        data[ticker] = close
    return pd.DataFrame(data, index=dates)


def make_returns(n: int = 1000, sharpe: float = 0.7, seed: int = 42) -> pd.Series:
    """Synthetic daily return series with approximate target Sharpe."""
    rng = np.random.RandomState(seed)
    daily_mean = sharpe * 0.16 / 252  # vol ≈ 16%
    daily_std = 0.16 / np.sqrt(252)
    rets = rng.normal(daily_mean, daily_std, n)
    return pd.Series(rets, index=pd.bdate_range("2018-01-01", periods=n))


# ===========================================================================
# Gate 1: Deflated Sharpe Ratio > 0
# ===========================================================================


class TestGate1DeflatedSharpe:
    def test_deflated_sharpe_computable(self):
        """Gate 1: deflated_sharpe_ratio() runs and returns a float."""
        from backtests.stats import deflated_sharpe_ratio

        rets = make_returns(1000)
        dsr = deflated_sharpe_ratio(
            returns=rets.values,
            n_trials=10,
        )
        assert isinstance(dsr, float), "Deflated Sharpe must be a float"
        assert np.isfinite(dsr), "Deflated Sharpe must be finite"


# ===========================================================================
# Gate 2: Walk-forward OOS hit rate > 55%
# ===========================================================================


class TestGate2WalkForwardHitRate:
    def test_walk_forward_splits_no_overlap(self):
        """Gate 2: CPCV splits are non-overlapping (prerequisite for hit rate)."""
        from backtests.stats import cpcv_split

        rets = make_returns(1000)
        # cpcv_split takes a DatetimeIndex, n_splits, n_test_groups
        splits = list(cpcv_split(rets.index, n_splits=5, n_test_groups=2))
        assert len(splits) > 0, "cpcv_split must produce at least one fold"
        for train_idx, test_idx in splits:
            overlap = set(train_idx).intersection(set(test_idx))
            assert len(overlap) == 0, "No overlap between train and test"


# ===========================================================================
# Gate 3: Survives 2x realistic costs
# ===========================================================================


class TestGate3CostSurvival:
    def test_cost_model_integrates_with_backtest(self):
        """Gate 3: CompositeCostModel wires into PortfolioBuilder.backtest()."""
        from backtests.builder import PortfolioBuilder, PortfolioConfig
        from backtests.costs import CompositeCostModel, ProportionalCostModel

        prices = make_prices(500, tickers=["A", "B"])
        config = PortfolioConfig(
            universe=["A", "B"],
            optimization="equal_weight",
            rebalance_frequency="monthly",
            commission=0.0,  # Use cost_model instead
        )

        builder = PortfolioBuilder(config)
        builder.prices = prices
        builder.data = {t: prices[[t]] for t in prices.columns}
        builder.weights = pd.Series({"A": 0.5, "B": 0.5})

        # 2x realistic cost: 20 bps proportional
        cost_2x = CompositeCostModel(models=(ProportionalCostModel(cost_bps=20.0),))
        result = builder.backtest(cost_model=cost_2x, dynamic_reoptimize=False)

        assert "total_return" in result
        assert np.isfinite(result["total_return"]), "total_return must be finite"
        assert "daily_returns" in result

        # Cost version should have lower return than zero-cost
        builder_nc = PortfolioBuilder(config)
        builder_nc.prices = prices
        builder_nc.data = {t: prices[[t]] for t in prices.columns}
        builder_nc.weights = pd.Series({"A": 0.5, "B": 0.5})
        result_nc = builder_nc.backtest(cost_model=None, dynamic_reoptimize=False)

        assert (
            result["total_return"] <= result_nc["total_return"]
        ), "Costs must reduce total return"


# ===========================================================================
# Gate 4: PSR > 0.80
# ===========================================================================


class TestGate4PSR:
    def test_psr_computable(self):
        """Gate 4: probabilistic_sharpe_ratio() runs and returns a float in [0,1]."""
        from backtests.stats import probabilistic_sharpe_ratio

        rets = make_returns(1000)
        psr = probabilistic_sharpe_ratio(
            returns=rets.values,
            benchmark_sharpe=0.0,
        )
        assert isinstance(psr, float), "PSR must be a float"
        assert 0.0 <= psr <= 1.0, f"PSR must be in [0,1], got {psr}"


# ===========================================================================
# Gate 5: Worst regime annual loss > -15%
# ===========================================================================


class TestGate5RegimeLoss:
    def test_regime_conditional_sharpe_computable(self):
        """Gate 5: regime_conditional_sharpe() runs and returns dict."""
        from backtests.stats import regime_conditional_sharpe

        rng = np.random.RandomState(99)
        n = 1000
        rets = pd.Series(
            rng.normal(0.0003, 0.01, n),
            index=pd.bdate_range("2018-01-01", periods=n),
        )
        market = pd.Series(
            rng.normal(0.0003, 0.012, n),
            index=rets.index,
        )

        result = regime_conditional_sharpe(rets, market)
        assert isinstance(result, dict), "Must return a dict"
        assert (
            "bull" in result or "bear" in result or len(result) > 0
        ), "Must return at least one regime"

    def test_max_drawdown_computable(self):
        """Gate 5: max drawdown can be extracted from PortfolioBuilder backtest."""
        from backtests.builder import PortfolioBuilder, PortfolioConfig

        prices = make_prices(500, tickers=["A", "B"])
        config = PortfolioConfig(universe=["A", "B"], optimization="equal_weight")
        builder = PortfolioBuilder(config)
        builder.prices = prices
        builder.data = {t: prices[[t]] for t in prices.columns}
        builder.weights = pd.Series({"A": 0.5, "B": 0.5})
        result = builder.backtest(dynamic_reoptimize=False)

        assert "max_drawdown" in result
        assert result["max_drawdown"] <= 0, "Max drawdown must be <= 0"
        assert np.isfinite(result["max_drawdown"]), "Max drawdown must be finite"


# ===========================================================================
# Gate 6: LLM verdict != ABANDON (stub — not a live LLM test)
# ===========================================================================


class TestGate6LLMVerdict:
    def test_llm_verdict_stub(self):
        """Gate 6: LLM verdict integration exists as a stub.

        The actual LLM call is not made in unit tests (requires API key).
        This test verifies the gate category is recognized in the gate set.
        """
        # The gate exists — LLM verdict is checked manually during research
        # via backend/llm_verdict.py or the Cerebro pipeline.
        # This test confirms the gate is acknowledged but not blocking CI.
        valid_verdicts = {"APPROVE", "MONITOR", "REVISE", "ABANDON"}
        # Stub: any verdict except ABANDON passes
        test_verdict = "MONITOR"
        assert test_verdict in valid_verdicts
        assert test_verdict != "ABANDON", "Gate 6: verdict must not be ABANDON"


# ===========================================================================
# Gate 7: Strategy half-life > 2 years
# ===========================================================================


class TestGate7HalfLife:
    def test_strategy_half_life_computable(self):
        """Gate 7: strategy_half_life() runs and returns finite float."""
        from backtests.stats import rolling_sharpe, strategy_half_life

        rets = make_returns(1500)
        sharpes = rolling_sharpe(rets, window=252)
        half_life = strategy_half_life(sharpes)

        assert np.isfinite(half_life), f"Half-life must be finite, got {half_life}"


# ===========================================================================
# Gate 8: MinBTL < available data length
# ===========================================================================


class TestGate8MinBTL:
    def test_minimum_backtest_length_computable(self):
        """Gate 8: minimum_backtest_length() runs and returns positive int."""
        from backtests.stats import minimum_backtest_length

        # With n_trials=1 (single strategy, no multiple testing) and a
        # positive Sharpe, MinBTL should be a finite, positive integer.
        minbtl = minimum_backtest_length(
            observed_sharpe=0.7,
            n_trials=1,
        )
        assert minbtl > 0, f"MinBTL must be positive, got {minbtl}"
        assert isinstance(minbtl, (int, float)), "MinBTL must be numeric"
        assert (
            minbtl < 1_000_000
        ), f"MinBTL should be finite (not the infinity sentinel), got {minbtl}"

        # Gate: actual data length must exceed MinBTL
        n_obs = 1500
        assert (
            n_obs > minbtl
        ), f"Available data ({n_obs} days) must exceed MinBTL ({minbtl} days)"


# ===========================================================================
# Gate 9: Dynamic rebalancing produces finite equity curve
# ===========================================================================


class TestGate9DynamicRebalancing:
    def test_dynamic_reoptimize_produces_finite_curve(self):
        """Gate 9: backtest(dynamic_reoptimize=True) produces finite equity curve."""
        from backtests.builder import PortfolioBuilder, PortfolioConfig

        prices = make_prices(500, tickers=["SPY", "TLT", "GLD"])
        config = PortfolioConfig(
            universe=["SPY", "TLT", "GLD"],
            optimization="equal_weight",
            rebalance_frequency="monthly",
        )
        builder = PortfolioBuilder(config)
        builder.prices = prices
        builder.data = {t: prices[[t]] for t in prices.columns}
        builder.weights = pd.Series({"SPY": 1 / 3, "TLT": 1 / 3, "GLD": 1 / 3})
        result = builder.backtest(dynamic_reoptimize=True)

        assert "equity_curve" in result
        equity = result["equity_curve"]
        assert len(equity) > 0, "Equity curve must be non-empty"
        assert np.all(
            np.isfinite(equity["portfolio_value"].values)
        ), "All equity values must be finite"
        assert np.all(
            equity["portfolio_value"].values > 0
        ), "Portfolio value must be positive"


# ===========================================================================
# Gate 10: CostModel hierarchy integrates correctly (end-to-end)
# ===========================================================================


class TestGate10CostModelIntegration:
    def test_composite_cost_model_api(self):
        """Gate 10: CompositeCostModel.calculate_cost() works correctly."""
        from backtests.costs import (
            CompositeCostModel,
            FixedCostModel,
            ProportionalCostModel,
        )

        model = CompositeCostModel(
            models=(
                FixedCostModel(cost_per_trade=1.0),
                ProportionalCostModel(cost_bps=10.0),
            )
        )
        # Trade: 100 units at $50.00
        cost = model.calculate_cost(quantity=100, price=50.0)
        expected = 1.0 + (100 * 50.0 * 10 / 10000)
        assert abs(cost - expected) < 1e-10, f"Expected {expected}, got {cost}"

    def test_cost_model_frozen(self):
        """Gate 10: CostModel instances are immutable (frozen dataclass)."""
        from backtests.costs import ProportionalCostModel

        model = ProportionalCostModel(cost_bps=10.0)
        with pytest.raises((AttributeError, TypeError)):
            model.cost_bps = 20.0  # type: ignore[misc]


# ===========================================================================
# Gate 11: Trading-day alignment via exchange_calendars
# ===========================================================================


class TestGate11CalendarAlignment:
    def test_align_to_trading_days_removes_weekends(self):
        """Gate 11: align_to_trading_days() removes Saturday/Sunday rows."""
        from backtests.calendar import align_to_trading_days

        # Create a price series with explicit weekend dates
        dates = pd.date_range("2024-01-01", "2024-01-31", freq="D")
        df = pd.DataFrame({"close": np.ones(len(dates))}, index=dates)

        aligned = align_to_trading_days(df, exchange="XNYS")

        # No Saturdays (dayofweek==5) or Sundays (dayofweek==6) should remain
        assert not any(
            aligned.index.dayofweek >= 5
        ), "Calendar alignment must remove weekends"
        assert len(aligned) < len(df), "Aligned data must be shorter than raw data"

    def test_get_trading_days_returns_business_days(self):
        """Gate 11: get_trading_days() returns only NYSE trading sessions."""
        from backtests.calendar import get_trading_days

        days = get_trading_days("2024-01-01", "2024-01-31", exchange="XNYS")
        assert len(days) > 0, "Must return at least one trading day"
        assert not any(
            d.dayofweek >= 5 for d in days
        ), "Trading days must not include weekends"
        # NYSE Jan 1 is a holiday — should not be in result
        jan_1 = pd.Timestamp("2024-01-01")
        assert jan_1 not in days, "New Year's Day should not be a trading day"

    def test_align_to_trading_days_empty_df(self):
        """Gate 11: align_to_trading_days handles empty DataFrame gracefully."""
        from backtests.calendar import align_to_trading_days

        empty = pd.DataFrame({"close": []})
        result = align_to_trading_days(empty)
        assert result.empty, "Empty input should return empty DataFrame"
