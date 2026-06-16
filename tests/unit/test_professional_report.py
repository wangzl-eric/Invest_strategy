"""Tests for the professional backtest report (artifact 03), 2026-06-16.

Verifies robust markdown generation with the full visualization deck (return vs.
buy-and-hold with buy/sell markers, drawdown, parameter stability, seasonality
decomposition, return distribution with skew/kurtosis, multi-index beta exposure,
rolling & vol-adjusted Sharpe), the signal math/rationale section, and the generated
PM review — plus graceful degradation when the optional richer artifacts are absent.
The existing report (02) and engine are untouched by this module.
"""
import json

import numpy as np
import pandas as pd
import pytest

from alpha_research.backtests.reporting.performance import compute_performance_metrics
from alpha_research.backtests.reporting.professional_report import (
    render_professional_report,
)


def _base_bundle(run_dir, *, n=900):
    """Write the standard run-bundle artifacts the pipeline always produces."""
    rng = np.random.default_rng(7)
    idx = pd.bdate_range("2018-01-01", periods=n)
    bench_spx = pd.Series(rng.normal(0.0003, 0.009, n), index=idx)
    bench_ndx = bench_spx * 1.1 + rng.normal(0, 0.004, n)
    r = 0.6 * bench_spx + rng.normal(0.0002, 0.006, n)  # has real beta + alpha
    equity = (1 + r).cumprod() * 100_000

    run_dir.mkdir(parents=True, exist_ok=True)
    pd.Series(r, index=idx).to_frame("returns").to_parquet(
        run_dir / "daily_returns.parquet"
    )
    pd.DataFrame({"date": equity.index, "portfolio_value": equity.values}).to_parquet(
        run_dir / "equity_curve.parquet"
    )
    (run_dir / "metrics.json").write_text(
        json.dumps(
            {
                "strategy_name": "Pro Test Strat",
                "sharpe_ratio": float(r.mean() / r.std() * np.sqrt(252)),
                "max_drawdown": -0.12,
                "annual_turnover": 1.4,
                "sharpe_vs_baseline": 0.18,
            }
        )
    )
    (run_dir / "performance.json").write_text(
        json.dumps(
            compute_performance_metrics(pd.Series(r, index=idx), benchmark=bench_spx)
        )
    )
    (run_dir / "stats_battery.json").write_text(
        json.dumps(
            {
                "psr": 0.95,
                "dsr": 0.7,
                "n_trials_effective": 4,
                "min_backtest_length_days": 500,
                "n_days": n,
                "minbtl_satisfied": True,
                "sharpe_ci_95": [0.3, 1.1],
                "walkforward_segments": [
                    {"sharpe": 1},
                    {"sharpe": -0.2},
                    {"sharpe": 0.8},
                    {"sharpe": 1.2},
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
                        "annualized_return": 0.10,
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
                "params": [
                    {
                        "param": "lookback",
                        "scale": 0.6,
                        "value": 12,
                        "sharpe_ratio": 0.7,
                    },
                    {
                        "param": "lookback",
                        "scale": 0.8,
                        "value": 16,
                        "sharpe_ratio": 0.85,
                    },
                    {
                        "param": "lookback",
                        "scale": 1.2,
                        "value": 24,
                        "sharpe_ratio": 0.88,
                    },
                    {
                        "param": "lookback",
                        "scale": 1.4,
                        "value": 28,
                        "sharpe_ratio": 0.6,
                    },
                    {
                        "param": "z_thresh",
                        "scale": 0.6,
                        "value": 0.6,
                        "sharpe_ratio": 0.4,
                    },
                    {
                        "param": "z_thresh",
                        "scale": 1.4,
                        "value": 1.4,
                        "sharpe_ratio": 0.95,
                    },
                ],
            }
        )
    )
    (run_dir / "gates.json").write_text(
        json.dumps(
            {
                "verdict": "REVISE",
                "gates": {
                    "psr": {"value": 0.95, "threshold": 0.9, "passed": True},
                    "dsr": {"value": 0.7, "threshold": 0.95, "passed": False},
                },
            }
        )
    )
    (run_dir / "engine_reconciliation.json").write_text(
        json.dumps(
            {
                "available": True,
                "reconciled": True,
                "max_daily_return_divergence": 1e-16,
                "vectorized": {"sharpe": 0.9},
                "event_driven": {"sharpe": 0.9},
            }
        )
    )
    (run_dir / "review.json").write_text(
        json.dumps(
            {
                "control": {
                    "primary_engine": "weights_contract_vectorized",
                    "validation_engines": ["event-driven (Backtrader adapter)"],
                    "data_source": "quant_data.api (local-first)",
                    "date_coverage": "2018-01-01 → 2021-06-30",
                    "execution_convention": "close_to_next_open",
                    "cost_model": "proportional 5bps",
                    "benchmark": "SPY",
                    "naive_baseline": "equal_weight",
                }
            }
        )
    )
    (run_dir / "manifest_snapshot.yaml").write_text(
        "strategy_id: pro_test\n"
        "name: Pro Test Strategy\n"
        "entrypoint: alpha_research.backtests.runners.pro:build_weights\n"
        "description: A cross-sectional momentum tilt with a volatility filter.\n"
        "benchmark: SPY\n"
        "universe: [AAA, BBB, CCC]\n"
        "params:\n"
        "  lookback: 20\n"
        "  z_thresh: 1.0\n"
    )
    return idx, r, bench_spx, bench_ndx


def _add_rich_artifacts(run_dir, idx, bench_spx, bench_ndx):
    """Optional richer artifacts that unlock buy/sell markers, buy-and-hold overlay,
    and multi-index beta."""
    rng = np.random.default_rng(11)
    tickers = ["AAA", "BBB", "CCC"]
    prices = pd.DataFrame(
        100 * (1 + rng.normal(0.0004, 0.01, (len(idx), 3))).cumprod(axis=0),
        index=idx,
        columns=tickers,
    )
    prices.reset_index(names="date").to_parquet(run_dir / "prices.parquet")

    # A weights frame that actually changes over time so markers are produced.
    w = pd.DataFrame(0.0, index=idx, columns=tickers)
    rebal = idx[::21]
    sig = rng.normal(0, 1, (len(rebal), 3))
    for i, d in enumerate(rebal):
        row = np.where(sig[i] > 0, 1.0, 0.0)
        row = row / row.sum() if row.sum() else row
        w.loc[d] = row
    w = w.replace(0.0, np.nan).ffill().fillna(0.0)
    w.reset_index(names="date").to_parquet(run_dir / "weights.parquet")

    spx_px = (1 + bench_spx).cumprod() * 4000
    ndx_px = (1 + bench_ndx).cumprod() * 14000
    pd.DataFrame(
        {"date": idx, "SP500": spx_px.values, "Nasdaq": ndx_px.values}
    ).to_parquet(run_dir / "benchmarks.parquet")


@pytest.mark.unit
def test_render_professional_report_full(tmp_path):
    run_root = tmp_path / "runs"
    run_dir = run_root / "pro123"
    idx, r, bench_spx, bench_ndx = _base_bundle(run_dir)
    _add_rich_artifacts(run_dir, idx, bench_spx, bench_ndx)

    out = tmp_path / "strategy_folder"
    info = render_professional_report(
        "pro123", run_root=run_root, out_dir=out, filename="03_PROFESSIONAL_REPORT.md"
    )

    report = (out / "03_PROFESSIONAL_REPORT.md").read_text()

    # Required sections.
    for heading in [
        "# Professional Backtest Report",
        "## Executive Summary",
        "## Signal Definition & Mathematical Rationale",
        "## Methodology & Backtest Rigor",
        "### Backtest horizon",
        "### Win probability",
        "### Data source",
        "### Backtest engine",
        "### How the backtest is carried out rigorously",
        "## Visualization Deck",
        "## Statistical Moments & Risk Definitions",
        "## Beta Exposure (multi-index)",
        "## Parameter Stability",
        "## Seasonality",
        "## Portfolio Manager Review",
    ]:
        assert heading in report, f"missing section: {heading}"

    # Methodology content is populated from the bundle.
    assert "Daily win rate" in report and "Profit factor" in report
    assert "weights_contract_vectorized" in report or "vectorized" in report
    assert "point-in-time" in report  # data look-ahead control described

    # Math is rendered with LaTeX delimiters.
    assert "$$" in report and "\\beta" in report and "\\sqrt{252}" in report
    # Multi-index beta surfaced both indices.
    assert "SP500" in report and "Nasdaq" in report
    # PM narrative produced real observations.
    assert "Risk-adjusted return" in report
    assert "Gate verdict" in report and "REVISE" in report

    # Charts rendered (matplotlib available in the dev/test env).
    if info["matplotlib"]:
        expected = {
            "return_vs_buyhold",
            "drawdown",
            "parameter_volatility",
            "seasonality",
            "distribution",
            "beta_exposures",
            "rolling_sharpe",
        }
        assert expected.issubset(set(info["charts_rendered"])), info["charts_rendered"]
        for c in info["charts_rendered"]:
            assert (out / "charts_pro" / f"{c}.png").exists()
        assert (
            "![Cumulative Return vs. Buy & Hold](charts_pro/return_vs_buyhold.png)"
            in report
        )

    # Beta exposures were computed against the supplied indices.
    assert set(info["betas"]) >= {"SP500", "Nasdaq"}
    # Parameter volatility = Sharpe dispersion per parameter.
    assert set(info["param_volatility"]) == {"lookback", "z_thresh"}


@pytest.mark.unit
def test_render_professional_report_degrades_without_optional_artifacts(tmp_path):
    """No weights/prices/benchmarks parquet — still a valid markdown file."""
    run_root = tmp_path / "runs"
    run_dir = run_root / "minimal"
    _base_bundle(run_dir, n=400)

    info = render_professional_report(
        "minimal", run_root=run_root, out_dir=tmp_path / "min_out"
    )
    report = (tmp_path / "min_out" / "03_PROFESSIONAL_REPORT.md").read_text()

    assert "# Professional Backtest Report" in report
    assert "## Portfolio Manager Review" in report
    assert "## Visualization Deck" in report
    # Falls back to the single benchmark recorded in performance.json for beta.
    assert info["betas"]  # non-empty from vs_benchmark fallback
    if info["matplotlib"]:
        # No multi-index data, so beta_exposures may still render from the fallback;
        # the core single-series charts must be present.
        assert "drawdown" in info["charts_rendered"]
        assert "rolling_sharpe" in info["charts_rendered"]
        # buy/sell + buy-and-hold overlay still draws (strategy line alone is valid).
        assert "return_vs_buyhold" in info["charts_rendered"]


@pytest.mark.unit
def test_render_professional_report_missing_bundle_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        render_professional_report("nope", run_root=tmp_path)


@pytest.mark.unit
def test_existing_report_untouched(tmp_path):
    """The professional report must not interfere with artifact 02 generation."""
    from alpha_research.backtests.reporting.report import render_backtest_report

    run_root = tmp_path / "runs"
    run_dir = run_root / "coexist"
    idx, r, bench_spx, bench_ndx = _base_bundle(run_dir)
    _add_rich_artifacts(run_dir, idx, bench_spx, bench_ndx)
    out = tmp_path / "folder"

    render_backtest_report(
        "coexist", run_root=run_root, out_dir=out, filename="02_BACKTEST_REPORT.md"
    )
    render_professional_report(
        "coexist", run_root=run_root, out_dir=out, filename="03_PROFESSIONAL_REPORT.md"
    )

    assert (out / "02_BACKTEST_REPORT.md").exists()
    assert (out / "03_PROFESSIONAL_REPORT.md").exists()
    # Distinct chart dirs — no collision.
    assert (out / "charts").exists()
    assert (out / "charts_pro").exists()
