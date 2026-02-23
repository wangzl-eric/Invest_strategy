# Data Lake (Parquet)

This folder is the canonical store for research datasets (raw/clean/features).

Layout:

- `raw/` vendor-native datasets
- `clean/` standardized canonical datasets
- `features/` derived features/signals/labels
- `research.duckdb` local DuckDB file for ad-hoc queries

See [`docs/QUANT_DATA_SPEC.md`](../docs/QUANT_DATA_SPEC.md) for naming + partitioning.

