"""Generic bars ingestion -> canonical Parquet lake + registry."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from quant_data.connectors.base import BarsConnector, BarsRequest
from quant_data.io.parquet_writer import ParquetWriteResult, write_bars_partitioned
from quant_data.meta_db import get_meta_db_context
from quant_data.paths import DataLakeConfig
from quant_data.qconfig import QuantDataSettings
from quant_data.registry import finish_ingestion_run, register_dataset_version, start_ingestion_run
from quant_data.spec import DatasetId, DatasetLayer


@dataclass(frozen=True)
class IngestBarsResult:
    dataset_version: str
    files_written: int


def ingest_bars_to_lake(
    *,
    connector: BarsConnector,
    dataset_id: DatasetId,
    req: BarsRequest,
    layer: DatasetLayer = DatasetLayer.CLEAN,
    version: str | None = None,
) -> IngestBarsResult:
    """Fetch bars and write to Parquet lake, tracking lineage in metadata DB."""

    settings = QuantDataSettings.from_env()
    lake_cfg = DataLakeConfig(root=settings.data_lake_root)

    with get_meta_db_context(settings) as db:
        reg = register_dataset_version(
            db,
            ds=dataset_id,
            version=version,
            description=f"{connector.provider} bars ingestion",
            start_date=req.start,
            end_date=req.end,
        )
        run = start_ingestion_run(
            db,
            dataset_version_id=reg.dataset_version_id,
            parameters={
                "provider": connector.provider,
                "symbols": req.symbols,
                "start": req.start,
                "end": req.end,
                "layer": layer.value,
            },
        )

        try:
            df = connector.fetch_bars(req)
            if df.empty:
                finish_ingestion_run(db, run_id=run.id, status="success")
                return IngestBarsResult(dataset_version=reg.version, files_written=0)

            write_res: ParquetWriteResult = write_bars_partitioned(
                cfg=lake_cfg,
                layer=layer,
                dataset_id=dataset_id,
                df=df,
                partition_by_symbol=True,
                venue=req.venue or None,
            )
            finish_ingestion_run(db, run_id=run.id, status="success")
            return IngestBarsResult(dataset_version=reg.version, files_written=write_res.files_written)
        except Exception as e:
            finish_ingestion_run(db, run_id=run.id, status="failed", error=str(e))
            raise

