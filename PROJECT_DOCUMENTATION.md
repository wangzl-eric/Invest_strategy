# IBKR Analytics Platform - Comprehensive User Guide

This document provides a complete overview of the investment strategy platform, covering all features, infrastructure, and workflows.

---

## Table of Contents

1. [Platform Overview](#1-platform-overview)
2. [Core Components](#2-core-components)
3. [Data Flow & Storage](#3-data-flow--storage)
4. [API Reference](#4-api-reference)
5. [Configuration](#5-configuration)
6. [Getting Started Workflows](#6-getting-started-workflows)
7. [Infrastructure](#7-infrastructure)
8. [Key Scripts](#8-key-scripts)
9. [Directory Structure Summary](#9-directory-structure-summary)
10. [Troubleshooting](#10-troubleshooting)
11. [Related Documentation](#11-related-documentation)

---

## 1. Platform Overview

This is a **full-stack quantitative analytics platform** for Interactive Brokers (IBKR) account management, backtesting, and strategy deployment.

### Key Features

- **Account Data Fetching**: Automated connection to IBKR TWS/Gateway API
- **Data Storage**: Historical snapshots of account state, positions, PnL, and trades
- **Performance Analytics**: Calculate returns, Sharpe ratio, Sortino ratio, maximum drawdown, and trade statistics
- **Interactive Dashboard**: Web-based visualization with real-time updates
- **Scheduled Updates**: Automatic intraday data refresh at configurable intervals
- **Backtesting**: Both Backtrader (event-driven) and research backtesting
- **QuantConnect Lean**: Professional-grade backtesting engine integration
- **Portfolio Optimization**: Mean-variance optimization with CVXPY
- **Execution Framework**: Paper/live trading with risk controls
- **Market Data Infrastructure**: Standardized pipelines for multi-source data

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCES                                    │
├─────────────────────┬─────────────────────┬─────────────────────────────────┤
│  IBKR TWS/Gateway   │  IBKR Flex Query    │  External Data                  │
│  (Real-time API)    │  (Historical Web)   │  (Stooq/Binance/Polygon)        │
└─────────┬───────────┴─────────┬───────────┴─────────────┬───────────────────┘
          │                     │                         │
          ▼                     ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND SERVICES                                   │
├─────────────────────┬─────────────────────┬─────────────────────────────────┤
│  FastAPI Server     │  APScheduler        │  Data Processor                 │
│  (port 8000)        │  (Periodic Fetch)   │  (Performance Calc)             │
└─────────┬───────────┴─────────────────────┴─────────────┬───────────────────┘
          │                                               │
          ▼                                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA STORAGE                                       │
├─────────────────────┬─────────────────────┬─────────────────────────────────┤
│  SQLite/PostgreSQL  │  Parquet Data Lake  │  DuckDB                         │
│  (Account Data)     │  (Market Data)      │  (Fast SQL Queries)             │
└─────────┬───────────┴─────────┬───────────┴─────────────────────────────────┘
          │                     │
          ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      RESEARCH & BACKTESTING                                  │
├─────────────────────┬─────────────────────┬─────────────────────────────────┤
│  Jupyter Notebooks  │  Vectorized BT      │  QuantConnect Lean              │
│                     │  (Fast Iteration)   │  (Production Grade)             │
│                     │                     │                                 │
│                     │  MLflow             │                                 │
│                     │  (Experiment Track) │                                 │
└─────────────────────┴─────────────────────┴─────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXECUTION                                          │
├─────────────────────┬─────────────────────┬─────────────────────────────────┤
│  Execution Runner   │  Risk Engine        │  Broker Interface               │
│  (Order Loop)       │  (Position Limits)  │  (IBKR/Simulator)               │
└─────────────────────┴─────────────────────┴─────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  Dash Dashboard (port 8050)                                                  │
│  - Portfolio Overview    - Performance Charts                                │
│  - Positions Table       - Trade History                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.10+, FastAPI, SQLAlchemy, ib_insync |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Data Processing** | pandas, numpy, DuckDB, PyArrow |
| **Scheduling** | APScheduler |
| **Frontend** | Plotly Dash, Bootstrap |
| **Optimization** | CVXPY, scipy |
| **ML/Experiments** | MLflow, scikit-learn |
| **Deployment** | Docker containers |

---

### Repository Layout

The repo is best understood as two primary product surfaces that share libraries:

| Surface | Main Paths | Purpose |
|---------|------------|---------|
| **Investment dashboard application** | `apps/dashboard/backend/`, `apps/dashboard/frontend/`, `data/` | broker/account workflows, APIs, UI, stored operational data |
| **Quant research workstation** | `workstation/backtests/`, `workstation/portfolio/`, `workstation/execution/`, `workstation/quant_data/`, `workstation/research/`, `workstation/notebooks/` | ingestion, strategy research, backtesting, optimization, paper-trading prep |
| **Optional extensions** | `extensions/cerebro/`, `qc_lean/` | separate research tooling and external-engine experiments |

Legacy root paths such as `backend/`, `frontend/`, `backtests/`, and `quant_data/` are currently kept as compatibility symlinks.

Important distinctions:

- `data/` stores files. `quant_data/` is the Python package that manages those files.
- `backtests/` is the research framework. `workstation/backtests/event_driven/backtest_engine.py` is the canonical event-driven execution adapter, and `backend/backtest_engine.py` is kept as a compatibility shim.
- `qc_lean/` is an optional local Lean workspace, not part of the core Python package graph.

See `docs/repo_layout.md` for the maintained stack map.

---

## 2. Core Components

### 2.1 Backend API (`backend/`)

**Technology**: FastAPI + SQLAlchemy + APScheduler

**Entry Point**: `backend/main.py` starts the API server on port 8000

**Key Modules**:

| Module | Description |
|--------|-------------|
| `ibkr_client.py` | IBKR TWS/Gateway connection using `ib_insync` |
| `data_fetcher.py` | Fetches account data, positions, trades from IBKR |
| `data_processor.py` | Calculates Sharpe, Sortino, drawdown, returns |
| `flex_query_client.py` | IBKR Flex Query Web Service client |
| `flex_parser.py` | Parses XML Flex Query responses |
| `flex_importer.py` | Imports Flex data to database with deduplication |
| `scheduler.py` | APScheduler for periodic data refresh |
| `models.py` | SQLAlchemy ORM models |
| `db_utils.py` | CLI utilities for database operations |
| `export.py` | Excel export functionality |
| `validators.py` | Data validation helpers |
| `metrics.py` | Prometheus metrics |
| `middleware.py` | Request logging middleware |

**API Routes** (`backend/api/`):
- `routes.py` - Main API endpoints (account, positions, trades, etc.)
- `backtest_routes.py` - Backtesting endpoints
- `schemas.py` - Pydantic request/response schemas

### 2.2 Frontend Dashboard (`frontend/`)

**Technology**: Plotly Dash + Bootstrap (CYBORG dark theme)

**Entry Point**: `frontend/app.py` starts the dashboard on port 8050

**Dashboard Tabs**:

| Tab | Description |
|-----|-------------|
| **Portfolio** | Asset allocation pie chart, top 10 holdings list |
| **Performance** | Equity curve over time, cumulative P&L bar chart |
| **Positions** | Detailed positions grouped by asset class (STK, OPT, etc.) |
| **History** | Recent trade executions with side, qty, price, commission |

**Components** (`frontend/components/`):
- `performance_metrics.py` - Risk/return metric cards
- `pnl_chart.py` - P&L visualization
- `positions_table.py` - Positions data table
- `trade_history.py` - Trade history table

**Features**:
- Auto-refresh every 5 minutes
- Manual refresh button
- Flex Query fetch button
- Connection status indicator
- Dark mode UI with gradient styling

### 2.3 Backtesting Framework (`backtests/`)

Two complementary layers are available:

| Layer | File(s) | Use Case |
|-------|---------|----------|
| **Research framework** | `backtests/builder.py`, `backtests/walkforward.py`, `backtests/stats/` | portfolio research, walk-forward validation, statistical tests |
| **Event-driven engine** | `workstation/backtests/event_driven/backtest_engine.py` | Backtrader-based simulation with execution realism |

#### Using BacktestEngine (Backtrader)

For event-driven backtesting with realistic order execution:

```python
from backend.backtest_engine import BacktestEngine, IBKRDataFeed
import backtrader as bt

# Define a strategy
class MyStrategy(bt.Strategy):
    params = (('period', 20),)

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.period
        )

    def next(self):
        if self.data.close[0] > self.sma[0]:
            self.buy()
        else:
            self.sell()

# Run backtest
engine = BacktestEngine(cash=100000, commission=0.001)
engine.add_data(IBKRDataFeed(dataname=df), name='ASSET')
engine.add_strategy(MyStrategy)
result = engine.run_backtest()

print(f"Return: {result['total_return']*100:.2f}%")
print(f"Sharpe: {result['sharpe_ratio']:.2f}")
```

**Features**:
- Realistic order execution simulation
- Multiple data feeds support
- Position tracking and analytics
- Full Backtrader feature set

#### Core Types (`backtests/core.py`)

```python
@dataclass(frozen=True)
class BacktestResult:
    equity: pd.Series      # Cumulative equity curve
    returns: pd.Series     # Daily net returns
    positions: pd.Series   # Position time series
    turnover: pd.Series    # Daily turnover
    stats: Dict[str, float]  # Performance statistics
    metadata: Dict[str, str]
```

### 2.4 QuantConnect Lean Integration (`qc_lean/`)

Optional QuantConnect Lean integration for local experimentation. Treat this directory as an isolated external-engine workspace:

**Directory Structure**:
```
qc_lean/
├── Lean/                    # Lean engine source / vendor subtree
├── Data/                    # Lean-formatted market data
├── Results/                 # Generated backtest output
├── config.json              # Lean configuration
├── MomentumDemoAlgorithm.py # Example strategy
└── .dotnet/                 # Local .NET runtime
```

**Example Strategy** (`MomentumDemoAlgorithm.py`):

```python
from AlgorithmImports import *

class MomentumDemoAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2018, 1, 1)
        self.SetEndDate(2024, 12, 31)
        self.SetCash(100000)

        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.roc = self.ROC(self.symbol, 63, Resolution.Daily)  # 3-month momentum
        self.SetWarmUp(63, Resolution.Daily)

    def OnData(self, data):
        if self.IsWarmingUp or not self.roc.IsReady:
            return

        target = 1.0 if self.roc.Current.Value > 0 else 0.0
        self.SetHoldings(self.symbol, target)
```

**Notebook Demo**: `notebooks/qc_lean_momentum_demo.ipynb`
- Running Lean backtests from Python
- Loading results JSON
- Plotting equity curves and drawdowns
- Extracting performance statistics

### 2.5 Portfolio Optimization (`portfolio/`)

**Mean-Variance Optimizer** (`portfolio/optimizer.py`):

```python
from portfolio.optimizer import mean_variance_optimize, OptimizationConfig

cfg = OptimizationConfig(
    risk_aversion=1.0,      # Higher = more risk penalty
    turnover_aversion=0.01, # L1 turnover penalty
    max_weight=0.10,        # Max 10% per asset
    min_weight=-0.10,       # Allow 10% short
    target_gross=1.5,       # Max 150% gross exposure
)

weights = mean_variance_optimize(
    expected_returns=alpha_series,
    cov=covariance_matrix,
    prev_weights=current_weights,
    cfg=cfg,
)
```

**Features**:
- CVXPY convex optimization
- Constraints: max/min weights, gross exposure
- Turnover aversion penalty (reduces trading costs)
- Covariance estimation: Ledoit-Wolf shrinkage or sample cov

**Risk Module** (`portfolio/risk.py`):
- `ledoit_wolf_cov()` - Shrinkage estimator for stable covariance
- `sample_cov()` - Sample covariance matrix

**Blending** (`portfolio/blend.py`):
- Combine multiple alpha signals

**Rebalancing** (`portfolio/rebalancer.py`):
- Convert target weights to orders

### 2.6 Execution Framework (`execution/`)

For paper/live trading deployment:

| Module | Description |
|--------|-------------|
| `runner.py` | Main execution loop with risk checks |
| `risk.py` | Risk engine with position/loss limits |
| `broker.py` | Broker interface abstraction |
| `sim_broker.py` | Simulated broker for paper trading |
| `audit.py` | Records orders, fills, risk events to DB |
| `types.py` | Order/Fill data classes |

**Risk Engine** (`execution/risk.py`):

```python
@dataclass(frozen=True)
class RiskLimits:
    max_position_notional: float = 50_000.0   # Per symbol
    max_gross_notional: float = 250_000.0     # Total portfolio
    max_daily_loss: float = 2_500.0           # Daily loss limit
    kill_switch_env: str = "KILL_SWITCH"      # Emergency stop
```

**Execution Runner** (`execution/runner.py`):

```python
from execution.runner import ExecutionRunner, RunnerConfig
from execution.broker import IBKRBroker  # or SimBroker

runner = ExecutionRunner(
    broker=IBKRBroker(),
    price_getter=get_current_price,
    risk_engine=RiskEngine(RiskLimits()),
    cfg=RunnerConfig(mode="paper", account_id="DU12345"),
)

# Submit orders with automatic risk checks
order_ids = runner.submit_orders([
    OrderRequest(symbol="AAPL", side="BUY", quantity=100),
    OrderRequest(symbol="MSFT", side="SELL", quantity=50),
])
```

### 2.7 Quant Data Infrastructure (`quant_data/`)

**Purpose**: Standardized market data pipelines for research

**Modules**:

| Module | Description |
|--------|-------------|
| `spec.py` | Canonical dataset schemas and enums |
| `paths.py` | Path/partition helpers |
| `duckdb_store.py` | DuckDB interface for Parquet queries |
| `meta_db.py` | Metadata database |
| `registry.py` | Dataset registry |
| `qconfig.py` | Configuration settings |

**Canonical Schema** (from `spec.py`):

```python
# OHLCV Bars
CANONICAL_BARS_COLUMNS = (
    "timestamp",  # UTC
    "symbol",
    "venue",
    "currency",
    "open", "high", "low", "close",
    "volume",
    "vwap",  # optional
)

# Trades
CANONICAL_TRADES_COLUMNS = (
    "timestamp", "symbol", "venue",
    "price", "size", "side",
)

# Quotes
CANONICAL_QUOTES_COLUMNS = (
    "timestamp", "symbol", "venue",
    "bid", "bid_size", "ask", "ask_size",
)
```

**Data Lake Layers**:

| Layer | Description |
|-------|-------------|
| `raw/` | Vendor-native fields preserved |
| `clean/` | Standardized columns/dtypes/UTC |
| `features/` | Derived signals and factors |

**Connectors** (`quant_data/connectors/`):

| Connector | Data Source |
|-----------|-------------|
| `stooq.py` | Stooq (free global equities) |
| `binance_public.py` | Binance (crypto OHLCV) |
| `polygon.py` | Polygon.io (US equities) |
| `ecb_fx.py` | ECB FX rates |

**DuckDB Store** (`duckdb_store.py`):

```python
from quant_data.duckdb_store import connect, register_parquet_view

con = connect()
register_parquet_view(
    con,
    view_name="bars",
    parquet_glob="data_lake/clean/stooq/bars/us_equities/1d/**/*.parquet"
)

df = con.execute("""
    SELECT timestamp, symbol, close
    FROM bars
    WHERE symbol = 'AAPL'
    ORDER BY timestamp
""").df()
```

---

## 3. Data Flow & Storage

### 3.1 Database Models (`backend/models.py`)

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `account_snapshots` | Account value history | net_liquidation, total_cash_value, buying_power |
| `positions` | Position snapshots | symbol, quantity, avg_cost, market_value, unrealized_pnl |
| `pnl_history` | Daily P&L records | realized_pnl, unrealized_pnl, total_pnl |
| `trades` | Trade executions | symbol, side, shares, price, commission, realized_pnl |
| `performance_metrics` | Calculated metrics | sharpe_ratio, sortino_ratio, max_drawdown |
| `execution_orders` | Strategy orders | symbol, side, quantity, status |
| `execution_fills` | Order fills | fill_price, quantity, commission |
| `risk_events` | Risk engine events | severity, event_type, message |

### 3.2 Trade Table Schema

```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    account_id TEXT NOT NULL,
    exec_id TEXT UNIQUE NOT NULL,
    exec_time DATETIME NOT NULL,

    -- Contract
    symbol TEXT NOT NULL,
    sec_type TEXT,           -- STK, OPT, FUT
    currency TEXT,
    exchange TEXT,

    -- Execution
    side TEXT,               -- BUY, SELL
    shares FLOAT NOT NULL,
    price FLOAT NOT NULL,

    -- Costs
    commission FLOAT DEFAULT 0.0,
    taxes FLOAT DEFAULT 0.0,

    -- P&L
    realized_pnl FLOAT DEFAULT 0.0,
    realized_pnl_base FLOAT DEFAULT 0.0,  -- In base currency (HKD)
    fx_rate_to_base FLOAT DEFAULT 1.0,

    -- Options
    underlying TEXT,
    strike FLOAT,
    expiry TEXT,
    put_call TEXT,
    multiplier FLOAT DEFAULT 1.0
);
```

### 3.3 Data Sources

**IBKR TWS/Gateway API**:
- Real-time account data via `ib_insync`
- Requires TWS/Gateway running locally
- Ports: 7497 (paper) / 7496 (live)

**IBKR Flex Query**:
- Historical data via web service
- Multiple report types: trades, positions, cash, MTM
- Auto-imports to database with deduplication
- Saved to `data/flex_reports/{date}/{type}/`

**External Market Data**:
- Parquet files in `data_lake/`
- Ingestion scripts in `scripts/`

---

## 4. API Reference

### Health & Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint, returns API info |
| `/health` | GET | Basic health check |
| `/api/health` | GET | API health check |
| `/api/health/detailed` | GET | Detailed health with component status |
| `/metrics` | GET | Prometheus metrics |

### Account & Portfolio

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/account/summary` | GET | Latest account summary (NAV, cash, buying power) |
| `/api/positions` | GET | Current positions with market values |
| `/api/pnl` | GET | P&L history with pagination |
| `/api/pnl/history` | GET | Cleaned P&L time series for charts |
| `/api/trades` | GET | Trade history with filters |
| `/api/performance` | GET | Performance metrics (Sharpe, etc.) |
| `/api/fetch-data` | POST | Trigger manual IBKR data fetch |

**Query Parameters**:
- `account_id` - Filter by account
- `start_date`, `end_date` - Date range
- `symbol` - Filter by symbol (trades)
- `limit` - Max records (default 100)

### Flex Query

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/flex-query/status` | GET | Check Flex Query configuration |
| `/api/flex-query/fetch-all-reports` | POST | Fetch ALL configured reports |
| `/api/flex-query/fetch-trades` | POST | Fetch trade history only |
| `/api/flex-query/portfolio-summary` | GET | Portfolio summary from Flex |
| `/api/flex-query/fetch-all` | POST | Comprehensive data fetch |

### Risk Analytics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/risk/metrics` | GET | Comprehensive risk metrics |
| `/api/risk/var` | GET | Value at Risk (historical/parametric) |
| `/api/risk/cvar` | GET | Conditional VaR / Expected Shortfall |
| `/api/risk/stress-test` | GET | Stress test scenarios |

**Query Parameters**:
- `confidence_level` - VaR confidence (default 0.95)
- `method` - "historical" or "parametric"
- `scenarios` - Comma-separated shock percentages

### Export

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/export/trades` | GET | Export trades to Excel |
| `/api/export/performance` | GET | Export performance to Excel |
| `/api/export/pnl` | GET | Export P&L to Excel |
| `/api/export/report` | GET | Combined multi-sheet report |

---

## 5. Configuration

### 5.1 Main Config (`config/app_config.yaml`)

```yaml
# IBKR TWS/Gateway Connection
ibkr:
  host: "127.0.0.1"
  port: 7497        # 7497=paper, 7496=live
  client_id: 1
  timeout: 30

# Flex Query Web Service
flex_query:
  # Token via FLEX_TOKEN env var (don't store in file)
  token: ""

  # Define all your Flex Query reports
  queries:
    - id: "1369526"
      name: "performance"
      type: "mark-to-market"
      description: "Daily Mark-to-Market P&L"

    - id: "1369536"
      name: "Historical Trades"
      type: "trades"
      description: "Detailed trade execution history"

# Database
database:
  url: "sqlite:///./ibkr_analytics.db"
  echo: false

# Application
app:
  debug: false
  log_level: "INFO"
  update_interval_minutes: 15
```

### 5.2 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `IBKR_HOST` | TWS/Gateway host | 127.0.0.1 |
| `IBKR_PORT` | TWS/Gateway port | 7497 |
| `IBKR_CLIENT_ID` | Client ID | 1 |
| `FLEX_TOKEN` | Flex Query web service token | - |
| `DB_URL` | Database connection URL | sqlite:///./ibkr_analytics.db |
| `APP_DEBUG` | Debug mode | false |
| `APP_LOG_LEVEL` | Log level | INFO |
| `APP_UPDATE_INTERVAL_MINUTES` | Auto-refresh interval | 15 |
| `KILL_SWITCH` | Emergency stop for execution | - |
| `LOG_FORMAT` | "json" for JSON logging | - |

### 5.3 Credentials (`.env` file)

For Portfolio Analyst automation:

```bash
IBKR_USERNAME=your_username
IBKR_PASSWORD=your_password
IBKR_ACCOUNT_ID=U1234567
```

---

## 6. Getting Started Workflows

### 6.1 Initial Setup

```bash
# 1. Navigate to project
cd "/Users/zelin/Desktop/PA Investment/Invest_strategy"

# 2. Create conda environment
conda create -n ibkr-analytics python=3.10
conda activate ibkr-analytics

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright for PA automation (optional)
playwright install chromium

# 5. Initialize database
python scripts/init_db.py

# 6. Configure IBKR
# Edit config/app_config.yaml with your settings

# 7. Start application
./start.sh
```

### 6.2 Daily Workflow

```bash
# Ensure TWS/Gateway is running and logged in first!

# Option A: Start full application
./start.sh
# Backend: http://localhost:8000
# Frontend: http://localhost:8050

# Option B: Manual fetch via API
curl -X POST "http://localhost:8000/api/fetch-data"

# Option C: Fetch Flex Query reports
curl -X POST "http://localhost:8000/api/flex-query/fetch-all-reports"

# Option D: Automated scheduler
python start_scheduler.py YOUR_ACCOUNT_ID
```

### 6.3 Research Workflow

```python
# In Jupyter notebook (notebooks/analysis.ipynb)

import sys
sys.path.insert(0, "/Users/zelin/Desktop/PA Investment/Invest_strategy")

from quant_data.duckdb_store import connect, register_parquet_view
from backend.backtest_engine import BacktestEngine, IBKRDataFeed

# Load market data from Parquet
con = connect()
register_parquet_view(
    con,
    view_name="bars",
    parquet_glob="data_lake/clean/stooq/bars/us_equities/1d/**/*.parquet"
)

df = con.execute("SELECT * FROM bars WHERE symbol='AAPL' ORDER BY timestamp").df()

# Define strategy
import backtrader as bt

class MomentumStrategy(bt.Strategy):
    def next(self):
        if self.data.close[0] > self.data.close[-1] * 1.01:  # 1% gain
            self.buy()
        elif self.data.close[0] < self.data.close[-1] * 0.99:  # 1% loss
            self.sell()

# Run backtest
engine = BacktestEngine(cash=100000, commission=0.001)
engine.add_data(IBKRDataFeed(dataname=df), name='AAPL')
engine.add_strategy(MomentumStrategy)
result = engine.run_backtest()

print(f"Total Return: {result['total_return']:.2%}")
print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {result.stats['max_drawdown']:.2%}")

# Plot equity curve
import matplotlib.pyplot as plt
result.equity.plot(title="Equity Curve")
plt.show()
```

### 6.4 Database Queries

```bash
cd "/Users/zelin/Desktop/PA Investment/Invest_strategy"
conda activate ibkr-analytics

# Trade summary by symbol
PYTHONPATH="$(pwd)" python -m backend.db_utils summary

# Daily P&L
PYTHONPATH="$(pwd)" python -m backend.db_utils daily

# Total P&L
PYTHONPATH="$(pwd)" python -m backend.db_utils totals

# Import trades from Flex reports
PYTHONPATH="$(pwd)" python -m backend.db_utils import

# Custom SQL query
PYTHONPATH="$(pwd)" python -m backend.db_utils query \
    "SELECT symbol, SUM(realized_pnl) as pnl FROM trades GROUP BY symbol ORDER BY pnl DESC"
```

### 6.5 Python Database API

```python
from backend.db_utils import (
    get_trades_df,
    get_daily_pnl,
    get_trade_summary,
    get_account_pnl_totals,
    query_trades
)

# Get all trades
trades = get_trades_df()

# Filter by symbol and date
aapl_trades = get_trades_df(
    symbol="AAPL",
    start_date="2025-01-01",
    side="BUY",
    limit=50
)

# P&L summaries
daily = get_daily_pnl()
summary = get_trade_summary()
totals = get_account_pnl_totals()

# Raw SQL
df = query_trades("""
    SELECT
        symbol,
        COUNT(*) as trades,
        SUM(realized_pnl) as total_pnl
    FROM trades
    GROUP BY symbol
    ORDER BY total_pnl DESC
""")
```

---

## 7. Infrastructure

### 7.1 Docker Deployment

```bash
cd infrastructure

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Build and start
docker-compose up --build

# Or run in background
docker-compose up -d
```

**Services**:
- `ibkr-backend` - FastAPI server (port 8000)
- `ibkr-frontend` - Dash dashboard (port 8050)
- Optional: PostgreSQL (uncomment in docker-compose.yml)

**Docker Compose Configuration** (`infrastructure/docker-compose.yml`):

```yaml
services:
  backend:
    build:
      context: ..
      dockerfile: infrastructure/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - IBKR_HOST=${IBKR_HOST:-127.0.0.1}
      - IBKR_PORT=${IBKR_PORT:-7497}
      - DB_URL=${DB_URL:-sqlite:///./ibkr_analytics.db}
    volumes:
      - ../backend:/app/backend
      - ../config:/app/config

  frontend:
    build:
      context: ..
      dockerfile: infrastructure/Dockerfile.frontend
    ports:
      - "8050:8050"
    environment:
      - API_BASE_URL=http://backend:8000/api
    depends_on:
      - backend
```

### 7.2 Scheduled Automation

**Portfolio Analyst Automation**:

```bash
# Setup macOS LaunchAgent (runs daily at 9 AM)
bash scripts/setup_pa_scheduler.sh

# Or run Python daemon
python scripts/pa_scheduler.py --daemon --time "09:00"

# Manual run
python scripts/automate_pa_daily.py

# Check status
launchctl list | grep pa_automation
```

**Flex Query Scheduler**:
- Configured in `app_config.yaml` via `update_interval_minutes`
- APScheduler runs automatically when backend starts

### 7.3 Research Environment

For Jupyter research:

```bash
cd infrastructure
docker-compose -f docker-compose.research.yml up
```

---

## 8. Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/init_db.py` | Initialize database tables |
| `scripts/init_quant_data_meta_db.py` | Initialize quant data metadata DB |
| `scripts/automate_pa_daily.py` | Full Portfolio Analyst automation |
| `scripts/download_portfolio_analyst.py` | Download PA CSV from IBKR |
| `scripts/import_portfolio_analyst.py` | Import PA CSV to database |
| `scripts/ingest_stooq_bars.py` | Ingest Stooq OHLCV data |
| `scripts/ingest_binance_bars.py` | Ingest Binance crypto bars |
| `scripts/qc_build_equity_daily.py` | Build QC Lean equity data |
| `scripts/qc_plot_backtest.py` | Plot QC backtest results |
| `scripts/run_paper_trader.py` | Start paper trading runner |
| `scripts/setup_ibkr.py` | IBKR setup helper |
| `scripts/pa_scheduler.py` | PA automation daemon |
| `scripts/setup_pa_scheduler.sh` | Install macOS LaunchAgent |
| `scripts/run_with_env.sh` | Run scripts with conda env |

---

## 9. Directory Structure Summary

```
Invest_strategy/
├── backend/                  # FastAPI backend
│   ├── api/                  # Routes, schemas
│   │   ├── routes.py         # Main API endpoints
│   │   ├── backtest_routes.py
│   │   └── schemas.py        # Pydantic models
│   ├── ibkr_client.py        # IBKR connection
│   ├── data_fetcher.py       # Data fetching
│   ├── data_processor.py     # Performance calculations
│   ├── flex_query_client.py  # Flex Query client
│   ├── flex_parser.py        # XML parser
│   ├── flex_importer.py      # Database importer
│   ├── models.py             # SQLAlchemy models
│   ├── database.py           # DB connection
│   ├── db_utils.py           # CLI utilities
│   ├── scheduler.py          # APScheduler
│   ├── export.py             # Excel export
│   ├── config.py             # Settings loader
│   └── main.py               # Entry point
│
├── apps/
│   └── dashboard/
│       ├── backend/          # FastAPI dashboard backend
│       └── frontend/         # Dash dashboard frontend
│
├── workstation/
│   ├── backtests/           # Research and validation framework
│   ├── portfolio/           # Optimization and allocation
│   ├── execution/           # Paper/live execution path
│   ├── quant_data/          # Market-data code: connectors, schemas, registry
│   ├── research/            # Strategy folders, reviews, and audit outputs
│   ├── notebooks/           # Notebooks and templates
│   ├── playground/          # Fast-iteration sandbox
│   └── books_and_papers/    # Reference library
│
├── data/                     # Stored market data and broker exports
│   ├── market_data/
│   └── flex_reports/
│
├── backend/                  # Compatibility symlink -> apps/dashboard/backend
├── frontend/                 # Compatibility symlink -> apps/dashboard/frontend
├── backtests/                # Compatibility symlink -> workstation/backtests
├── portfolio/                # Compatibility symlink -> workstation/portfolio
├── execution/                # Compatibility symlink -> workstation/execution
├── quant_data/               # Compatibility symlink -> workstation/quant_data
├── research/                 # Compatibility symlink -> workstation/research
├── notebooks/                # Compatibility symlink -> workstation/notebooks
├── playground/               # Compatibility symlink -> workstation/playground
├── books_and_papers/         # Compatibility symlink -> workstation/books_and_papers
│
├── extensions/
│   └── cerebro/             # Optional research-ingestion extension
│
├── qc_lean/                  # Optional external Lean workspace
│   ├── Lean/                 # Lean engine source
│   ├── Data/                 # Lean-formatted market data
│   ├── Results/              # Generated backtest output
│   ├── config.json           # Lean config
│   └── *.py                  # Strategy files
│
├── scripts/                  # Utility scripts
│   ├── init_db.py
│   ├── automate_pa_daily.py
│   ├── ingest_*.py
│   └── ...
│
├── tests/                    # Test suite
│
├── config/                   # Configuration
│   ├── app_config.yaml
│   ├── app_config.yaml.example
│   └── ibkr_config.yaml.example
│
├── infrastructure/           # Docker files
│   ├── docker-compose.yml
│   ├── docker-compose.research.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── Dockerfile.research
│
├── data/                     # Data storage
│   └── flex_reports/         # Flex Query raw data
│
├── data_lake/                # Parquet data lake
│   └── README.md
│
├── guides/                   # Setup and usage guides
│   ├── DATABASE_GUIDE.md
│   ├── IBKR_SETUP_GUIDE.md
│   ├── FLEX_QUERY_SETUP.md
│   ├── PA_AUTOMATION_SETUP.md
│   ├── ALERT_SETUP_GUIDE.md
│   ├── EMAIL_ALERT_SETUP.md
│   ├── PNL_QUERY_GUIDE.md
│   ├── PNL_HISTORY_QUERY_GUIDE.md
│   ├── ADVANCED_ANALYTICS_USAGE.md
│   └── ML_FEATURES_USAGE.md
│
├── docs/                     # Documentation
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── QUANT_DATA_SPEC.md
│   └── QUICK_REFERENCE.md
│
├── logs/                     # Log files
│
├── requirements.txt          # Python dependencies
├── environment.yml           # Conda environment
├── start.sh                  # Startup script
├── start_scheduler.py        # Scheduler entry
├── README.md                 # Main readme
└── PROJECT_DOCUMENTATION.md  # This file
```

---

## 10. Troubleshooting

### IBKR Connection Issues

**"Failed to connect to IBKR TWS/Gateway"**

1. **Ensure TWS/Gateway is running** and you're logged in
2. **Enable API**: Configure → API → Settings → Enable ActiveX and Socket Clients
3. **Check port**: 7497 (paper) or 7496 (live)
4. **Add trusted IP**: 127.0.0.1
5. **Restart TWS/Gateway** after changing API settings

**Test connection**:
```bash
python test_ibkr_connection.py
```

### Environment Issues

```bash
# Verify environment
conda run -n ibkr-analytics python --version
# Should show Python 3.10.x

# Check packages
conda run -n ibkr-analytics python -c "import pandas, fastapi, ib_insync; print('OK')"

# Reinstall dependencies
conda activate ibkr-analytics
pip install -r requirements.txt
```

### Database Issues

```bash
# Initialize/recreate tables
PYTHONPATH="$(pwd)" python -m backend.db_utils init

# Reset trades table (WARNING: deletes data!)
PYTHONPATH="$(pwd)" python -m backend.db_utils reset

# Re-import from Flex
PYTHONPATH="$(pwd)" python -m backend.db_utils import
```

### Port Conflicts

```bash
# Check what's using port 8000
lsof -i :8000

# Check port 8050
lsof -i :8050

# Kill process if needed
kill -9 <PID>
```

### Flex Query Issues

1. **Token not configured**: Set `FLEX_TOKEN` env var or add to `app_config.yaml`
2. **Query ID invalid**: Verify query ID in IBKR Account Management
3. **Rate limiting**: Wait 1 minute between requests

### Common Errors

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | Activate conda env: `conda activate ibkr-analytics` |
| `Connection refused` | Start TWS/Gateway first |
| `No account snapshot found` | Fetch data: `curl -X POST localhost:8000/api/fetch-data` |
| `Table not found` | Run `python scripts/init_db.py` |

---

## 11. Related Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Main project readme |
| [DATABASE_GUIDE.md](docs/guides/DATABASE_GUIDE.md) | Database queries, P&L analysis |
| [IBKR_SETUP_GUIDE.md](docs/guides/IBKR_SETUP_GUIDE.md) | IBKR TWS/Gateway configuration |
| [FLEX_QUERY_SETUP.md](docs/guides/FLEX_QUERY_SETUP.md) | Flex Query web service setup |
| [PA_AUTOMATION_SETUP.md](docs/guides/PA_AUTOMATION_SETUP.md) | Portfolio Analyst automation |
| [QUANT_DATA_SPEC.md](docs/QUANT_DATA_SPEC.md) | Canonical data specifications |
| [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) | Quick reference commands |
| [DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md) | Production deployment checklist |

---

## 12. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-13 | Initial comprehensive documentation |

---

*This documentation was auto-generated based on the repository structure and source code analysis.*
