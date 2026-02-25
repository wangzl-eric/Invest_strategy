# IBKR Portfolio Analytics & Quantitative Research Platform

A full-stack quantitative analytics platform for Interactive Brokers (IBKR) accounts. Covers the entire workflow from data ingestion and research through backtesting, portfolio optimization, execution, and real-time monitoring with alerts.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Feature Summary](#feature-summary)
- [Technology Stack](#technology-stack)
- [Module Reference](#module-reference)
  - [Backend API Service](#1-backend-api-service)
  - [IBKR Integration](#2-ibkr-integration)
  - [Database & Models](#3-database--models)
  - [Frontend Dashboard](#4-frontend-dashboard)
  - [Portfolio Construction](#5-portfolio-construction)
  - [Backtesting Engine](#6-backtesting-engine)
  - [Execution Framework](#7-execution-framework)
  - [Quantitative Data Lake](#8-quantitative-data-lake)
  - [Alert & Notification System](#9-alert--notification-system)
  - [Reporting & Export](#10-reporting--export)
  - [Observability](#11-observability)
  - [Research Notebooks](#12-research-notebooks)
  - [Automation Scripts](#13-automation-scripts)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Docker Deployment](#docker-deployment)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Security](#security)

---

## Architecture Overview

```
┌───────────────────────────────────────────────────────────────────┐
│                         Data Sources                              │
│  IBKR TWS/Gateway ─ Flex Queries ─ Stooq ─ Polygon ─ Binance    │
│  ECB FX ─ Yahoo Finance ─ Portfolio Analyst CSV                   │
└────────────────────────────┬──────────────────────────────────────┘
                             │
            ┌────────────────▼────────────────┐
            │        Ingestion Layer           │
            │  ib_insync · Flex Query Client   │
            │  Quant Data Connectors · CSV     │
            └────────────────┬────────────────┘
                             │
     ┌───────────────────────▼───────────────────────┐
     │              Storage Layer                      │
     │  SQLite / PostgreSQL ─ Parquet Data Lake        │
     │  DuckDB (ad-hoc SQL) ─ InfluxDB / TimescaleDB  │
     │  Redis (cache)                                  │
     └──────────┬──────────────────────┬──────────────┘
                │                      │
   ┌────────────▼──────────┐  ┌────────▼──────────────┐
   │   FastAPI Backend     │  │  Research / Notebooks  │
   │  REST + WebSocket     │  │  Jupyter · DuckDB SQL  │
   │  Auth · Rate Limit    │  │  MLflow Experiments    │
   │  Alerts · Scheduler   │  └───────────────────────┘
   └────────────┬──────────┘
                │
   ┌────────────▼──────────┐
   │   Plotly Dash Frontend │
   │  Dark-themed SPA       │
   │  Real-time WebSocket   │
   └────────────────────────┘
```

---

## Feature Summary

| Area | Capabilities |
|------|-------------|
| **IBKR Integration** | Live connection via TWS/Gateway, Flex Query Web Service, Portfolio Analyst CSV import |
| **Data Ingestion** | Multi-vendor connectors (Stooq, Polygon, Binance, ECB FX, yfinance), canonical schema normalization |
| **Database** | SQLAlchemy ORM, SQLite/PostgreSQL, time-series DB support (TimescaleDB, InfluxDB) |
| **API** | FastAPI with Swagger/ReDoc, JWT + API key auth, RBAC, rate limiting, CORS |
| **Dashboard** | Plotly Dash with dark theme, account summary, positions, PnL charts, trade history, performance metrics |
| **Markets Tab** | Cross-asset monitor: rates (full Treasury curve, TIPS, inflation), FX (G10), equities, commodities, yield curves, forward rates, Fed QE/QT monitor, macro pulse. 30-day sparklines, 1W/1M change columns, click-to-expand historical charts |
| **Data Manager** | Parquet data lake browser, pull data from yfinance/FRED, incremental updates, time-series viewer/chart, catalog with freshness indicators |
| **Portfolio Optimization** | Markowitz mean-variance, risk parity, Black-Litterman, minimum variance, cvxpy convex programs |
| **Risk Management** | Covariance estimation (sample, Ledoit-Wolf), stress testing, VaR, position/notional limits, kill switch |
| **Backtesting** | Vectorized (fast research) and event-driven (realistic fills) engines with cost/slippage models |
| **Execution** | Paper/live runner with pre-trade risk checks, order audit trail, simulated broker |
| **Alerts** | Configurable rules (PnL, drawdown, position size, volatility), multi-channel notifications (Email, SMS, Slack, Teams, Webhook, Push) |
| **Reporting** | PDF generation (ReportLab), Excel export, combined multi-sheet reports |
| **Observability** | Prometheus metrics, Sentry error tracking, OpenTelemetry tracing, structured JSON logging, circuit breaker |
| **Data Lake** | Parquet partitions, DuckDB SQL views, pandera validation, MLflow experiment tracking |
| **Automation** | Playwright-based PA download, daily cron scheduler, Flex Query scheduled fetches |
| **QuantConnect** | Local Lean engine integration for C#/Python algorithm backtests |

---

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| Language | Python 3.10+ |
| Backend | FastAPI, Uvicorn, SQLAlchemy, APScheduler |
| Frontend | Plotly Dash, Dash Bootstrap Components (Cyborg dark theme) |
| Broker API | ib_insync (TWS/Gateway), aiohttp (Flex Query REST) |
| Data Science | pandas, numpy, scipy, scikit-learn, statsmodels, cvxpy |
| Data Lake | DuckDB, PyArrow, Polars, pandera, Parquet |
| Experiment Tracking | MLflow |
| Database | SQLite (dev), PostgreSQL (prod), TimescaleDB, InfluxDB |
| Caching | Redis |
| Auth | python-jose (JWT), passlib (bcrypt), API key header |
| Notifications | smtplib, Twilio (SMS), pywebpush, aiohttp (Slack/Teams/Webhook) |
| Monitoring | prometheus-client, sentry-sdk, opentelemetry |
| PDF/Excel | ReportLab, openpyxl |
| Browser Automation | Playwright |
| Containerization | Docker, Docker Compose |
| QuantConnect | Lean Engine (.NET SDK) |

---

## Module Reference

### 1. Backend API Service

**Entry point:** `backend/main.py`

FastAPI application that wires together all routers, middleware, and lifecycle hooks.

- **Routers** registered at startup: core routes (`/api`), auth (`/api/auth`), backtest (`/api`), advanced analytics (`/api/analytics`), alerts (`/api`), reporting (`/api`), WebSocket (`/api`).
- **Middleware:** CORS, custom metrics collection (`MetricsMiddleware`), rate limiting.
- **Lifecycle hooks:** on startup the app launches the real-time broadcaster, alert scheduler, and registers the IBKR broker adapter. On shutdown it tears them down gracefully.

**Key backend modules:**

| Module | Purpose |
|--------|---------|
| `config.py` | Pydantic settings loaded from `app_config.yaml` and env vars |
| `database.py` | SQLAlchemy engine/session factory, `get_db` dependency |
| `models.py` | All ORM models (see [Database & Models](#3-database--models)) |
| `data_fetcher.py` | Pulls account state, positions, PnL from IBKR in real time |
| `data_processor.py` | Computes returns, Sharpe, Sortino, drawdown, win rate, profit factor |
| `data_providers.py` | Abstract `MarketDataProvider` interface + Yahoo Finance implementation |
| `benchmark_service.py` | Fetches S&P 500 data via yfinance with in-memory TTL cache for comparison |
| `validators.py` | Input validation utilities |
| `middleware.py` | Request timing and Prometheus metric collection |
| `rate_limiter.py` | Per-IP rate limiting middleware |

**API route files:**

| File | Prefix | Responsibilities |
|------|--------|-----------------|
| `routes.py` | `/api` | Account summary, positions, PnL time-series, trades, Flex Query fetch, data export, benchmark comparison |
| `auth_routes.py` | `/api/auth` | Register, login, token refresh, user management, API key CRUD |
| `backtest_routes.py` | `/api` | Submit and retrieve backtest results |
| `advanced_analytics_routes.py` | `/api/analytics` | Portfolio optimization, Monte Carlo simulation, factor analysis, correlation |
| `advanced_analytics_routes_extended.py` | `/api/analytics` | ML predictions, regime detection, stress testing |
| `alert_routes.py` | `/api` | CRUD for alert rules/channels, alert history, test notifications |
| `reporting_routes.py` | `/api` | PDF/Excel report generation and download |
| `websocket_routes.py` | `/api` | WebSocket endpoint for real-time PnL/position streaming |
| `schemas.py` | — | Pydantic request/response models for all endpoints |

### 2. IBKR Integration

Three complementary data paths connect to Interactive Brokers:

**a) Live TWS/Gateway connection** (`backend/ibkr_client.py`)

- Wraps `ib_insync` with automatic reconnection (exponential back-off up to 5 retries).
- Event-driven handlers for connect, disconnect, and error.
- Circuit breaker protection (`backend/circuit_breaker.py`) to avoid cascading failures when TWS is down.
- Methods: `connect`, `disconnect`, `get_account_summary`, `get_positions`, `get_pnl`, `place_order`.

**b) Flex Query Web Service** (`backend/flex_query_client.py`)

- Async client using aiohttp to call IBKR's Flex Query REST API.
- Two-phase flow: request statement → poll for result → parse XML/CSV response.
- Parses into typed dataclasses (`FlexTrade`, `FlexPosition`, `FlexQueryResult`).
- Query IDs and token configured in `config/app_config.yaml`.

**c) Flex / Portfolio Analyst CSV Import** (`backend/flex_importer.py`)

- Imports mark-to-market PnL CSV files into `pnl_history`.
- Imports trade execution history from Flex Query XML/CSV into the `trades` table.
- Calculates and backfills `daily_return` and `cumulative_return` columns.

**Broker abstraction** (`backend/broker_interface.py`): adapter pattern so the execution framework can target IBKR, a simulator, or future brokers through the same interface.

### 3. Database & Models

**ORM models** (`backend/models.py`) — 17 tables:

| Model | Table | Description |
|-------|-------|-------------|
| `AccountSnapshot` | `account_snapshots` | Point-in-time account values (NAV, cash, buying power, equity) |
| `Position` | `positions` | Snapshot of holdings with market value and unrealized PnL |
| `PnLHistory` | `pnl_history` | Daily PnL breakdown (realized, unrealized, MTM) with returns |
| `Trade` | `trades` | Trade executions with full detail (FX, options greeks, commission) |
| `PerformanceMetric` | `performance_metrics` | Computed risk-adjusted metrics (Sharpe, Sortino, drawdown, win rate) |
| `ExecutionOrder` | `execution_orders` | Orders from the strategy runner (paper/live/sim) |
| `ExecutionFill` | `execution_fills` | Broker fills linked to orders |
| `RiskEvent` | `risk_events` | Risk engine events (blocks, warnings, kill-switch triggers) |
| `User` | `users` | User accounts with hashed passwords |
| `UserAccount` | `user_accounts` | Links users to IBKR account IDs |
| `UserPreferences` | `user_preferences` | Theme, timezone, notification settings |
| `APIKey` | `api_keys` | Hashed API keys for programmatic access |
| `Role` / `UserRole` | `roles` / `user_roles` | RBAC role definitions and assignments |
| `AuditLog` | `audit_logs` | Audit trail for user actions |
| `AlertRule` | `alert_rules` | Configurable alert rule definitions |
| `Alert` | `alerts` | Triggered alert instances with status tracking |
| `AlertHistory` | `alert_history` | Historical audit of alert lifecycle events |
| `AlertChannel` | `alert_channels` | Notification channel configurations |

**Database utilities** (`backend/db_utils.py`): CLI interface for importing Flex data, querying trades, viewing daily PnL, and running ad-hoc SQL from the command line.

**Time-series DB** (`backend/timeseries_db.py`): abstraction layer supporting TimescaleDB and InfluxDB for high-frequency time-range queries.

### 4. Frontend Dashboard

**Technology:** Plotly Dash with Dash Bootstrap Components (Cyborg dark theme), custom CSS.

**Entry point:** `frontend/app.py` — a single-page app with tab-based navigation.

**Pages:**

| Tab | Content |
|-----|---------|
| **Portfolio** | Metric cards (NAV, daily PnL, total return, Sharpe), account value time-series chart |
| **Performance** | Cumulative return chart with S&P 500 overlay, drawdown chart, risk metrics panel |
| **Positions** | Interactive table of current holdings with unrealized PnL and sector breakdown |
| **History** | Filterable/sortable trade history table with date range and symbol filters |
| **Markets** | Cross-asset dashboard: rates (UST curve, TIPS, inflation), FX (G10 + DXY), equities (global indices + VIX), commodities (energy + metals). Yield curve / forward rate charts, Fed QE/QT monitor, macro pulse. All tables include 30-day sparklines, 1W/1M change columns, and click-to-expand 1Y historical charts |
| **Data** | Data Manager: catalog of stored Parquet datasets, pull form (yfinance/FRED, ticker/date selection), data viewer with time-series chart and table preview. "Update All" for incremental backfill |

**Components** (`frontend/components/`):

- `charts.py` — reusable Plotly chart builders
- `metrics_cards.py` — KPI card layout
- `performance_metrics.py` — risk metric displays
- `pnl_chart.py` — PnL waterfall and time-series charts
- `positions_table.py` — positions data table
- `trade_history.py` — trade log component
- `market_panels.py` — Markets tab: sparklines, rate/FX/equity/commodity panels, curves, Fed QE/QT monitor
- `data_manager.py` — Data Manager tab: catalog table, pull form, data viewer

**Real-time:** `frontend/websocket_client.py` and `frontend/realtime_integration.js` connect to the backend WebSocket for live PnL/position updates.

### 5. Portfolio Construction

The `portfolio/` package implements a research-to-execution pipeline:

**Signal blending** (`portfolio/blend.py`):
- `Signal` dataclass carrying per-asset scores with a weight.
- `blend_signals()` z-scores each signal and produces a weighted composite alpha.

**Optimization** (`portfolio/optimizer.py`):
- Solves a convex program via cvxpy: maximize expected return minus risk penalty minus turnover penalty.
- Constraints: fully invested (sum = 1), per-asset weight bounds, optional gross exposure limit.
- `weights_from_alpha()` convenience function to go from alpha scores to optimal weights in one call.

**Risk models** (`portfolio/risk.py`):
- Sample covariance and Ledoit-Wolf shrinkage estimators.
- `StressScenario` for scenario-based PnL approximation.

**Risk analytics** (`portfolio/risk_analytics.py`):
- Extended risk calculations for VaR, CVaR, factor exposures.

**Advanced analytics** (`portfolio/advanced_analytics.py`):
- Extended analytics for portfolio-level metrics.

**Rebalancer** (`portfolio/rebalancer.py`):
- Automated rebalancing with configurable drift threshold, minimum interval, and dry-run mode.
- Computes target weights, diffs against current positions, generates orders, and routes them through the execution runner.

**Backend analytics** (`backend/advanced_analytics.py`):
- `PortfolioOptimizer` with four strategies: Markowitz, risk parity, Black-Litterman, minimum variance.
- `MonteCarloSimulator` for forward-looking return distribution estimation.
- `FactorAnalyzer` for PCA-based factor decomposition of returns.

### 6. Backtesting Engine

Two backtesting modes in the `backtests/` package:

**a) Vectorized** (`backtests/vectorized.py`) — for fast alpha research:
- `VectorStrategy` protocol: implement `generate_positions(bars) -> Series`.
- `run_vectorized_backtest()` applies position shift (execution delay), turnover-based cost model, slippage model.
- Returns `BacktestResult` with equity curve, net returns, positions, turnover, and summary stats (Sharpe, max drawdown, total return).

**b) Event-driven** (`backtests/event_driven/engine.py`) — for realistic simulation:
- Queue-based engine processing `MarketEvent` → `SignalEvent` → `OrderEvent` → `FillEvent`.
- `PortfolioState` tracks cash and positions.
- Extensible: override `on_market()` and `on_signal()` to implement custom strategies.

**Metrics** (`backtests/metrics.py`): `annualized_sharpe`, `max_drawdown`, `total_return`.

**Core types** (`backtests/core.py`): `CostModel`, `SlippageModel`, `BacktestResult`.

**QuantConnect / Lean** (`qc_lean/`): local Lean engine installation with .NET SDK for running QuantConnect algorithms. Includes a `MomentumDemoAlgorithm.py` example and results output.

### 7. Execution Framework

The `execution/` package bridges backtesting signals to real/paper trading:

**Types** (`execution/types.py`): `OrderRequest`, `Fill` dataclasses.

**Risk engine** (`execution/risk.py`):
- Pre-trade checks: max position notional, max gross notional, max daily loss, environment kill switch.
- Returns `RiskDecision(allowed, reason, context)`.

**Broker interface** (`execution/broker.py`): abstract `Broker` protocol + `IBKRBroker` implementation.

**Simulated broker** (`execution/sim_broker.py`): in-memory order matching for paper trading.

**Runner** (`execution/runner.py`):
- `ExecutionRunner` takes a broker, price getter, and risk engine.
- `submit_orders()`: validates each order through risk engine, submits to broker, records to DB.
- `poll_and_record_fills()`: fetches fills from broker and writes to `execution_fills`.

**Audit** (`execution/audit.py`): `record_order()`, `record_fill()`, `record_risk_event()` persist every action to the database for compliance and debugging.

### 8. Quantitative Data Lake

The `quant_data/` package provides a vendor-agnostic research data layer:

**Canonical schema** (`quant_data/spec.py`):
- Enums for `DatasetLayer` (raw/clean/features), `DatasetFrequency`, `MarketDataKind`.
- Standardized column definitions for bars, trades, and quotes.
- `DatasetId` for partition-path generation: `{provider}/{kind}/{universe}/{frequency}`.

**Connectors** (`quant_data/connectors/`):

| Connector | Source | Data |
|-----------|--------|------|
| `stooq.py` | Stooq.com | Free daily OHLCV (global equities) |
| `polygon.py` | Polygon.io | Paid tick/bar data |
| `binance_public.py` | Binance REST | Public klines (crypto) |
| `ecb_fx.py` | ECB Data API | EUR-based daily FX rates |

**Storage:**
- `parquet_writer.py` — writes normalized DataFrames to Parquet with date partitioning.
- `duckdb_store.py` — creates DuckDB views over Parquet globs for fast ad-hoc SQL.
- `meta_db.py` / `meta_models.py` — metadata catalog tracking ingested datasets.

**Pipelines** (`quant_data/pipelines/ingest_bars.py`): orchestrates fetch → normalize → validate → write for bar data.

**Configuration** (`quant_data/qconfig.py`): `QuantDataSettings` loaded from environment variables, defining paths and DuckDB location.

### 9. Alert & Notification System

**Alert engine** (`backend/alert_engine.py`):
- Evaluates all enabled `AlertRule` records on a schedule.
- Rule types: `PNL_THRESHOLD`, `POSITION_SIZE`, `DRAWDOWN`, `VOLATILITY`, `CORRELATION`.
- Respects per-rule cooldown to prevent duplicate alerts.
- Supports escalation after a configurable timeout.

**Alert scheduler** (`backend/alert_scheduler.py`): APScheduler job that periodically calls `alert_engine.evaluate_all_rules()`.

**Notification channels** (`backend/notifications.py`):

| Channel | Implementation |
|---------|---------------|
| Email | smtplib with MIME formatting |
| SMS | Twilio SDK |
| Slack | Incoming webhook via aiohttp |
| Microsoft Teams | Incoming webhook via aiohttp |
| Webhook | Generic HTTP POST with custom headers |
| Web Push | pywebpush with VAPID keys |

**Models:** `AlertRule`, `Alert`, `AlertHistory`, `AlertChannel` (see [Database & Models](#3-database--models)).

### 10. Reporting & Export

**PDF reports** (`backend/reporting.py`):
- `ReportGenerator` builds multi-page PDF documents using ReportLab.
- Sections: title page, account summary table, PnL breakdown, performance metrics, trade history.
- Custom paragraph styles for professional formatting.

**Excel export** (`backend/export.py`):
- `export_trades_excel()`, `export_performance_excel()`, `export_pnl_excel()` — single-concern exports.
- `export_combined_report()` — multi-sheet workbook with trades, positions, PnL, and performance.
- Date/symbol filtering on all exports.

**API routes** (`backend/api/reporting_routes.py`): endpoints return `StreamingResponse` with correct content type and filename headers.

### 11. Observability

| Concern | Module | Details |
|---------|--------|---------|
| **Metrics** | `backend/metrics.py` | Prometheus client; `/metrics` endpoint for scraping |
| **Logging** | `backend/logging_config.py` | Configurable structured JSON or plaintext logging |
| **Error tracking** | `backend/error_tracking.py` | Sentry SDK integration (optional, via `SENTRY_DSN`) |
| **Tracing** | `backend/tracing.py` | OpenTelemetry with OTLP exporter; instruments FastAPI and SQLAlchemy |
| **Circuit breaker** | `backend/circuit_breaker.py` | Protects IBKR calls; states: closed → open → half-open |
| **Caching** | `backend/cache.py` | Redis-backed cache manager with TTL; `@cached` decorator for endpoints |
| **Health checks** | `backend/main.py` | `/health`, `/api/health`, `/api/health/detailed` (DB, IBKR, cache, alerts status) |
| **Real-time** | `backend/websocket_manager.py` / `backend/realtime_broadcaster.py` | WebSocket connection manager with pub/sub channels |

### 12. Research Notebooks

| Notebook | Purpose |
|----------|---------|
| `notebooks/analysis.ipynb` | Exploratory data analysis on account and trade data |
| `notebooks/pnl_query_tutorial.ipynb` | Tutorial for querying PnL history with advanced filters and visualizations |
| `notebooks/qc_lean_momentum_demo.ipynb` | QuantConnect Lean momentum strategy backtest demo |
| `notebooks/test_connection.py` | Quick IBKR connection smoke test |

**Research experiments** (`research/experiments/`):
- `run_example_momentum.py` — end-to-end momentum strategy using the vectorized backtest engine.
- `run_example_portfolio_opt.py` — portfolio optimization example using the portfolio package.

### 13. Automation Scripts

| Script | Purpose |
|--------|---------|
| `scripts/init_db.py` | Initialize database tables |
| `scripts/automate_pa_daily.py` | Download IBKR Portfolio Analyst CSV and import to DB |
| `scripts/download_portfolio_analyst.py` | Playwright-based browser automation to download PA reports |
| `scripts/import_portfolio_analyst.py` | Import a PA CSV file into `pnl_history` |
| `scripts/pa_scheduler.py` | Cron-like daily scheduler for PA automation |
| `scripts/setup_ibkr.py` | Interactive IBKR connection setup helper |
| `scripts/backfill_mtm_from_csv.py` | Backfill mark-to-market data from CSV files |
| `scripts/recalculate_returns.py` | Recalculate daily/cumulative returns across all records |
| `scripts/add_returns_columns_to_pnl_history.py` | Migration: add return columns to existing data |
| `scripts/query_pnl_example.py` | Example PnL query script |
| `scripts/ingest_binance_bars.py` | Ingest crypto bars from Binance into the data lake |
| `scripts/ingest_stooq_bars.py` | Ingest equity bars from Stooq into the data lake |
| `scripts/init_quant_data_meta_db.py` | Initialize the quant data metadata database |
| `scripts/qc_build_equity_daily.py` | Build daily equity curves from QuantConnect results |
| `scripts/qc_plot_backtest.py` | Plot QuantConnect backtest results |
| `scripts/run_paper_trader.py` | Start the paper trading execution runner |
| `start_scheduler.py` | Start the PnL data fetch scheduler |
| `test_ibkr_connection.py` | Test IBKR TWS/Gateway connectivity |

---

## API Endpoints

### Authentication
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, receive JWT |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/auth/me` | Get current user profile |
| POST | `/api/auth/api-keys` | Create API key |

### Account & Portfolio
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/account/summary` | Latest account snapshot |
| GET | `/api/positions` | Current positions |
| GET | `/api/pnl` | PnL history with date filters |
| GET | `/api/pnl/timeseries` | PnL time-series for charting |
| GET | `/api/performance` | Performance metrics |
| GET | `/api/trades` | Trade history with filters |
| POST | `/api/fetch-data` | Trigger live data fetch from IBKR |

### Flex Query
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/flex-query/status` | Check Flex Query configuration |
| POST | `/api/flex-query/fetch-all-reports` | Fetch all configured reports |

### Advanced Analytics
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/analytics/optimize` | Run portfolio optimization |
| POST | `/api/analytics/monte-carlo` | Monte Carlo simulation |
| POST | `/api/analytics/factor-analysis` | Factor decomposition |
| GET | `/api/analytics/correlation` | Correlation matrix |
| POST | `/api/analytics/stress-test` | Stress testing |
| POST | `/api/analytics/regime-detection` | Market regime detection |

### Alerts
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/alerts/rules` | Create alert rule |
| GET | `/api/alerts/rules` | List alert rules |
| PUT | `/api/alerts/rules/{id}` | Update alert rule |
| GET | `/api/alerts` | List triggered alerts |
| POST | `/api/alerts/channels` | Create notification channel |
| POST | `/api/alerts/test` | Send test notification |

### Reporting & Export
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/export/trades` | Export trades to Excel |
| GET | `/api/export/performance` | Export performance to Excel |
| GET | `/api/export/pnl` | Export PnL to Excel |
| GET | `/api/export/report` | Combined multi-sheet report |
| GET | `/api/report/pdf` | Generate PDF report |

### WebSocket
| Path | Description |
|------|-------------|
| `/api/ws/{connection_id}` | Real-time PnL and position updates |

### Market Data
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/market/overview` | Combined snapshot of all market panels |
| GET | `/api/market/rates` | UST yields, FRED rates, spreads |
| GET | `/api/market/fx` | G10 FX spot prices |
| GET | `/api/market/equities` | Major equity indices and VIX |
| GET | `/api/market/commodities` | Energy and metals prices |
| GET | `/api/market/macro` | FRED macro indicators |
| GET | `/api/market/what-changed` | Cross-asset z-score movers |
| GET | `/api/market/curves` | Yield curve, forward rates |
| GET | `/api/market/fed-liquidity` | Fed balance sheet / QE-QT monitor |
| GET | `/api/market/cb-meetings` | Central bank meeting tracker (FOMC countdown, policy rates, implied path) |
| GET | `/api/market/sparklines` | Batch 30-day sparkline data |
| GET | `/api/market/historical/{symbol}` | Historical daily closes (up to 1Y) |

### Data Management
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/data/catalog` | Metadata for all stored Parquet datasets |
| POST | `/api/data/pull` | Trigger a data download (yfinance or FRED) |
| GET | `/api/data/query` | Query stored time-series data |
| POST | `/api/data/update-all` | Incremental update of all tracked instruments |
| GET | `/api/data/pull-status/{job_id}` | Check status of a background pull job |

### System
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Basic health check |
| GET | `/api/health/detailed` | Component-level health (DB, IBKR, cache, alerts) |
| GET | `/metrics` | Prometheus metrics |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Conda (recommended) or virtualenv
- IBKR account with TWS or IB Gateway
- Docker (optional, for containerized deployment)

### 1. Create Environment

```bash
conda create -n ibkr-analytics python=3.10
conda activate ibkr-analytics
pip install -r requirements.txt

# For Portfolio Analyst browser automation
playwright install chromium
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your IBKR credentials and settings
```

Edit `config/app_config.yaml` with your IBKR connection and Flex Query settings.

### 3. Initialize Database

```bash
python scripts/init_db.py
```

### 4. Run

**Backend** (port 8000):
```bash
python backend/main.py
```

**Frontend** (port 8050):
```bash
python frontend/app.py
```

Or use Docker:
```bash
cd infrastructure && docker-compose up --build
```

Access:
- API docs: http://localhost:8000/docs
- Dashboard: http://localhost:8050

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `IBKR_HOST` | `127.0.0.1` | TWS/Gateway host |
| `IBKR_PORT` | `7497` | TWS/Gateway port (7497 paper, 7496 live) |
| `IBKR_CLIENT_ID` | `1` | Client ID for API connection |
| `DB_URL` | `sqlite:///./ibkr_analytics.db` | Database connection string |
| `FLEX_TOKEN` | — | IBKR Flex Query Web Service token |
| `JWT_SECRET_KEY` | auto-generated | Secret for JWT signing |
| `JWT_EXPIRE_MINUTES` | `1440` | Token expiry (24h) |
| `SENTRY_DSN` | — | Sentry error tracking DSN |
| `TRACING_ENABLED` | `false` | Enable OpenTelemetry tracing |
| `OTLP_ENDPOINT` | — | OTLP collector endpoint |
| `LOG_FORMAT` | `text` | Set to `json` for structured logging |
| `POLYGON_API_KEY` | — | Polygon.io API key |
| `KILL_SWITCH` | — | Set to `true` to halt all order submission |

### Configuration Files

| File | Purpose |
|------|---------|
| `config/app_config.yaml` | IBKR connection, Flex Query IDs, database URL, app settings |
| `.env` | Secrets and environment-specific overrides |
| `pyrightconfig.json` | Python type checker configuration |
| `environment.yml` | Conda environment specification |

---

## Docker Deployment

```bash
# Copy and edit environment
cp infrastructure/.env.example infrastructure/.env

# Build and run
cd infrastructure
docker-compose up --build
```

Services:
- `backend` — FastAPI on port 8000
- `frontend` — Dash on port 8050
- PostgreSQL available as an optional service (uncomment in `docker-compose.yml`)

A research-focused `docker-compose.research.yml` is also available for Jupyter-based workflows.

---

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=backend --cov=portfolio --cov=backtests --cov=execution

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/
```

**Test modules:**

| File | Coverage |
|------|----------|
| `tests/unit/test_vectorized_backtest.py` | Vectorized backtest engine |
| `tests/unit/test_optimizer.py` | Portfolio optimizer (cvxpy) |
| `tests/unit/test_portfolio_blend.py` | Signal blending |
| `tests/unit/test_risk.py` | Risk model (covariance, stress) |
| `tests/unit/test_execution_risk.py` | Pre-trade risk checks |
| `tests/unit/test_data_processor.py` | Performance metric calculations |
| `tests/unit/test_blend.py` | Alpha blending |
| `tests/unit/test_portfolio_optimizer.py` | Markowitz/risk parity |
| `tests/integration/test_api_routes.py` | FastAPI route integration |
| `tests/conftest.py` | Shared fixtures |

---

## Project Structure

```
Invest_strategy/
├── backend/                    # FastAPI backend service
│   ├── api/                    # Route handlers and schemas
│   │   ├── routes.py           # Core API routes
│   │   ├── auth_routes.py      # Authentication endpoints
│   │   ├── backtest_routes.py  # Backtest endpoints
│   │   ├── advanced_analytics_routes.py
│   │   ├── alert_routes.py     # Alert CRUD
│   │   ├── reporting_routes.py # Report generation
│   │   ├── websocket_routes.py # WebSocket endpoint
│   │   └── schemas.py          # Pydantic models
│   ├── main.py                 # FastAPI app entry point
│   ├── models.py               # SQLAlchemy ORM models
│   ├── database.py             # DB engine and session
│   ├── config.py               # Settings from YAML + env
│   ├── ibkr_client.py          # IBKR TWS/Gateway client
│   ├── flex_query_client.py    # Flex Query Web Service client
│   ├── flex_importer.py        # CSV/XML import logic
│   ├── flex_parser.py          # Flex response parsing
│   ├── db_utils.py             # CLI database utilities
│   ├── data_fetcher.py         # Live data fetching
│   ├── data_processor.py       # Performance calculations
│   ├── data_providers.py       # Market data provider interface
│   ├── benchmark_service.py    # S&P 500 benchmark data
│   ├── advanced_analytics.py   # Optimization, Monte Carlo, factor analysis
│   ├── auth.py                 # JWT + API key authentication
│   ├── broker_interface.py     # Broker adapter pattern
│   ├── alert_engine.py         # Alert rule evaluation
│   ├── alert_scheduler.py      # Scheduled alert checks
│   ├── notifications.py        # Multi-channel notification dispatch
│   ├── reporting.py            # PDF report generation
│   ├── export.py               # Excel export
│   ├── cache.py                # Redis caching layer
│   ├── circuit_breaker.py      # Circuit breaker pattern
│   ├── websocket_manager.py    # WebSocket connection manager
│   ├── realtime_broadcaster.py # Real-time data broadcasting
│   ├── scheduler.py            # PnL fetch scheduler
│   ├── timeseries_db.py        # TimescaleDB / InfluxDB abstraction
│   ├── middleware.py           # Request metrics middleware
│   ├── rate_limiter.py         # Rate limiting
│   ├── metrics.py              # Prometheus metrics
│   ├── logging_config.py       # Structured logging setup
│   ├── error_tracking.py       # Sentry integration
│   ├── tracing.py              # OpenTelemetry tracing
│   └── validators.py           # Input validation
│
├── frontend/                   # Plotly Dash dashboard
│   ├── app.py                  # Dash application
│   ├── websocket_client.py     # WebSocket client
│   ├── realtime_integration.js # JS WebSocket handler
│   ├── assets/custom.css       # Custom styles
│   └── components/             # Reusable UI components
│       ├── charts.py
│       ├── metrics_cards.py
│       ├── performance_metrics.py
│       ├── pnl_chart.py
│       ├── positions_table.py
│       └── trade_history.py
│
├── portfolio/                  # Portfolio construction library
│   ├── optimizer.py            # cvxpy mean-variance optimizer
│   ├── blend.py                # Signal blending
│   ├── risk.py                 # Covariance estimation, stress tests
│   ├── risk_analytics.py       # Extended risk analytics
│   ├── rebalancer.py           # Automated rebalancing
│   └── advanced_analytics.py   # Portfolio-level analytics
│
├── backtests/                  # Backtesting engines
│   ├── core.py                 # Core types (CostModel, BacktestResult)
│   ├── vectorized.py           # Fast vectorized backtester
│   ├── metrics.py              # Sharpe, drawdown, total return
│   └── event_driven/           # Event-driven backtester
│       ├── engine.py           # Queue-based engine
│       └── events.py           # Event type definitions
│
├── execution/                  # Trade execution framework
│   ├── runner.py               # Paper/live execution runner
│   ├── risk.py                 # Pre-trade risk controls
│   ├── broker.py               # Broker interface
│   ├── sim_broker.py           # Simulated broker
│   ├── audit.py                # Order/fill audit trail
│   └── types.py                # OrderRequest, Fill types
│
├── quant_data/                 # Research data lake
│   ├── spec.py                 # Canonical dataset schemas
│   ├── connectors/             # Market data connectors
│   │   ├── stooq.py            # Stooq (free daily OHLCV)
│   │   ├── polygon.py          # Polygon.io (paid)
│   │   ├── binance_public.py   # Binance (crypto)
│   │   └── ecb_fx.py           # ECB FX rates
│   ├── pipelines/              # Data ingestion pipelines
│   │   └── ingest_bars.py
│   ├── io/parquet_writer.py    # Parquet output
│   ├── duckdb_store.py         # DuckDB SQL layer
│   ├── meta_db.py              # Metadata catalog
│   └── qconfig.py              # Data lake settings
│
├── qc_lean/                    # QuantConnect Lean engine
│   ├── MomentumDemoAlgorithm.py
│   ├── config.json
│   ├── Data/                   # Market hours database
│   ├── Results/                # Backtest output
│   └── Lean/                   # Lean engine (submodule)
│
├── research/                   # Research experiments
│   └── experiments/
│       ├── run_example_momentum.py
│       └── run_example_portfolio_opt.py
│
├── scripts/                    # Utility and automation scripts
├── notebooks/                  # Jupyter notebooks
├── tests/                      # Unit and integration tests
├── infrastructure/             # Docker configuration
│   ├── docker-compose.yml
│   ├── docker-compose.research.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── Dockerfile.research
├── config/                     # Application configuration
│   └── app_config.yaml
├── guides/                     # User guides
│   ├── DATABASE_GUIDE.md
│   ├── FLEX_QUERY_SETUP.md
│   ├── IBKR_SETUP_GUIDE.md
│   ├── PA_AUTOMATION_SETUP.md
│   ├── ADVANCED_ANALYTICS_USAGE.md
│   ├── ALERT_SETUP_GUIDE.md
│   ├── EMAIL_ALERT_SETUP.md
│   ├── ML_FEATURES_USAGE.md
│   └── PNL_QUERY_GUIDE.md
├── docs/                       # Technical specifications
├── data_lake/                  # Parquet data storage
├── requirements.txt
├── environment.yml
├── .env.example
└── .gitignore
```

---

## Security

- Secrets (tokens, passwords, API keys) are loaded from `.env` and never committed (`.env` is in `.gitignore`).
- JWT authentication with bcrypt password hashing.
- API key authentication with SHA-256 hashing (only prefix stored in plaintext).
- Role-based access control (admin, viewer, trader, analyst).
- Audit logging for all user actions.
- Rate limiting on all API endpoints.
- IBKR credentials stay local — the app connects to TWS/Gateway on `127.0.0.1`.

---

## Documentation Guides

| Guide | Description |
|-------|-------------|
| [DATABASE_GUIDE.md](guides/DATABASE_GUIDE.md) | Database queries, P&L analysis, sample code |
| [FLEX_QUERY_SETUP.md](guides/FLEX_QUERY_SETUP.md) | Setting up IBKR Flex Queries |
| [IBKR_SETUP_GUIDE.md](guides/IBKR_SETUP_GUIDE.md) | TWS/Gateway configuration |
| [PA_AUTOMATION_SETUP.md](guides/PA_AUTOMATION_SETUP.md) | Portfolio Analyst download automation |
| [ADVANCED_ANALYTICS_USAGE.md](guides/ADVANCED_ANALYTICS_USAGE.md) | Optimization, Monte Carlo, factor analysis |
| [ALERT_SETUP_GUIDE.md](guides/ALERT_SETUP_GUIDE.md) | Alert rules and notification channels |
| [EMAIL_ALERT_SETUP.md](guides/EMAIL_ALERT_SETUP.md) | Email notification configuration |
| [ML_FEATURES_USAGE.md](guides/ML_FEATURES_USAGE.md) | Machine learning features |
| [PNL_QUERY_GUIDE.md](guides/PNL_QUERY_GUIDE.md) | P&L querying guide |

---

## License

This project is for personal use. Please ensure compliance with IBKR API terms of service.
