---
name: data-pulling
description: Pull, refresh, and validate research data in this repository from the Parquet lake, IBKR, yfinance, or FRED. Use when a task needs source selection, freshness checks, gap analysis, symbol coverage validation, or a consistent data-pull report with explicit caveats.
---

# Data Pulling

Use this skill for any research task that depends on market or macro data quality. The default job is not just "download data". The job is to choose the right source, verify coverage, update the lake only when needed, and report what was actually used.

## Environment

Run from the repo root with:

```bash
conda activate ibkr-analytics
export PYTHONPATH=.
```

If shell activation is awkward, prefer:

```bash
conda run -n ibkr-analytics python ...
```

## Source Order

- Tradable equity, FX, and futures history: `ibkr` first, then existing `ibkr_*` parquet, then `yfinance` only as fallback.
- Macro and rates: `fred` first, then existing parquet, then `yfinance` proxies only if the user accepts approximation.
- Exploratory analysis: query the existing Parquet lake before pulling anything new.
- Never mix sources silently inside one answer. If mixed sources are necessary, label each series clearly.

## Canonical Files

- `data/market_data/catalog.json`
- `backend/market_data_store.py`
- `backend/api/data_routes.py`
- `backend/market_data_service.py`
- `backend/research/duckdb_utils.py`
- `config/ticker_universe.py`

Read [source-map.md](references/source-map.md) when you need the exact asset-class keys, endpoint shapes, or source-specific caveats.

## Workflow

1. Scope the request.
   Capture symbols or FRED series IDs, date range, frequency, fields, preferred source, and whether the user needs a refresh or only existing data.

2. Inspect local coverage first.
   Check `catalog.json`, relevant parquet files, and DuckDB views before pulling from the network or live brokers.

3. Choose the source deliberately.
   Use `IBKR` for execution-grade tradable history when available.
   Use `FRED` for macro/rates with publication-lag awareness.
   Use `yfinance` for fast exploratory OHLCV or when higher-quality sources are unavailable.

4. Pull through repository-native paths.
   Prefer `backend.market_data_store.MarketDataStore` methods or the matching API routes in `backend/api/data_routes.py`.
   Do not invent one-off download code if the repo already supports the asset type.

5. Validate after the pull.
   Confirm row count, min/max date, distinct symbols, duplicate keys, and whether the catalog updated.
   Flag partial failures, empty symbols, stale tails, or source-specific limitations.

6. Return a consistent report.
   Every answer should state what was requested, what source was used, what was written or queried, what coverage was achieved, and what caveats remain.

## Non-Negotiables

- Report the exact source used for each dataset.
- State whether data was pulled fresh or read from existing parquet.
- For FRED, call out publication lag and revision risk when it matters to a signal.
- For continuous futures or proxy instruments, call out roll or proxy limitations.
- For FX, distinguish spot history from carry or rollover inputs.
- If IBKR is unavailable, say so explicitly instead of silently downgrading quality.
- If coverage is incomplete, list the missing symbols or series IDs.

## Output Contract

Use this structure in final answers:

```text
Data request:
Source used:
Coverage:
Quality checks:
Caveats:
Next step:
```

Keep it short, but always include all six lines.
