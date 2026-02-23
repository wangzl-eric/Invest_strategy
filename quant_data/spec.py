"""Canonical dataset specifications for research + backtesting.

Goals:
- Make data from different vendors/venues consistent (column names, dtypes, tz).
- Encode naming + partitioning conventions for the data lake.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping, Sequence


class DatasetLayer(str, Enum):
    """Data lake layers."""

    RAW = "raw"
    CLEAN = "clean"
    FEATURES = "features"


class DatasetFrequency(str, Enum):
    """Standardized data frequencies."""

    TICK = "tick"
    SECOND = "1s"
    MINUTE = "1m"
    HOUR = "1h"
    DAY = "1d"


class MarketDataKind(str, Enum):
    """Standard market datasets you will commonly use."""

    BARS = "bars"
    TRADES = "trades"
    QUOTES = "quotes"
    FUNDAMENTALS = "fundamentals"
    CORPORATE_ACTIONS = "corporate_actions"
    FUTURES_CHAIN = "futures_chain"
    OPTIONS_CHAIN = "options_chain"
    FX_RATES = "fx_rates"
    ONCHAIN = "onchain"
    NEWS = "news"


@dataclass(frozen=True)
class DatasetId:
    """Canonical dataset identity.

    Example:
      - provider="stooq"
      - kind=MarketDataKind.BARS
      - universe="global"
      - frequency=DatasetFrequency.DAY
    """

    provider: str
    kind: MarketDataKind
    universe: str
    frequency: DatasetFrequency

    def slug(self) -> str:
        return f"{self.provider}/{self.kind.value}/{self.universe}/{self.frequency.value}"


# ---- Canonical schemas (column names) ---------------------------------------

CANONICAL_BARS_COLUMNS: Sequence[str] = (
    "timestamp",  # UTC, tz-aware when in-memory; stored as ISO or int ns
    "symbol",
    "venue",  # exchange/venue if applicable
    "currency",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "vwap",  # optional
)

CANONICAL_TRADES_COLUMNS: Sequence[str] = (
    "timestamp",  # UTC
    "symbol",
    "venue",
    "price",
    "size",
    "side",  # BUY/SELL where available
)

CANONICAL_QUOTES_COLUMNS: Sequence[str] = (
    "timestamp",  # UTC
    "symbol",
    "venue",
    "bid",
    "bid_size",
    "ask",
    "ask_size",
)


def validate_columns(
    *,
    dataset: str,
    columns: Iterable[str],
    required: Sequence[str],
) -> None:
    """Lightweight column validation for pipelines (fast, no heavy deps)."""

    colset = set(columns)
    missing = [c for c in required if c not in colset]
    if missing:
        raise ValueError(f"{dataset}: missing required columns: {missing}")


def normalize_column_map(column_map: Mapping[str, str]) -> dict[str, str]:
    """Normalize a vendor->canonical column rename mapping."""

    return {str(k).strip(): str(v).strip() for k, v in column_map.items()}

