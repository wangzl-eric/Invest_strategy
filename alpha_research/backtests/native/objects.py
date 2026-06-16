"""Core data objects for the native event-driven backtester.

Design lineage (see docs/guides/backtesting_engine_comparison.md):

* **vnpy** — explicit, immutable market/trade objects flowing through an event
  loop (``Bar``, ``Order``, ``Trade``) and a clean ``Position`` value object.
* **qlib** — an ``Account`` that separates *cash* from *positions* and values the
  book point-in-time, so equity, exposure, and PnL are always derivable from
  state rather than bolted on after the fact.

Everything here is plain dataclasses with no pandas/broker dependencies so the
objects stay cheap to create inside the per-bar loop and trivial to unit test.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict


class Direction(str, Enum):
    """Trade direction. ``LONG`` increases (buys), ``SHORT`` decreases (sells)."""

    LONG = "LONG"
    SHORT = "SHORT"

    @property
    def sign(self) -> int:
        return 1 if self is Direction.LONG else -1


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class Bar:
    """One OHLCV bar for a single symbol (vnpy ``BarData`` analogue)."""

    dt: datetime
    symbol: str
    close: float
    open: float = float("nan")
    high: float = float("nan")
    low: float = float("nan")
    volume: float = float("nan")

    def price(self, field_name: str = "close") -> float:
        return float(getattr(self, field_name))


@dataclass
class Order:
    """A target instruction emitted by a strategy before execution.

    ``quantity`` is *signed* in share space (positive = buy, negative = sell).
    Orders are mutable only in that the broker stamps a status/fill onto them.
    """

    symbol: str
    quantity: float
    order_type: OrderType = OrderType.MARKET
    limit_price: float = float("nan")
    created_dt: datetime | None = None
    status: OrderStatus = OrderStatus.SUBMITTED

    @property
    def direction(self) -> Direction:
        return Direction.LONG if self.quantity >= 0 else Direction.SHORT


@dataclass(frozen=True)
class Trade:
    """An executed fill: the realised economics of an order at the broker."""

    dt: datetime
    symbol: str
    quantity: float  # signed share delta actually filled
    price: float  # slippage-adjusted fill price
    commission: float = 0.0
    slippage: float = 0.0  # currency cost attributable to slippage

    @property
    def direction(self) -> Direction:
        return Direction.LONG if self.quantity >= 0 else Direction.SHORT

    @property
    def notional(self) -> float:
        return abs(self.quantity) * self.price


@dataclass
class Position:
    """Net holding in one symbol with a running average cost.

    Tracks realised PnL on partial/closing trades so the account can attribute
    performance to trading rather than only marking to market.
    """

    symbol: str
    quantity: float = 0.0
    avg_price: float = 0.0
    realized_pnl: float = 0.0

    def market_value(self, price: float) -> float:
        return self.quantity * price

    def unrealized_pnl(self, price: float) -> float:
        return (price - self.avg_price) * self.quantity

    def apply_trade(self, quantity: float, price: float) -> None:
        """Update the position for a signed share delta filled at ``price``.

        Average price is recomputed when adding in the same direction; realised
        PnL is booked when the trade reduces or flips the position.
        """
        if quantity == 0:
            return
        old_qty = self.quantity
        new_qty = old_qty + quantity

        same_direction = (old_qty >= 0) == (quantity >= 0)
        if old_qty == 0 or same_direction:
            # Opening or adding — blend the average price.
            total_cost = self.avg_price * abs(old_qty) + price * abs(quantity)
            denom = abs(old_qty) + abs(quantity)
            self.avg_price = total_cost / denom if denom else 0.0
        else:
            # Reducing or flipping — realise PnL on the closed portion.
            closed = min(abs(quantity), abs(old_qty))
            self.realized_pnl += (
                (price - self.avg_price) * closed * (1 if old_qty > 0 else -1)
            )
            if abs(quantity) > abs(old_qty):
                # Flipped through zero — the residual opens a new leg at price.
                self.avg_price = price
            # else avg_price unchanged on a pure reduction.

        self.quantity = new_qty
        if abs(self.quantity) < 1e-12:
            self.quantity = 0.0
            self.avg_price = 0.0


@dataclass
class Account:
    """Cash + open positions; the single source of truth for portfolio state.

    Equity is always ``cash + sum(market value of positions)`` — never a tracked
    scalar that can drift out of sync (qlib's account discipline).
    """

    cash: float
    positions: Dict[str, Position] = field(default_factory=dict)

    def position(self, symbol: str) -> Position:
        return self.positions.setdefault(symbol, Position(symbol))

    def equity(self, prices: Dict[str, float]) -> float:
        total = self.cash
        for sym, pos in self.positions.items():
            px = prices.get(sym)
            if px is not None and px == px:  # not NaN
                total += pos.market_value(px)
        return total

    def gross_exposure(self, prices: Dict[str, float]) -> float:
        """Sum of |position market value| — the gross leverage in currency."""
        total = 0.0
        for sym, pos in self.positions.items():
            px = prices.get(sym)
            if px is not None and px == px:
                total += abs(pos.market_value(px))
        return total

    def weights(self, prices: Dict[str, float]) -> Dict[str, float]:
        """Current portfolio weights (position value / equity) per symbol."""
        eq = self.equity(prices)
        if eq == 0:
            return {}
        out: Dict[str, float] = {}
        for sym, pos in self.positions.items():
            px = prices.get(sym)
            if px is not None and px == px:
                out[sym] = pos.market_value(px) / eq
        return out


__all__ = [
    "Direction",
    "OrderType",
    "OrderStatus",
    "Bar",
    "Order",
    "Trade",
    "Position",
    "Account",
]
