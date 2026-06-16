"""Simulated broker: turns orders into fills and keeps the account honest.

Design lineage:

* **backtrader** — a ``Broker`` that owns cash, applies a commission scheme, and
  is the only component allowed to mutate the cash/position ledger. Strategies
  request; the broker disposes.
* **vnpy** — a gateway that receives orders and emits trades, applying execution
  frictions (slippage) at the boundary so the strategy never sees idealised
  fills.

The broker is deliberately decoupled from the existing cost machinery: it reuses
``alpha_research.backtests.costs`` (``CostModel`` for commission, ``SlippageModel``
for fill-price impact) rather than re-implementing fees, so the native engine and
the review pipeline charge costs the same way.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from alpha_research.backtests.costs.slippage import FixedSlippageModel, SlippageModel
from alpha_research.backtests.costs.transaction_costs import (
    CostModel,
    ProportionalCostModel,
)

from .objects import Account, Order, OrderStatus, Trade


class SimBroker:
    """A fill-at-reference-price broker with commission and slippage.

    Args:
        initial_cash: Starting cash balance.
        cost_model: Commission model (``calculate_cost(quantity, price)``).
            Defaults to a 1 bps proportional commission.
        slippage_model: Fill-price impact model
            (``calculate_slippage(price, quantity, direction)``). Defaults to
            zero slippage so the broker is exactly reconcilable with the
            vectorized engine unless the caller opts into frictions.
        allow_short: When False, sell orders are clipped so a position can never
            go below zero (long-only books).
    """

    def __init__(
        self,
        initial_cash: float = 100_000.0,
        *,
        cost_model: Optional[CostModel] = None,
        slippage_model: Optional[SlippageModel] = None,
        allow_short: bool = True,
    ) -> None:
        self.account = Account(cash=float(initial_cash))
        self.cost_model: CostModel = cost_model or ProportionalCostModel(cost_bps=0.0)
        self.slippage_model: SlippageModel = slippage_model or FixedSlippageModel(
            slippage_bps=0.0
        )
        self.allow_short = allow_short
        self.trades: List[Trade] = []
        self.total_commission = 0.0
        self.total_slippage = 0.0

    # -- execution ---------------------------------------------------------
    def execute(self, order: Order, ref_price: float, dt: datetime) -> Optional[Trade]:
        """Fill ``order`` at ``ref_price`` (plus slippage); update the account.

        Returns the resulting ``Trade`` or ``None`` when nothing traded (zero
        quantity, NaN price, or a short clipped away on a long-only book).
        """
        qty = float(order.quantity)
        if ref_price is None or ref_price != ref_price:  # NaN guard
            return None

        if not self.allow_short:
            pos = self.account.position(order.symbol)
            # Never let a sell drive the position negative.
            if qty < 0:
                qty = max(qty, -pos.quantity)
        if abs(qty) < 1e-12:
            return None

        direction = "BUY" if qty > 0 else "SELL"
        fill_price = self.slippage_model.calculate_slippage(
            price=ref_price, quantity=abs(qty), direction=direction
        )
        slippage_cost = abs(fill_price - ref_price) * abs(qty)
        commission = self.cost_model.calculate_cost(quantity=abs(qty), price=fill_price)

        # Cash: pay notional in the trade direction, then fees.
        self.account.cash -= qty * fill_price
        self.account.cash -= commission

        self.account.position(order.symbol).apply_trade(qty, fill_price)

        self.total_commission += commission
        self.total_slippage += slippage_cost
        order.status = OrderStatus.FILLED

        trade = Trade(
            dt=dt,
            symbol=order.symbol,
            quantity=qty,
            price=fill_price,
            commission=commission,
            slippage=slippage_cost,
        )
        self.trades.append(trade)
        return trade

    # -- valuation ---------------------------------------------------------
    def equity(self, prices: Dict[str, float]) -> float:
        return self.account.equity(prices)

    def weights(self, prices: Dict[str, float]) -> Dict[str, float]:
        return self.account.weights(prices)


__all__ = ["SimBroker"]
