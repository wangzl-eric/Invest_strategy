"""ECB FX reference rates connector (free).

The ECB provides EUR-based daily reference rates. This is useful for research-time FX normalization.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from quant_data.connectors.base import FxRequest


@dataclass(frozen=True)
class EcbFxConfig:
    venue: str = "ECB"
    base_ccy: str = "EUR"


class EcbFxConnector:
    provider = "ecb"

    def __init__(self, cfg: Optional[EcbFxConfig] = None):
        self.cfg = cfg or EcbFxConfig()

    def fetch_fx_rates(self, req: FxRequest) -> pd.DataFrame:
        # CSV endpoint (daily rates)
        # Columns: TIME_PERIOD, OBS_VALUE, CURRENCY, CURRENCY_DENOM, ...
        url = "https://data-api.ecb.europa.eu/service/data/EXR/D..EUR.SP00.A?format=csvdata"
        df = pd.read_csv(url)
        if df.empty:
            return pd.DataFrame()

        # Normalize to timestamp + base/quote/rate
        df = df.rename(
            columns={
                "TIME_PERIOD": "timestamp",
                "CURRENCY": "quote_ccy",
                "CURRENCY_DENOM": "base_ccy",
                "OBS_VALUE": "rate",
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        start = pd.Timestamp(req.start, tz="UTC")
        end = pd.Timestamp(req.end, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        df = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)]

        df["venue"] = self.cfg.venue
        return df[["timestamp", "base_ccy", "quote_ccy", "rate", "venue"]].reset_index(drop=True)

