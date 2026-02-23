"""Stooq connector (free daily OHLCV).

Stooq provides free historical daily bars for many symbols.
This connector is intended for **research/idea generation**, not execution pricing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from quant_data.connectors.base import BarsRequest
from quant_data.spec import DatasetFrequency, DatasetId, MarketDataKind, validate_columns


@dataclass(frozen=True)
class StooqConfig:
    # Stooq symbols are typically lowercase with suffixes like ".us"
    symbol_suffix: str = ".us"
    venue: str = "STOOQ"
    currency: str = "USD"


class StooqBarsConnector:
    provider = "stooq"

    def __init__(self, cfg: Optional[StooqConfig] = None):
        self.cfg = cfg or StooqConfig()

    def fetch_bars(self, req: BarsRequest) -> pd.DataFrame:
        # Stooq exports full history per symbol as CSV.
        frames: list[pd.DataFrame] = []
        for sym in req.symbols:
            stooq_sym = sym.lower()
            if self.cfg.symbol_suffix and not stooq_sym.endswith(self.cfg.symbol_suffix):
                stooq_sym = f"{stooq_sym}{self.cfg.symbol_suffix}"

            url = f"https://stooq.com/q/d/l/?s={stooq_sym}&i=d"
            df = pd.read_csv(url)
            # Columns: Date, Open, High, Low, Close, Volume
            if df.empty:
                continue
            df = df.rename(
                columns={
                    "Date": "timestamp",
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                }
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
            df["symbol"] = sym.upper()
            df["venue"] = req.venue or self.cfg.venue
            df["currency"] = req.currency or self.cfg.currency
            df["vwap"] = pd.NA

            # Filter by date range (inclusive)
            start = pd.Timestamp(req.start, tz="UTC")
            end = pd.Timestamp(req.end, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            df = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)]
            frames.append(df[["timestamp", "symbol", "venue", "currency", "open", "high", "low", "close", "volume", "vwap"]])

        if not frames:
            return pd.DataFrame()

        out = pd.concat(frames, ignore_index=True)
        out = out.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
        validate_columns(dataset="stooq bars", columns=out.columns, required=("timestamp", "symbol", "open", "high", "low", "close", "volume"))
        return out

    @staticmethod
    def dataset_id(*, universe: str = "us_equities") -> DatasetId:
        return DatasetId(provider="stooq", kind=MarketDataKind.BARS, universe=universe, frequency=DatasetFrequency.DAY)

