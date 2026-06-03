"""Slippage models for backtesting execution simulation.

Models the difference between expected execution price and actual fill price.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class SlippageModel(ABC):
    """Abstract base for slippage models."""

    @abstractmethod
    def calculate_slippage(
        self, price: float, quantity: float, direction: str, **context
    ) -> float:
        """Calculate slippage-adjusted fill price.

        Args:
            price: Market price at time of order.
            quantity: Absolute quantity to trade.
            direction: "BUY" or "SELL".
            **context: Additional context (volume, bid_ask_spread, etc.).

        Returns:
            Adjusted fill price (always worse than market for the trader).
        """
        ...


@dataclass(frozen=True)
class FixedSlippageModel(SlippageModel):
    """Fixed slippage in basis points."""

    slippage_bps: float = 5.0

    def calculate_slippage(
        self, price: float, quantity: float, direction: str, **context
    ) -> float:
        slip = price * (self.slippage_bps / 10000)
        if direction == "BUY":
            return price + slip
        return price - slip


@dataclass(frozen=True)
class VolumeWeightedSlippageModel(SlippageModel):
    """Volume-weighted slippage: larger orders get worse fills.

    slippage = base_bps + volume_factor * (quantity / adv)

    Args:
        base_bps: Minimum slippage in basis points.
        volume_factor_bps: Additional bps per unit of participation rate.
        adv: Average daily volume.
    """

    base_bps: float = 2.0
    volume_factor_bps: float = 50.0
    adv: float = 1_000_000.0

    def calculate_slippage(
        self, price: float, quantity: float, direction: str, **context
    ) -> float:
        adv = context.get("adv", self.adv)
        participation = abs(quantity) / adv if adv > 0 else 0

        total_bps = self.base_bps + self.volume_factor_bps * participation
        slip = price * (total_bps / 10000)

        if direction == "BUY":
            return price + slip
        return price - slip


@dataclass(frozen=True)
class BidAskSlippageModel(SlippageModel):
    """Bid-ask spread based slippage.

    Assumes crossing half the spread for each trade.

    Args:
        spread_bps: Typical bid-ask spread in basis points.
    """

    spread_bps: float = 10.0

    def calculate_slippage(
        self, price: float, quantity: float, direction: str, **context
    ) -> float:
        spread = context.get("spread_bps", self.spread_bps)
        half_spread = price * (spread / 10000 / 2)

        if direction == "BUY":
            return price + half_spread  # Buy at ask
        return price - half_spread  # Sell at bid
