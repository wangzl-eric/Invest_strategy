"""Tests for the auto-generated backtest report (artifact 02), 2026-06-14."""
import json

import numpy as np
import pandas as pd
import pytest

from alpha_research.backtests.reporting.performance import compute_performance_metrics
from alpha_research.backtests.reporting.report import render_backtest_report


def _make_bundle(run_dir):
    rng = np.random.default_rng(0)
    idx = pd.bdate_range("2018-01-01", periods=800)
    r = pd.Series(rng.normal(0.0004, 0.01, len(idx)), index=idx)
    equity = (1 + r).cumprod() * 100_000

    run_dir.mkdir(parents=True, exist_ok=True)
    r.to_frame("returns").to_parquet(run_dir / "daily_returns.parquet")
    pd.DataFrame({"date": equity.index, "portfolio_value": equity.values}).to_parquet(
        run_dir / "equity_curve.parquet"
    )
    (run_dir / "metrics.json").write_text(
        json.dumps(
            {
                "strategy_name": "Test Strat",
                "sharpe_ratio": float(r.mean() / r.std() * np.sqrt(252)),
                "max_drawdown": -0.1,
                "annual_turnover": 1.2,
                "sharpe_vs_baseline": 0.1,
            }
        )
    )
    (run_dir / "performance.json").write_text(
        json.dumps(
            compute_performance_metrics(
                r, benchmark=r * 0.7 + rng.normal(0, 0.005, len(idx))
            )
        )
    )
    (run_dir / "stats_battery.json").write_text(
        json.dumps(
            {
                "psr": 0.97,
                "dsr": 0.8,
                "n_trials_effective": 5,
                "min_backtest_length_days": 500,
                "n_days": 800,
                "minbtl_satisfied": True,
                "sharpe_ci_95": [0.2, 1.0],
                "walkforward_segments": [
                    {"sharpe": 1},
                    {"sharpe": -1},
                    {"sharpe": 1},
                    {"sharpe": 1},
                ],
                "walkforward_positive_segments": 3,
            }
        )
    )
    (run_dir / "sensitivity.json").write_text(
        json.dumps(
            {
                "cost": [
                    {
                        "cost_multiplier": 1.0,
                        "cost_bps": 5,
                        "sharpe_ratio": 0.9,
                        "annualized_return": 0.1,
                    },
                    {
                        "cost_multiplier": 2.0,
                        "cost_bps": 10,
                        "sharpe_ratio": 0.6,
                        "annualized_return": 0.07,
                    },
                    {
                        "cost_multiplier": 3.0,
                        "cost_bps": 15,
                        "sharpe_ratio": 0.3,
                        "annualized_return": 0.04,
                    },
                ],
                "params": [],
            }
        )
    )
    (run_dir / "gates.json").write_text(
        json.dumps(
            {
                "verdict": "PASS",
                "gates": {
                    "psr": {"value": 0.97, "threshold": 0.9, "passed": True},
                    "dsr": {"value": 0.8, "threshold": 0.95, "passed": False},
                },
            }
        )
    )
    (run_dir / "engine_reconciliation.json").write_text(
        json.dumps(
            {
                "available": True,
                "reconciled": True,
                "max_daily_return_divergence": 1e-17,
                "vectorized": {"sharpe": 0.9},
                "event_driven": {"sharpe": 0.9},
            }
        )
    )


@pytest.mark.unit
def test_render_backtest_report(tmp_path):
    run_root = tmp_path / "runs"
    _make_bundle(run_root / "abc123")
    out = tmp_path / "strategy_folder"
    info = render_backtest_report(
        "abc123", run_root=run_root, out_dir=out, filename="02_BACKTEST_REPORT.md"
    )

    report = (out / "02_BACKTEST_REPORT.md").read_text()
    assert "# Backtest Report" in report
    assert "## Headline" in report
    assert "## Promotion gates" in report
    assert "## Statistical significance" in report
    assert "Engine reconciliation" in report
    assert "✅" in report  # at least one gate / reconciliation tick
    # benchmark + risk sections present
    assert "Vs benchmark" in report
    assert "Risk detail" in report

    # charts rendered (matplotlib is available in the dev/test env)
    if info["matplotlib"]:
        assert info["charts_rendered"], "expected charts to render"
        for c in info["charts_rendered"]:
            assert (out / "charts" / f"{c}.png").exists()
        assert "![Equity & drawdown](charts/equity_drawdown.png)" in report


@pytest.mark.unit
def test_render_missing_bundle_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        render_backtest_report("nope", run_root=tmp_path)
