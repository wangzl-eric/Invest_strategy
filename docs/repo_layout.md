# Repository Layout

This repository contains a few different kinds of top-level directories. They should not all be read as equal "stacks".

The most useful framing is:

- an **investment dashboard application** for broker/account monitoring and operational workflows
- a **quant research workstation** for ingestion, strategy research, backtesting, and optimization
- a small set of **optional extensions** that should stay isolated

The current physical layout now groups those areas under `apps/`, `workstation/`, and `extensions/`. Legacy root paths are kept as compatibility symlinks during the transition.

## Stack Map

| Path | Category | Status | Purpose |
|------|----------|--------|---------|
| `apps/dashboard/backend/` | Dashboard app | Active | FastAPI service, IBKR integration, persistence, APIs |
| `apps/dashboard/frontend/` | Dashboard app | Active | Dash dashboard for monitoring and controls |
| `data/` | Shared runtime data | Active | Pulled datasets, market data files, broker exports, catalogs |
| `workstation/backtests/` | Research workstation | Active | Signal research, walk-forward analysis, stats, reporting |
| `workstation/portfolio/` | Research workstation | Active | Alpha blending, optimization, risk analytics, rebalancing |
| `workstation/execution/` | Research workstation | Active | Paper/live order flow, broker abstraction, risk checks |
| `workstation/quant_data/` | Research workstation | Active | Data-ingestion code, schemas, connectors, registry, DuckDB helpers |
| `workstation/research/` | Research output | Active | Strategy notes, reviews, tracker, framework audits |
| `workstation/notebooks/` | Research workspace | Active | Exploratory notebooks and templates |
| `extensions/cerebro/` | Optional extension | Experimental | Research-ingestion and idea-generation pipeline |
| `qc_lean/` | Optional external integration | Isolated | Local QuantConnect Lean runtime, engine source, results |
| `docs/` | Documentation | Active | Guides, specs, architecture notes |
| `scripts/` | Tooling | Active | CLI entry points, ingestion jobs, automation |
| `tests/` | Verification | Active | Unit and integration coverage |

## Compatibility

These legacy root paths currently remain in place as symlinks:

- `backend/`
- `frontend/`
- `backtests/`
- `portfolio/`
- `execution/`
- `quant_data/`
- `research/`
- `notebooks/`
- `playground/`
- `books_and_papers/`
- `cerebro/`

## Naming Decisions

### `data/` vs `quant_data/`

- `data/` is not a Python package. It is the runtime storage root for pulled datasets and broker artifacts.
- `workstation/quant_data/` is the Python package that fetches, validates, normalizes, and registers those datasets.
- The names overlap semantically, but they represent different layers: storage vs code.

### `backtests/` vs `backend/backtest_engine.py`

- `backtests/` is the research framework: signals, portfolio builder, walk-forward analysis, statistics, reporting.
- `backend/backtest_engine.py` is an event-driven execution adapter around Backtrader and sits closer to the API/live stack.
- They should stay separate unless the event-driven engine is migrated deliberately with compatibility imports.

### `backend/` and `frontend/`

- These are deployable apps.
- `backtests/`, `portfolio/`, `execution/`, and `quant_data/` are shared domain libraries used by apps and scripts.

### `qc_lean/`

- `qc_lean/` should be treated as an optional external engine, not a first-class peer of the Python packages.
- It contains vendor source, local runtime files, example algorithms, and generated outputs.
- If you want a deeper physical cleanup later, the likely target is `external/qc_lean/` or a separate sibling repository.

## Recommended Boundaries

- Put API, DB, broker, and scheduler code in `apps/dashboard/backend/`.
- Put UI code in `apps/dashboard/frontend/`.
- Put reusable research logic in `workstation/backtests/`, `workstation/portfolio/`, `workstation/execution/`, or `workstation/quant_data/`.
- Put raw or generated files in `data/`.
- Keep optional or experimental integrations clearly marked, like `extensions/cerebro/` and `qc_lean/`.

## Follow-Up Refactors

These are reasonable next steps, but were intentionally not done in this pass because they are import- and path-sensitive:

1. Move `qc_lean/` under `external/` or out of the repo entirely.
2. Move `backend/backtest_engine.py` into `workstation/backtests/event_driven/` and keep a compatibility import.
3. Replace the compatibility symlinks with updated imports and path references once the new grouped layout has settled.
4. Split optional systems like `cerebro/` into their own package or workspace once the interfaces stabilize.
