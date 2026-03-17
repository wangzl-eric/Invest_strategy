# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IBKR Portfolio Analytics & Quantitative Research Platform — a full-stack quant analytics platform for Interactive Brokers accounts. Covers data ingestion, research, backtesting, portfolio optimization, execution, and real-time monitoring.

## Commands

```bash
# Environment
conda activate ibkr-analytics          # Python 3.10
export PYTHONPATH=.                     # Required before running anything

# Tests
make test                              # All tests
make test-cov                          # Tests with coverage (backend, portfolio, backtests, execution)
pytest tests/unit/test_foo.py -v       # Single test file
pytest tests/unit/test_foo.py::TestClass::test_method -v  # Single test

# Lint & Format
make lint                              # flake8 + black --check
make format                            # black + isort (--profile black)
make typecheck                         # mypy backend/

# Servers
make serve-backend                     # FastAPI on :8000 (with --reload)
make serve-frontend                    # Dash on :8050
```

Flake8 config: `--max-line-length=120 --ignore=E501,W503`

## Architecture

```
backend/           FastAPI API service + data processing + IBKR integration
  api/             Route handlers (15+ routers: auth, backtest, data, market, news, research, etc.)
  research/        Feature engineering (features.py), DuckDB helpers
  main.py          App entry point — CORS, metrics, rate limiting, APScheduler
  config.py        Pydantic BaseSettings (env prefix: IBKR_, DB_, APP_)
  models.py        SQLAlchemy models (AccountSnapshot, Position, PnLHistory, Trade, PerformanceMetric)
  database.py      Engine creation, session management
frontend/          Dash web dashboard (CYBORG dark theme)
  app.py           Entry point, callbacks, tab rendering
  components/      UI panels (charts, positions table, market panels, data manager, cerebro)
portfolio/         Portfolio optimization (CVXPY mean-variance, risk parity, rebalancing)
backtests/         Backtesting engines
  builder.py       Vectorized backtesting
  walkforward.py   Walk-forward analysis
  event_driven/    Event-driven engine (realistic fills/slippage)
  forward_pass/    Forward-pass tracking & comparison
  strategies/      Signal framework, Backtrader compatibility
  stats/           Statistical tests (PSR, deflated Sharpe, CPCV, bootstrap)
  costs/           Transaction cost & slippage models
cerebro/           AI-powered research discovery (arXiv, SSRN, blogs, scoring, proposals)
execution/         Trade execution framework
  runner.py        Order execution loop
  risk.py          Risk controls (position limits, drawdown stops)
  sim_broker.py    Paper trading simulator
  audit.py         Trade audit logging
quant_data/        Data lake & market data pipelines
  connectors/      Data sources (Binance, Stooq, Polygon, ECB FX)
  pipelines/       Ingestion pipelines
  duckdb_store.py  DuckDB queries on Parquet files
  registry.py      Dataset registry
research/          Strategy research notes, tracker, external ideas (docs only)
scripts/           Automation (PA downloads, data ingestion, backfill, scheduling, tests)
docs/              Documentation and setup guides
  guides/          Setup and usage guides (IBKR, alerts, backtesting, etc.)
config/            App config YAML, ticker universe
data/              Flex reports (CSV), market data (Parquet), catalog.json
```

## Data Flow

IBKR TWS/Gateway (real-time) + Flex Query (historical CSV) + External APIs (yfinance, FRED, Stooq, Binance)
→ Data Fetcher/Processor → SQLite/PostgreSQL (account data) + Parquet data lake (market data via DuckDB)
→ Research/Backtesting → Portfolio Optimization → Execution → Dashboard

## Key Patterns

- **Config**: Pydantic BaseSettings with env prefixes (`IBKR_HOST`, `DB_URL`, `APP_DEBUG`, `FLEX_TOKEN`, `FRED_API_KEY`). Loads `.env` from project root.
- **Database**: SQLAlchemy 2.0 declarative base. Default SQLite (`ibkr_analytics.db`), PostgreSQL in production.
- **API responses**: Pydantic schemas in `backend/api/schemas.py`. Consistent envelope (success, data, error, metadata).
- **Parquet schema**: prices = `(date, ticker, open, high, low, close, volume)`, FRED = `(date, series_id, value)`. `catalog.json` auto-updated on pull — don't edit manually.
- **Test fixtures**: `tests/conftest.py` provides `test_db` (in-memory SQLite), `mock_ibkr_client`, sample data series. Markers: `unit`, `integration`, `slow`, `requires_ibkr`, `requires_db`.

## Look-Ahead Bias Prevention (Backtesting)

When writing signals in backtesting code:
- End-of-day trading (trade after close): use `[0]` for current bar
- Intraday / start-of-day: use `[-1]` for previous bar (safe, no look-ahead)
- Every `self.data.X[0]` access should have a comment explaining why `[0]` is valid

## Adding Market Data

1. Add FRED series ID + metadata to the appropriate dict in `market_data_service.py`
2. Add instrument definition (tooltip) to `DEFINITIONS` in `frontend/components/market_panels.py`
3. If new category, add to `CATEGORY_ORDER` in `market_panels.py`
4. Test: `curl http://localhost:8000/api/market/overview | python3 -m json.tool`

For Parquet data lake: define tickers in `market_data_store.py`, map to file path, use Data Manager UI or `POST /api/data/pull`.

## Research Work Tracking (MANDATORY)

Any work — code, fixes, analysis, or discussion — that directly addresses topics covered in `research/` **must** be logged with a timestamp, regardless of which files are actually modified. This includes:

- Fixes or changes to `backtests/`, `portfolio/`, `execution/`, `backend/`, etc. that are motivated by a research finding or strategy requirement
- Conversations or analysis that resolve open questions in a strategy doc
- New signals, parameter changes, or risk rule adjustments tied to a research strategy
- Any work on the Cerebro pipeline that feeds into research proposals

**Format — append to `research/STRATEGY_TRACKER.md` under the relevant strategy or topic section:**
```
### YYYY-MM-DD — <short description>
- What changed / what was discussed and why
- Files modified (if any; write "discussion only" if no code changed)
- Status: [IN PROGRESS | COMPLETE | BLOCKED]
```

**Rules:**
- Log the date and a one-line summary as a comment (`# YYYY-MM-DD: <what>`) at the top of any edited `research/` file.
- If creating a new file under `research/`, add the creation date and author context in the file header.
- Do not batch multiple days of work into a single entry — one entry per session.
- The tracker (`research/STRATEGY_TRACKER.md`) is the source of truth for all research-related history.

## Agent-Deck (Multi-Agent Session Manager)

The research team uses [agent-deck](https://github.com/asheshgoplani/agent-deck) for session management, worktree isolation, and cross-model orchestration.

```bash
# Launch research team
./scripts/launch_research_team.sh <strategy_name> <researcher>  # elena or marco

# Cleanup
./scripts/cleanup_research_team.sh          # stop sessions (preserve worktrees)
./scripts/cleanup_research_team.sh --remove # full teardown

# TUI
agent-deck                                  # open session manager
```

**Session architecture:**
- Researchers (Marco, Elena) and Dev each get isolated git worktrees
- PM and Cerebro work on main branch
- Codex (GPT-5.4) assists with backtest execution, parameter sweeps, and code review
- Conductor session orchestrates the v2 challenge loop automatically
- MCP socket pooling shares servers across all sessions

**Key commands from TUI:** `/` fuzzy search, `G` global search, fork sessions for A/B research exploration.

**Config:** `~/.agent-deck/config.toml` | Conductor: `~/.agent-deck/conductor/research/CLAUDE.md`

## Gotchas

See `~/.claude/projects/-Users-zelin-Desktop-PA-Investment-Invest-strategy/memory/GOTCHAS.md` for detailed technical pitfalls (14 gotchas across 8 categories: Dash, FastAPI, FRED, yfinance, Backtrader, Pandas, DuckDB, Jupyter).
