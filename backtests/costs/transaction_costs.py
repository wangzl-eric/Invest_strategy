"""Transaction cost models.

Models:
- FixedCostModel: Flat fee per trade
- ProportionalCostModel: Percentage of trade value
- MarketImpactModel: Simplified Almgren-Chriss square-root impact
- CompositeCostModel: Combine multiple models
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


class CostModel(ABC):
    """Abstract base for transaction cost models."""

    @abstractmethod
    def calculate_cost(self, quantity: float, price: float, **context) -> float:
        """Calculate transaction cost.

        Args:
            quantity: Number of shares/units traded (absolute value).
            price: Execution price per unit.
            **context: Additional context (e.g. volume, volatility).

        Returns:
            Total cost in currency units (always >= 0).
        """
        ...


@dataclass(frozen=True)
class FixedCostModel(CostModel):
    """Fixed cost per trade (e.g. $1.00 per trade)."""

    cost_per_trade: float = 1.0

    def calculate_cost(self, quantity: float, price: float, **context) -> float:
        if quantity == 0:
            return 0.0
        return self.cost_per_trade


@dataclass(frozen=True)
class ProportionalCostModel(CostModel):
    """Proportional cost as fraction of trade value.

    Args:
        cost_bps: Cost in basis points (10 bps = 0.1%).
    """

    cost_bps: float = 10.0

    def calculate_cost(self, quantity: float, price: float, **context) -> float:
        trade_value = abs(quantity) * price
        return trade_value * (self.cost_bps / 10000)


@dataclass(frozen=True)
class MarketImpactModel(CostModel):
    """Simplified Almgren-Chriss square-root market impact model.

    Cost = sigma * sqrt(Q / ADV) * price * Q

    where:
    - sigma: daily volatility of the asset
    - Q: quantity traded
    - ADV: average daily volume

    This captures the empirical observation that impact scales with
    the square root of participation rate.

    Args:
        volatility: Annualized volatility (will be converted to daily).
        adv: Average daily volume in shares.
        participation_rate: Max fraction of ADV (for scaling, default 0.1).
    """

    volatility: float = 0.20
    adv: float = 1_000_000.0
    participation_rate: float = 0.10

    def calculate_cost(self, quantity: float, price: float, **context) -> float:
        if quantity == 0 or self.adv == 0:
            return 0.0

        # Override with context if provided
        vol = context.get("volatility", self.volatility)
        adv = context.get("adv", self.adv)

        daily_vol = vol / (252**0.5)
        participation = abs(quantity) / adv

        # Square-root impact
        impact_bps = daily_vol * (participation**0.5) * 10000
        trade_value = abs(quantity) * price

        return trade_value * (impact_bps / 10000)


@dataclass(frozen=True)
class CompositeCostModel(CostModel):
    """Combine multiple cost models (costs are additive)."""

    models: tuple  # Tuple[CostModel, ...] for immutability

    def calculate_cost(self, quantity: float, price: float, **context) -> float:
        return sum(m.calculate_cost(quantity, price, **context) for m in self.models)


def default_equity_cost_model() -> CompositeCostModel:
    """Reasonable default cost model for US equities.

    - $0.005/share commission (IB-like)
    - 5bps proportional spread cost
    - Square-root market impact
    """
    return CompositeCostModel(
        models=(
            FixedCostModel(cost_per_trade=1.0),
            ProportionalCostModel(cost_bps=5.0),
        )
    )
