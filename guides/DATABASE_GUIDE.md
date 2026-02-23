# IBKR Analytics Database Guide

This guide explains how to use the database for storing, querying, and analyzing your IBKR trading data.

## Table of Contents

- [Quick Start](#quick-start)
- [Database Overview](#database-overview)
- [CLI Commands](#cli-commands)
- [Python API](#python-api)
- [Sample Queries](#sample-queries)
- [Importing Data](#importing-data)
- [Direct SQLite Access](#direct-sqlite-access)

---

## Quick Start

```bash
cd "/Users/zelin/Desktop/PA Investment/Invest_strategy"
source /Users/zelin/opt/anaconda3/etc/profile.d/conda.sh
conda activate ibkr-analytics

# 1. Import trades from Flex Query files
PYTHONPATH="$(pwd)" python -m backend.db_utils import

# 2. View trade summary
PYTHONPATH="$(pwd)" python -m backend.db_utils summary

# 3. View daily P&L
PYTHONPATH="$(pwd)" python -m backend.db_utils daily
```

---

## Database Overview

### Location
```
/Users/zelin/Desktop/PA Investment/Invest_strategy/ibkr_analytics.db
```

### Tables

| Table | Description |
|-------|-------------|
| `trades` | Trade executions with P&L in USD and HKD |
| `positions` | Position snapshots |
| `pnl_history` | Daily P&L records |
| `account_snapshots` | Account value history |
| `performance_metrics` | Performance statistics |

### Key Columns in `trades` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT | Primary key |
| `exec_time` | DATETIME | Execution timestamp |
| `symbol` | TEXT | Ticker symbol |
| `sec_type` | TEXT | Security type (STK, OPT, etc.) |
| `side` | TEXT | BUY or SELL |
| `shares` | FLOAT | Number of shares/contracts |
| `price` | FLOAT | Execution price |
| `currency` | TEXT | Trade currency (USD, HKD, etc.) |
| `commission` | FLOAT | Commission paid |
| `realized_pnl` | FLOAT | Realized P&L in trade currency |
| `realized_pnl_base` | FLOAT | Realized P&L in base currency (HKD) |
| `fx_rate_to_base` | FLOAT | FX rate used for conversion |

---

## CLI Commands

### Initialize Database
```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils init
```

### Import Trades from Flex Query
```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils import
```

### View Trade Summary by Symbol
```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils summary
```

### View Daily P&L
```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils daily
```

### View Total P&L
```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils totals
```

### Run Custom SQL Query
```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils query "SELECT * FROM trades WHERE symbol = 'IAU'"
```

### Reset Trades Table (Warning: Deletes All Data!)
```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils reset
```

---

## Python API

### Basic Setup

```python
import sys
sys.path.insert(0, "/Users/zelin/Desktop/PA Investment/Invest_strategy")

from backend.db_utils import (
    import_trades_from_flex,
    get_trades_df,
    get_daily_pnl,
    get_trade_summary,
    get_account_pnl_totals,
    query_trades
)
```

### Import Trades

```python
# Import all trades from Flex Query files
stats = import_trades_from_flex("data/flex_reports")
print(f"Imported: {stats['imported']}, Skipped: {stats['skipped']}")
```

### Query Trades

```python
# Get all trades as DataFrame
trades = get_trades_df()

# Filter by symbol
iau_trades = get_trades_df(symbol="IAU")

# Filter by date range
jan_trades = get_trades_df(start_date="2025-01-01", end_date="2025-01-31")

# Filter by side (BUY/SELL)
buys = get_trades_df(side="BUY")

# Filter by currency
usd_trades = get_trades_df(currency="USD")

# Pattern matching (% = wildcard)
vix_trades = get_trades_df(symbol="VIX%")

# Combine filters
filtered = get_trades_df(
    symbol="IAU",
    start_date="2025-01-01",
    side="BUY",
    limit=50
)
```

### Get P&L Summaries

```python
# Daily P&L with cumulative totals
daily = get_daily_pnl()
print(daily[['date', 'realized_pnl', 'realized_pnl_hkd', 'cumulative_pnl_usd', 'cumulative_pnl_hkd']])

# P&L by symbol
summary = get_trade_summary()
print(summary[['trade_count', 'realized_pnl_usd', 'realized_pnl_hkd']])

# Overall totals
totals = get_account_pnl_totals()
print(f"Total P&L (USD): ${totals['total_pnl_usd']:,.2f}")
print(f"Total P&L (HKD): HK${totals['total_pnl_hkd']:,.2f}")
print(f"Total Commissions: ${totals['total_commissions']:,.2f}")
```

### Run Raw SQL

```python
# Any SQL query
df = query_trades("SELECT * FROM trades WHERE realized_pnl > 0")

# Aggregation
df = query_trades("""
    SELECT 
        symbol,
        COUNT(*) as trades,
        SUM(realized_pnl) as total_pnl,
        AVG(realized_pnl) as avg_pnl
    FROM trades 
    GROUP BY symbol 
    ORDER BY total_pnl DESC
""")
print(df)
```

---

## Sample Queries

### Top Profitable Trades

```python
df = query_trades("""
    SELECT exec_time, symbol, side, shares, price, realized_pnl, currency
    FROM trades 
    WHERE realized_pnl > 0
    ORDER BY realized_pnl DESC
    LIMIT 10
""")
```

### Worst Losing Trades

```python
df = query_trades("""
    SELECT exec_time, symbol, side, shares, price, realized_pnl, currency
    FROM trades 
    WHERE realized_pnl < 0
    ORDER BY realized_pnl ASC
    LIMIT 10
""")
```

### Monthly P&L Summary

```python
df = query_trades("""
    SELECT 
        strftime('%Y-%m', exec_time) as month,
        COUNT(*) as trades,
        SUM(realized_pnl) as pnl_usd,
        SUM(realized_pnl_base) as pnl_hkd,
        SUM(commission) as commissions
    FROM trades 
    GROUP BY strftime('%Y-%m', exec_time)
    ORDER BY month
""")
```

### P&L by Security Type

```python
df = query_trades("""
    SELECT 
        sec_type,
        COUNT(*) as trades,
        SUM(realized_pnl) as pnl_usd,
        SUM(commission) as commissions
    FROM trades 
    GROUP BY sec_type
    ORDER BY pnl_usd DESC
""")
```

### Win/Loss Statistics

```python
df = query_trades("""
    SELECT 
        CASE WHEN realized_pnl > 0 THEN 'Win' 
             WHEN realized_pnl < 0 THEN 'Loss' 
             ELSE 'Breakeven' END as outcome,
        COUNT(*) as count,
        SUM(realized_pnl) as total_pnl,
        AVG(realized_pnl) as avg_pnl
    FROM trades 
    WHERE realized_pnl != 0
    GROUP BY outcome
""")
```

### Options vs Stocks Performance

```python
df = query_trades("""
    SELECT 
        CASE WHEN sec_type = 'OPT' THEN 'Options' ELSE 'Stocks' END as type,
        COUNT(*) as trades,
        SUM(realized_pnl) as pnl_usd,
        SUM(commission) as commissions,
        SUM(realized_pnl) - ABS(SUM(commission)) as net_pnl
    FROM trades 
    GROUP BY type
""")
```

### VIX Options Breakdown

```python
df = query_trades("""
    SELECT 
        symbol,
        put_call,
        expiry,
        strike,
        SUM(shares) as total_contracts,
        SUM(realized_pnl) as pnl
    FROM trades 
    WHERE symbol LIKE 'VIX%'
    GROUP BY symbol
    ORDER BY pnl DESC
""")
```

---

## Importing Data

### From Flex Query Files

1. **Download Flex Query reports** from IBKR Account Management
2. **Save to** `data/flex_reports/` directory
3. **Run import:**

```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils import
```

### File Organization

Files are organized by date and type:
```
data/flex_reports/
├── 2026-01-10/
│   ├── trades/
│   │   └── Historical_Trades_093646.xml
│   └── mark-to-market/
│       └── performance_093640.xml
└── flex_query_1368462_20260109_232951.csv
```

---

## Direct SQLite Access

### Using sqlite3 CLI

```bash
sqlite3 ibkr_analytics.db

# List tables
.tables

# Describe table structure
.schema trades

# Query data
SELECT * FROM trades LIMIT 10;

# Export to CSV
.headers on
.mode csv
.output trades_export.csv
SELECT * FROM trades;
.output stdout

# Exit
.quit
```

### Using Python sqlite3

```python
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('ibkr_analytics.db')

# Query to DataFrame
df = pd.read_sql("SELECT * FROM trades", conn)

# Execute updates
cursor = conn.cursor()
cursor.execute("UPDATE trades SET realized_pnl = 100 WHERE id = 1")
conn.commit()

# Close connection
conn.close()
```

### Using DB Browser for SQLite (GUI)

1. Download: https://sqlitebrowser.org/
2. Open: `ibkr_analytics.db`
3. Browse tables, run queries, export data

---

## Backup & Restore

### Backup Database

```bash
cp ibkr_analytics.db ibkr_analytics_backup_$(date +%Y%m%d).db
```

### Export to CSV

```python
from backend.db_utils import get_trades_df

trades = get_trades_df(limit=100000)
trades.to_csv("trades_backup.csv", index=False)
```

### Restore from Backup

```bash
cp ibkr_analytics_backup_20260110.db ibkr_analytics.db
```

---

## Troubleshooting

### "Table not found" Error
```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils init
```

### "Column not found" Error
Reset the trades table to get new schema:
```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils reset
PYTHONPATH="$(pwd)" python -m backend.db_utils import
```

### Duplicate Trades
The import process automatically skips duplicates based on `exec_id`.

---

## Next Steps

- **Market Data**: Coming soon - store historical price data
- **Automated Recording**: Schedule daily P&L snapshots
- **Performance Analytics**: Calculate Sharpe ratio, drawdowns, etc.
