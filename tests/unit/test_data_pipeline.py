import time
from contextlib import contextmanager

import pandas as pd

from backend.data_pipeline import LocalDataRequest, UnifiedDataPipeline


def test_resolve_dataset_from_legacy_selector():
    pipeline = UnifiedDataPipeline()

    spec = pipeline.resolve_dataset(source="ibkr", asset_class="fx")

    assert spec.key == "ibkr_fx"
    assert spec.view_name == "ibkr_fx"
    assert spec.identifier_column == "ticker"


def test_query_local_builds_duckdb_query(monkeypatch):
    pipeline = UnifiedDataPipeline()
    seen = {}

    class FakeDB:
        def execute(self, query):
            seen["query"] = query
            return pd.DataFrame({"ticker": ["AAPL"], "date": ["2024-01-02"]})

    @contextmanager
    def fake_research_db():
        yield FakeDB()

    monkeypatch.setattr("backend.data_pipeline.get_research_db", fake_research_db)

    req = LocalDataRequest(
        dataset="ibkr_equities",
        identifiers=("AAPL", "MSFT"),
        start_date="2024-01-01",
        end_date="2024-01-31",
    )
    df = pipeline.query_local(req)

    assert not df.empty
    assert "FROM ibkr_equities" in seen["query"]
    assert "ticker IN ('AAPL', 'MSFT')" in seen["query"]
    assert "date >= '2024-01-01'" in seen["query"]
    assert "date <= '2024-01-31'" in seen["query"]


def test_query_local_refreshes_when_missing(monkeypatch):
    pipeline = UnifiedDataPipeline()
    calls = {"count": 0}

    def fake_query(req):
        calls["count"] += 1
        if calls["count"] == 1:
            return pd.DataFrame()
        return pd.DataFrame({"ticker": ["AAPL"], "date": ["2024-01-02"]})

    refresh_calls = {}

    def fake_refresh(req):
        refresh_calls["dataset"] = req.dataset
        refresh_calls["identifiers"] = req.identifiers
        return 7

    monkeypatch.setattr(pipeline, "_query_local_frame", fake_query)
    monkeypatch.setattr(pipeline, "refresh_from_source", fake_refresh)

    req = LocalDataRequest(
        dataset="ibkr_equities",
        identifiers=("AAPL",),
        start_date="2024-01-01",
        end_date="2024-01-31",
        refresh_if_missing=True,
    )

    df = pipeline.query_local(req)

    assert not df.empty
    assert refresh_calls["dataset"] == "ibkr_equities"
    assert refresh_calls["identifiers"] == ("AAPL",)
    assert calls["count"] == 2


def test_start_refresh_job_tracks_completion(monkeypatch):
    pipeline = UnifiedDataPipeline()

    def fake_refresh(req):
        return 12

    monkeypatch.setattr(pipeline, "refresh_from_source", fake_refresh)

    req = pipeline.build_refresh_request(
        dataset="equities",
        identifiers=["AAPL"],
        start_date="2024-01-01",
        end_date="2024-01-31",
    )
    job_id = pipeline.start_refresh_job(req)

    status = None
    for _ in range(100):
        status = pipeline.get_job_status(job_id)
        if status and status["status"] != "running":
            break
        time.sleep(0.01)

    assert status is not None
    assert status["status"] == "completed"
    assert status["rows_written"] == 12
