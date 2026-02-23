# Querying pnl_history Table - Complete Guide

## Overview

The `pnl_history` table stores **daily** P&L records imported from Flex Query performance reports. Each row represents one day's account snapshot.

## Table Structure

```python
class PnLHistory:
    id: int                    # Primary key
    account_id: str            # Account ID (e.g., 'U13798787')
    date: datetime             # Date (normalized to midnight for daily records)
    net_liquidation: float     # Account value (EndingValue from Flex Query)
    total_pnl: float           # Total P&L (EndingValue - StartingValue)
    realized_pnl: float        # Realized P&L
    unrealized_pnl: float      # Unrealized P&L
    total_cash: float          # Cash balance
    created_at: datetime        # Record creation timestamp
```

---

## Method 1: Using `get_daily_returns()` (RECOMMENDED)

**Best for:** Getting daily return series for analysis

```python
from backend.db_utils import get_daily_returns

# Get all daily returns
returns = get_daily_returns(use_pnl_history=True)

# With filters
returns = get_daily_returns(
    account_id='U13798787',
    start_date='2025-01-01',
    end_date='2025-12-31',
    use_pnl_history=True
)

# Returns DataFrame with:
# - date: Daily date
# - daily_return: Daily return (as decimal, e.g., 0.01 = 1%)
# - cumulative_return: Cumulative return from start
# - net_liquidation: Account value at end of day
```

**Example:**
```python
returns = get_daily_returns(use_pnl_history=True)
print(returns.head())

# Output:
#         date  daily_return  cumulative_return  net_liquidation
# 0 2025-01-13      0.000000           0.000000        158522.61
# 1 2025-01-14      0.001713           0.001713        158794.23
# 2 2025-01-15      0.012744           0.014500        160817.96
```

---

## Method 2: Direct SQLAlchemy Query

**Best for:** Custom queries, filtering by specific fields, getting raw data

```python
from backend.database import get_db_context
from backend.models import PnLHistory
from datetime import datetime

# Get all records
with get_db_context() as db:
    records = db.query(PnLHistory).order_by(PnLHistory.date).all()
    
    for record in records:
        print(f"{record.date}: {record.net_liquidation}")

# With filters
with get_db_context() as db:
    records = db.query(PnLHistory).filter(
        PnLHistory.account_id == 'U13798787',
        PnLHistory.date >= datetime(2025, 1, 1),
        PnLHistory.date <= datetime(2025, 12, 31)
    ).order_by(PnLHistory.date).all()

# Get specific columns
with get_db_context() as db:
    records = db.query(
        PnLHistory.date,
        PnLHistory.net_liquidation,
        PnLHistory.total_pnl
    ).filter(
        PnLHistory.account_id == 'U13798787'
    ).order_by(PnLHistory.date).all()
```

---

## Method 3: Convert to Pandas DataFrame

**Best for:** Data analysis, plotting, filtering

```python
from backend.database import get_db_context
from backend.models import PnLHistory
import pandas as pd

with get_db_context() as db:
    records = db.query(PnLHistory).filter(
        PnLHistory.account_id == 'U13798787'
    ).order_by(PnLHistory.date).all()
    
    # Convert to DataFrame
    data = []
    for r in records:
        data.append({
            'date': r.date,
            'net_liquidation': r.net_liquidation,
            'total_pnl': r.total_pnl,
            'realized_pnl': r.realized_pnl,
            'unrealized_pnl': r.unrealized_pnl,
        })
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    
    # Now you can use pandas operations
    print(df.head())
    print(df.describe())
    df.plot(x='date', y='net_liquidation')
```

---

## Method 4: Raw SQL Query (for debugging)

**Best for:** Quick debugging, complex SQL queries

```python
import sqlite3
import pandas as pd
from pathlib import Path

db_path = Path("ibkr_analytics.db")
conn = sqlite3.connect(str(db_path))

# Simple query
df = pd.read_sql_query(
    """SELECT * FROM pnl_history
       WHERE account_id = 'U13798787'
       ORDER BY date
       LIMIT 10""",
    conn
)

# Complex query
df = pd.read_sql_query(
    """SELECT 
           date,
           net_liquidation,
           total_pnl,
           LAG(net_liquidation) OVER (ORDER BY date) as prev_value,
           (net_liquidation - LAG(net_liquidation) OVER (ORDER BY date)) / 
           LAG(net_liquidation) OVER (ORDER BY date) as daily_return
       FROM pnl_history
       WHERE account_id = 'U13798787'
       ORDER BY date""",
    conn
)

conn.close()
```

---

## Common Query Patterns

### 1. Get latest account value
```python
from backend.database import get_db_context
from backend.models import PnLHistory
from sqlalchemy import desc

with get_db_context() as db:
    latest = db.query(PnLHistory).filter(
        PnLHistory.account_id == 'U13798787'
    ).order_by(desc(PnLHistory.date)).first()
    
    print(f"Latest value: {latest.net_liquidation} on {latest.date}")
```

### 2. Get monthly summary
```python
import pandas as pd
from backend.database import get_db_context
from backend.models import PnLHistory

with get_db_context() as db:
    records = db.query(PnLHistory).filter(
        PnLHistory.account_id == 'U13798787'
    ).order_by(PnLHistory.date).all()
    
    df = pd.DataFrame([{
        'date': r.date,
        'net_liquidation': r.net_liquidation,
        'total_pnl': r.total_pnl
    } for r in records])
    
    df['date'] = pd.to_datetime(df['date'])
    df['year_month'] = df['date'].dt.to_period('M')
    
    monthly = df.groupby('year_month').agg({
        'net_liquidation': 'last',  # End of month value
        'total_pnl': 'sum'
    })
    
    print(monthly)
```

### 3. Calculate statistics
```python
from backend.db_utils import get_daily_returns
import numpy as np

returns = get_daily_returns(use_pnl_history=True)

if not returns.empty:
    daily_returns = returns['daily_return']
    
    print(f"Mean daily return: {daily_returns.mean():.4%}")
    print(f"Std dev: {daily_returns.std():.4%}")
    print(f"Sharpe ratio (annualized): {(daily_returns.mean() / daily_returns.std()) * np.sqrt(252):.2f}")
    print(f"Total return: {returns['cumulative_return'].iloc[-1]:.4%}")
```

### 4. Filter by date range
```python
from backend.db_utils import get_daily_returns
from datetime import datetime

# Using get_daily_returns (easiest)
returns = get_daily_returns(
    account_id='U13798787',
    start_date='2025-01-01',
    end_date='2025-03-31',
    use_pnl_history=True
)

# Or using direct query
from backend.database import get_db_context
from backend.models import PnLHistory

with get_db_context() as db:
    records = db.query(PnLHistory).filter(
        PnLHistory.account_id == 'U13798787',
        PnLHistory.date >= datetime(2025, 1, 1),
        PnLHistory.date <= datetime(2025, 3, 31)
    ).order_by(PnLHistory.date).all()
```

---

## Important Notes

1. **Database Location:** All queries read from local database:
   - Path: `ibkr_analytics.db` (in project root)
   - Connection: Managed by `backend.database.get_db_context()`

2. **Data Source:** `pnl_history` is populated from:
   - Flex Query performance CSV files (daily data)
   - Automatically imported when fetching Flex Query reports

3. **Date Format:** Dates are stored as `datetime` objects, normalized to midnight (00:00:00) for daily records

4. **Deduplication:** The import process automatically skips duplicate dates (one record per day per account)

---

## Quick Reference

| Use Case | Method | Example |
|----------|--------|---------|
| Daily returns | `get_daily_returns()` | `get_daily_returns(use_pnl_history=True)` |
| Raw PnL data | Direct SQLAlchemy | `db.query(PnLHistory).all()` |
| Custom analysis | Pandas DataFrame | Convert query results to DataFrame |
| Complex SQL | Raw SQL | `pd.read_sql_query(...)` |
| Latest value | SQLAlchemy + `desc()` | `order_by(desc(PnLHistory.date)).first()` |
