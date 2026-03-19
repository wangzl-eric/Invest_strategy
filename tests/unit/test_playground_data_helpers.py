import pandas as pd
import pytest

import playground.shared.data_helpers as helpers


def test_get_prices_uses_local_first_dataset_order(monkeypatch):
    built_datasets = []

    class FakePipeline:
        def build_local_request(self, **kwargs):
            built_datasets.append(kwargs["dataset"])
            return kwargs

        def query_local(self, req):
            if req["dataset"] == "ibkr_equities":
                return pd.DataFrame()
            return pd.DataFrame(
                {
                    "date": ["2024-01-02", "2024-01-03"],
                    "ticker": ["SPY", "SPY"],
                    "open": [100.0, 101.0],
                    "high": [101.0, 102.0],
                    "low": [99.0, 100.0],
                    "close": [100.5, 101.5],
                    "volume": [1000, 1100],
                }
            )

    monkeypatch.setattr(helpers, "data_pipeline", FakePipeline())

    df = helpers.get_prices("SPY", start="2024-01-01", end="2024-01-31")

    assert built_datasets == ["ibkr_equities", "equities"]
    assert list(df["ticker"].unique()) == ["SPY"]
    assert list(df["close"]) == [100.5, 101.5]


def test_refresh_prices_waits_for_job_completion(monkeypatch):
    built_request = {}
    status_responses = [
        {"status": "running"},
        {"status": "completed", "rows_written": 12},
    ]

    class FakePipeline:
        def build_refresh_request(self, **kwargs):
            built_request.update(kwargs)
            return kwargs

        def start_refresh_job(self, req):
            assert req["dataset"] == "equities"
            return "job-123"

        def get_job_status(self, job_id):
            assert job_id == "job-123"
            return status_responses.pop(0)

    monkeypatch.setattr(helpers, "data_pipeline", FakePipeline())
    monkeypatch.setattr(helpers.time, "sleep", lambda _: None)

    result = helpers.refresh_prices(
        ["SPY", "TLT"],
        start="2024-01-01",
        end="2024-01-31",
        dataset="equities",
    )

    assert result == {"status": "completed", "rows_written": 12}
    assert built_request["identifiers"] == ["SPY", "TLT"]
    assert built_request["start_date"] == "2024-01-01"
    assert built_request["end_date"] == "2024-01-31"


def test_load_market_data_alias_forwards_arguments(monkeypatch):
    captured = {}

    def fake_get_prices(
        tickers,
        *,
        start,
        end=None,
        source="auto",
        dataset=None,
        refresh_if_missing=False,
    ):
        captured["tickers"] = tickers
        captured["start"] = start
        captured["end"] = end
        captured["source"] = source
        captured["dataset"] = dataset
        captured["refresh_if_missing"] = refresh_if_missing
        return "sentinel"

    monkeypatch.setattr(helpers, "get_prices", fake_get_prices)

    result = helpers.load_market_data(
        "SPY",
        start="2024-01-01",
        end="2024-01-31",
        dataset="ibkr_equities",
        refresh_if_missing=True,
    )

    assert result == "sentinel"
    assert captured == {
        "tickers": "SPY",
        "start": "2024-01-01",
        "end": "2024-01-31",
        "source": "auto",
        "dataset": "ibkr_equities",
        "refresh_if_missing": True,
    }


def test_get_prices_rejects_blank_identifiers():
    with pytest.raises(
        ValueError, match="Price lookup requires at least one identifier"
    ):
        helpers.get_prices("   ", start="2024-01-01")
