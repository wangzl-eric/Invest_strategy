"""Unified local-first market data access and refresh jobs.

This module provides one canonical interface for:
- querying locally stored research data
- optionally refreshing missing data from an upstream API source
- running refresh jobs asynchronously for API routes and scripts

It intentionally sits above ``market_data_store`` so existing Parquet storage
and catalog behavior remain stable while research and app code converge on a
single request model.
"""

from __future__ import annotations

import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Sequence

import pandas as pd

from backend.market_data_store import get_job_status as get_legacy_job_status
from backend.market_data_store import market_data_store
from backend.research.duckdb_utils import get_research_db

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DatasetSpec:
    key: str
    source: str
    storage_key: str
    view_name: str
    identifier_column: str
    default_interval: str = "1 day"
    default_sec_type: str = "STK"
    default_exchange: str = "SMART"


_DATASET_SPECS: dict[str, DatasetSpec] = {
    "equities": DatasetSpec(
        key="equities",
        source="yfinance",
        storage_key="equities",
        view_name="yf_equities",
        identifier_column="ticker",
    ),
    "fx": DatasetSpec(
        key="fx",
        source="yfinance",
        storage_key="fx",
        view_name="yf_fx",
        identifier_column="ticker",
    ),
    "commodities": DatasetSpec(
        key="commodities",
        source="yfinance",
        storage_key="commodities",
        view_name="yf_commodities",
        identifier_column="ticker",
    ),
    "rates_yf": DatasetSpec(
        key="rates_yf",
        source="yfinance",
        storage_key="rates_yf",
        view_name="yf_rates",
        identifier_column="ticker",
    ),
    "treasury_yields": DatasetSpec(
        key="treasury_yields",
        source="fred",
        storage_key="treasury_yields",
        view_name="fred_treasury",
        identifier_column="series_id",
    ),
    "macro_indicators": DatasetSpec(
        key="macro_indicators",
        source="fred",
        storage_key="macro_indicators",
        view_name="fred_macro",
        identifier_column="series_id",
    ),
    "fed_liquidity": DatasetSpec(
        key="fed_liquidity",
        source="fred",
        storage_key="fed_liquidity",
        view_name="fred_liquidity",
        identifier_column="series_id",
    ),
    "ibkr_equities": DatasetSpec(
        key="ibkr_equities",
        source="ibkr",
        storage_key="ibkr_equities",
        view_name="ibkr_equities",
        identifier_column="ticker",
        default_sec_type="STK",
        default_exchange="SMART",
    ),
    "ibkr_fx": DatasetSpec(
        key="ibkr_fx",
        source="ibkr",
        storage_key="ibkr_fx",
        view_name="ibkr_fx",
        identifier_column="ticker",
        default_sec_type="CASH",
        default_exchange="IDEALPRO",
    ),
    "ibkr_futures": DatasetSpec(
        key="ibkr_futures",
        source="ibkr",
        storage_key="ibkr_futures",
        view_name="ibkr_futures",
        identifier_column="ticker",
        default_sec_type="FUT",
        default_exchange="CME",
    ),
    "ibkr_options": DatasetSpec(
        key="ibkr_options",
        source="ibkr",
        storage_key="ibkr_options",
        view_name="ibkr_options",
        identifier_column="ticker",
        default_sec_type="OPT",
        default_exchange="SMART",
    ),
}

_SOURCE_ALIASES = {
    "yf": "yfinance",
    "yfinance": "yfinance",
    "fred": "fred",
    "ibkr": "ibkr",
}

_LEGACY_DATASET_MAP = {
    ("yfinance", "equities"): "equities",
    ("yfinance", "fx"): "fx",
    ("yfinance", "commodities"): "commodities",
    ("yfinance", "rates_yf"): "rates_yf",
    ("fred", "treasury_yields"): "treasury_yields",
    ("fred", "macro_indicators"): "macro_indicators",
    ("fred", "fed_liquidity"): "fed_liquidity",
    ("ibkr", "ibkr_equities"): "ibkr_equities",
    ("ibkr", "ibkr_fx"): "ibkr_fx",
    ("ibkr", "ibkr_futures"): "ibkr_futures",
    ("ibkr", "ibkr_options"): "ibkr_options",
    ("ibkr", "equity"): "ibkr_equities",
    ("ibkr", "equities"): "ibkr_equities",
    ("ibkr", "fx"): "ibkr_fx",
    ("ibkr", "futures"): "ibkr_futures",
    ("yf", "equity"): "equities",
    ("yfinance", "equity"): "equities",
    ("yf", "fx"): "fx",
    ("yfinance", "fx"): "fx",
    ("yf", "commodity"): "commodities",
    ("yfinance", "commodity"): "commodities",
    ("fred", "rate"): "treasury_yields",
    ("fred", "rates"): "treasury_yields",
}


@dataclass(frozen=True)
class LocalDataRequest:
    dataset: str
    identifiers: tuple[str, ...] = field(default_factory=tuple)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: Optional[int] = None
    refresh_if_missing: bool = False
    interval: Optional[str] = None
    sec_type: Optional[str] = None
    exchange: Optional[str] = None


@dataclass(frozen=True)
class RefreshRequest:
    dataset: str
    identifiers: tuple[str, ...]
    start_date: str
    end_date: str
    interval: Optional[str] = None
    sec_type: Optional[str] = None
    exchange: Optional[str] = None


def _normalize_source(value: Optional[str]) -> str:
    if not value:
        return ""
    return _SOURCE_ALIASES.get(value.lower(), value.lower())


def _sql_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _normalize_identifiers(values: Optional[Sequence[str]]) -> tuple[str, ...]:
    if not values:
        return ()
    cleaned = [str(v).strip() for v in values if str(v).strip()]
    return tuple(cleaned)


class UnifiedDataPipeline:
    """Local-first access layer for research data and refresh jobs."""

    def __init__(self):
        self._jobs: dict[str, dict[str, Any]] = {}
        self._jobs_lock = threading.Lock()

    def resolve_dataset(
        self,
        *,
        dataset: Optional[str] = None,
        source: Optional[str] = None,
        asset_class: Optional[str] = None,
    ) -> DatasetSpec:
        if dataset:
            key = dataset.lower().strip()
        else:
            normalized_source = _normalize_source(source)
            normalized_asset = (asset_class or "").lower().strip()
            key = _LEGACY_DATASET_MAP.get((normalized_source, normalized_asset), "")

        if key not in _DATASET_SPECS:
            available = ", ".join(sorted(_DATASET_SPECS))
            raise ValueError(
                f"Unknown dataset selection. dataset={dataset!r}, "
                f"source={source!r}, asset_class={asset_class!r}. "
                f"Available datasets: {available}"
            )
        return _DATASET_SPECS[key]

    def list_datasets(self) -> list[str]:
        return sorted(_DATASET_SPECS)

    def build_local_request(
        self,
        *,
        dataset: Optional[str] = None,
        source: Optional[str] = None,
        asset_class: Optional[str] = None,
        identifiers: Optional[Sequence[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None,
        refresh_if_missing: bool = False,
        interval: Optional[str] = None,
        sec_type: Optional[str] = None,
        exchange: Optional[str] = None,
    ) -> LocalDataRequest:
        spec = self.resolve_dataset(
            dataset=dataset,
            source=source,
            asset_class=asset_class,
        )
        return LocalDataRequest(
            dataset=spec.key,
            identifiers=_normalize_identifiers(identifiers),
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            refresh_if_missing=refresh_if_missing,
            interval=interval,
            sec_type=sec_type,
            exchange=exchange,
        )

    def build_refresh_request(
        self,
        *,
        dataset: Optional[str] = None,
        source: Optional[str] = None,
        asset_class: Optional[str] = None,
        identifiers: Optional[Sequence[str]] = None,
        start_date: str,
        end_date: str,
        interval: Optional[str] = None,
        sec_type: Optional[str] = None,
        exchange: Optional[str] = None,
    ) -> RefreshRequest:
        spec = self.resolve_dataset(
            dataset=dataset,
            source=source,
            asset_class=asset_class,
        )
        normalized = _normalize_identifiers(identifiers)
        if not normalized:
            raise ValueError("Refresh requests require at least one identifier")
        return RefreshRequest(
            dataset=spec.key,
            identifiers=normalized,
            start_date=start_date,
            end_date=end_date,
            interval=interval or spec.default_interval,
            sec_type=sec_type or spec.default_sec_type,
            exchange=exchange or spec.default_exchange,
        )

    def _query_duckdb(self, req: LocalDataRequest) -> pd.DataFrame:
        spec = self.resolve_dataset(dataset=req.dataset)
        query = f"SELECT * FROM {spec.view_name} WHERE 1=1"

        if req.identifiers:
            quoted = ", ".join(_sql_quote(v) for v in req.identifiers)
            query += f" AND {spec.identifier_column} IN ({quoted})"
        if req.start_date:
            query += f" AND date >= {_sql_quote(req.start_date)}"
        if req.end_date:
            query += f" AND date <= {_sql_quote(req.end_date)}"

        order_by = (
            f"{spec.identifier_column}, date" if spec.identifier_column else "date"
        )
        query += f" ORDER BY {order_by}"

        with get_research_db() as db:
            return db.execute(query)

    def _query_local_frame(self, req: LocalDataRequest) -> pd.DataFrame:
        try:
            df = self._query_duckdb(req)
        except Exception as exc:
            logger.warning(
                "DuckDB local query failed for %s, falling back to parquet query: %s",
                req.dataset,
                exc,
            )
            spec = self.resolve_dataset(dataset=req.dataset)
            df = market_data_store.query(
                spec.storage_key,
                list(req.identifiers) if req.identifiers else None,
                req.start_date,
                req.end_date,
            )

        if req.limit and len(df) > req.limit:
            df = df.tail(req.limit)
        return df

    def query_local(self, req: LocalDataRequest) -> pd.DataFrame:
        df = self._query_local_frame(req)
        if not df.empty or not req.refresh_if_missing:
            return df

        if not req.identifiers or not req.start_date or not req.end_date:
            return df

        refresh_req = RefreshRequest(
            dataset=req.dataset,
            identifiers=req.identifiers,
            start_date=req.start_date,
            end_date=req.end_date,
            interval=req.interval,
            sec_type=req.sec_type,
            exchange=req.exchange,
        )
        rows = self.refresh_from_source(refresh_req)
        logger.info(
            "Auto-refresh for %s wrote %s rows before local re-query",
            req.dataset,
            rows,
        )
        return self._query_local_frame(req)

    def refresh_from_source(self, req: RefreshRequest) -> int:
        spec = self.resolve_dataset(dataset=req.dataset)
        identifiers = list(req.identifiers)

        if spec.source == "yfinance":
            return market_data_store.pull_yf_data(
                identifiers,
                req.start_date,
                req.end_date,
                spec.storage_key,
            )

        if spec.source == "fred":
            return market_data_store.pull_fred_data(
                identifiers,
                req.start_date,
                req.end_date,
                spec.storage_key,
            )

        if spec.source == "ibkr":
            return market_data_store.pull_ibkr_data(
                tickers=identifiers,
                start_date=req.start_date,
                end_date=req.end_date,
                asset_class=spec.storage_key,
                interval=req.interval or spec.default_interval,
                sec_type=req.sec_type or spec.default_sec_type,
                exchange=req.exchange or spec.default_exchange,
            )

        raise ValueError(f"Unsupported source for dataset {req.dataset}: {spec.source}")

    def _create_job(self, req: RefreshRequest) -> str:
        spec = self.resolve_dataset(dataset=req.dataset)
        job_id = str(uuid.uuid4())[:8]
        with self._jobs_lock:
            self._jobs[job_id] = {
                "id": job_id,
                "status": "running",
                "dataset": req.dataset,
                "source": spec.source,
                "identifiers": list(req.identifiers),
                "started": datetime.utcnow().isoformat(),
                "finished": None,
                "rows_written": 0,
                "error": None,
            }
        return job_id

    def _finish_job(
        self,
        job_id: str,
        *,
        rows_written: int = 0,
        error: Optional[str] = None,
    ) -> None:
        with self._jobs_lock:
            if job_id not in self._jobs:
                return
            self._jobs[job_id]["status"] = "error" if error else "completed"
            self._jobs[job_id]["finished"] = datetime.utcnow().isoformat()
            self._jobs[job_id]["rows_written"] = rows_written
            self._jobs[job_id]["error"] = error

    def _run_refresh_job(self, job_id: str, req: RefreshRequest) -> None:
        try:
            rows = self.refresh_from_source(req)
            self._finish_job(job_id, rows_written=rows)
        except Exception as exc:
            logger.error("Refresh job %s failed: %s", job_id, exc)
            self._finish_job(job_id, error=str(exc))

    def start_refresh_job(self, req: RefreshRequest) -> str:
        job_id = self._create_job(req)
        thread = threading.Thread(
            target=self._run_refresh_job,
            args=(job_id, req),
            daemon=True,
        )
        thread.start()
        return job_id

    def get_job_status(self, job_id: str) -> Optional[dict[str, Any]]:
        with self._jobs_lock:
            status = self._jobs.get(job_id)
        if status is not None:
            return status
        return get_legacy_job_status(job_id)


data_pipeline = UnifiedDataPipeline()
