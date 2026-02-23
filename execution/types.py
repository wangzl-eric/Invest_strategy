"""Shared execution types (orders, fills)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional


Side = Literal["BUY", "SELL"]
OrderType = Literal["MKT", "LMT"]


@dataclass(frozen=True)
class OrderRequest:
    symbol: str
    side: Side
    quantity: float
    order_type: OrderType = "MKT"
    limit_price: Optional[float] = None
    sec_type: str = "STK"
    currency: str = "USD"
    exchange: str = ""


@dataclass(frozen=True)
class Fill:
    timestamp: datetime
    symbol: str
    side: Side
    quantity: float
    fill_price: float
    commission: float = 0.0
    venue: str = ""
    exec_id: str = ""

