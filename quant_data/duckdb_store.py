"""DuckDB helpers for local research.

Idea:
- Keep Parquet lake as the source of truth.
- Use DuckDB for fast ad-hoc SQL across Parquet partitions without ingesting into Postgres.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import duckdb

from quant_data.qconfig import QuantDataSettings


def connect(settings: QuantDataSettings | None = None) -> duckdb.DuckDBPyConnection:
    s = settings or QuantDataSettings.from_env()
    s.duckdb_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(s.duckdb_path))


def register_parquet_view(
    con: duckdb.DuckDBPyConnection,
    *,
    view_name: str,
    parquet_glob: str,
    replace: bool = True,
) -> None:
    """Create a view over a parquet glob, e.g. '/path/to/date=*/**/*.parquet'."""

    if replace:
        con.execute(f"CREATE OR REPLACE VIEW {view_name} AS SELECT * FROM read_parquet('{parquet_glob}')")
    else:
        con.execute(f"CREATE VIEW {view_name} AS SELECT * FROM read_parquet('{parquet_glob}')")


def vacuum(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("VACUUM")

