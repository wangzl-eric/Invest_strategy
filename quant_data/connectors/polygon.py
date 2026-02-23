"""Polygon.io connector (paid; skeleton).

This is a minimal implementation so you can plug in your API key and extend.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd

from quant_data.connectors.base import BarsRequest
from quant_data.spec import DatasetFrequency, DatasetId, MarketDataKind


@dataclass(frozen=True)
class PolygonConfig:
    api_key: str
    base_url: str = "https://api.polygon.io"
    venue: str = "POLYGON"
    currency: str = "USD"

    @classmethod
    def from_env(cls) -> "PolygonConfig":
        key = os.getenv("POLYGON_API_KEY", "")
        if not key:
            raise ValueError("POLYGON_API_KEY is not set")
        return cls(api_key=key)


class PolygonBarsConnector:
    provider = "polygon"

    def __init__(self, cfg: Optional[PolygonConfig] = None):
        self.cfg = cfg or PolygonConfig.from_env()

    def fetch_bars(self, req: BarsRequest) -> pd.DataFrame:
        # Polygon aggregates are fetched per symbol. This implementation uses 1 day bars.
        frames: list[pd.DataFrame] = []
        for sym in req.symbols:
            frames.append(self._fetch_symbol(sym, start=req.start, end=req.end))
        frames = [f for f in frames if not f.empty]
        if not frames:
            return pd.DataFrame()
        out = pd.concat(frames, ignore_index=True)
        out = out.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
        return out

    def _fetch_symbol(self, symbol: str, *, start: str, end: str) -> pd.DataFrame:
        # https://polygon.io/docs/stocks/get_v2_aggs_ticker__stocksticker__range__multiplier___timespan___from___to
        path = f"/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}"
        params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": self.cfg.api_key}
        url = f"{self.cfg.base_url}{path}?{urlencode(params)}"
        with urlopen(url, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))

        results = payload.get("results") or []
        if not results:
            return pd.DataFrame()

        rows = []
        for r in results:
            # t in ms since epoch UTC
            ts = pd.to_datetime(int(r["t"]), unit="ms", utc=True)
            rows.append(
                {
                    "timestamp": ts,
                    "symbol": symbol,
                    "venue": self.cfg.venue,
                    "currency": self.cfg.currency,
                    "open": float(r.get("o", 0.0)),
                    "high": float(r.get("h", 0.0)),
                    "low": float(r.get("l", 0.0)),
                    "close": float(r.get("c", 0.0)),
                    "volume": float(r.get("v", 0.0)),
                    "vwap": float(r["vw"]) if r.get("vw") is not None else pd.NA,
                }
            )
        return pd.DataFrame(rows)

    @staticmethod
    def dataset_id(*, universe: str = "us_equities") -> DatasetId:
        return DatasetId(provider="polygon", kind=MarketDataKind.BARS, universe=universe, frequency=DatasetFrequency.DAY)

