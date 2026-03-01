"""Market data API routes for cross-asset monitoring dashboard."""

import logging
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from backend.market_data_service import market_data_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/market/rates")
async def get_rates():
    """UST yields, spreads, Fed Funds rate, and breakeven inflation."""
    return market_data_service.get_rates_snapshot()


@router.get("/market/fx")
async def get_fx():
    """G10 FX spot prices and daily changes with DXY."""
    return market_data_service.get_fx_snapshot()


@router.get("/market/equities")
async def get_equities():
    """Major equity indices and VIX."""
    return market_data_service.get_equities_snapshot()


@router.get("/market/commodities")
async def get_commodities():
    """Energy and metals commodity prices."""
    return market_data_service.get_commodities_snapshot()


@router.get("/market/macro")
async def get_macro():
    """Latest FRED macro indicators (unemployment, CPI, GDP, NFCI, etc.)."""
    return market_data_service.get_macro_pulse()


@router.get("/market/what-changed")
async def get_what_changed(
    sigma: float = Query(default=1.5, ge=0.5, le=5.0, description="Z-score threshold"),
):
    """Cross-asset movers ranked by z-score vs 20-day realized vol."""
    return market_data_service.get_what_changed(sigma_threshold=sigma)


@router.get("/market/curves")
async def get_curves():
    """Yield curve, swap curve, swap spread, and forward rates for charting."""
    return market_data_service.get_curves_data()


@router.get("/market/fed-liquidity")
async def get_fed_liquidity():
    """Fed balance sheet, RRP, reserves, TGA — QE/QT monitor with 2-year history."""
    return market_data_service.get_fed_liquidity_data()


@router.get("/market/cb-meetings")
async def get_cb_meetings():
    """Central bank meeting tracker: FOMC countdown, policy rates, implied path proxy."""
    return market_data_service.get_cb_meeting_tracker()


@router.get("/market/overview")
async def get_market_overview():
    """Combined snapshot of all market panels in a single call."""
    return market_data_service.get_overview()


@router.get("/market/sparklines")
async def get_sparklines(
    days: int = Query(default=30, ge=1, le=90, description="Number of days of history"),
):
    """Batch sparkline data for all tracked yfinance instruments."""
    return market_data_service.get_batch_sparklines(days)


@router.get("/market/historical/{symbol:path}")
async def get_historical(
    symbol: str,
    days: int = Query(default=30, ge=1, le=365, description="Number of days of history"),
):
    """Historical daily close prices for sparkline charts."""
    return {"symbol": symbol, "data": market_data_service.get_historical(symbol, days)}


# ---------------------------------------------------------------------------
# Data source fallback endpoints
# ---------------------------------------------------------------------------


class DataWithFallbackRequest(BaseModel):
    """Request model for data with fallback."""
    symbol: str
    asset_class: str
    days: int = 30
    preferred_source: Optional[str] = None


@router.get("/market/data-with-fallback")
async def get_data_with_fallback(
    symbol: str = Query(..., description="Ticker symbol or FRED series ID"),
    asset_class: str = Query(..., description="Asset class (equity, fx, rates, macro, commodities)"),
    days: int = Query(default=30, ge=1, le=365, description="Number of days of history"),
    preferred_source: Optional[str] = Query(None, description="Preferred data source (yfinance, ibkr, fred, parquet)"),
):
    """Fetch data with automatic fallback through available sources.

    This endpoint tries multiple data sources in priority order:
    1. Preferred source (if specified and available)
    2. IBKR (for equities, FX, commodities)
    3. Parquet store (if data already cached)
    4. yfinance (always available as final fallback)

    Returns metadata indicating which source was used.
    """
    result = market_data_service.get_data_with_fallback(
        symbol=symbol,
        asset_class=asset_class,
        days=days
    )

    # Add request metadata
    result["requested_symbol"] = symbol
    result["requested_asset_class"] = asset_class
    result["requested_days"] = days

    return result


@router.get("/market/source-status")
async def get_source_status():
    """Get status of all available data sources.

    Returns health status and supported asset classes for each source.
    """
    return market_data_service.get_source_status()


@router.get("/market/data-source-info")
async def get_data_source_info():
    """Get information about data source priorities and capabilities."""
    from backend.data_source_manager import data_source_manager, DEFAULT_PRIORITY_ORDER, SOURCE_CAPABILITIES

    return {
        "priority_order": {
            asset_class: [s.value for s in sources]
            for asset_class, sources in DEFAULT_PRIORITY_ORDER.items()
        },
        "capabilities": {
            source.value: classes
            for source, classes in SOURCE_CAPABILITIES.items()
        },
        "source_health": data_source_manager.get_source_info()
    }
