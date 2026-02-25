"""Data management API routes for the Parquet market data lake."""

import logging
import threading
from typing import List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from backend.market_data_store import market_data_store, get_job_status

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class PullRequest(BaseModel):
    source: str  # "yfinance" | "fred"
    asset_class: str
    tickers: List[str]
    start_date: str
    end_date: str


class PullResponse(BaseModel):
    job_id: str
    status: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/data/catalog")
async def get_catalog():
    """Return metadata about all stored market data."""
    return market_data_store.get_catalog()


@router.post("/data/pull")
async def pull_data(req: PullRequest):
    """Trigger a data pull and run it in a background thread."""
    from backend.market_data_store import _create_job, _finish_job

    job_id = _create_job(f"pull {req.source}/{req.asset_class}")

    def _run():
        try:
            if req.source == "yfinance":
                rows = market_data_store.pull_yf_data(
                    req.tickers, req.start_date, req.end_date, req.asset_class,
                )
            elif req.source == "fred":
                rows = market_data_store.pull_fred_data(
                    req.tickers, req.start_date, req.end_date, req.asset_class,
                )
            else:
                _finish_job(job_id, error=f"Unknown source: {req.source}")
                return
            _finish_job(job_id, rows=rows)
        except Exception as e:
            logger.error(f"Pull job {job_id} failed: {e}")
            _finish_job(job_id, error=str(e))

    threading.Thread(target=_run, daemon=True).start()
    return PullResponse(job_id=job_id, status="running")


@router.get("/data/query")
async def query_data(
    asset_class: str = Query(..., description="Asset class or FRED category"),
    tickers: Optional[str] = Query(None, description="Comma-separated tickers"),
    start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(500, ge=1, le=10000),
):
    """Query stored market data from Parquet files."""
    ticker_list = [t.strip() for t in tickers.split(",")] if tickers else None
    df = market_data_store.query(asset_class, ticker_list, start, end)
    if df.empty:
        return {"rows": [], "total": 0}
    total = len(df)
    df = df.tail(limit)
    return {"rows": df.to_dict(orient="records"), "total": total}


@router.post("/data/update-all")
async def update_all():
    """Incremental update of all tracked tickers/series."""
    job_id = market_data_store.update_all()
    return PullResponse(job_id=job_id, status="running")


@router.get("/data/pull-status/{job_id}")
async def pull_status(job_id: str):
    """Check status of a background data pull job."""
    status = get_job_status(job_id)
    if status is None:
        return {"error": "Job not found", "job_id": job_id}
    return status
