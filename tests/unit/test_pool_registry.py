"""Tests for the strategy pool registry (WP-1.5)."""
import pytest

from alpha_research.backtests.strategies.manifest import StrategyManifest
from alpha_research.pool.registry import PoolRegistry, TransitionError


@pytest.fixture
def manifest():
    return StrategyManifest.model_validate(
        {
            "strategy_id": "pool_test_strategy",
            "name": "Pool Test",
            "track": "etf_rotation",
            "universe": ["SPY", "TLT"],
            "entrypoint": "alpha_research.backtests.runners.sector_rotation:build_weights",
        }
    )


@pytest.fixture
def pool(test_db):
    return PoolRegistry(session=test_db)


@pytest.mark.unit
class TestPoolRegistry:
    def test_register_creates_candidate(self, pool, manifest):
        entry = pool.register(manifest, manifest_path="x/manifest.yaml")
        assert entry["state"] == "candidate"
        assert entry["track"] == "etf_rotation"
        assert entry["state_history"][0]["state"] == "candidate"

    def test_reregister_preserves_state(self, pool, manifest):
        pool.register(manifest, manifest_path="x/manifest.yaml")
        pool.set_state("pool_test_strategy", "paper", reason="gates passed")
        entry = pool.register(manifest, manifest_path="y/manifest.yaml")
        assert entry["state"] == "paper"
        assert entry["manifest_path"] == "y/manifest.yaml"

    def test_legal_lifecycle_path(self, pool, manifest):
        pool.register(manifest, manifest_path="m.yaml")
        assert (
            pool.set_state("pool_test_strategy", "paper", reason="r")["state"]
            == "paper"
        )
        assert (
            pool.set_state("pool_test_strategy", "live", reason="r")["state"] == "live"
        )
        assert (
            pool.set_state("pool_test_strategy", "retired", reason="r")["state"]
            == "retired"
        )

    def test_candidate_cannot_jump_to_live(self, pool, manifest):
        pool.register(manifest, manifest_path="m.yaml")
        with pytest.raises(TransitionError, match="illegal transition"):
            pool.set_state("pool_test_strategy", "live", reason="shortcut")

    def test_retired_is_terminal(self, pool, manifest):
        pool.register(manifest, manifest_path="m.yaml")
        pool.set_state("pool_test_strategy", "retired", reason="r")
        with pytest.raises(TransitionError):
            pool.set_state("pool_test_strategy", "candidate", reason="resurrect")

    def test_demotions_allowed(self, pool, manifest):
        pool.register(manifest, manifest_path="m.yaml")
        pool.set_state("pool_test_strategy", "paper", reason="up")
        assert (
            pool.set_state("pool_test_strategy", "candidate", reason="demote")["state"]
            == "candidate"
        )

    def test_unknown_state_rejected(self, pool, manifest):
        pool.register(manifest, manifest_path="m.yaml")
        with pytest.raises(TransitionError, match="unknown state"):
            pool.set_state("pool_test_strategy", "zombie", reason="r")

    def test_unregistered_strategy_raises(self, pool):
        with pytest.raises(KeyError):
            pool.set_state("ghost", "paper", reason="r")

    def test_state_history_audited(self, pool, manifest):
        pool.register(manifest, manifest_path="m.yaml")
        pool.set_state("pool_test_strategy", "paper", reason="passed gates")
        history = pool.get("pool_test_strategy")["state_history"]
        assert [h["state"] for h in history] == ["candidate", "paper"]
        assert history[1]["reason"] == "passed gates"
        assert "at" in history[1]

    def test_attach_run_and_verdict(self, pool, manifest):
        pool.register(manifest, manifest_path="m.yaml")
        entry = pool.attach_run("pool_test_strategy", run_id="abc123", verdict="PASS")
        assert entry["latest_run_id"] == "abc123"
        assert entry["latest_verdict"] == "PASS"

    def test_update_health_merges(self, pool, manifest):
        pool.register(manifest, manifest_path="m.yaml")
        pool.update_health("pool_test_strategy", {"rolling_sharpe": 0.7})
        pool.update_health("pool_test_strategy", {"tracking_error": 0.02})
        health = pool.get("pool_test_strategy")["health"]
        assert health == {"rolling_sharpe": 0.7, "tracking_error": 0.02}

    def test_list_entries_filters(self, pool, manifest):
        pool.register(manifest, manifest_path="m.yaml")
        other = manifest.model_copy(update={"strategy_id": "other_strategy"})
        pool.register(other, manifest_path="o.yaml")
        pool.set_state("other_strategy", "retired", reason="r")

        assert len(pool.list_entries()) == 2
        assert len(pool.list_entries(state="candidate")) == 1
        active = pool.list_entries(active_only=True)
        assert list(active["strategy_id"]) == ["pool_test_strategy"]

    def test_list_empty_pool(self, pool):
        assert pool.list_entries().empty
