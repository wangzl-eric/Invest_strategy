"""Simple simulation broker (paper trading without IBKR)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import count
from typing import Dict, Optional

import pandas as pd

from execution.broker import Broker
from execution.types import Fill, OrderRequest


@dataclass
class SimMarket:
    """A minimal price source for fills."""

    last_prices: Dict[str, float]

    def get_price(self, symbol: str) -> Optional[float]:
        return self.last_prices.get(symbol)


class SimBrokerImpl:
    name = "sim"

    def __init__(self, market: SimMarket, *, commission_per_order: float = 0.0, venue: str = "SIM"):
        self.market = market
        self.commission_per_order = commission_per_order
        self.venue = venue
        self._order_id = count(1)
        self._fills: list[Fill] = []

    def submit_order(self, order: OrderRequest) -> str:
        oid = f"SIM-{next(self._order_id)}"
        px = self.market.get_price(order.symbol)
        if px is None:
            raise ValueError(f"No market price for {order.symbol}")

        fill = Fill(
            timestamp=datetime.now(tz=timezone.utc),
            symbol=order.symbol,
            side=order.side,
            quantity=float(order.quantity),
            fill_price=float(px),
            commission=float(self.commission_per_order),
            venue=self.venue,
            exec_id=oid,
        )
        self._fills.append(fill)
        return oid

    def poll_fills(self) -> list[Fill]:
        fills = self._fills
        self._fills = []
        return fills

