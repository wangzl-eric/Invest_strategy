"""Tests for the one-call review CLI (alpha_research.review.__main__)."""
import json

import pytest

import alpha_research.review.__main__ as review_cli


def _stub_result():
    return {
        "run_id": "abcd1234",
        "verdict": "PASS",
        "qc_status": "pass",
        "metrics": {"sharpe_ratio": 1.234},
        "artifacts": {"run_dir": "/tmp/runs/abcd1234"},
    }


@pytest.fixture
def captured_run_review(monkeypatch):
    """Replace run_review with a stub recording the kwargs it was called with."""
    calls = {}

    def _stub(manifest, **kwargs):
        calls["manifest"] = manifest
        calls.update(kwargs)
        return _stub_result()

    monkeypatch.setattr(review_cli, "run_review", _stub)
    return calls


@pytest.mark.unit
class TestReviewCLI:
    def test_run_defaults(self, captured_run_review, capsys):
        rc = review_cli.main(["run", "path/to/manifest.yaml"])
        assert rc == 0
        assert captured_run_review["manifest"] == "path/to/manifest.yaml"
        # Defaults: force off, tearsheet/register on
        assert captured_run_review["force"] is False
        assert captured_run_review["tearsheet"] is True
        assert captured_run_review["register"] is True
        assert captured_run_review["output_dir"] == "data/backtest_runs"

        printed = json.loads(capsys.readouterr().out)
        assert printed["run_id"] == "abcd1234"
        assert printed["verdict"] == "PASS"
        assert printed["qc_status"] == "pass"
        assert printed["sharpe_ratio"] == 1.234
        assert printed["artifacts"] == {"run_dir": "/tmp/runs/abcd1234"}

    def test_flags_passthrough(self, captured_run_review, capsys):
        rc = review_cli.main(
            [
                "run",
                "m.yaml",
                "--force",
                "--no-tearsheet",
                "--no-register",
                "--output-dir",
                "/custom/out",
            ]
        )
        assert rc == 0
        assert captured_run_review["force"] is True
        assert captured_run_review["tearsheet"] is False
        assert captured_run_review["register"] is False
        assert captured_run_review["output_dir"] == "/custom/out"
        capsys.readouterr()  # drain

    def test_missing_subcommand_errors(self, captured_run_review):
        with pytest.raises(SystemExit):
            review_cli.main([])

    def test_unknown_subcommand_errors(self, captured_run_review):
        with pytest.raises(SystemExit):
            review_cli.main(["frobnicate"])
