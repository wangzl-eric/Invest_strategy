"""Data lake path conventions.

We store datasets as Parquet, partitioned by common keys, so they can be:
- read quickly by date range
- merged/rebuilt deterministically
- uploaded to object storage (S3-compatible) without changing layout
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from quant_data.spec import DatasetId, DatasetLayer


@dataclass(frozen=True)
class DataLakeConfig:
    root: Path

    def layer_root(self, layer: DatasetLayer) -> Path:
        return self.root / layer.value


def dataset_root(cfg: DataLakeConfig, *, layer: DatasetLayer, dataset_id: DatasetId) -> Path:
    # {root}/{layer}/{provider}/{kind}/{universe}/{frequency}/
    return cfg.layer_root(layer) / dataset_id.provider / dataset_id.kind.value / dataset_id.universe / dataset_id.frequency.value


def parquet_partition_path(
    cfg: DataLakeConfig,
    *,
    layer: DatasetLayer,
    dataset_id: DatasetId,
    date: str,
    symbol: Optional[str] = None,
    venue: Optional[str] = None,
) -> Path:
    """Standard partition layout.

    - Always partition by `date=YYYY-MM-DD`
    - Optionally partition by `symbol=` and/or `venue=` when it improves read patterns
    """

    base = dataset_root(cfg, layer=layer, dataset_id=dataset_id) / f"date={date}"
    if symbol:
        base = base / f"symbol={symbol}"
    if venue:
        base = base / f"venue={venue}"
    return base

