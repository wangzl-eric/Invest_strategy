"""Binance public market data connector (research only).

Uses the public REST endpoint for klines (no auth).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd

from quant_data.connectors.base import BarsRequest
from quant_data.spec import DatasetFrequency, DatasetId, MarketDataKind


@dataclass(frozen=True)
class BinancePublicConfig:
    base_url: str = "https://api.binance.com"
    venue: str = "BINANCE"
    currency: str = "USDT"


class BinancePublicKlinesConnector:
    provider = "binance_public"

    def __init__(self, cfg: Optional[BinancePublicConfig] = None):
        self.cfg = cfg or BinancePublicConfig()

    def fetch_bars(self, req: BarsRequest) -> pd.DataFrame:
        # Binance uses symbols like BTCUSDT; req.symbols should already be formatted.
        # Klines are fetched per symbol; API limits apply (this is a simple research connector).
        frames: list[pd.DataFrame] = []
        for sym in req.symbols:
            frames.append(self._fetch_symbol_klines(sym, start=req.start, end=req.end))
        frames = [f for f in frames if not f.empty]
        if not frames:
            return pd.DataFrame()
        out = pd.concat(frames, ignore_index=True)
        out = out.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
        return out

    def _fetch_symbol_klines(self, symbol: str, *, start: str, end: str) -> pd.DataFrame:
        # interval=1d for now (extend as needed)
        start_ms = int(pd.Timestamp(start, tz="UTC").timestamp() * 1000)
        end_ms = int((pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1)).timestamp() * 1000) - 1

        params = {
            "symbol": symbol,
            "interval": "1d",
            "startTime": start_ms,
            "endTime": end_ms,
            "limit": 1000,
        }
        url = f"{self.cfg.base_url}/api/v3/klines?{urlencode(params)}"
        with urlopen(url, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))

        if not payload:
            return pd.DataFrame()

        # https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data
        rows = []
        for k in payload:
            open_time_ms = int(k[0])
            ts = datetime.fromtimestamp(open_time_ms / 1000, tz=timezone.utc)
            rows.append(
                {
                    "timestamp": ts,
                    "symbol": symbol,
                    "venue": self.cfg.venue,
                    "currency": self.cfg.currency,
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                    "vwap": pd.NA,
                }
            )
        return pd.DataFrame(rows)

    @staticmethod
    def dataset_id(*, universe: str = "crypto_core") -> DatasetId:
        return DatasetId(provider="binance_public", kind=MarketDataKind.BARS, universe=universe, frequency=DatasetFrequency.DAY)

