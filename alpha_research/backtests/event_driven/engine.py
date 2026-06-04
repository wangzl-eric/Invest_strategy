"""Minimal event-driven backtesting engine.

This is not a full-fledged simulator yet; it provides a stable interface
you can extend with realistic execution models.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Iterable, Optional

import pandas as pd

from backtests.event_driven.events import (
    Event,
    FillEvent,
    MarketEvent,
    OrderEvent,
    SignalEvent,
)


@dataclass
class PortfolioState:
    cash: float = 1_000_000.0
    positions: Dict[str, float] = None

    def __post_init__(self) -> None:
        if self.positions is None:
            self.positions = {}


class EventDrivenBacktester:
    """Single-threaded queue-based engine."""

    def __init__(
        self,
        *,
        initial_cash: float = 1_000_000.0,
        commission_rate: float = 0.001,
        slippage_bps: float = 5.0,
    ):
        self.state = PortfolioState(cash=initial_cash)
        self.events: Deque[Event] = deque()
        self.fills: list[FillEvent] = []
        self.commission_rate = commission_rate
        self.slippage_bps = slippage_bps

    def seed_market_events(self, market_events: Iterable[MarketEvent]) -> None:
        for e in market_events:
            self.events.append(e)

    def on_market(self, event: MarketEvent) -> Optional[SignalEvent]:
        # Placeholder: user-defined strategies should override/compose this.
        return None

    def on_signal(self, event: SignalEvent) -> Optional[OrderEvent]:
        # Placeholder: convert signal to order (position sizing rules live here).
        return None

    def execute_order(self, order: OrderEvent, market_price: float) -> FillEvent:
        # Apply slippage: adverse price movement proportional to slippage_bps
        slippage_mult = self.slippage_bps / 10000
        if order.direction == "BUY":
            fill_price = market_price * (1 + slippage_mult)
        else:
            fill_price = market_price * (1 - slippage_mult)

        # Calculate commission
        commission = abs(order.quantity * fill_price * self.commission_rate)

        return FillEvent(
            type="FILL",
            timestamp=order.timestamp,
            symbol=order.symbol,
            direction=order.direction,
            quantity=order.quantity,
            fill_price=fill_price,
            commission=commission,
        )

    def apply_fill(self, fill: FillEvent) -> None:
        sign = 1.0 if fill.direction == "BUY" else -1.0
        qty = sign * fill.quantity
        self.state.positions[fill.symbol] = (
            self.state.positions.get(fill.symbol, 0.0) + qty
        )
        self.state.cash -= qty * fill.fill_price + fill.commission
        self.fills.append(fill)

    def run(self) -> pd.DataFrame:
        """Run until queue empty. Returns fills as a DataFrame."""

        last_prices: Dict[str, float] = {}

        while self.events:
            e = self.events.popleft()
            if isinstance(e, MarketEvent):
                last_prices[e.symbol] = e.price
                sig = self.on_market(e)
                if sig:
                    self.events.append(sig)
            elif isinstance(e, SignalEvent):
                order = self.on_signal(e)
                if order:
                    self.events.append(order)
            elif isinstance(e, OrderEvent):
                px = last_prices.get(e.symbol)
                if px is None:
                    continue
                fill = self.execute_order(e, market_price=px)
                self.apply_fill(fill)

        if not self.fills:
            return pd.DataFrame()
        return pd.DataFrame([f.__dict__ for f in self.fills])
