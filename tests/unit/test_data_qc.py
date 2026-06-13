"""Tests for the data QC preflight (WP-1.3)."""
import json

import numpy as np
import pandas as pd
import pytest

from alpha_research.quant_data.qc import FAIL, PASS, WARN, run_price_qc


def _clean_prices(n_days=250, tickers=("AAA", "BBB"), seed=7):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2023-01-02", periods=n_days)
    data = {
        t: 100.0 * np.cumprod(1 + rng.normal(0.0003, 0.01, n_days)) for t in tickers
    }
    return pd.DataFrame(data, index=idx)


@pytest.mark.unit
class TestPriceQC:
    def test_clean_data_passes(self):
        prices = _clean_prices()
        report = run_price_qc(prices)
        assert not report.failed
        assert report.status in (PASS, WARN)
        assert report.n_tickers == 2

    def test_empty_frame_fails(self):
        report = run_price_qc(pd.DataFrame())
        assert report.failed

    def test_non_datetime_index_fails(self):
        df = pd.DataFrame({"AAA": [1.0, 2.0, 3.0]})
        report = run_price_qc(df)
        assert report.failed
        assert any(f.check == "index_type" for f in report.failures)

    def test_missing_bars_fail(self):
        prices = _clean_prices(250)
        # Knock out 20% of one ticker's bars
        gappy = prices.copy()
        gappy.loc[gappy.index[50:100], "AAA"] = np.nan
        report = run_price_qc(gappy)
        assert any(
            f.ticker == "AAA" and f.check == "missing_bars" and f.severity == FAIL
            for f in report.findings
        )

    def test_stale_end_coverage_fails(self):
        prices = _clean_prices(250)
        report = run_price_qc(
            prices, start=str(prices.index.min().date()), end="2026-12-31"
        )
        assert any(f.check == "coverage_end" for f in report.failures)

    def test_late_inception_only_warns(self):
        prices = _clean_prices(250)
        report = run_price_qc(
            prices, start="2020-01-01", end=str(prices.index.max().date())
        )
        assert not report.failed
        assert any(f.check == "coverage_start" for f in report.warnings)

    def test_stale_prices_warn(self):
        prices = _clean_prices(250)
        prices.loc[prices.index[100:110], "BBB"] = 123.45
        report = run_price_qc(prices)
        assert any(
            f.ticker == "BBB" and f.check == "stale_prices" and f.severity == WARN
            for f in report.findings
        )

    def test_extreme_returns_fail(self):
        prices = _clean_prices(250)
        # Simulate a bad split adjustment: several 2x jumps
        for i in (50, 90, 130, 170):
            prices.iloc[i:, 0] = prices.iloc[i:, 0] * 2.0
        report = run_price_qc(prices)
        assert any(
            f.check == "extreme_returns" and f.severity == FAIL for f in report.findings
        )

    def test_non_positive_prices_fail(self):
        prices = _clean_prices(250)
        prices.iloc[10, 1] = -5.0
        report = run_price_qc(prices)
        assert any(f.check == "non_positive" for f in report.failures)

    def test_report_serializes_and_saves(self, tmp_path):
        report = run_price_qc(_clean_prices())
        d = report.to_dict()
        assert d["status"] == report.status
        path = report.save(tmp_path / "qc.json")
        loaded = json.loads(path.read_text())
        assert loaded["n_tickers"] == 2

    def test_summary_mentions_failures(self):
        prices = _clean_prices(250)
        prices.iloc[10, 1] = -5.0
        report = run_price_qc(prices)
        assert "non_positive" in report.summary()
