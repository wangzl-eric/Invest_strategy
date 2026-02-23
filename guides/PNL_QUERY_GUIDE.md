# How to Query Past PnL Data from the Database

This guide teaches you how to query historical P&L (Profit & Loss) data from your local SQLite database.

## Table of Contents

1. [Understanding PnL Data Structure](#understanding-pnl-data-structure)
2. [Quick Start - CLI Commands](#quick-start---cli-commands)
3. [Python API Examples](#python-api-examples)
4. [Direct SQL Queries](#direct-sql-queries)
5. [Common Use Cases](#common-use-cases)
6. [Visualizing PnL Data](#visualizing-pnl-data)

---

## Understanding PnL Data Structure

Your database stores PnL data in two main tables:

### 1. `trades` Table
Contains individual trade executions with realized P&L:

| Column | Description |
|--------|-------------|
| `exec_time` | When the trade was executed |
| `symbol` | Stock/option symbol |
| `side` | BUY or SELL |
| `shares` | Number of shares/contracts |
| `price` | Execution price |
| `realized_pnl` | P&L in trade currency (USD, HKD, etc.) |
| `realized_pnl_base` | P&L in base currency (HKD) |
| `commission` | Commission paid |

### 2. `pnl_history` Table
Contains daily aggregated P&L snapshots:

| Column | Description |
|--------|-------------|
| `date` | Date of the snapshot |
| `realized_pnl` | Realized P&L for the day |
| `unrealized_pnl` | Unrealized P&L (mark-to-market) |
| `total_pnl` | Total P&L (realized + unrealized) |
| `net_liquidation` | Account value |
| `total_cash` | Cash balance |

---

## Quick Start - CLI Commands

The easiest way to query PnL data is using the built-in CLI commands.

### Setup

```bash
cd "/Users/zelin/Desktop/PA Investment/Invest_strategy"
conda activate ibkr-analytics
```

### 1. View Daily P&L

Shows daily P&L with cumulative totals:

```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils daily
```

**Output Example:**
```
================================================================================
DAILY P&L
================================================================================

Date         Trades   Daily USD      Daily HKD   Cumul USD      Cumul HKD
--------------------------------------------------------------------------------
2025-01-10        5       125.50       977.39       125.50       977.39
2025-01-11        3       -45.20      -352.06        80.30       625.33
2025-01-12        8       200.75     1,561.84       281.05     1,187.17
================================================================================
```

### 2. View Trade Summary by Symbol

Shows total P&L grouped by symbol:

```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils summary
```

**Output Example:**
```
======================================================================
TRADE SUMMARY BY SYMBOL
======================================================================

Symbol                    Trades   P&L (USD)      P&L (HKD)
----------------------------------------------------------------------
AAPL                          15      1,250.00      9,735.00
MSFT                          12        850.50      6,626.89
IAU                           20        500.25      3,901.95
----------------------------------------------------------------------
TOTAL                         47      2,600.75     20,263.84
Commissions                                   125.50
======================================================================
```

### 3. View Total P&L

Quick overview of all-time totals:

```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils totals
```

**Output:**
```
Total P&L (USD): $2,600.75
Total P&L (HKD): HK$20,263.84
Total Commissions: $125.50
Total Trades: 47
```

### 4. Run Custom SQL Query

Query the database directly with SQL:

```bash
# Get all trades for a specific symbol
PYTHONPATH="$(pwd)" python -m backend.db_utils query \
    "SELECT exec_time, symbol, side, shares, price, realized_pnl FROM trades WHERE symbol = 'AAPL' ORDER BY exec_time DESC LIMIT 10"

# Get monthly P&L summary
PYTHONPATH="$(pwd)" python -m backend.db_utils query \
    "SELECT strftime('%Y-%m', exec_time) as month, SUM(realized_pnl) as pnl FROM trades GROUP BY month ORDER BY month"
```

---

## Python API Examples

For more advanced analysis, use the Python API in Jupyter notebooks or scripts.

### Setup

```python
import sys
sys.path.insert(0, "/Users/zelin/Desktop/PA Investment/Invest_strategy")

from backend.db_utils import (
    get_trades_df,
    get_daily_pnl,
    get_trade_summary,
    get_account_pnl_totals,
    query_trades
)
import pandas as pd
```

### 1. Get All Trades

```python
# Get all trades as a DataFrame
trades = get_trades_df()
print(trades.head())
print(f"Total trades: {len(trades)}")
```

### 2. Filter Trades by Date Range

```python
# Get trades from January 2025
jan_trades = get_trades_df(
    start_date="2025-01-01",
    end_date="2025-01-31"
)

# Calculate total P&L for the month
jan_pnl = jan_trades['realized_pnl'].sum()
print(f"January P&L: ${jan_pnl:,.2f}")
```

### 3. Filter by Symbol

```python
# Get all AAPL trades
aapl_trades = get_trades_df(symbol="AAPL")

# Calculate AAPL P&L
aapl_pnl = aapl_trades['realized_pnl'].sum()
print(f"AAPL Total P&L: ${aapl_pnl:,.2f}")
print(f"AAPL Trade Count: {len(aapl_trades)}")
```

### 4. Get Daily P&L

```python
# Get daily P&L for all time
daily = get_daily_pnl()

# Or filter by date range
daily_jan = get_daily_pnl(
    start_date="2025-01-01",
    end_date="2025-01-31"
)

# View the data
print(daily[['date', 'realized_pnl', 'realized_pnl_hkd', 'cumulative_pnl_usd']].head(10))

# Calculate statistics
print(f"Best day: ${daily['realized_pnl'].max():,.2f}")
print(f"Worst day: ${daily['realized_pnl'].min():,.2f}")
print(f"Average daily P&L: ${daily['realized_pnl'].mean():,.2f}")
```

### 5. Get Trade Summary by Symbol

```python
# Get summary grouped by symbol
summary = get_trade_summary()

# View top performers
print(summary.head(10))

# Filter symbols with positive P&L
profitable = summary[summary['realized_pnl_usd'] > 0]
print(f"Profitable symbols: {len(profitable)}")

# Filter symbols with negative P&L
losing = summary[summary['realized_pnl_usd'] < 0]
print(f"Losing symbols: {len(losing)}")
```

### 6. Get Total P&L

```python
# Get overall totals
totals = get_account_pnl_totals()

print(f"Total P&L (USD): ${totals['total_pnl_usd']:,.2f}")
print(f"Total P&L (HKD): HK${totals['total_pnl_hkd']:,.2f}")
print(f"Total Commissions: ${totals['total_commissions']:,.2f}")
print(f"Total Trades: {totals['trade_count']}")
```

### 7. Advanced Filtering

```python
# Combine multiple filters
filtered = get_trades_df(
    symbol="AAPL",
    start_date="2025-01-01",
    side="BUY",  # Only BUY trades
    currency="USD",
    limit=100
)

# Pattern matching (all VIX options)
vix_trades = get_trades_df(symbol="VIX%")

# Only profitable trades
profitable_trades = get_trades_df()
profitable_trades = profitable_trades[profitable_trades['realized_pnl'] > 0]
```

---

## Direct SQL Queries

For maximum flexibility, query the database directly with SQL.

### Using Python

```python
# Run any SQL query
df = query_trades("""
    SELECT 
        symbol,
        COUNT(*) as trade_count,
        SUM(realized_pnl) as total_pnl,
        AVG(realized_pnl) as avg_pnl,
        MIN(realized_pnl) as worst_trade,
        MAX(realized_pnl) as best_trade
    FROM trades 
    GROUP BY symbol 
    ORDER BY total_pnl DESC
    LIMIT 10
""")

print(df)
```

### Using SQLite CLI

```bash
# Open database directly
sqlite3 ibkr_analytics.db

# List tables
.tables

# View trades table structure
.schema trades

# Query data
SELECT symbol, SUM(realized_pnl) as pnl 
FROM trades 
GROUP BY symbol 
ORDER BY pnl DESC;

# Exit
.quit
```

### Common SQL Queries

#### Monthly P&L Summary

```sql
SELECT 
    strftime('%Y-%m', exec_time) as month,
    COUNT(*) as trades,
    SUM(realized_pnl) as pnl_usd,
    SUM(realized_pnl_base) as pnl_hkd,
    SUM(commission) as commissions
FROM trades 
GROUP BY month 
ORDER BY month;
```

#### Win/Loss Statistics

```sql
SELECT 
    CASE 
        WHEN realized_pnl > 0 THEN 'Win'
        WHEN realized_pnl < 0 THEN 'Loss'
        ELSE 'Breakeven'
    END as outcome,
    COUNT(*) as count,
    SUM(realized_pnl) as total_pnl,
    AVG(realized_pnl) as avg_pnl
FROM trades 
WHERE realized_pnl != 0
GROUP BY outcome;
```

#### Top 10 Best Trades

```sql
SELECT 
    exec_time,
    symbol,
    side,
    shares,
    price,
    realized_pnl,
    currency
FROM trades 
WHERE realized_pnl > 0
ORDER BY realized_pnl DESC
LIMIT 10;
```

#### Worst 10 Trades

```sql
SELECT 
    exec_time,
    symbol,
    side,
    shares,
    price,
    realized_pnl,
    currency
FROM trades 
WHERE realized_pnl < 0
ORDER BY realized_pnl ASC
LIMIT 10;
```

#### P&L by Security Type

```sql
SELECT 
    sec_type,
    COUNT(*) as trades,
    SUM(realized_pnl) as pnl_usd,
    SUM(commission) as commissions
FROM trades 
GROUP BY sec_type
ORDER BY pnl_usd DESC;
```

#### Daily P&L (Manual Calculation)

```sql
SELECT 
    DATE(exec_time) as date,
    COUNT(*) as trades,
    SUM(realized_pnl) as daily_pnl,
    SUM(realized_pnl_base) as daily_pnl_hkd
FROM trades 
GROUP BY DATE(exec_time)
ORDER BY date DESC;
```

---

## Common Use Cases

### 1. Calculate Monthly Returns

```python
# Get daily P&L
daily = get_daily_pnl()

# Convert to monthly
daily['date'] = pd.to_datetime(daily['date'])
daily['year_month'] = daily['date'].dt.to_period('M')

monthly = daily.groupby('year_month').agg({
    'realized_pnl': 'sum',
    'realized_pnl_hkd': 'sum',
    'trade_count': 'sum'
})

print(monthly)
```

### 2. Find Best/Worst Performing Symbols

```python
summary = get_trade_summary()

# Best performers
best = summary.nlargest(10, 'realized_pnl_usd')
print("Top 10 Symbols:")
print(best[['trade_count', 'realized_pnl_usd']])

# Worst performers
worst = summary.nsmallest(10, 'realized_pnl_usd')
print("\nBottom 10 Symbols:")
print(worst[['trade_count', 'realized_pnl_usd']])
```

### 3. Calculate Win Rate

```python
trades = get_trades_df()

# Calculate win rate
total_trades = len(trades)
winning_trades = len(trades[trades['realized_pnl'] > 0])
losing_trades = len(trades[trades['realized_pnl'] < 0])

win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

print(f"Total Trades: {total_trades}")
print(f"Winning Trades: {winning_trades}")
print(f"Losing Trades: {losing_trades}")
print(f"Win Rate: {win_rate:.2f}%")
```

### 4. Analyze P&L Distribution

```python
import matplotlib.pyplot as plt

trades = get_trades_df()

# Plot P&L distribution
plt.figure(figsize=(10, 6))
plt.hist(trades['realized_pnl'], bins=50, edgecolor='black')
plt.xlabel('Realized P&L (USD)')
plt.ylabel('Frequency')
plt.title('Distribution of Trade P&L')
plt.axvline(0, color='red', linestyle='--', label='Breakeven')
plt.legend()
plt.show()

# Statistics
print(f"Mean P&L: ${trades['realized_pnl'].mean():,.2f}")
print(f"Median P&L: ${trades['realized_pnl'].median():,.2f}")
print(f"Std Dev: ${trades['realized_pnl'].std():,.2f}")
```

### 5. Compare USD vs HKD P&L

```python
trades = get_trades_df()

# Calculate totals
usd_total = trades['realized_pnl'].sum()
hkd_total = trades['realized_pnl_hkd'].sum()
fx_rate = hkd_total / usd_total if usd_total != 0 else 0

print(f"Total P&L (USD): ${usd_total:,.2f}")
print(f"Total P&L (HKD): HK${hkd_total:,.2f}")
print(f"Effective FX Rate: {fx_rate:.4f}")
```

### 6. Time Series Analysis

```python
# Get daily P&L
daily = get_daily_pnl()
daily['date'] = pd.to_datetime(daily['date'])

# Calculate rolling statistics
daily['rolling_7d_pnl'] = daily['realized_pnl'].rolling(7).sum()
daily['rolling_30d_pnl'] = daily['realized_pnl'].rolling(30).sum()

# Plot cumulative P&L
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(daily['date'], daily['cumulative_pnl_usd'], label='Cumulative P&L')
plt.xlabel('Date')
plt.ylabel('Cumulative P&L (USD)')
plt.title('Cumulative P&L Over Time')
plt.legend()
plt.grid(True)
plt.show()
```

---

## Visualizing PnL Data

### Simple Plotting with Pandas

```python
import matplotlib.pyplot as plt

# Daily P&L chart
daily = get_daily_pnl()
daily['date'] = pd.to_datetime(daily['date'])

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Daily P&L bars
ax1.bar(daily['date'], daily['realized_pnl'], 
        color=['green' if x > 0 else 'red' for x in daily['realized_pnl']])
ax1.set_title('Daily P&L')
ax1.set_ylabel('P&L (USD)')
ax1.axhline(0, color='black', linestyle='-', linewidth=0.5)

# Cumulative P&L line
ax2.plot(daily['date'], daily['cumulative_pnl_usd'], linewidth=2)
ax2.set_title('Cumulative P&L')
ax2.set_xlabel('Date')
ax2.set_ylabel('Cumulative P&L (USD)')
ax2.grid(True)

plt.tight_layout()
plt.show()
```

### Using Plotly (Interactive)

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots

daily = get_daily_pnl()
daily['date'] = pd.to_datetime(daily['date'])

fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=('Daily P&L', 'Cumulative P&L'),
    vertical_spacing=0.1
)

# Daily P&L bars
colors = ['green' if x > 0 else 'red' for x in daily['realized_pnl']]
fig.add_trace(
    go.Bar(x=daily['date'], y=daily['realized_pnl'], 
           marker_color=colors, name='Daily P&L'),
    row=1, col=1
)

# Cumulative line
fig.add_trace(
    go.Scatter(x=daily['date'], y=daily['cumulative_pnl_usd'], 
               mode='lines', name='Cumulative', line=dict(width=2)),
    row=2, col=1
)

fig.update_layout(height=800, title_text="P&L Analysis")
fig.show()
```

---

## Quick Reference

### CLI Commands

```bash
# Daily P&L
PYTHONPATH="$(pwd)" python -m backend.db_utils daily

# Summary by symbol
PYTHONPATH="$(pwd)" python -m backend.db_utils summary

# Totals
PYTHONPATH="$(pwd)" python -m backend.db_utils totals

# Custom SQL
PYTHONPATH="$(pwd)" python -m backend.db_utils query "SELECT ..."
```

### Python Functions

```python
from backend.db_utils import (
    get_trades_df,      # Get trades DataFrame
    get_daily_pnl,      # Get daily P&L
    get_trade_summary,  # Get summary by symbol
    get_account_pnl_totals,  # Get totals
    query_trades        # Run SQL
)
```

### Database Location

```
/Users/zelin/Desktop/PA Investment/Invest_strategy/ibkr_analytics.db
```

---

## Next Steps

- Explore the [DATABASE_GUIDE.md](DATABASE_GUIDE.md) for more advanced queries
- Check [PROJECT_DOCUMENTATION.md](../PROJECT_DOCUMENTATION.md) for full API reference
- Use the frontend dashboard at `http://localhost:8050` for visual analysis
