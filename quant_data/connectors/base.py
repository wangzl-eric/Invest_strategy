"""Connector interfaces for retrieving external data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd


@dataclass(frozen=True)
class BarsRequest:
    symbols: list[str]
    start: str  # YYYY-MM-DD
    end: str  # YYYY-MM-DD (inclusive)
    currency: str = "USD"
    venue: str = ""


class BarsConnector(Protocol):
    provider: str

    def fetch_bars(self, req: BarsRequest) -> pd.DataFrame:
        """Return canonical bars with at least:
        timestamp, symbol, venue, currency, open, high, low, close, volume
        """


@dataclass(frozen=True)
class FxRequest:
    start: str
    end: str


class FxConnector(Protocol):
    provider: str

    def fetch_fx_rates(self, req: FxRequest) -> pd.DataFrame:
        """Return canonical FX rates table with at least:
        timestamp, base_ccy, quote_ccy, rate
        """

