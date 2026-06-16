"""Integration tests for the one-call review pipeline (WP-1.4) on synthetic data."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from alpha_research.backtests.strategies.manifest import StrategyManifest
from alpha_research.pool.registry import PoolRegistry
from alpha_research.review.pipeline import run_review

UNIVERSE = ["XLK", "XLF", "XLE", "XLV"]


def _make_manifest(strategy_id="pipeline_test", **overrides):
    payload = {
        "strategy_id": strategy_id,
        "name": "Pipeline Test Strategy",
        "track": "etf_rotation",
        "universe": UNIVERSE,
        "entrypoint": "alpha_research.backtests.runners.sector_rotation:build_weights",
        "params": {
            "mom_lookback": 60,
            "mom_skip": 10,
            "rs_lookback": 30,
            "macro_window": 20,
            "tilt_scale": 0.6,
            "max_weight": 0.5,
        },
        "benchmark": "SPY",
        "n_trials": 5,
        "description": "synthetic pipeline test",
    }
    payload.update(overrides)
    return StrategyManifest.model_validate(payload)


def _price_loader_factory(n=420, seed=42):
    def loader(tickers, start, end):
        rng = np.random.default_rng(seed)
        idx = pd.bdate_range("2022-01-03", periods=n)
        return pd.DataFrame(
            {t: 100.0 * np.cumprod(1 + rng.normal(0.0004, 0.011, n)) for t in tickers},
            index=idx,
        )

    return loader


def _macro_loader(series_ids, start, end, index):
    return {
        sid: pd.Series(np.linspace(0.0, 1.0, len(index)), index=index)
        for sid in series_ids
    }


@pytest.fixture
def pool(test_db):
    return PoolRegistry(session=test_db)


@pytest.mark.unit
class TestRunReview:
    def test_end_to_end_artifacts_and_registration(self, tmp_path, pool):
        manifest = _make_manifest()
        result = run_review(
            manifest,
            output_dir=str(tmp_path),
            price_loader=_price_loader_factory(),
            macro_loader=_macro_loader,
            pool=pool,
            tearsheet=False,
        )

        assert result["verdict"] in ("PASS", "REVISE")
        assert result["qc_status"] in ("pass", "warn")

        run_dir = Path(result["artifacts"]["run_dir"])
        for artifact in (
            "config.yaml",
            "metrics.json",
            "manifest_snapshot.yaml",
            "qc_report.json",
            "stats_battery.json",
            "sensitivity.json",
            "correlations.json",
            "gates.json",
            "verdict.md",
            "review.json",
            "review.md",
            "daily_returns.parquet",
            "equity_curve.parquet",
            # Professional report (artifact 03) + its support frames, auto-rendered.
            "03_PROFESSIONAL_REPORT.md",
            "weights.parquet",
            "prices.parquet",
            "benchmarks.parquet",
        ):
            assert (run_dir / artifact).exists(), f"missing artifact: {artifact}"

        # Both reports are surfaced in the returned artifact paths.
        assert result["artifacts"]["professional_report_md"]
        assert Path(result["artifacts"]["professional_report_md"]).exists()
        # The professional report carries the rigor/methodology section.
        pro = (run_dir / "03_PROFESSIONAL_REPORT.md").read_text()
        assert "## Methodology & Backtest Rigor" in pro
        assert "## Portfolio Manager Review" in pro

        # Pool entry created as candidate with the run attached
        entry = pool.get("pipeline_test")
        assert entry["state"] == "candidate"
        assert entry["latest_run_id"] == result["run_id"]
        assert entry["latest_verdict"] == result["verdict"]

    def test_battery_contents(self, tmp_path, pool):
        result = run_review(
            _make_manifest(),
            output_dir=str(tmp_path),
            price_loader=_price_loader_factory(),
            macro_loader=_macro_loader,
            pool=pool,
            tearsheet=False,
        )
        battery = result["battery"]
        assert 0.0 <= battery["psr"] <= 1.0
        assert 0.0 <= battery["dsr"] <= 1.0
        assert battery["dsr"] <= battery["psr"] + 1e-9  # DSR deflates PSR
        assert battery["n_trials_declared"] == 5
        assert len(battery["walkforward_segments"]) == 4

        sens = json.loads(
            (Path(result["artifacts"]["run_dir"]) / "sensitivity.json").read_text()
        )
        assert [r["cost_multiplier"] for r in sens["cost"]] == [1.0, 2.0, 3.0]
        # Sharpe must be monotonically non-increasing in costs
        sharpes = [r["sharpe_ratio"] for r in sens["cost"]]
        assert sharpes[0] >= sharpes[1] >= sharpes[2]
        # Param sensitivity covers each numeric param at 4 scales
        n_numeric = 6
        assert len(sens["params"]) == n_numeric * 4

    def test_reproducible_metrics_across_runs(self, tmp_path, pool):
        kwargs = dict(
            output_dir=str(tmp_path),
            price_loader=_price_loader_factory(),
            macro_loader=_macro_loader,
            pool=pool,
            tearsheet=False,
        )
        r1 = run_review(_make_manifest(), **kwargs)
        r2 = run_review(_make_manifest(), **kwargs)
        assert r1["run_id"] != r2["run_id"]
        assert r1["metrics"]["sharpe_ratio"] == r2["metrics"]["sharpe_ratio"]
        assert r1["battery"]["psr"] == r2["battery"]["psr"]

    def test_qc_failure_blocks_without_force(self, tmp_path, pool):
        def gappy_loader(tickers, start, end):
            px = _price_loader_factory()(tickers, start, end)
            px.iloc[100:200, 0] = np.nan  # 25% of one ticker missing
            return px

        with pytest.raises(RuntimeError, match="Data QC failed"):
            run_review(
                _make_manifest(),
                output_dir=str(tmp_path),
                price_loader=gappy_loader,
                macro_loader=_macro_loader,
                pool=pool,
                tearsheet=False,
            )

        # force=True proceeds past QC
        result = run_review(
            _make_manifest(),
            output_dir=str(tmp_path),
            price_loader=gappy_loader,
            macro_loader=_macro_loader,
            pool=pool,
            tearsheet=False,
            force=True,
        )
        assert result["qc_status"] == "fail"

    def test_correlation_gate_fires_against_clone_strategy(self, tmp_path, pool):
        """A second, identical strategy must fail the correlation gate."""
        kwargs = dict(
            output_dir=str(tmp_path),
            price_loader=_price_loader_factory(),
            macro_loader=_macro_loader,
            pool=pool,
            tearsheet=False,
        )
        run_review(_make_manifest("original_strategy"), **kwargs)
        result = run_review(_make_manifest("clone_strategy"), **kwargs)

        corr_gate = result["gate_result"]["gates"]["correlation"]
        assert corr_gate["value"] == pytest.approx(1.0, abs=1e-6)
        assert not corr_gate["passed"]
        assert result["verdict"] == "REVISE"

    def test_no_register_leaves_pool_untouched(self, tmp_path, pool):
        run_review(
            _make_manifest("unregistered"),
            output_dir=str(tmp_path),
            price_loader=_price_loader_factory(),
            macro_loader=_macro_loader,
            pool=pool,
            tearsheet=False,
            register=False,
        )
        with pytest.raises(KeyError):
            pool.get("unregistered")

    def test_excessive_gross_exposure_rejected(self, tmp_path, pool):
        manifest = _make_manifest(
            "levered",
            entrypoint="tests.unit.test_review_pipeline:levered_weights",
            universe=["XLK", "XLF"],
        )
        with pytest.raises(ValueError, match="gross exposure"):
            run_review(
                manifest,
                output_dir=str(tmp_path),
                price_loader=_price_loader_factory(),
                macro_loader=_macro_loader,
                pool=pool,
                tearsheet=False,
            )


def levered_weights(prices, macro, params):
    """Deliberately violates the gross-exposure sanity bound (test helper)."""
    return pd.DataFrame(5.0, index=prices.index, columns=prices.columns)


@pytest.mark.unit
class TestDefaultLoaders:
    def test_default_price_loader_pivots(self, monkeypatch):
        from alpha_research.review import pipeline

        long_df = pd.DataFrame(
            {
                "date": list(pd.bdate_range("2020-01-01", periods=3)) * 2,
                "ticker": ["SPY"] * 3 + ["TLT"] * 3,
                "close": [100.0, 101.0, 102.0, 50.0, 49.0, 51.0],
            }
        )
        monkeypatch.setattr(
            "alpha_research.quant_data.api.get_data",
            lambda tickers, start, end: long_df.copy(),
        )
        wide = pipeline.default_price_loader(["SPY", "TLT"], "2020-01-01", "2020-02-01")
        assert list(wide.columns) == ["SPY", "TLT"]
        assert isinstance(wide.index, pd.DatetimeIndex)
        assert wide.index.is_monotonic_increasing

    def test_default_price_loader_empty(self, monkeypatch):
        from alpha_research.review import pipeline

        monkeypatch.setattr(
            "alpha_research.quant_data.api.get_data",
            lambda tickers, start, end: pd.DataFrame(),
        )
        assert pipeline.default_price_loader(["SPY"], "2020-01-01", "2020-02-01").empty

    def test_default_macro_loader_no_ids(self):
        from alpha_research.review import pipeline

        idx = pd.bdate_range("2020-01-01", periods=5)
        assert pipeline.default_macro_loader([], "2020-01-01", "2020-02-01", idx) == {}

    def test_default_macro_loader_aligns_series(self, monkeypatch):
        from alpha_research.review import pipeline

        idx = pd.bdate_range("2020-01-01", periods=10)
        raw = pd.DataFrame(
            {
                "date": pd.bdate_range("2020-01-01", periods=5),
                "series_id": "DGS10",
                "value": [1.0, 1.1, 1.2, 1.3, 1.4],
            }
        )
        monkeypatch.setattr(
            "alpha_research.quant_data.api.get_data",
            lambda series_ids, start, end, source, pit: raw.copy(),
        )
        monkeypatch.setattr(
            "alpha_research.quant_data.pit.as_of_series",
            lambda raw_df, sid, index: pd.Series(1.0, index=index),
        )
        out = pipeline.default_macro_loader(["DGS10"], "2020-01-01", "2020-02-01", idx)
        assert "DGS10" in out
        assert out["DGS10"].index.equals(idx)

    def test_default_macro_loader_empty_raw(self, monkeypatch):
        from alpha_research.review import pipeline

        idx = pd.bdate_range("2020-01-01", periods=5)
        monkeypatch.setattr(
            "alpha_research.quant_data.api.get_data",
            lambda series_ids, start, end, source, pit: pd.DataFrame(),
        )
        assert (
            pipeline.default_macro_loader(["DGS10"], "2020-01-01", "2020-02-01", idx)
            == {}
        )
