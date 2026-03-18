"""Tests for backtest reporting and review helpers."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from backtests.reporting import (
    ReviewConfig,
    build_review_bundle_from_run,
    build_review_payload,
    compare_with_pypfopt,
    generate_quantstats_tearsheet,
    load_series_from_file,
    render_review_markdown,
)
from backtests.run_manager import RunManager


def make_returns() -> pd.Series:
    idx = pd.bdate_range("2024-01-01", periods=20)
    return pd.Series([0.001, -0.002, 0.003, 0.0, 0.002] * 4, index=idx)


def make_equity() -> pd.DataFrame:
    idx = pd.bdate_range("2024-01-01", periods=20)
    vals = (1 + make_returns()).cumprod() * 100_000
    return pd.DataFrame({"date": idx, "portfolio_value": vals.values})


class TestOptionalBackends:
    def test_quantstats_missing_returns_graceful_error(self, tmp_path):
        result = generate_quantstats_tearsheet(
            pd.Series(dtype=float),
            output_html=tmp_path / "report.html",
        )
        assert result["generated"] is False
        assert "empty" in result["error"]

    def test_pypfopt_missing_or_invalid_graceful_error(self):
        result = compare_with_pypfopt(
            expected_return=pd.Series(dtype=float),
            cov=pd.DataFrame(),
        )
        assert result["available"] is False

    def test_load_series_from_file_requires_dates_for_csv(self, tmp_path):
        csv_path = tmp_path / "benchmark.csv"
        csv_path.write_text("returns\n0.01\n-0.02\n0.03\n")

        with pytest.raises(ValueError, match="date-like column"):
            load_series_from_file(csv_path)


class TestReviewRendering:
    def test_render_review_markdown_includes_required_sections(self):
        payload = build_review_payload(
            run=type(
                "Run",
                (),
                {
                    "run_id": "abcd1234",
                    "strategy_name": "test_strategy",
                    "git_commit": "deadbeef",
                    "timestamp": pd.Timestamp("2024-01-31"),
                    "params": {"lookback": 20},
                    "description": "test",
                },
            )(),
            review_config=ReviewConfig(
                execution_convention="close_to_next_open",
                benchmark="SPY",
                naive_baseline="equal_weight",
                data_source="parquet",
                date_coverage="2020-01-01 to 2024-12-31",
                hypothesis="Trend persistence persists after costs",
            ),
            metrics={"sharpe_ratio": 1.2},
            daily_returns=make_returns(),
            equity_curve=make_equity(),
            gate_summary={"psr": "PASS"},
            key_review_lenses=["baseline", "stability"],
            residual_risks=["mixed-engine comparability"],
        )
        markdown = render_review_markdown(payload)
        assert "# Backtest Review: test_strategy" in markdown
        assert "## Hypothesis" in markdown
        assert "## Engine Path" in markdown
        assert "## Data and Timing" in markdown
        assert "## Baseline and Benchmark" in markdown
        assert "## Gate Summary" in markdown
        assert "## Verdict" in markdown


class TestReviewBundle:
    def test_build_review_bundle_from_run_writes_review_artifacts(self, tmp_path):
        mgr = RunManager(output_dir=str(tmp_path))
        run = mgr.save_run(
            strategy_name="momentum",
            params={"lookback": 20},
            metrics={"sharpe_ratio": 1.1, "total_return": 0.15},
            equity_curve=make_equity(),
            daily_returns=make_returns(),
            description="bundle test",
        )

        bundle = build_review_bundle_from_run(
            run_manager=mgr,
            run_id=run.run_id,
            review_config=ReviewConfig(
                strategy_archetype="optimizer_heavy",
                execution_convention="close_to_next_open",
                report_backend="native",
                optimizer_backend="both",
                verdict="REVISE",
            ),
            gate_summary={"psr": "PASS", "dsr": "PASS"},
            key_review_lenses=["optimizer dependence", "baseline"],
            optimizer_comparison={"status": "not_required"},
            residual_risks=["turnover series not captured"],
        )

        review_json = tmp_path / run.run_id / "review.json"
        review_md = tmp_path / run.run_id / "review.md"
        assert review_json.exists()
        assert review_md.exists()

        payload = json.loads(review_json.read_text())
        assert payload["run"]["strategy_name"] == "momentum"
        assert payload["artifact_status"]["daily_returns"] is True
        assert "Optimizer Comparison" in review_md.read_text()

    def test_build_review_bundle_serializes_nested_numpy_values(self, tmp_path):
        mgr = RunManager(output_dir=str(tmp_path))
        run = mgr.save_run(
            strategy_name="momentum",
            params={"lookback": 20},
            metrics={"sharpe_ratio": 1.1},
            equity_curve=make_equity(),
            daily_returns=make_returns(),
            description="nested serialization",
        )

        build_review_bundle_from_run(
            run_manager=mgr,
            run_id=run.run_id,
            review_config=ReviewConfig(report_backend="native"),
            gate_summary={"psr": np.float64(0.83), "nested": {"dsr": np.float64(0.11)}},
            optimizer_comparison={
                "available": True,
                "weights": {"SPY": np.float64(0.6), "TLT": np.float64(0.4)},
            },
        )

        payload = json.loads((tmp_path / run.run_id / "review.json").read_text())
        assert payload["gate_summary"]["psr"] == pytest.approx(0.83)
        assert payload["optimizer_comparison"]["weights"]["SPY"] == pytest.approx(0.6)
