"""Core types for backtesting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Protocol

import pandas as pd


@dataclass(frozen=True)
class CostModel:
    """Transaction cost model using turnover-based approximation.

    cost_tps: cost in decimal return per unit turnover.
      Example: 10 bps roundtrip per 1.0 notional turnover -> cost_tps=0.001
    """

    cost_tps: float = 0.0

    def apply(self, gross_returns: pd.Series, *, turnover: pd.Series) -> pd.Series:
        return gross_returns - (self.cost_tps * turnover)


@dataclass(frozen=True)
class SlippageModel:
    """Slippage model (bps per unit turnover)."""

    slippage_bps: float = 0.0

    def apply(self, gross_returns: pd.Series, *, turnover: pd.Series) -> pd.Series:
        return gross_returns - ((self.slippage_bps / 10000.0) * turnover)


@dataclass(frozen=True)
class BacktestResult:
    equity: pd.Series
    returns: pd.Series
    positions: pd.Series
    turnover: pd.Series
    stats: Dict[str, float]
    metadata: Dict[str, str]


class VectorStrategy(Protocol):
    name: str

    def generate_positions(self, bars: pd.DataFrame) -> pd.Series:
        """Return target position (e.g. 0/1 or -1..1) indexed by timestamp."""


def ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if "timestamp" in df.columns:
        out = df.copy()
        out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
        return out.set_index("timestamp").sort_index()
    if isinstance(df.index, pd.DatetimeIndex):
        return df.sort_index()
    raise ValueError("bars must have a DatetimeIndex or a 'timestamp' column")

