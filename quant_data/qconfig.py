"""Configuration for the quant research data layer."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _workspace_root() -> Path:
    # Assumes this file lives in {root}/quant_data/qconfig.py
    return Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class QuantDataSettings:
    """Settings for data lake + metadata store.

    Env vars:
      - DATA_LAKE_ROOT: root folder for Parquet lake (default: {repo}/data_lake)
      - QDATA_META_DB_URL: SQLAlchemy URL for metadata registry (default: sqlite:///./quant_data_meta.db)
      - QDATA_DUCKDB_PATH: DuckDB file path for ad-hoc research store (default: {repo}/data_lake/research.duckdb)
    """

    data_lake_root: Path
    meta_db_url: str
    duckdb_path: Path

    @classmethod
    def from_env(cls) -> "QuantDataSettings":
        root = _workspace_root()
        data_lake_root = Path(os.getenv("DATA_LAKE_ROOT", str(root / "data_lake"))).expanduser()
        meta_db_url = os.getenv("QDATA_META_DB_URL", "sqlite:///./quant_data_meta.db")
        duckdb_path = Path(os.getenv("QDATA_DUCKDB_PATH", str(data_lake_root / "research.duckdb"))).expanduser()
        return cls(data_lake_root=data_lake_root, meta_db_url=meta_db_url, duckdb_path=duckdb_path)

