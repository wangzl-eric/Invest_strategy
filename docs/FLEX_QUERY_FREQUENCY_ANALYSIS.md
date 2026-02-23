# Flex Query Frequency Analysis

## Issue Summary

Your Flex Query reports are configured to return **weekly/last business day** data instead of **daily** data. This document explains the findings and how to fix it.

## Findings

### 1. XML File Analysis

The Flex Query XML files show:
```xml
<FlexStatement accountId="U13798787" fromDate="20260108" toDate="20260108" period="LastBusinessDay" ...>
```

**Key Issue**: `period="LastBusinessDay"` means the query only returns data for the **last business day**, not historical daily data.

### 2. Database Analysis

**Trades Table:**
- Trades are scattered across dates (not daily)
- Date range: 2025-01-22 to 2025-12-29
- Only 20 unique dates with trades out of ~340 possible trading days

**PnL History Table:**
- Large gaps between records:
  - 13 days between 2025-12-25 and 2026-01-07
  - 5 days between 2026-01-08 and 2026-01-13
  - Multiple single-day records instead of continuous daily data

### 3. Current Import Process

The import process (`backend/flex_importer.py` and `backend/flex_query_client.py`) correctly:
- ✅ Parses XML/CSV data
- ✅ Extracts trade dates
- ✅ Stores data in database
- ✅ Handles deduplication

**However**, it can only import what the Flex Query returns. If the query is configured for "LastBusinessDay", it will only return that single day's data.

## Solution: Configure Flex Query for Daily Data

### Step 1: Edit Flex Query in IBKR Account Management

1. Log into **IBKR Account Management** (Client Portal)
2. Go to: **Performance & Reports → Flex Queries**
3. Find your query (ID: 1369526 for "performance" or 1369536 for "Historical Trades")
4. Click **Edit** on the query

### Step 2: Change Date Range Settings

For **Mark-to-Market Performance Query** (1369526):
- **Period**: Change from "LastBusinessDay" to **"DateRange"**
- **From Date**: Set to your desired start date (e.g., 1 year ago: `2025-01-01`)
- **To Date**: Leave as "LastBusinessDay" or set to today
- **Frequency**: Ensure it's set to **"Daily"** (not "Weekly" or "Monthly")

For **Historical Trades Query** (1369536):
- **Period**: Change to **"DateRange"**
- **From Date**: Set to your desired start date
- **To Date**: Set to today or "LastBusinessDay"
- **Level of Detail**: Should be "EXECUTION" (not "SUMMARY")

### Step 3: Verify Query Settings

Make sure the query includes:
- ✅ **Daily frequency** (not weekly/monthly)
- ✅ **Date range** covering your desired history
- ✅ **All required sections** (Trades, Positions, Equity Summary, etc.)

### Step 4: Save and Test

1. **Save** the query
2. **Test** it in IBKR to verify it returns daily data
3. **Re-fetch** using your application:
   ```bash
   # Via frontend: Click "Fetch Flex Query" button
   # Or via API:
   curl -X POST http://localhost:8000/api/flex-query/fetch-all-reports
   ```

## Alternative: Use Multiple Date Ranges

If IBKR doesn't support daily frequency for certain query types, you can:

1. **Create multiple queries** for different date ranges:
   - Query 1: Last 30 days (daily)
   - Query 2: Last 90 days (daily)
   - Query 3: Last year (weekly/monthly summary)

2. **Schedule periodic fetches** to build up daily history over time

## Verification After Fix

After updating the Flex Query configuration:

1. **Check XML file structure**:
   ```bash
   # Look for date range in XML
   grep -A 5 "FlexStatement" data/flex_reports/*/mark-to-market/*.xml | head -20
   ```

2. **Verify database has daily data**:
   ```python
   from backend.db_utils import get_daily_pnl
   daily = get_daily_pnl()
   print(f"Daily records: {len(daily)}")
   print(f"Date range: {daily['date'].min()} to {daily['date'].max()}")
   print(f"Gaps: {daily['date'].diff().dt.days.value_counts()}")
   ```

3. **Check for gaps**:
   ```sql
   -- Should show mostly 1-day gaps (daily data)
   SELECT 
       date,
       LAG(date) OVER (ORDER BY date) as prev_date,
       julianday(date) - julianday(LAG(date) OVER (ORDER BY date)) as days_diff
   FROM pnl_history
   ORDER BY date DESC
   LIMIT 30;
   ```

## Current Database State

### Trades
- **Total**: 100 trades
- **Date range**: 2025-01-22 to 2025-12-29
- **Frequency**: Irregular (not daily)

### PnL History
- **Total records**: ~180 records
- **Date range**: 2025-12-21 to 2026-01-13
- **Frequency**: Irregular with gaps (13 days, 5 days, etc.)
- **Most recent**: 73 records on 2026-01-13 (from TWS real-time updates)

## Recommendations

1. **Immediate**: Update Flex Query configuration in IBKR to use daily frequency
2. **Short-term**: Re-fetch all historical data with the new configuration
3. **Long-term**: Set up automated daily fetches to maintain daily history

## Notes

- The **import process is working correctly** - the issue is with the Flex Query configuration in IBKR
- **Real-time TWS data** (from `data_fetcher.py`) provides daily updates, but historical data needs Flex Query
- **Flex Query period settings** are configured in IBKR Account Management, not in this application
