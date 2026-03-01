# Research Workspace

This folder is for reproducible research (notebooks + parameterized experiments).

Recommended workflow:

1. Ingest market data into `data_lake/` (Parquet).
2. Use DuckDB (`data_lake/research.duckdb`) for fast ad-hoc SQL across Parquet.
3. Run parameterized experiments from `research/experiments/` and track results with MLflow.

Key modules:

- `quant_data/`: dataset spec, connectors, ingestion pipelines, DuckDB helper
- `backtests/`: strategy evaluation using Backtrader
- `portfolio/`: portfolio optimization + constraints
