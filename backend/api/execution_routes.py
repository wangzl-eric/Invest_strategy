"""API routes for execution orders, fills, and strategy monitor."""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models import ExecutionOrder, ExecutionFill, Position, PnLHistory
from backend.auth import get_current_user_or_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/execution", tags=["execution"])


def _order_to_dict(o) -> dict:
    return {
        "id": o.id,
        "created_at": o.created_at.isoformat() if o.created_at else None,
        "account_id": o.account_id,
        "mode": o.mode,
        "symbol": o.symbol,
        "side": o.side,
        "quantity": float(o.quantity),
        "status": o.status,
        "external_order_id": o.external_order_id,
        "error": o.error,
    }


def _fill_to_dict(f) -> dict:
    return {
        "id": f.id,
        "created_at": f.created_at.isoformat() if f.created_at else None,
        "order_id": f.order_id,
        "symbol": f.symbol,
        "side": f.side,
        "quantity": float(f.quantity),
        "fill_price": float(f.fill_price),
        "commission": float(f.commission or 0),
        "venue": f.venue,
        "exec_id": f.exec_id,
    }


@router.get("/orders")
async def get_execution_orders(
    limit: int = Query(100, ge=1, le=500),
    account_id: Optional[str] = Query(None),
    current_user: Optional = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
):
    """Get recent execution orders for the strategy monitor."""
    query = db.query(ExecutionOrder).order_by(desc(ExecutionOrder.created_at)).limit(limit)
    if account_id:
        query = query.filter(ExecutionOrder.account_id == account_id)
    orders = query.all()
    return {"orders": [_order_to_dict(o) for o in orders]}


@router.get("/fills")
async def get_execution_fills(
    limit: int = Query(100, ge=1, le=500),
    current_user: Optional = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
):
    """Get recent execution fills for the strategy monitor."""
    fills = db.query(ExecutionFill).order_by(desc(ExecutionFill.created_at)).limit(limit).all()
    return {"fills": [_fill_to_dict(f) for f in fills]}


@router.get("/strategy-monitor")
async def get_strategy_monitor_data(
    account_id: Optional[str] = Query(None),
    current_user: Optional = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
):
    """Aggregate data for the Strategy Monitor panel: positions, target weights placeholder, paper PnL, order log."""
    # Current positions (latest per symbol)
    pos_query = db.query(Position).order_by(desc(Position.timestamp))
    if account_id:
        pos_query = pos_query.filter(Position.account_id == account_id)
    positions = pos_query.limit(500).all()
    latest_positions = {}
    for p in positions:
        key = (p.account_id or "", p.symbol)
        if key not in latest_positions or p.timestamp > latest_positions[key].timestamp:
            latest_positions[key] = p

    positions_list = []
    total_mv = 0.0
    for p in latest_positions.values():
        mv = p.market_value or (float(p.quantity or 0) * float(p.market_price or 0))
        total_mv += abs(mv)
        positions_list.append({
            "symbol": p.symbol,
            "quantity": float(p.quantity or 0),
            "market_value": mv,
            "market_price": float(p.market_price or 0),
        })

    # Recent PnL (paper/live)
    pnl_query = db.query(PnLHistory).order_by(desc(PnLHistory.date)).limit(30)
    if account_id:
        pnl_query = pnl_query.filter(PnLHistory.account_id == account_id)
    pnl_rows = pnl_query.all()
    pnl_summary = {
        "daily": [{"date": r.date.isoformat()[:10] if r.date else None, "total_pnl": float(r.total_pnl or 0)} for r in pnl_rows[:7]],
        "total_recent": sum(float(r.total_pnl or 0) for r in pnl_rows),
    }

    # Recent orders
    orders = db.query(ExecutionOrder).order_by(desc(ExecutionOrder.created_at)).limit(50).all()
    orders_list = [_order_to_dict(o) for o in orders]

    # Recent fills
    fills = db.query(ExecutionFill).order_by(desc(ExecutionFill.created_at)).limit(50).all()
    fills_list = [_fill_to_dict(f) for f in fills]

    return {
        "positions": positions_list,
        "total_market_value": total_mv,
        "pnl_summary": pnl_summary,
        "orders": orders_list,
        "fills": fills_list,
    }
