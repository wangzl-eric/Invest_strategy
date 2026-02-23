"""Event types for event-driven backtesting.

This is a small skeleton to evolve into realistic futures/options/FX execution simulation
(roll rules, contract specs, partial fills, market hours).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional


EventType = Literal["MARKET", "SIGNAL", "ORDER", "FILL"]


@dataclass(frozen=True)
class Event:
    type: EventType
    timestamp: datetime


@dataclass(frozen=True)
class MarketEvent(Event):
    symbol: str
    price: float


@dataclass(frozen=True)
class SignalEvent(Event):
    symbol: str
    direction: Literal["BUY", "SELL"]
    strength: float = 1.0


@dataclass(frozen=True)
class OrderEvent(Event):
    symbol: str
    direction: Literal["BUY", "SELL"]
    quantity: float
    order_type: Literal["MKT", "LMT"] = "MKT"
    limit_price: Optional[float] = None


@dataclass(frozen=True)
class FillEvent(Event):
    symbol: str
    direction: Literal["BUY", "SELL"]
    quantity: float
    fill_price: float
    commission: float = 0.0

