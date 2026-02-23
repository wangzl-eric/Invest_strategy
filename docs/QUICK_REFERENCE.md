# IBKR Analytics Quick Reference

## 🚀 Common Commands

### Start Services
```bash
cd "/Users/zelin/Desktop/PA Investment/Invest_strategy"
./start.sh
```

### Import Trades from Flex Query
```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils import
```

### View P&L Summary
```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils summary
```

### View Daily P&L
```bash
PYTHONPATH="$(pwd)" python -m backend.db_utils daily
```

---

## 📊 Python Snippets

### Setup (Run Once per Session)
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
```

### Get All Trades
```python
trades = get_trades_df()
```

### Filter Trades
```python
# By symbol
trades = get_trades_df(symbol="IAU")

# By date
trades = get_trades_df(start_date="2025-01-01", end_date="2025-12-31")

# By side
buys = get_trades_df(side="BUY")

# Wildcards
vix = get_trades_df(symbol="VIX%")
```

### P&L Summary
```python
# By symbol
summary = get_trade_summary()

# Daily
daily = get_daily_pnl()

# Totals
totals = get_account_pnl_totals()
print(f"P&L USD: ${totals['total_pnl_usd']:,.2f}")
print(f"P&L HKD: HK${totals['total_pnl_hkd']:,.2f}")
```

### Custom SQL
```python
# Any query
df = query_trades("SELECT * FROM trades WHERE realized_pnl > 100")

# Aggregation
df = query_trades("""
    SELECT symbol, SUM(realized_pnl) as pnl
    FROM trades 
    GROUP BY symbol 
    ORDER BY pnl DESC
""")
```

### Export to CSV
```python
trades = get_trades_df()
trades.to_csv("my_trades.csv", index=False)
```

---

## 🔍 Useful SQL Queries

### Top Winners
```sql
SELECT symbol, realized_pnl, exec_time 
FROM trades 
WHERE realized_pnl > 0 
ORDER BY realized_pnl DESC 
LIMIT 10
```

### Monthly P&L
```sql
SELECT 
    strftime('%Y-%m', exec_time) as month,
    SUM(realized_pnl) as pnl_usd,
    SUM(realized_pnl_base) as pnl_hkd
FROM trades 
GROUP BY month
ORDER BY month
```

### Options vs Stocks
```sql
SELECT 
    sec_type,
    COUNT(*) as trades,
    SUM(realized_pnl) as pnl
FROM trades 
GROUP BY sec_type
```

### Win Rate
```sql
SELECT 
    COUNT(CASE WHEN realized_pnl > 0 THEN 1 END) as wins,
    COUNT(CASE WHEN realized_pnl < 0 THEN 1 END) as losses,
    ROUND(100.0 * COUNT(CASE WHEN realized_pnl > 0 THEN 1 END) / COUNT(*), 1) as win_pct
FROM trades 
WHERE realized_pnl != 0
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `ibkr_analytics.db` | SQLite database |
| `config/app_config.yaml` | Configuration |
| `data/flex_reports/` | Flex Query downloads |
| `backend/db_utils.py` | Database utilities |
| `backend/flex_parser.py` | Flex Query parser |

---

## 🌐 URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:8050 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## 📖 Full Documentation

- [DATABASE_GUIDE.md](../guides/DATABASE_GUIDE.md) - Complete database guide
- [FLEX_QUERY_SETUP.md](../guides/FLEX_QUERY_SETUP.md) - Flex Query setup
- [README.md](../README.md) - Project overview
