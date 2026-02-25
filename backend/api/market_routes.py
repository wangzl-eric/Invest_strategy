"""Market data API routes for cross-asset monitoring dashboard."""

import logging
from typing import Optional

from fastapi import APIRouter, Query

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
