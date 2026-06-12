"""Tests for the strategy manifest schema (WP-1.1)."""
from pathlib import Path

import pytest
from pydantic import ValidationError

from alpha_research.backtests.strategies.manifest import (
    ExecutionConvention,
    StrategyManifest,
    Track,
    load_manifest,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _valid_payload(**overrides):
    payload = {
        "strategy_id": "test_strategy",
        "name": "Test Strategy",
        "track": "etf_rotation",
        "universe": ["SPY", "TLT"],
        "entrypoint": "alpha_research.backtests.runners.sector_rotation:build_weights",
    }
    payload.update(overrides)
    return payload


@pytest.mark.unit
class TestStrategyManifest:
    def test_valid_manifest_parses_with_defaults(self):
        m = StrategyManifest.model_validate(_valid_payload())
        assert m.track is Track.ETF_ROTATION
        assert m.rebalance.frequency == "monthly"
        assert m.rebalance.execution_convention is ExecutionConvention.T_CLOSE
        assert m.promotion_rules.min_dsr == 0.95
        assert m.n_trials == 1

    def test_invalid_strategy_id_rejected(self):
        with pytest.raises(ValidationError, match="strategy_id"):
            StrategyManifest.model_validate(_valid_payload(strategy_id="Bad-Name!"))

    def test_invalid_entrypoint_rejected(self):
        with pytest.raises(ValidationError, match="entrypoint"):
            StrategyManifest.model_validate(_valid_payload(entrypoint="no_colon_here"))

    def test_empty_universe_rejected(self):
        with pytest.raises(ValidationError, match="universe"):
            StrategyManifest.model_validate(_valid_payload(universe=[]))

    def test_duplicate_universe_rejected(self):
        with pytest.raises(ValidationError, match="duplicate"):
            StrategyManifest.model_validate(_valid_payload(universe=["SPY", "SPY"]))

    def test_unknown_track_rejected(self):
        with pytest.raises(ValidationError):
            StrategyManifest.model_validate(_valid_payload(track="crypto_hft"))

    def test_bad_data_requirement_kind_rejected(self):
        with pytest.raises(ValidationError, match="kind"):
            StrategyManifest.model_validate(
                _valid_payload(data_requirements=[{"id": "CPIAUCSL", "kind": "vibes"}])
            )

    def test_n_trials_must_be_positive(self):
        with pytest.raises(ValidationError, match="n_trials"):
            StrategyManifest.model_validate(_valid_payload(n_trials=0))

    def test_yaml_round_trip(self, tmp_path):
        m = StrategyManifest.model_validate(_valid_payload(params={"lookback": 60}))
        path = m.save(tmp_path / "manifest.yaml")
        loaded = load_manifest(path)
        assert loaded == m

    def test_load_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_manifest(tmp_path / "nope.yaml")

    def test_resolve_entrypoint_returns_callable(self):
        m = StrategyManifest.model_validate(_valid_payload())
        fn = m.resolve_entrypoint()
        assert callable(fn)

    def test_resolve_entrypoint_missing_function_raises(self):
        m = StrategyManifest.model_validate(
            _valid_payload(
                entrypoint="alpha_research.backtests.runners.sector_rotation:nope"
            )
        )
        with pytest.raises(ImportError):
            m.resolve_entrypoint()

    def test_execution_convention_shift_bars(self):
        assert ExecutionConvention.T_CLOSE.shift_bars == 1
        assert ExecutionConvention.T1_OPEN.shift_bars == 2
        assert ExecutionConvention.T1_CLOSE.shift_bars == 2


@pytest.mark.unit
def test_checked_in_sector_rotation_manifest_is_valid():
    """The reference strategy's manifest must always validate."""
    path = (
        REPO_ROOT
        / "alpha_research"
        / "research"
        / "pool"
        / "sector_rotation_v1"
        / "manifest.yaml"
    )
    m = load_manifest(path)
    assert m.strategy_id == "sector_rotation_v1"
    assert "XLI" in m.universe
    assert len(m.universe) == 11
    assert callable(m.resolve_entrypoint())
