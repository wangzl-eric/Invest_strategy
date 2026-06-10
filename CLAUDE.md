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

The repo is a three-layer DAG — `core/` (infrastructure) at the bottom, then the
three product components. `core/` depends on nothing internal; `alpha_research/`
and `dashboard/` depend on `core/`; `dashboard/` may also use `alpha_research/`
(one-way). See `docs/repo_layout.md` for the full stack map.

```
core/                Shared infrastructure (bottom layer — imports nothing internal)
  config.py          Pydantic BaseSettings (env prefix: IBKR_, DB_, APP_)
  models.py          SQLAlchemy models (AccountSnapshot, Position, PnLHistory, Trade, PerformanceMetric)
  database.py        Engine creation, session management
  db_utils.py, data_processor.py        Persistence helpers + account-data processing
  flex_*.py          IBKR Flex Query ingestion (parser, query_client, importer)
  ibkr_client.py, circuit_breaker.py    Broker connectivity
  market_data_store.py, market_data_service.py, data_providers.py,
    data_source_manager.py, cb_meeting_schedule.py   Market-data platform
  llm_client.py, token_tracker.py, llm_verdict.py    LLM plumbing + verdicts
dashboard/           Component 1 — IBKR portfolio analytics + market-data app
  backend/           FastAPI API service (imports core.* for infra)
    api/             Route handlers (15+ routers: auth, backtest, data, market, news, research, etc.)
    research/        Feature engineering (features.py), DuckDB helpers
    main.py          App entry point — CORS, metrics, rate limiting, APScheduler
  frontend/          Dash web dashboard (CYBORG dark theme)
    app.py           Entry point, callbacks, tab rendering
    components/      UI panels (charts, positions table, market panels, data manager, cerebro)
alpha_research/      Component 2 — alpha research & backtesting infrastructure
  backtests/         Backtesting engines
    builder.py       Vectorized backtesting
    walkforward.py   Walk-forward analysis
    event_driven/    Event-driven engine (realistic fills/slippage) — canonical engine
    forward_pass/    Forward-pass tracking & comparison
    strategies/      Signal framework, Backtrader compatibility
    stats/           Statistical tests (PSR, deflated Sharpe, CPCV, bootstrap)
    costs/           Transaction cost & slippage models
  portfolio/         Portfolio optimization (CVXPY mean-variance, risk parity, rebalancing)
  execution/         Trade execution framework (runner, risk, sim_broker, audit)
  quant_data/        Data lake & market data pipelines (connectors, pipelines, duckdb_store, registry)
  cerebro/           AI-powered research discovery (arXiv, SSRN, blogs, scoring, proposals)
  research/          Strategy research notes, tracker, external ideas (docs only)
  notebooks/         Exploratory research notebooks and templates
book_notes/          Component 3 — learning material
  playground/        Playground study environment (studies, agents, skills)
  books_and_papers/  Source PDFs of books and papers
bin/                 Entry scripts & launchers (start.sh/.bat, stop.sh, start_scheduler.py, .app/.command)
scripts/             Automation (PA downloads, data ingestion, backfill, scheduling, agent-deck teams)
config/              App config YAML, ticker universe
data/                Flex reports (CSV), market data (Parquet), catalog.json
data_lake/           DuckDB research lake (research.duckdb)
docs/                Documentation and setup guides (docs/guides/)
infrastructure/      Docker / docker-compose deployment configs
tests/               Unit + integration tests
```

**Imports**: components are imported by their full, component-qualified path —
`from core.config import settings`, `from core.database import ...`,
`from core.models import ...`, `from alpha_research.portfolio... import`, etc.
Shared infrastructure (config, DB, broker, market data, LLM) lives in `core/` —
**never** import it from `dashboard.backend`. Layering rule: `core` imports
nothing internal; `alpha_research` and `dashboard` import `core`; `dashboard` may
import `alpha_research` (not vice-versa). Repo root must be on `PYTHONPATH`
(pytest sets `pythonpath = .`; the Makefile/bin launchers run from repo root).
There are **no compatibility symlinks**. `config/`, `data/`, `data_lake/` are not
Python packages (the settings package is `core.config`).

## Data Flow

IBKR TWS/Gateway (real-time) + Flex Query (historical CSV) + External APIs (yfinance, FRED, Stooq, Binance)
→ Data Fetcher/Processor → SQLite/PostgreSQL (account data) + Parquet data lake (market data via DuckDB)
→ Research/Backtesting → Portfolio Optimization → Execution → Dashboard

## Key Patterns

- **Config**: Pydantic BaseSettings with env prefixes (`IBKR_HOST`, `DB_URL`, `APP_DEBUG`, `FLEX_TOKEN`, `FRED_API_KEY`). Loads `.env` from project root.
- **Database**: SQLAlchemy 2.0 declarative base. Default SQLite (`ibkr_analytics.db`), PostgreSQL in production.
- **API responses**: Pydantic schemas in `dashboard/backend/api/schemas.py`. Consistent envelope (success, data, error, metadata).
- **Parquet schema**: prices = `(date, ticker, open, high, low, close, volume)`, FRED = `(date, series_id, value)`. `catalog.json` auto-updated on pull — don't edit manually.
- **Test fixtures**: `tests/conftest.py` provides `test_db` (in-memory SQLite), `mock_ibkr_client`, sample data series. Markers: `unit`, `integration`, `slow`, `requires_ibkr`, `requires_db`.

## Look-Ahead Bias Prevention (Backtesting)

When writing signals in backtesting code:
- End-of-day trading (trade after close): use `[0]` for current bar
- Intraday / start-of-day: use `[-1]` for previous bar (safe, no look-ahead)
- Every `self.data.X[0]` access should have a comment explaining why `[0]` is valid

## Adding Market Data

1. Add FRED series ID + metadata to the appropriate dict in `core/market_data_service.py`
2. Add instrument definition (tooltip) to `DEFINITIONS` in `dashboard/frontend/components/market_panels.py`
3. If new category, add to `CATEGORY_ORDER` in `dashboard/frontend/components/market_panels.py`
4. Test: `curl http://localhost:8000/api/market/overview | python3 -m json.tool`

For Parquet data lake: define tickers in `core/market_data_store.py`, map to file path, use Data Manager UI or `POST /api/data/pull`.

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

# Inspect effective models + override points
./scripts/show_agent_team.sh

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

**Model defaults and overrides:**
- Claude-role defaults live in `.claude/agents/*.md` frontmatter (`model:`). This is the shared source of truth for Claude subagents and the `agent-deck` launcher.
- One-off `agent-deck` launch overrides use env vars like `RESEARCH_PM_MODEL=sonnet` or `RESEARCH_DATA_MODEL=opus` before `./scripts/launch_research_team.sh`.
- Codex runner override uses `RESEARCH_CODEX_MODEL=...`.
- `scripts/sync_agents.sh` attempts to refresh the saved `agent-deck` session command when `.claude/agents/*.md` changes, then notifies the live session to re-read its identity file; restart the session when you want the new model to take effect.

## Playground (Market Study Platform)

The `playground/` directory is a **separate space** from formal research for learning, exploration, and hypothesis generation:

```
playground/
├── README.md                    # Overview and quick start
├── QUICK_REFERENCE.md          # Common tasks cheat sheet
├── data_helpers.py             # Simplified data access wrappers
├── notebooks/                  # Interactive exploration notebooks
│   ├── 00_getting_started.ipynb
│   ├── 01_market_overview.ipynb
│   ├── 02_correlation_explorer.ipynb
│   ├── 03_regime_detector.ipynb
│   └── 04_signal_sandbox.ipynb
├── studies/                    # Saved exploration results
│   └── {date}_{topic}/        # Timestamped study folders
├── agents/                     # Playground-specific agents
│   ├── tutor.md               # Educational guide (no rigor gates)
│   └── explorer.md            # Hypothesis generator
└── skills/                     # Playground-specific skills
    └── market-study/          # Exploratory workflow
```

**Philosophy:**
- **Process-driven and logical** — Material understanding is systematic: extract structure, identify key claims, condense knowledge points rigorously
- **Quant researcher focus** — Target audience is a quantitative researcher. Cover frontier methodologies, market microstructure, portfolio theory, factor models, and adjacent fields
- **No rigor gates** — No statistical thresholds or PM review. Fast iteration and learning-focused
- **Lightweight docs** — Simple findings.md instead of formal proposals

**Reading-Type Protocols:**

*Books:*
- Track content progression and the author's central argument arc chapter by chapter
- Extract technicalities (formulas, methods, frameworks) and draft structured documentation to maintain context across sessions
- Produce key notes: concepts encountered, how they build on each other, and what the author is ultimately trying to convey

*Articles / Papers:*
- Identify the core focus, narrative, and central claim
- Suggest concrete ways to validate or challenge the author's perspective (data, replication, alternative methodology)
- Note data sources, methodology choices, and replication potential

**Material Scoring (apply to all related materials surfaced during reading):**

| Dimension | Description |
|-----------|-------------|
| Credibility (1–5) | Author reputation, publication venue, methodology soundness |
| Relevance (1–5) | Direct applicability to quant research and current playground scope |
| Actionability (1–5) | Can findings be implemented, tested, or studied concretely? |

Only materials scoring ≥ 3 in all three dimensions warrant deeper follow-up.

**Agents:**
- **Cerebro** — Paper discovery, reading queue management, literature maps, adjacent field expansion. Scores all related materials on credibility, relevance, and actionability. When writing paper notes, MUST explicitly check if any paper findings contradict, expose issues in, or validate existing strategy code, signals, or notebooks in the codebase. Flag any discrepancies directly in the paper notes.
- **Tutor** — Explains concepts, methods, and reading content. For books: tracks progression and author intent. For articles: unpacks focus, story, and validation paths
- **Explorer** — Generates study ideas from readings. MUST invoke brainstorm skill to relate main topics with materials available online. Surfaces connections across domains
- **Dev** — Notebook scaffolding, tooling, and reproducible study infrastructure

**Playground team scripts:**
- `./scripts/launch_playground_team.sh "topic"` — launches Explorer, Tutor, Cerebro, and Dev for paper reading and knowledge expansion
- `./scripts/cleanup_playground_team.sh` — stops playground team sessions
- `./scripts/show_playground_team.sh` — shows effective models and override points

**Directory structure:**
- All study artifacts live under `book_notes/playground/studies/<book_or_topic>/`
- Each study folder is organized as:
  ```
  {date}_{topic}/
  ├── notes/          # chXX_notes.md files (one per book chapter)
  ├── notebooks/      # .ipynb files + *_assets/ dirs
  ├── paper_notes_*.md
  ├── reading_queue.md
  ├── FINDINGS_LOG.md
  └── (briefings, book maps, data files at root)
  ```
- Example: `book_notes/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/`

**Markdown math rendering:**
- All markdown notes must use standard LaTeX delimiters: `$...$` for inline, `$$...$$` for display math
- Dev must review all markdown files produced and fix any math formatting issues before considering work complete

**Leverages existing infrastructure:**
- Data: `quant_data/`, `market_data_store`, `market_data_service`
- Skills: `data-pulling` (relaxed validation), `market-intelligence-synthesizer`
- Notebooks: Complements existing tutorials in `notebooks/`

**Completion protocol:** When any agent finishes a task, it MUST send a summary message to `conductor-playground` via agent-deck without waiting to be asked. Include: what was completed, files created or modified, and suggested next steps.

**Migration to research:** When playground study shows promise, follow migration path in `playground/README.md` (check lessons learned, message Cerebro, create strategy folder, use formal template, follow v2 workflow).

## Gotchas

See `~/.claude/projects/-Users-zelin-Desktop-PA-Investment-Invest-strategy/memory/GOTCHAS.md` for detailed technical pitfalls (14 gotchas across 8 categories: Dash, FastAPI, FRED, yfinance, Backtrader, Pandas, DuckDB, Jupyter).
