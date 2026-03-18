# Data, Backtest, and Report Pipeline

This repository has more than one data and reporting surface. The important thing is to keep the pipeline boundaries explicit so the dashboard app and the quant workstation do not silently drift apart.

## Canonical Pipeline

```text
Sources
  IBKR / FRED / yfinance / parquet cache / Flex reports
    ->
Ingestion code
  apps/dashboard/backend/market_data_store.py
  workstation/quant_data/pipelines/ingest_bars.py
    ->
Storage
  data/market_data/   for dashboard-compatible OHLCV/FRED parquet + catalog
  data_lake/          for partitioned quant-data datasets + lineage metadata
    ->
Research access
  backend.research.duckdb_utils
  workstation/quant_data/duckdb_store.py
    ->
Backtesting
  workstation/backtests/builder.py
  workstation/backtests/walkforward.py
  workstation/backtests/event_driven/backtest_engine.py
    ->
Run persistence
  workstation/backtests/run_manager.py
    ->
Research reporting
  workstation/backtests/reporting/review.py
  workstation/research/strategies/... notebooks and PM reviews
```

## Layer Responsibilities

### 1. Data ingestion

- `apps/dashboard/backend/market_data_store.py` is the dashboard-facing adapter for pulling and querying the shared market-data cache in `data/market_data/`.
- `workstation/quant_data/` is the reusable ingestion library for cleaner, partitioned, versioned datasets in `data_lake/`.
- `data/` is storage.
- `workstation/quant_data/` is code.

### 2. Research access

- `backend.research.duckdb_utils` reads the shared Parquet cache in `data/market_data/`.
- `workstation/quant_data/duckdb_store.py` is the DuckDB helper for the newer partitioned `data_lake/` side.
- Today, many dashboard and notebook flows still consume `data/market_data/` directly, so treating `data_lake/` as an automatic replacement would be incorrect.

### 3. Backtesting

There are two distinct backtest lanes:

- Vectorized research lane:
  - `workstation/backtests/builder.py`
  - `workstation/backtests/walkforward.py`
  - used for fast iteration, optimizer work, and notebook research
- Event-driven validation lane:
  - `workstation/backtests/event_driven/backtest_engine.py`
  - used for more realistic execution-style checks and compatibility with older imports

Recommended rule:

- Use `PortfolioBuilder` and `WalkForwardAnalyzer` as the main research path.
- Use the event-driven engine as a validation or execution-aligned lane, not as a replacement for the full research workflow.

### 4. Run artifacts

Research runs should be persisted with `RunManager` into `data/backtest_runs/<run_id>/`.

Expected artifacts:

- `config.yaml`
- `metrics.json`
- `equity_curve.parquet`
- `daily_returns.parquet`
- `review.json`
- `review.md`
- `quantstats_report.html` when available

### 5. Reporting

There are also two reporting lanes:

- Research reporting:
  - `workstation/backtests/reporting/review.py`
  - outputs markdown/json/QuantStats review artifacts for strategy evaluation
- Operational dashboard reporting:
  - `apps/dashboard/backend/reporting.py`
  - outputs PDF reports for account performance and trade-history workflows

These should not be conflated. A dashboard PDF is not the canonical research verdict artifact.

## Current Boundary Decisions

After the restructure, the recommended interpretation is:

- `apps/` owns deployable application surfaces.
- `workstation/` owns reusable research and quant libraries.
- `data/market_data/` is the shared runtime cache that existing dashboard and research routes already understand.
- `data_lake/` is the structured next-generation dataset store for `workstation/quant_data/`.

## Skills To Use

- `skills/data-pulling/SKILL.md` for source selection, freshness checks, and coverage validation
- `skills/rigorous-backtest/SKILL.md` for serious backtest execution and review
- `skills/research-pipeline/SKILL.md` when the task spans the full data -> backtest -> report path

## Residual Risks

- `data/market_data/` and `data_lake/` are both valid stores, but they do not feed every downstream consumer equally yet.
- Some example runners are still illustrative rather than production-grade.
- Dashboard PDF reporting is still operational reporting, not a strategy-approval workflow.
