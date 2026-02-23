#!/usr/bin/env python3
"""Ingest daily crypto bars from Binance public API into the Parquet data lake.

Example:
  PYTHONPATH="$(pwd)" python scripts/ingest_binance_bars.py --symbols BTCUSDT,ETHUSDT --start 2018-01-01 --end 2026-01-10
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from quant_data.connectors.base import BarsRequest
from quant_data.connectors.binance_public import BinancePublicKlinesConnector
from quant_data.pipelines.ingest_bars import ingest_bars_to_lake
from quant_data.spec import DatasetLayer


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--symbols", required=True, help="Comma-separated symbols (e.g. BTCUSDT,ETHUSDT)")
    p.add_argument("--start", required=True, help="YYYY-MM-DD")
    p.add_argument("--end", required=True, help="YYYY-MM-DD")
    p.add_argument("--universe", default="crypto_core")
    args = p.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    connector = BinancePublicKlinesConnector()
    dataset_id = connector.dataset_id(universe=args.universe)
    req = BarsRequest(symbols=symbols, start=args.start, end=args.end, venue="BINANCE", currency="USDT")

    res = ingest_bars_to_lake(connector=connector, dataset_id=dataset_id, req=req, layer=DatasetLayer.CLEAN)
    print(f"Wrote {res.files_written} parquet partitions for version={res.dataset_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

