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


# ---------------------------------------------------------------------------
# IBKR-specific endpoints
# ---------------------------------------------------------------------------

class IBKRPullRequest(BaseModel):
    """Request model for IBKR data pulls."""
    asset_class: str  # "ibkr_equities", "ibkr_fx", "ibkr_futures"
    tickers: List[str]
    start_date: str
    end_date: str
    interval: str = "1 day"  # "1 day", "1 min", "5 mins", etc.
    sec_type: str = "STK"    # "STK", "CASH", "FUT"
    exchange: str = "SMART"  # "SMART", "IDEALPRO", "CME"


@router.post("/data/ibkr/pull-historical")
async def pull_ibkr_historical(req: IBKRPullRequest):
    """Pull historical data from IBKR and store in Parquet.
    
    Requires IB Gateway or TWS to be running with API access enabled.
    """
    from backend.market_data_store import _create_job, _finish_job
    
    # Validate asset class
    valid_asset_classes = ["ibkr_equities", "ibkr_fx", "ibkr_futures", "ibkr_options"]
    if req.asset_class not in valid_asset_classes:
        return {"error": f"Invalid asset class. Must be one of: {valid_asset_classes}"}
    
    job_id = _create_job(f"ibkr pull {req.asset_class}")
    
    def _run():
        try:
            rows = market_data_store.pull_ibkr_data(
                tickers=req.tickers,
                start_date=req.start_date,
                end_date=req.end_date,
                asset_class=req.asset_class,
                interval=req.interval,
                sec_type=req.sec_type,
                exchange=req.exchange,
            )
            _finish_job(job_id, rows=rows)
            logger.info(f"IBKR pull job {job_id} completed: {rows} rows")
        except Exception as e:
            logger.error(f"IBKR pull job {job_id} failed: {e}")
            _finish_job(job_id, error=str(e))
    
    threading.Thread(target=_run, daemon=True).start()
    return PullResponse(job_id=job_id, status="running")


@router.get("/data/ibkr/subscription-status")
async def ibkr_subscription_status():
    """Check if IBKR Gateway/TWS is connected and get subscription info."""
    from backend.ibkr_client import IBKRClient
    
    client = IBKRClient()
    
    try:
        # Try to connect
        connected = await client.connect()
        
        if not connected:
            return {
                "connected": False,
                "error": "Could not connect to IBKR. Is Gateway/TWS running?",
                "instructions": [
                    "1. Make sure IB Gateway or TWS is running",
                    "2. Ensure API access is enabled in Gateway/TWS settings",
                    "3. Check that the port matches (7497 for paper, 7496 for live)"
                ]
            }
        
        # Get account summary (this also verifies the connection is working)
        try:
            summary = await client.get_account_summary()
        except Exception:
            summary = {}
        
        await client.disconnect()
        
        return {
            "connected": True,
            "account": summary.get("AccountId", "Unknown"),
            "note": "Connection successful. Market data subscriptions are handled by IBKR."
        }
        
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }


@router.get("/data/ibkr/symbol-search")
async def ibkr_symbol_search(symbol: str = Query(..., description="Symbol to search for")):
    """Search for symbols in IBKR's database."""
    from backend.ibkr_client import IBKRClient
    
    client = IBKRClient()
    
    try:
        connected = await client.connect()
        if not connected:
            return {"error": "Could not connect to IBKR"}
        
        results = await client.search_symbols(symbol)
        await client.disconnect()
        
        return {
            "symbol": symbol,
            "matches": results,
            "count": len(results)
        }
        
    except Exception as e:
        return {"error": str(e)}


@router.post("/data/ibkr/pull-options")
async def pull_ibkr_options(
    underlying: str = Query(..., description="Underlying symbol (e.g., AAPL)"),
    exchange: str = Query("SMART", description="Exchange"),
):
    """Get options chain for an underlying symbol."""
    from backend.ibkr_client import IBKRClient
    
    client = IBKRClient()
    
    try:
        connected = await client.connect()
        if not connected:
            return {"error": "Could not connect to IBKR"}
        
        chain = await client.get_options_chain(underlying, exchange)
        await client.disconnect()
        
        if not chain:
            return {
                "error": f"No options chain found for {underlying}",
                "note": "Make sure you have options market data subscription"
            }
        
        return chain
        
    except Exception as e:
        return {"error": str(e)}


@router.get("/data/ibkr/tickers")
async def ibkr_tickers(
    asset_class: str = Query(..., description="Asset class (ibkr_equities, ibkr_fx, ibkr_futures)")
):
    """Get default ticker list for an IBKR asset class."""
    from backend.market_data_store import _IBKR_ASSET_TICKERS
    
    tickers = _IBKR_ASSET_TICKERS.get(asset_class, [])
    return {
        "asset_class": asset_class,
        "tickers": tickers,
        "count": len(tickers)
    }


@router.post("/data/ibkr/quote")
async def ibkr_quote(
    symbol: str = Query(..., description="Symbol to get quote for"),
    sec_type: str = Query("STK", description="Security type (STK, CASH, FUT)"),
    exchange: str = Query("SMART", description="Exchange"),
):
    """Get real-time quote from IBKR."""
    from backend.ibkr_client import IBKRClient
    
    client = IBKRClient()
    
    try:
        connected = await client.connect()
        if not connected:
            return {"error": "Could not connect to IBKR"}
        
        quote = await client.get_quote(symbol, sec_type, exchange)
        await client.disconnect()
        
        return quote
        
    except Exception as e:
        return {"error": str(e)}
