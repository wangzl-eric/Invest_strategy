"""Persist orders/fills/risk events to the existing backend DB."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from backend.database import get_db_context
from backend.models import ExecutionFill, ExecutionOrder, RiskEvent
from execution.types import Fill, OrderRequest


def record_order(
    *,
    mode: str,
    order: OrderRequest,
    status: str,
    external_order_id: str = "",
    account_id: str = "",
    error: str = "",
) -> int:
    with get_db_context() as db:
        row = ExecutionOrder(
            account_id=account_id or None,
            mode=mode,
            symbol=order.symbol,
            sec_type=order.sec_type,
            currency=order.currency,
            exchange=order.exchange,
            side=order.side,
            quantity=order.quantity,
            order_type=order.order_type,
            limit_price=order.limit_price,
            status=status,
            external_order_id=external_order_id or None,
            error=error or "",
        )
        db.add(row)
        db.flush()
        return int(row.id)


def record_fill(*, order_id: int, fill: Fill) -> int:
    with get_db_context() as db:
        row = ExecutionFill(
            order_id=order_id,
            symbol=fill.symbol,
            side=fill.side,
            quantity=fill.quantity,
            fill_price=fill.fill_price,
            commission=fill.commission,
            venue=fill.venue,
            exec_id=fill.exec_id or None,
        )
        db.add(row)
        db.flush()
        return int(row.id)


def record_risk_event(*, severity: str, event_type: str, message: str, context: dict) -> int:
    with get_db_context() as db:
        row = RiskEvent(
            severity=severity,
            event_type=event_type,
            message=message,
            context_json=json.dumps(context or {}, sort_keys=True),
        )
        db.add(row)
        db.flush()
        return int(row.id)

