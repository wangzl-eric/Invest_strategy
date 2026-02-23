"""Risk controls for strategy deployment.

This is intentionally conservative: it blocks trades when uncertain.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from execution.types import OrderRequest


@dataclass(frozen=True)
class RiskLimits:
    max_position_notional: float = 50_000.0  # per symbol
    max_gross_notional: float = 250_000.0
    max_daily_loss: float = 2_500.0
    kill_switch_env: str = "KILL_SWITCH"


@dataclass
class RiskState:
    # Approximate; can be replaced by DB-driven real PnL
    gross_notional: float = 0.0
    position_notional: Dict[str, float] = None
    daily_pnl: float = 0.0

    def __post_init__(self) -> None:
        if self.position_notional is None:
            self.position_notional = {}


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    reason: str = ""
    context: dict = None


def _killswitch_enabled(env_name: str) -> bool:
    v = os.getenv(env_name, "").strip().lower()
    return v in {"1", "true", "yes", "on"}


class RiskEngine:
    def __init__(self, limits: Optional[RiskLimits] = None):
        self.limits = limits or RiskLimits()

    def check_order(self, *, state: RiskState, order: OrderRequest, price: float) -> RiskDecision:
        if _killswitch_enabled(self.limits.kill_switch_env):
            return RiskDecision(allowed=False, reason="Kill switch enabled", context={"env": self.limits.kill_switch_env})

        if state.daily_pnl <= -abs(self.limits.max_daily_loss):
            return RiskDecision(
                allowed=False,
                reason="Max daily loss breached",
                context={"daily_pnl": state.daily_pnl, "max_daily_loss": self.limits.max_daily_loss},
            )

        notional = float(order.quantity) * float(price)
        sym_notional = state.position_notional.get(order.symbol, 0.0) + (notional if order.side == "BUY" else -notional)
        if abs(sym_notional) > abs(self.limits.max_position_notional):
            return RiskDecision(
                allowed=False,
                reason="Max position notional exceeded",
                context={"symbol": order.symbol, "symbol_notional": sym_notional, "limit": self.limits.max_position_notional},
            )

        gross_after = state.gross_notional + abs(notional)
        if gross_after > abs(self.limits.max_gross_notional):
            return RiskDecision(
                allowed=False,
                reason="Max gross notional exceeded",
                context={"gross_after": gross_after, "limit": self.limits.max_gross_notional},
            )

        return RiskDecision(allowed=True, context={"notional": notional, "symbol_notional_after": sym_notional, "gross_after": gross_after})

