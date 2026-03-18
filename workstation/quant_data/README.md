# Quant Data

`quant_data/` is the Python package for market-data ingestion and dataset management.

It is easy to confuse with `data/`, but the split is intentional:

- `quant_data/` = code: connectors, schemas, registry, ingestion pipelines, DuckDB helpers
- `data/` = files: pulled datasets, Parquet outputs, broker exports, catalogs

Use this package for source adapters and canonical dataset definitions, not for storing the resulting data files themselves.
