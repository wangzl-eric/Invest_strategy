#!/usr/bin/env python3
"""Build minimal QuantConnect Lean equity daily dataset from a free source (Stooq).

This script creates the minimum files Lean expects for backtesting a US equity:
- daily trade bars zip:   Data/equity/usa/daily/{symbol}.zip (contains {symbol}.csv)
- map file:              Data/equity/usa/map_files/{symbol}.csv
- factor file:           Data/equity/usa/factor_files/{symbol}.csv

Notes on format:
- Daily bars are stored as integers scaled by 10000 (QC convention).
- Each line is: "yyyyMMdd 00:00,open,high,low,close,volume"
- Factor file lines are: "yyyyMMdd,priceFactor,splitFactor,referencePrice"
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from quant_data.connectors.base import BarsRequest
from quant_data.connectors.stooq import StooqBarsConnector


def _scale_price_to_qc_int(x: float) -> int:
    # QC tradebar convention for equities: price * 10000
    return int(round(float(x) * 10000))


def build_equity_daily(
    *,
    out_data_root: Path,
    symbol: str,
    start: str,
    end: str,
    market: str = "usa",
    primary_exchange: str = "ARCA",
) -> None:
    symbol = symbol.upper()
    connector = StooqBarsConnector()
    df = connector.fetch_bars(BarsRequest(symbols=[symbol], start=start, end=end, venue="STOOQ", currency="USD"))
    if df.empty:
        raise SystemExit(f"No data returned for {symbol} {start}..{end}")

    df = df.sort_values("timestamp")
    df["date"] = pd.to_datetime(df["timestamp"], utc=True).dt.strftime("%Y%m%d")

    # Build QC daily tradebar rows
    #
    # Important: Lean expects daily trade bars to have a time component in the
    # "yyyyMMdd HH:mm" format. Using the market close time (16:00) avoids
    # edge cases where midnight timestamps can be treated as outside market hours.
    rows = []
    for _, r in df.iterrows():
        rows.append(
            ",".join(
                [
                    f"{r['date']} 16:00",
                    str(_scale_price_to_qc_int(r["open"])),
                    str(_scale_price_to_qc_int(r["high"])),
                    str(_scale_price_to_qc_int(r["low"])),
                    str(_scale_price_to_qc_int(r["close"])),
                    str(int(float(r["volume"]) if pd.notna(r["volume"]) else 0)),
                ]
            )
        )

    # Paths
    daily_dir = out_data_root / "equity" / market / "daily"
    map_dir = out_data_root / "equity" / market / "map_files"
    factor_dir = out_data_root / "equity" / market / "factor_files"
    daily_dir.mkdir(parents=True, exist_ok=True)
    map_dir.mkdir(parents=True, exist_ok=True)
    factor_dir.mkdir(parents=True, exist_ok=True)

    sym_lower = symbol.lower()
    zip_path = daily_dir / f"{sym_lower}.zip"
    entry_name = f"{sym_lower}.csv"

    # Write zip containing csv entry
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(entry_name, "\n".join(rows) + "\n")

    # Minimal map file (no remaps): start far in the past
    map_path = map_dir / f"{sym_lower}.csv"
    map_path.write_text(f"19900101,{symbol},{primary_exchange}\n", encoding="utf-8")

    # Factor file: one row per day with no adjustments (1,1,referenceClose)
    factor_path = factor_dir / f"{sym_lower}.csv"
    factor_rows = []
    for _, r in df.iterrows():
        d = pd.to_datetime(r["timestamp"], utc=True).strftime("%Y%m%d")
        factor_rows.append(f"{d},1,1,{float(r['close']):.4f}")
    factor_path.write_text("\n".join(factor_rows) + "\n", encoding="utf-8")

    print(f"✓ Wrote {zip_path}")
    print(f"✓ Wrote {map_path}")
    print(f"✓ Wrote {factor_path}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True, help="Output Data folder path")
    p.add_argument("--symbol", required=True, help="Symbol, e.g. SPY")
    p.add_argument("--start", required=True, help="YYYY-MM-DD")
    p.add_argument("--end", required=True, help="YYYY-MM-DD")
    args = p.parse_args()

    build_equity_daily(out_data_root=Path(args.out), symbol=args.symbol, start=args.start, end=args.end)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

