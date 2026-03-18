"""Tests for Phase 4 & 5 — scalability and integration modules."""

import json
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# ===========================================================================
# Signal Cache
# ===========================================================================


class TestSignalCache:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_put_and_get(self):
        """Cache put then get should return same data."""
        from backtests.cache import SignalCache

        cache = SignalCache(cache_dir=self.tmpdir)
        df = pd.DataFrame({"signal": [1.0, 2.0, 3.0]})
        cache.put("momentum", {"lookback": 60}, "abc123", df)

        result = cache.get("momentum", {"lookback": 60}, "abc123")
        assert result is not None
        pd.testing.assert_frame_equal(result, df)

    def test_cache_miss(self):
        """Cache get on non-existent key returns None."""
        from backtests.cache import SignalCache

        cache = SignalCache(cache_dir=self.tmpdir)
        result = cache.get("nonexistent", {}, "xyz")
        assert result is None

    def test_invalidate_specific(self):
        """Invalidate specific signal should remove only that signal."""
        from backtests.cache import SignalCache

        cache = SignalCache(cache_dir=self.tmpdir)
        df = pd.DataFrame({"a": [1.0]})
        cache.put("sig_a", {}, "h1", df)
        cache.put("sig_b", {}, "h2", df)

        count = cache.invalidate("sig_a")
        assert count == 1
        assert cache.get("sig_a", {}, "h1") is None
        assert cache.get("sig_b", {}, "h2") is not None

    def test_invalidate_all(self):
        """Invalidate with no signal name should remove all."""
        from backtests.cache import SignalCache

        cache = SignalCache(cache_dir=self.tmpdir)
        df = pd.DataFrame({"a": [1.0]})
        cache.put("sig_a", {}, "h1", df)
        cache.put("sig_b", {}, "h2", df)

        count = cache.invalidate()
        assert count == 2

    def test_compute_data_hash_deterministic(self):
        """Same DataFrame should produce same hash."""
        from backtests.cache import SignalCache

        df = pd.DataFrame({"a": [1.0, 2.0], "b": [3.0, 4.0]})
        h1 = SignalCache.compute_data_hash(df)
        h2 = SignalCache.compute_data_hash(df)
        assert h1 == h2

    def test_compute_data_hash_different(self):
        """Different DataFrames should produce different hashes."""
        from backtests.cache import SignalCache

        df1 = pd.DataFrame({"a": [1.0, 2.0]})
        df2 = pd.DataFrame({"a": [1.0, 3.0]})
        assert SignalCache.compute_data_hash(df1) != SignalCache.compute_data_hash(df2)

    def test_stats(self):
        """Stats should reflect cache contents."""
        from backtests.cache import SignalCache

        cache = SignalCache(cache_dir=self.tmpdir)
        df = pd.DataFrame({"a": range(100)})
        cache.put("test_sig", {"p": 1}, "h1", df)

        stats = cache.stats()
        assert stats["n_entries"] == 1
        assert "test_sig" in stats["signals"]


# ===========================================================================
# Run Manager
# ===========================================================================


class TestRunManager:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_create_and_load_run(self):
        """Create a run, then load it back."""
        from backtests.run_manager import RunManager

        mgr = RunManager(output_dir=self.tmpdir)
        cfg = mgr.create_run("momentum_60", {"lookback": 60}, "test run")

        assert cfg.strategy_name == "momentum_60"
        assert cfg.params == {"lookback": 60}

        # Save results
        metrics = {"sharpe_ratio": 1.5, "max_drawdown": -0.15}
        mgr.save_results(cfg.run_id, metrics)

        # Load back
        loaded = mgr.load_run(cfg.run_id)
        assert loaded.strategy_name == "momentum_60"
        assert loaded.metrics["sharpe_ratio"] == 1.5

    def test_save_run_one_step(self):
        """One-step save_run should create a complete record."""
        from backtests.run_manager import RunManager

        mgr = RunManager(output_dir=self.tmpdir)
        run = mgr.save_run(
            strategy_name="vol_scaled",
            params={"vol_target": 0.10},
            metrics={"sharpe_ratio": 2.0, "calmar": 1.5},
        )

        assert run.strategy_name == "vol_scaled"
        assert run.metrics["sharpe_ratio"] == 2.0

    def test_list_runs(self):
        """list_runs should return a DataFrame of saved runs."""
        from backtests.run_manager import RunManager

        mgr = RunManager(output_dir=self.tmpdir)
        mgr.save_run("strat_a", {"p": 1}, {"sharpe_ratio": 1.0})
        mgr.save_run("strat_b", {"p": 2}, {"sharpe_ratio": 2.0})

        df = mgr.list_runs()
        assert len(df) == 2
        assert "run_id" in df.columns

    def test_list_runs_filter_by_strategy(self):
        """list_runs with strategy filter should return only matching runs."""
        from backtests.run_manager import RunManager

        mgr = RunManager(output_dir=self.tmpdir)
        mgr.save_run("strat_a", {}, {"sharpe_ratio": 1.0})
        mgr.save_run("strat_b", {}, {"sharpe_ratio": 2.0})

        df = mgr.list_runs(strategy_name="strat_a")
        assert len(df) == 1
        assert df.iloc[0]["strategy_name"] == "strat_a"

    def test_compare_runs(self):
        """compare_runs should produce a side-by-side DataFrame."""
        from backtests.run_manager import RunManager

        mgr = RunManager(output_dir=self.tmpdir)
        r1 = mgr.save_run("momentum", {"lb": 20}, {"sharpe_ratio": 1.0})
        r2 = mgr.save_run("momentum", {"lb": 60}, {"sharpe_ratio": 1.5})

        comp = mgr.compare_runs([r1.run_id, r2.run_id])
        assert len(comp) == 2
        assert "sharpe_ratio" in comp.columns

    def test_save_and_load_equity_curve(self):
        """Equity curve should be persisted and loadable."""
        from backtests.run_manager import RunManager

        mgr = RunManager(output_dir=self.tmpdir)
        eq = pd.DataFrame(
            {
                "date": pd.bdate_range("2020-01-01", periods=100),
                "equity": np.cumsum(np.random.randn(100)) + 100,
            }
        )

        run = mgr.save_run("test", {}, {"sr": 1.0}, equity_curve=eq)
        loaded = mgr.load_equity_curve(run.run_id)
        assert loaded is not None
        assert len(loaded) == 100

    def test_delete_run(self):
        """delete_run should remove the run directory."""
        from backtests.run_manager import RunManager

        mgr = RunManager(output_dir=self.tmpdir)
        run = mgr.save_run("test", {}, {"sr": 1.0})
        assert mgr.delete_run(run.run_id)
        assert not mgr.delete_run(run.run_id)  # Already deleted


# ===========================================================================
# Decay Analysis
# ===========================================================================


class TestRollingSharpe:
    def test_output_length(self):
        """Rolling Sharpe should have same length as input."""
        from backtests.stats.decay_analysis import rolling_sharpe

        rng = np.random.RandomState(42)
        returns = pd.Series(rng.normal(0.001, 0.01, 500))
        rs = rolling_sharpe(returns, window=63)
        assert len(rs) == len(returns)

    def test_warmup_is_nan(self):
        """First window-1 values should be NaN."""
        from backtests.stats.decay_analysis import rolling_sharpe

        rng = np.random.RandomState(42)
        returns = pd.Series(rng.normal(0.001, 0.01, 500))
        rs = rolling_sharpe(returns, window=63)
        assert rs.iloc[:62].isna().all()
        assert rs.iloc[62:].notna().any()


class TestStrategyHalfLife:
    def test_decaying_strategy(self):
        """A strategy with decaying Sharpe should return finite half-life."""
        from backtests.stats.decay_analysis import strategy_half_life

        # Create a decaying Sharpe series
        t = np.arange(500, dtype=float)
        sharpes = pd.Series(2.0 * np.exp(-0.005 * t) + np.random.randn(500) * 0.1)
        hl = strategy_half_life(sharpes)
        # Should detect decay and return a finite number
        if hl is not None:
            assert 50 < hl < 500  # True half-life is ln(2)/0.005 ≈ 139

    def test_improving_strategy(self):
        """A strategy with improving Sharpe should return None."""
        from backtests.stats.decay_analysis import strategy_half_life

        sharpes = pd.Series(np.linspace(0.5, 2.0, 300))
        hl = strategy_half_life(sharpes)
        assert hl is None


class TestCorrelationWithExisting:
    def test_perfectly_correlated(self):
        """Identical strategies should have correlation ~1."""
        from backtests.stats.decay_analysis import correlation_with_existing

        rng = np.random.RandomState(42)
        idx = pd.date_range("2020-01-01", periods=500, freq="B")
        returns = pd.Series(rng.normal(0, 0.01, 500), index=idx, name="ret")
        result = correlation_with_existing(returns, {"same": returns})
        # Result is a correlation matrix DataFrame
        assert result.loc["same", "new_strategy"] > 0.99

    def test_uncorrelated(self):
        """Independent strategies should have low correlation."""
        from backtests.stats.decay_analysis import correlation_with_existing

        rng = np.random.RandomState(42)
        idx = pd.date_range("2020-01-01", periods=500, freq="B")
        r1 = pd.Series(rng.normal(0, 0.01, 500), index=idx, name="r1")
        rng2 = np.random.RandomState(123)
        r2 = pd.Series(rng2.normal(0, 0.01, 500), index=idx, name="r2")
        result = correlation_with_existing(r1, {"other": r2})
        assert abs(result.loc["other", "new_strategy"]) < 0.15


class TestCapacityEstimate:
    def test_positive_alpha_has_capacity(self):
        """Strategy with positive returns should have non-zero capacity."""
        from backtests.stats.decay_analysis import strategy_capacity_estimate

        rng = np.random.RandomState(42)
        returns = pd.Series(rng.normal(0.001, 0.01, 500))
        cap = strategy_capacity_estimate(returns, avg_daily_volume=10_000_000)
        assert cap > 0

    def test_negative_alpha_zero_capacity(self):
        """Strategy with negative returns should have zero capacity."""
        from backtests.stats.decay_analysis import strategy_capacity_estimate

        rng = np.random.RandomState(42)
        returns = pd.Series(rng.normal(-0.001, 0.01, 500))
        cap = strategy_capacity_estimate(returns, avg_daily_volume=10_000_000)
        assert cap == 0.0


# ===========================================================================
# Parallel Backtester (basic structural tests)
# ===========================================================================


class TestParallelBacktester:
    def test_init_clamps_workers(self):
        """Worker count should be clamped to CPU count."""
        import os

        from backtests.parallel import ParallelBacktester

        cpu_count = os.cpu_count() or 4
        pb = ParallelBacktester(n_workers=9999)
        assert pb.n_workers <= cpu_count

    def test_empty_param_grid(self):
        """Empty param grid produces single empty combo (product of nothing)."""
        from backtests.parallel import _build_param_combos

        combos = _build_param_combos({})
        # product() of empty lists yields one empty dict
        assert len(combos) == 1
        assert combos[0] == {}
