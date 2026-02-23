"""Parquet writing helpers for canonical lake layout."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd

from quant_data.paths import DataLakeConfig, parquet_partition_path
from quant_data.spec import DatasetId, DatasetLayer, validate_columns, CANONICAL_BARS_COLUMNS


@dataclass(frozen=True)
class ParquetWriteResult:
    files_written: int


def write_bars_partitioned(
    *,
    cfg: DataLakeConfig,
    layer: DatasetLayer,
    dataset_id: DatasetId,
    df: pd.DataFrame,
    partition_by_symbol: bool = True,
    venue: Optional[str] = None,
) -> ParquetWriteResult:
    """Write canonical bars to Parquet partitions.

    Partitioning:
      - always: date=YYYY-MM-DD
      - optionally: symbol=...
    """

    if df.empty:
        return ParquetWriteResult(files_written=0)

    validate_columns(dataset=f"{dataset_id.slug()} bars", columns=df.columns, required=CANONICAL_BARS_COLUMNS[:9])

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["date"] = df["timestamp"].dt.date.astype(str)

    files = 0
    for date, df_d in df.groupby("date"):
        if partition_by_symbol:
            for symbol, df_s in df_d.groupby("symbol"):
                out_dir = parquet_partition_path(
                    cfg,
                    layer=layer,
                    dataset_id=dataset_id,
                    date=date,
                    symbol=str(symbol),
                    venue=venue,
                )
                out_dir.mkdir(parents=True, exist_ok=True)
                out_file = out_dir / "part-000.parquet"
                df_s.drop(columns=["date"]).to_parquet(out_file, index=False)
                files += 1
        else:
            out_dir = parquet_partition_path(cfg, layer=layer, dataset_id=dataset_id, date=date, venue=venue)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / "part-000.parquet"
            df_d.drop(columns=["date"]).to_parquet(out_file, index=False)
            files += 1

    return ParquetWriteResult(files_written=files)

