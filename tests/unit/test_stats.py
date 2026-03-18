"""Tests for backtests/stats/ — statistical rigor module."""

import numpy as np
import pandas as pd
import pytest

# ===========================================================================
# Sharpe Tests
# ===========================================================================


class TestProbabilisticSharpeRatio:
    def test_psr_range(self):
        """PSR should be in [0, 1]."""
        from backtests.stats.sharpe_tests import probabilistic_sharpe_ratio

        rng = np.random.RandomState(42)
        returns = rng.normal(0.0005, 0.01, 500)
        psr = probabilistic_sharpe_ratio(returns)
        assert 0 <= psr <= 1

    def test_psr_zero_for_negative_sharpe(self):
        """PSR should be low for a strategy with negative expected returns."""
        from backtests.stats.sharpe_tests import probabilistic_sharpe_ratio

        rng = np.random.RandomState(42)
        returns = rng.normal(-0.002, 0.01, 500)  # Negative expected return
        psr = probabilistic_sharpe_ratio(returns, benchmark_sharpe=0.0)
        assert psr < 0.5

    def test_psr_high_for_strong_strategy(self):
        """PSR should be high for a strategy with clear positive Sharpe."""
        from backtests.stats.sharpe_tests import probabilistic_sharpe_ratio

        rng = np.random.RandomState(42)
        returns = rng.normal(0.003, 0.01, 1000)  # Strong positive Sharpe
        psr = probabilistic_sharpe_ratio(returns, benchmark_sharpe=0.0)
        assert psr > 0.95


class TestDeflatedSharpeRatio:
    def test_dsr_leq_psr(self):
        """DSR should always be <= PSR (more conservative)."""
        from backtests.stats.sharpe_tests import (
            deflated_sharpe_ratio,
            probabilistic_sharpe_ratio,
        )

        rng = np.random.RandomState(42)
        returns = rng.normal(0.001, 0.01, 500)
        psr = probabilistic_sharpe_ratio(returns)
        dsr = deflated_sharpe_ratio(returns, n_trials=100)
        assert dsr <= psr + 1e-10  # Small tolerance for float

    def test_dsr_decreases_with_more_trials(self):
        """More trials should reduce DSR (higher multiple testing penalty)."""
        from backtests.stats.sharpe_tests import deflated_sharpe_ratio

        rng = np.random.RandomState(42)
        returns = rng.normal(0.001, 0.01, 500)
        dsr_10 = deflated_sharpe_ratio(returns, n_trials=10)
        dsr_1000 = deflated_sharpe_ratio(returns, n_trials=1000)
        assert dsr_1000 < dsr_10

    def test_random_strategy_near_zero(self):
        """DSR of a random strategy with many trials should be near 0."""
        from backtests.stats.sharpe_tests import deflated_sharpe_ratio

        rng = np.random.RandomState(42)
        returns = rng.normal(0.0, 0.01, 252)  # Zero-mean returns
        dsr = deflated_sharpe_ratio(returns, n_trials=500)
        assert dsr < 0.5


class TestSharpeConfidenceInterval:
    def test_ci_contains_point_estimate(self):
        """Point estimate should be within confidence interval."""
        from backtests.stats.sharpe_tests import sharpe_confidence_interval

        rng = np.random.RandomState(42)
        returns = rng.normal(0.001, 0.01, 500)
        lower, point, upper = sharpe_confidence_interval(returns)
        assert lower <= point <= upper

    def test_wider_ci_with_less_data(self):
        """CI should be wider with less data."""
        from backtests.stats.sharpe_tests import sharpe_confidence_interval

        rng = np.random.RandomState(42)
        returns_long = rng.normal(0.001, 0.01, 1000)
        returns_short = returns_long[:100]

        _, _, upper_long = sharpe_confidence_interval(returns_long)
        lower_long, _, _ = sharpe_confidence_interval(returns_long)
        _, _, upper_short = sharpe_confidence_interval(returns_short)
        lower_short, _, _ = sharpe_confidence_interval(returns_short)

        width_long = upper_long - lower_long
        width_short = upper_short - lower_short
        assert width_short > width_long


# ===========================================================================
# Multiple Testing
# ===========================================================================


class TestBonferroniCorrection:
    def test_bonferroni_most_conservative(self):
        """Bonferroni should reject fewer than FDR."""
        from backtests.stats.multiple_testing import (
            bonferroni_correction,
            fdr_correction,
        )

        p_values = np.array([0.001, 0.01, 0.03, 0.05, 0.10, 0.50])
        bonf_reject, _ = bonferroni_correction(p_values, alpha=0.05)
        fdr_reject, _ = fdr_correction(p_values, alpha=0.05)
        assert bonf_reject.sum() <= fdr_reject.sum()

    def test_bonferroni_adjusted_pvalues(self):
        """Adjusted p-values should be original * n, capped at 1."""
        from backtests.stats.multiple_testing import bonferroni_correction

        p_values = np.array([0.01, 0.10, 0.50])
        _, adjusted = bonferroni_correction(p_values)
        np.testing.assert_allclose(adjusted, [0.03, 0.30, 1.00])


class TestFDRCorrection:
    def test_fdr_rejects_more_than_bonferroni(self):
        """FDR should generally reject at least as many as Bonferroni."""
        from backtests.stats.multiple_testing import (
            bonferroni_correction,
            fdr_correction,
        )

        p_values = np.array([0.001, 0.005, 0.01, 0.03, 0.05, 0.50])
        bonf_reject, _ = bonferroni_correction(p_values, alpha=0.10)
        fdr_reject, _ = fdr_correction(p_values, alpha=0.10)
        assert fdr_reject.sum() >= bonf_reject.sum()


class TestWhitesRealityCheck:
    def test_random_strategies_high_pvalue(self):
        """Random strategies should have high p-value (fail to reject null)."""
        from backtests.stats.multiple_testing import whites_reality_check

        rng = np.random.RandomState(42)
        n_days = 500
        n_strategies = 10
        strategy_returns = rng.normal(0, 0.01, (n_days, n_strategies))
        benchmark_returns = rng.normal(0, 0.01, n_days)

        _, p_value = whites_reality_check(
            strategy_returns, benchmark_returns, n_bootstrap=500
        )
        assert p_value > 0.05


# ===========================================================================
# Cross-Validation
# ===========================================================================


class TestPurgedKFold:
    def test_no_overlap_with_embargo(self):
        """Train and test sets should not overlap, even with embargo."""
        from backtests.stats.cross_validation import purged_kfold_split

        dates = pd.bdate_range("2020-01-01", periods=500)
        splits = purged_kfold_split(dates, n_splits=5, embargo_pct=0.02)

        assert len(splits) == 5
        for train_idx, test_idx in splits:
            overlap = np.intersect1d(train_idx, test_idx)
            assert len(overlap) == 0

    def test_embargo_excludes_adjacent(self):
        """Embargo should exclude observations adjacent to test set."""
        from backtests.stats.cross_validation import purged_kfold_split

        dates = pd.bdate_range("2020-01-01", periods=1000)
        splits = purged_kfold_split(dates, n_splits=5, embargo_pct=0.02)

        for train_idx, test_idx in splits:
            test_end = test_idx[-1]
            embargo_size = int(1000 * 0.02)
            # Observations right after test should NOT be in training
            post_test = np.arange(test_end + 1, min(test_end + embargo_size + 1, 1000))
            for idx in post_test:
                assert idx not in train_idx


class TestCPCV:
    def test_cpcv_more_paths_than_kfold(self):
        """CPCV should produce more paths than standard K-fold."""
        from backtests.stats.cross_validation import cpcv_split, purged_kfold_split

        dates = pd.bdate_range("2020-01-01", periods=500)
        kfold_splits = purged_kfold_split(dates, n_splits=6)
        cpcv_splits = cpcv_split(dates, n_splits=6, n_test_groups=2)

        assert len(cpcv_splits) > len(kfold_splits)
        # C(6,2) = 15 combinations
        assert len(cpcv_splits) == 15


class TestWalkForwardSplit:
    def test_non_overlapping_test_windows(self):
        """With default step = test_window, test windows should not overlap."""
        from backtests.stats.cross_validation import walk_forward_split

        dates = pd.bdate_range("2020-01-01", periods=1000)
        splits = walk_forward_split(dates, train_window=252, test_window=63)

        assert len(splits) >= 5
        for i in range(len(splits) - 1):
            _, test1 = splits[i]
            _, test2 = splits[i + 1]
            overlap = np.intersect1d(test1, test2)
            assert len(overlap) == 0


# ===========================================================================
# Bootstrap
# ===========================================================================


class TestBlockBootstrap:
    def test_bootstrap_preserves_mean(self):
        """Bootstrapped mean should be close to sample mean."""
        from backtests.stats.bootstrap import block_bootstrap

        rng = np.random.RandomState(42)
        data = rng.normal(5.0, 1.0, 500)
        boot_means = block_bootstrap(data, stat_func=np.mean, n_bootstrap=1000)

        assert abs(np.mean(boot_means) - np.mean(data)) < 0.2


# ===========================================================================
# Minimum Backtest Length
# ===========================================================================


class TestMinimumBacktestLength:
    def test_more_trials_needs_longer_backtest(self):
        """More trials should require longer minimum backtest."""
        from backtests.stats.minimum_backtest import minimum_backtest_length

        # Use high Sharpe so it exceeds expected max even with many trials
        min_bt_5 = minimum_backtest_length(observed_sharpe=3.0, n_trials=5)
        min_bt_50 = minimum_backtest_length(observed_sharpe=3.0, n_trials=50)
        assert min_bt_50 > min_bt_5

    def test_higher_sharpe_needs_shorter_backtest(self):
        """Higher Sharpe should require shorter minimum backtest."""
        from backtests.stats.minimum_backtest import minimum_backtest_length

        # Keep n_trials low so both Sharpes exceed the expected max
        min_bt_low = minimum_backtest_length(observed_sharpe=1.5, n_trials=3)
        min_bt_high = minimum_backtest_length(observed_sharpe=3.0, n_trials=3)
        assert min_bt_high < min_bt_low

    def test_negative_sharpe_returns_large(self):
        """Negative Sharpe should return very large minimum."""
        from backtests.stats.minimum_backtest import minimum_backtest_length

        result = minimum_backtest_length(observed_sharpe=-0.5, n_trials=10)
        assert result >= 100000


# ===========================================================================
# Cost Models
# ===========================================================================


class TestCostModels:
    def test_proportional_cost(self):
        """10bps on $150 * 100 shares = $15."""
        from backtests.costs.transaction_costs import ProportionalCostModel

        model = ProportionalCostModel(cost_bps=10.0)
        cost = model.calculate_cost(quantity=100, price=150.0)
        assert abs(cost - 15.0) < 0.01

    def test_fixed_cost(self):
        """Fixed cost should be constant regardless of trade size."""
        from backtests.costs.transaction_costs import FixedCostModel

        model = FixedCostModel(cost_per_trade=5.0)
        assert model.calculate_cost(1, 100) == 5.0
        assert model.calculate_cost(10000, 100) == 5.0
        assert model.calculate_cost(0, 100) == 0.0

    def test_composite_cost_additive(self):
        """Composite cost should sum individual models."""
        from backtests.costs.transaction_costs import (
            CompositeCostModel,
            FixedCostModel,
            ProportionalCostModel,
        )

        model = CompositeCostModel(
            models=(FixedCostModel(1.0), ProportionalCostModel(10.0))
        )
        cost = model.calculate_cost(100, 150.0)
        assert cost == 1.0 + 15.0  # Fixed + proportional

    def test_market_impact_increases_with_size(self):
        """Market impact should increase with order size."""
        from backtests.costs.transaction_costs import MarketImpactModel

        model = MarketImpactModel(volatility=0.20, adv=1_000_000)
        cost_small = model.calculate_cost(100, 150.0)
        cost_large = model.calculate_cost(100_000, 150.0)
        assert cost_large > cost_small


class TestSlippageModels:
    def test_buy_slippage_above_market(self):
        """BUY slippage should give fill price above market."""
        from backtests.costs.slippage import FixedSlippageModel

        model = FixedSlippageModel(slippage_bps=5.0)
        fill = model.calculate_slippage(150.0, 100, "BUY")
        assert fill > 150.0

    def test_sell_slippage_below_market(self):
        """SELL slippage should give fill price below market."""
        from backtests.costs.slippage import FixedSlippageModel

        model = FixedSlippageModel(slippage_bps=5.0)
        fill = model.calculate_slippage(150.0, 100, "SELL")
        assert fill < 150.0

    def test_volume_weighted_larger_order_worse_fill(self):
        """Larger orders should get worse fills."""
        from backtests.costs.slippage import VolumeWeightedSlippageModel

        model = VolumeWeightedSlippageModel(adv=1_000_000)
        fill_small = model.calculate_slippage(150.0, 100, "BUY")
        fill_large = model.calculate_slippage(150.0, 100_000, "BUY")
        assert fill_large > fill_small
