"""IBKR paper trading broker adapter implementing the Broker protocol."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from itertools import count
from typing import Optional

from execution.broker import Broker
from execution.types import Fill, OrderRequest

logger = logging.getLogger(__name__)

# Paper trading port (7497); live uses 7496
DEFAULT_PAPER_PORT = 7497


def _ib_fill_to_fill(ib_fill) -> Fill:
    """Convert ib_insync Fill to execution.types.Fill."""
    exec_obj = ib_fill.execution
    comm = 0.0
    if ib_fill.commissionReport is not None:
        comm = float(getattr(ib_fill.commissionReport, "commission", 0) or 0)
    ts = ib_fill.time if ib_fill.time else (exec_obj.time if hasattr(exec_obj, "time") else datetime.now(timezone.utc))
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return Fill(
        timestamp=ts,
        symbol=ib_fill.contract.symbol,
        side=exec_obj.side.upper() if exec_obj.side else "BUY",
        quantity=float(exec_obj.shares),
        fill_price=float(exec_obj.price),
        commission=comm,
        venue=exec_obj.exchange or "IBKR",
        exec_id=exec_obj.execId or "",
    )


class IBKRBroker(Broker):
    """Broker implementation for IBKR paper trading via ib_insync.

    Uses port 7497 by default (paper). Set port=7496 for live.
    """

    name = "ibkr_paper"

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = DEFAULT_PAPER_PORT,
        client_id: int = 1,
        timeout: float = 30.0,
    ):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.timeout = timeout
        self._ib = None
        self._order_id_gen = count(1)
        self._reported_fill_ids: set = set()

    def _ensure_connected(self) -> bool:
        """Connect to IBKR if not already connected."""
        try:
            from ib_insync import IB, MarketOrder, Stock
        except ImportError as e:
            raise ImportError("ib_insync is required for IBKRBroker. pip install ib_insync") from e

        if self._ib is not None and self._ib.isConnected():
            return True

        self._ib = IB()
        try:
            self._ib.connect(
                self.host,
                self.port,
                clientId=self.client_id,
                timeout=int(self.timeout),
            )
            logger.info(f"Connected to IBKR at {self.host}:{self.port} (paper)" if self.port == 7497 else f"Connected to IBKR at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"IBKR connection failed: {e}")
            self._ib = None
            return False

    def submit_order(self, order: OrderRequest) -> str:
        """Submit a market order to IBKR. Returns external order id (execId or orderId)."""
        if not self._ensure_connected():
            raise ConnectionError("Not connected to IBKR")

        try:
            from ib_insync import MarketOrder, Stock
        except ImportError as e:
            raise ImportError("ib_insync is required") from e

        contract = Stock(order.symbol, "SMART", order.currency or "USD")
        qty = int(order.quantity) if order.quantity == int(order.quantity) else float(order.quantity)
        ib_order = MarketOrder(order.side, qty)

        order_id = next(self._order_id_gen)
        trade = self._ib.placeOrder(order_id, contract, ib_order)
        ext_id = str(trade.order.orderId)
        logger.info(f"Submitted order {ext_id}: {order.symbol} {order.side} {qty}")
        return ext_id

    def poll_fills(self) -> list[Fill]:
        """Return new fills since last poll. Converts ib_insync fills to execution.types.Fill."""
        if self._ib is None or not self._ib.isConnected():
            return []

        fills: list[Fill] = []
        try:
            ib_fills = self._ib.fills()
            for ib_f in ib_fills:
                exec_id = ib_f.execution.execId if ib_f.execution else ""
                if exec_id and exec_id not in self._reported_fill_ids:
                    fills.append(_ib_fill_to_fill(ib_f))
                    self._reported_fill_ids.add(exec_id)
        except Exception as e:
            logger.warning(f"Error polling IBKR fills: {e}")
        return fills

    def disconnect(self) -> None:
        """Disconnect from IBKR."""
        if self._ib is not None:
            try:
                self._ib.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting from IBKR: {e}")
            self._ib = None
