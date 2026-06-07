# Repository Layout

This repository is organized into **three product components**, each a top-level directory:

1. **`dashboard/`** — IBKR portfolio analytics & market-price application (FastAPI backend + Dash frontend)
2. **`alpha_research/`** — alpha research & backtesting infrastructure (signal/backtest/portfolio/execution libraries, data ingestion, research notes, notebooks, and the Cerebro discovery pipeline)
3. **`book_notes/`** — learning material: notes on books/papers and the playground study environment

For the end-to-end research flow, see [`docs/data_backtest_report_pipeline.md`](./data_backtest_report_pipeline.md).

The project runs on a flat `PYTHONPATH=.` import namespace (`from backend...`, `from portfolio...`, etc.). To keep that namespace working after the physical grouping, root-level **compatibility symlinks** point each importable package name at its new location inside a component. This is a physical/organizational grouping, not enforced module isolation — the dashboard and research libraries still import each other freely.

## Stack Map

| Path | Component | Status | Purpose |
|------|-----------|--------|---------|
| `dashboard/backend/` | Dashboard | Active | FastAPI service, IBKR integration, persistence, APIs |
| `dashboard/frontend/` | Dashboard | Active | Dash dashboard for monitoring and controls |
| `alpha_research/backtests/` | Alpha research | Active | Signal research, walk-forward analysis, stats, reporting |
| `alpha_research/portfolio/` | Alpha research | Active | Alpha blending, optimization, risk analytics, rebalancing |
| `alpha_research/execution/` | Alpha research | Active | Paper/live order flow, broker abstraction, risk checks |
| `alpha_research/quant_data/` | Alpha research | Active | Data-ingestion code, schemas, connectors, registry, DuckDB helpers |
| `alpha_research/research/` | Alpha research | Active | Strategy notes, reviews, tracker, framework audits |
| `alpha_research/notebooks/` | Alpha research | Active | Exploratory notebooks and templates |
| `alpha_research/cerebro/` | Alpha research | Experimental | Research-ingestion and idea-generation pipeline |
| `book_notes/playground/` | Book notes | Active | Playground study environment (studies, agents, skills) |
| `book_notes/books_and_papers/` | Book notes | Active | Source PDFs of books and papers |
| `data/` | Shared runtime data | Active | Pulled datasets, market data files, broker exports, catalogs |
| `docs/` | Documentation | Active | Guides, specs, architecture notes |
| `scripts/` | Tooling | Active | CLI entry points, ingestion jobs, automation |
| `tests/` | Verification | Active | Unit and integration coverage |

## Compatibility symlinks

These root paths are symlinks that preserve the flat import namespace. Do not delete them
without first rewriting the corresponding imports/path references.

| Symlink | Target |
|---------|--------|
| `backend/` | `dashboard/backend/` |
| `frontend/` | `dashboard/frontend/` |
| `backtests/` | `alpha_research/backtests/` |
| `portfolio/` | `alpha_research/portfolio/` |
| `execution/` | `alpha_research/execution/` |
| `quant_data/` | `alpha_research/quant_data/` |
| `research/` | `alpha_research/research/` |
| `notebooks/` | `alpha_research/notebooks/` |
| `cerebro/` | `alpha_research/cerebro/` |
| `books_and_papers/` | `book_notes/books_and_papers/` |

## Naming Decisions

### `data/` vs `alpha_research/quant_data/`

- `data/` is not a Python package. It is the runtime storage root for pulled datasets and broker artifacts.
- `alpha_research/quant_data/` (importable as `quant_data`) is the Python package that fetches, validates, normalizes, and registers those datasets.
- The names overlap semantically, but they represent different layers: storage vs code.

### `data/` vs `data_lake/`

- `data/` is the primary runtime storage root used by the dashboard and most pipelines
  (Flex reports, market-data Parquet under `data/market_data/`, `catalog.json`).
- `data_lake/` is the DuckDB-backed research lake used by `alpha_research/quant_data`
  (default `data_lake/research.duckdb`, overridable via `DATA_LAKE_ROOT`/`QDATA_DUCKDB_PATH`).
- They are separate stores by design; consolidating them is a possible future cleanup.

### `alpha_research/backtests/` vs `dashboard/backend/backtest_engine.py`

- `alpha_research/backtests/` is the research framework: signals, portfolio builder, walk-forward analysis, statistics, reporting.
- `alpha_research/backtests/event_driven/backtest_engine.py` is the canonical event-driven execution adapter around Backtrader.
- `dashboard/backend/backtest_engine.py` is kept only as a compatibility shim for existing imports.

### `dashboard/`

- `dashboard/backend/` and `dashboard/frontend/` are the deployable app.
- `backtests/`, `portfolio/`, `execution/`, and `quant_data/` (under `alpha_research/`) are shared domain libraries used by the app and scripts.

### Backtesting engine

- The in-house engine under `alpha_research/backtests/` is the single supported
  backtesting framework (vectorized builder, walk-forward, event-driven engine, stats).
- The former QuantConnect Lean workspace (`qc_lean/`) has been **removed/deprecated**;
  do not reintroduce an external engine without a deliberate decision.

## Recommended Boundaries

- Put API, DB, broker, and scheduler code in `dashboard/backend/`.
- Put UI code in `dashboard/frontend/`.
- Put reusable research logic in `alpha_research/{backtests,portfolio,execution,quant_data}/`.
- Put strategy notes and exploratory notebooks in `alpha_research/{research,notebooks}/`.
- Put book/paper learning material in `book_notes/`.
- Put raw or generated files in `data/`.
- Keep optional or experimental integrations clearly marked (`alpha_research/cerebro/`).

## Follow-Up Refactors

Reasonable next steps, intentionally not done because they are import- and path-sensitive:

1. Replace the `dashboard/backend/backtest_engine.py` compatibility shim with direct imports once downstream callers are updated.
2. Extract a shared `core` (DB models, IBKR client, market-data store) to break the dashboard↔research import coupling, if true module isolation becomes desirable.
