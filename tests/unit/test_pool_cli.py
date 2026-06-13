"""Tests for the strategy pool CLI (alpha_research.pool.__main__)."""
import pandas as pd
import pytest

import alpha_research.pool.__main__ as pool_cli
from alpha_research.pool.registry import PoolRegistry


@pytest.fixture
def patched_registry(monkeypatch, test_db):
    """Patch the CLI's PoolRegistry so every `main()` call uses the in-memory DB."""

    def _factory(*args, **kwargs):
        return PoolRegistry(session=test_db)

    monkeypatch.setattr(pool_cli, "PoolRegistry", _factory)
    return PoolRegistry(session=test_db)


def _register(pool, strategy_id="cli_strategy"):
    from alpha_research.backtests.strategies.manifest import StrategyManifest

    manifest = StrategyManifest.model_validate(
        {
            "strategy_id": strategy_id,
            "name": "CLI Test",
            "track": "etf_rotation",
            "universe": ["SPY", "TLT"],
            "entrypoint": (
                "alpha_research.backtests.runners.sector_rotation:build_weights"
            ),
        }
    )
    pool.register(manifest, manifest_path="x/manifest.yaml")
    return manifest


@pytest.mark.unit
class TestPoolCLI:
    def test_list_empty(self, patched_registry, capsys):
        rc = pool_cli.main(["list"])
        assert rc == 0
        assert "(pool is empty)" in capsys.readouterr().out

    def test_list_populated(self, patched_registry, capsys):
        _register(patched_registry)
        rc = pool_cli.main(["list"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "cli_strategy" in out
        assert "candidate" in out

    def test_list_with_state_filter(self, patched_registry, capsys):
        _register(patched_registry)
        rc = pool_cli.main(["list", "--state", "paper"])
        assert rc == 0
        # No paper strategies yet -> empty
        assert "(pool is empty)" in capsys.readouterr().out

    def test_show_outputs_json(self, patched_registry, capsys):
        _register(patched_registry)
        rc = pool_cli.main(["show", "cli_strategy"])
        assert rc == 0
        out = capsys.readouterr().out
        assert '"strategy_id": "cli_strategy"' in out
        assert '"state": "candidate"' in out

    def test_promote(self, patched_registry, capsys):
        _register(patched_registry)
        rc = pool_cli.main(
            ["promote", "cli_strategy", "--to", "paper", "--reason", "gates"]
        )
        assert rc == 0
        assert "-> paper" in capsys.readouterr().out
        assert patched_registry.get("cli_strategy")["state"] == "paper"

    def test_retire(self, patched_registry, capsys):
        _register(patched_registry)
        rc = pool_cli.main(["retire", "cli_strategy", "--reason", "deprecated"])
        assert rc == 0
        assert "-> retired" in capsys.readouterr().out
        assert patched_registry.get("cli_strategy")["state"] == "retired"

    def test_unknown_command_errors(self, patched_registry):
        with pytest.raises(SystemExit):
            pool_cli.main(["bogus"])

    def test_missing_subcommand_errors(self, patched_registry):
        with pytest.raises(SystemExit):
            pool_cli.main([])

    def test_list_uses_expected_columns(self, monkeypatch, capsys):
        """The list branch selects a fixed column subset for display."""
        captured = {}

        class _StubPool:
            def list_entries(self, state=None):
                captured["state"] = state
                return pd.DataFrame(
                    [
                        {
                            "strategy_id": "s1",
                            "track": "etf_rotation",
                            "state": "candidate",
                            "latest_run_id": "run1",
                            "latest_verdict": "PASS",
                            "registered_at": "2026-06-12T00:00:00",
                            "extra_col": "ignored",
                        }
                    ]
                )

        monkeypatch.setattr(pool_cli, "PoolRegistry", lambda *a, **k: _StubPool())
        rc = pool_cli.main(["list", "--state", "candidate"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "s1" in out
        assert "extra_col" not in out
        assert captured["state"] == "candidate"
