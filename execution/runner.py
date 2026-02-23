"""Paper/live runner loop with risk controls.

This runner is intentionally simple:
- read target orders (or target weights) from a file or strategy
- run risk checks
- submit via broker
- record to DB
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Optional

from execution.audit import record_fill, record_order, record_risk_event
from execution.broker import Broker
from execution.risk import RiskEngine, RiskLimits, RiskState
from execution.types import Fill, OrderRequest


PriceGetter = Callable[[str], float]


@dataclass
class RunnerConfig:
    mode: str = "paper"  # paper/live/sim
    account_id: str = ""


class ExecutionRunner:
    def __init__(self, *, broker: Broker, price_getter: PriceGetter, risk_engine: Optional[RiskEngine] = None, cfg: Optional[RunnerConfig] = None):
        self.broker = broker
        self.price_getter = price_getter
        self.risk_engine = risk_engine or RiskEngine(RiskLimits())
        self.cfg = cfg or RunnerConfig()
        self.state = RiskState()

    def submit_orders(self, orders: Iterable[OrderRequest]) -> list[int]:
        order_row_ids: list[int] = []
        for o in orders:
            px = float(self.price_getter(o.symbol))
            decision = self.risk_engine.check_order(state=self.state, order=o, price=px)
            if not decision.allowed:
                record_risk_event(
                    severity="ERROR",
                    event_type="ORDER_BLOCKED",
                    message=decision.reason,
                    context={"symbol": o.symbol, "side": o.side, "qty": o.quantity, "price": px, **(decision.context or {})},
                )
                record_order(mode=self.cfg.mode, account_id=self.cfg.account_id, order=o, status="rejected", error=decision.reason)
                continue

            ext_id = ""
            order_id = record_order(mode=self.cfg.mode, account_id=self.cfg.account_id, order=o, status="submitted")
            try:
                ext_id = self.broker.submit_order(o)
            except Exception as e:
                record_risk_event(
                    severity="ERROR",
                    event_type="BROKER_ERROR",
                    message=str(e),
                    context={"symbol": o.symbol, "side": o.side, "qty": o.quantity},
                )
                record_order(mode=self.cfg.mode, account_id=self.cfg.account_id, order=o, status="rejected", error=str(e))
                continue

            # Update internal risk state (approximate, since fills may differ)
            notional = float(o.quantity) * px
            self.state.gross_notional += abs(notional)
            self.state.position_notional[o.symbol] = self.state.position_notional.get(o.symbol, 0.0) + (notional if o.side == "BUY" else -notional)

            order_row_ids.append(order_id)
        return order_row_ids

    def poll_and_record_fills(self, *, order_id_map: Optional[Dict[str, int]] = None) -> list[int]:
        """Poll broker fills and write them to DB. Optionally map exec_id->order_id."""
        fill_row_ids: list[int] = []
        fills: list[Fill] = self.broker.poll_fills()
        for f in fills:
            oid = (order_id_map or {}).get(f.exec_id, 0)
            if oid == 0:
                # No linkage available; still record fill with order_id NULL-like (0)
                oid = None  # type: ignore[assignment]
            fill_row_ids.append(record_fill(order_id=oid, fill=f))  # type: ignore[arg-type]
        return fill_row_ids

