# Data

`data/` is the runtime storage root for datasets and broker artifacts.

Typical contents:

- `market_data/` for pulled and normalized market datasets
- `flex_reports/` for IBKR and Portfolio Analyst exports

This directory is not a Python package. Code that reads or writes these files belongs in `quant_data/`, `backend/`, or `scripts/`.
