# Quant Data Specification (Canonical Research Datasets)

This repository started as **IBKR portfolio analytics** (account snapshots, PnL, trades).  
This document defines a **canonical data layer** so you can research multi-asset alpha signals with consistent schemas.

## Existing data sources in this repo

- **IBKR API (TWS/Gateway)** → stored to DB via [`backend/data_fetcher.py`](../backend/data_fetcher.py)
  - `account_snapshots`, `positions`, `pnl_history`, `trades`, `performance_metrics` in [`backend/models.py`](../backend/models.py)
- **IBKR Flex Query reports** → stored on disk under `data/flex_reports/` and parsed by [`backend/flex_parser.py`](../backend/flex_parser.py)

## Canonical data lake layers

- **raw**: vendor-native fields preserved (minimal transforms), Parquet
- **clean**: standardized columns/dtypes/timezones, Parquet
- **features**: derived features (signals, factors, labels), Parquet

Default local location (recommended): `data_lake/`

## Naming convention

We identify datasets by:

- **provider**: `ibkr`, `stooq`, `fred`, `polygon`, `binance_public`, etc.
- **kind**: `bars`, `trades`, `quotes`, `fundamentals`, `fx_rates`, ...
- **universe**: `us_equities`, `g10_fx`, `crypto_top50`, `multiasset_core`, ...
- **frequency**: `tick`, `1s`, `1m`, `1h`, `1d`

Combined slug:

`{provider}/{kind}/{universe}/{frequency}`

## Partitioning convention (Parquet)

Required partition:

- `date=YYYY-MM-DD`

Optional partitions (when useful for read patterns):

- `symbol=...`
- `venue=...`

Example:

`data_lake/clean/stooq/bars/us_equities/1d/date=2026-01-10/symbol=AAPL/part-000.parquet`

## Canonical schemas (minimum required columns)

### OHLCV bars

Required columns:

- `timestamp` (UTC)
- `symbol`
- `venue` (optional if unknown, but column should exist)
- `currency`
- `open`, `high`, `low`, `close`
- `volume`

Optional:

- `vwap`

### Trades (prints)

- `timestamp` (UTC)
- `symbol`, `venue`
- `price`, `size`
- `side` (if available)

### Quotes (NBBO/L1)

- `timestamp` (UTC)
- `symbol`, `venue`
- `bid`, `bid_size`, `ask`, `ask_size`

## How IBKR data maps to the canonical lake

- **Trades**:
  - Source: `trades` SQL table (from IBKR API) and/or Flex Query trades (`backend/flex_parser.py`)
  - Canonical target: `clean/ibkr/trades/{universe}/{frequency}`
  - Notes:
    - IBKR “trades” are executions/fills; for research you may also want market trades/quotes from a market data vendor.
    - Normalize `exec_time` → `timestamp` UTC.

- **Positions / account snapshots / PnL**:
  - Source: `account_snapshots`, `positions`, `pnl_history`
  - Canonical target: treat as **accounting datasets** rather than market data (still Parquet-able):
    - `clean/ibkr/account_snapshots/{account}/{frequency}`
    - `clean/ibkr/positions/{account}/{frequency}`
    - `clean/ibkr/pnl/{account}/{frequency}`

## Implementation references

- Dataset spec + enums: [`quant_data/spec.py`](../quant_data/spec.py)
- Path/partition helpers: [`quant_data/paths.py`](../quant_data/paths.py)


