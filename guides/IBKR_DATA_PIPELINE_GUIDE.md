# IBKR Data Pipeline Guide

This guide explains how to use the IBKR data pipeline to pull high-quality market data for research.

## Overview

The IBKR data pipeline leverages your IBKR Pro membership fee-waived subscriptions to fetch:
- US and international equities
- Forex pairs (more reliable than yfinance)
- Futures contracts
- Options chains

## Prerequisites

### 1. IB Gateway Setup

Before using the data pipeline, you need to set up IB Gateway:

1. **Download IB Gateway**: https://www.interactivebrokers.com/en/index.php?f=16042
2. **Install and launch** IB Gateway
3. **Log in** with your IBKR credentials
4. **Enable API Access**:
   - Go to **Edit > Global Configuration > API > Settings**
   - Check **Enable ActiveX and Socket Clients**
   - Check **Allow connections from localhost only**
   - Set **Socket Port** to `7497` (paper trading) or `7496` (live)
5. **Keep IB Gateway running** while fetching data

### 2. Verify Market Data Subscriptions

1. Log into IB Gateway or TWS
2. Navigate to **Account Settings > Market Data Subscriptions**
3. Verify you have the subscriptions you need
4. Update `config/ibkr_data_subscriptions.yaml` with your subscription status

## Quick Start

### Using the API Endpoints

```bash
# Check if IBKR is connected
curl http://localhost:8000/api/data/ibkr/subscription-status

# Get list of available tickers
curl "http://localhost:8000/api/data/ibkr/tickers?asset_class=ibkr_equities"

# Pull historical data (via background job)
curl -X POST http://localhost:8000/api/data/ibkr/pull-historical \
  -H "Content-Type: application/json" \
  -d '{
    "asset_class": "ibkr_equities",
    "tickers": ["AAPL", "MSFT", "GOOGL"],
    "start_date": "2024-01-01",
    "end_date": "2025-01-01",
    "interval": "1 day"
  }'

# Check job status
curl http://localhost:8000/api/data/pull-status/{job_id}

# Query stored data
curl "http://localhost:8000/api/data/query?asset_class=ibkr_equities&tickers=AAPL"
```

### Using Python Code

```python
import asyncio
from backend.ibkr_data_fetcher import fetch_equities, fetch_forex, fetch_futures

async def main():
    # Fetch equity data
    results = await fetch_equities(
        symbols=["AAPL", "MSFT", "GOOGL"],
        duration="1 Y",
        interval="1 day"
    )
    
    for symbol, df in results.items():
        print(f"{symbol}: {len(df)} rows")
    
    # Fetch forex data
    forex = await fetch_forex(
        pairs=["EURUSD", "GBPUSD"],
        duration="6 M"
    )
    
    # Fetch futures
    futures = await fetch_futures(
        symbols=["ES", "CL", "GC"],
        duration="3 M"
    )

asyncio.run(main())
```

### Incremental Updates

```python
from backend.ibkr_data_fetcher import incremental_update

# Update all equities (only fetches new data since last update)
new_rows = await incremental_update(
    asset_class="ibkr_equities",
    interval="1 day"
)

# Force refresh (re-fetch all data)
new_rows = await incremental_update(
    asset_class="ibkr_equities",
    force_refresh=True
)
```

### Data Validation

```python
from backend.ibkr_data_fetcher import validate_data, validate_and_clean

# Validate data quality
df = ...  # Your DataFrame
report = validate_data(df)

if not report.is_valid():
    print("Issues:", report.issues)
    print("Warnings:", report.warnings)

# Validate and clean
cleaned_df = validate_and_clean(df)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/data/ibkr/subscription-status` | GET | Check if IBKR is connected |
| `/api/data/ibkr/tickers` | GET | Get default ticker list |
| `/api/data/ibkr/symbol-search` | GET | Search for symbols |
| `/api/data/ibkr/pull-historical` | POST | Pull historical data |
| `/api/data/ibkr/pull-options` | POST | Get options chain |
| `/api/data/ibkr/quote` | POST | Get real-time quote |
| `/api/data/query` | GET | Query stored data |
| `/api/data/pull-status/{job_id}` | GET | Check job status |

## Data Storage

Data is stored in Parquet files in `data/market_data/prices/`:

```
data/market_data/prices/
├── ibkr_equities.parquet   # US/international equities
├── ibkr_fx.parquet         # Forex pairs
├── ibkr_futures.parquet    # Futures contracts
└── ibkr_options.parquet    # Options data
```

The catalog is maintained in `data/market_data/catalog.json`.

## Supported Data Types

### Equities
- **Securities**: US stocks, ETFs
- **Intervals**: 1 sec, 1 min, 5 mins, 15 mins, 30 mins, 1 hour, 1 day
- **Duration**: Up to 2 years (longer durations may have gaps)
- **Exchange**: SMART (default), direct exchanges

### Forex
- **Pairs**: Major (EURUSD, GBPUSD, etc.), Minor
- **Intervals**: 1 sec, 1 min, 5 mins, 1 hour, 1 day
- **Exchange**: IDEALPRO (IBKR's forex platform)
- **Note**: More reliable than yfinance for forex

### Futures
- **Contracts**: ES, NQ, CL, GC, etc.
- **Exchange**: CME, NYMEX, COMEX, etc.
- **Note**: Requires futures subscription in IBKR

### Options
- **Data**: Chains with strikes and expirations
- **Use case**: IV analysis, options pricing
- **Note**: Requires options subscription

## Rate Limits

- IBKR allows approximately 50 requests per second
- The code includes automatic rate limiting (0.2-0.3s delays)
- For bulk fetches, use the background job endpoint

## Troubleshooting

### "Could not connect to IBKR"

1. Is IB Gateway running?
2. Did you enable API access in settings?
3. Is the port correct (7497 paper, 7496 live)?
4. Did you approve the connection in IB Gateway?

### "No market data subscription"

1. Check your subscriptions in Account Settings
2. Some data requires specific subscriptions
3. As IBKR Pro, you may have fee-waived subscriptions

### "No data returned"

1. Check the symbol is correct
2. Verify you have subscription for that market
3. Try a different exchange (e.g., "NASDAQ" instead of "SMART")

### Data gaps or missing dates

1. Market may have been closed (weekends, holidays)
2. Some historical data may not be available
3. Use `validate_data()` to check quality

## Configuration

Edit `config/app_config.yaml` to configure the IBKR connection:

```yaml
ibkr:
  host: "127.0.0.1"
  port: 7497  # 7497 for paper, 7496 for live
  client_id: 1
  timeout: 30
```

## Cost Savings

Using IBKR's fee-waived subscriptions can save significantly:

| Data Source | Typical Cost | IBKR Pro Cost |
|-------------|--------------|---------------|
| Daily equity data | $5-10/month | $0 |
| Intraday data | $20-50/month | $0 |
| Forex data | $5-15/month | $0 |
| Futures data | $10-30/month | $0 |
| Options chains | $10-20/month | $0 |

## Best Practices

1. **Keep IB Gateway running** - It must be active to fetch data
2. **Log in regularly** - Market data subscriptions expire after 60 days
3. **Use incremental updates** - Only fetch new data to save time
4. **Validate data** - Check quality after pulling
5. **Back up data** - Parquet files can be backed up to cloud storage
6. **Use paper trading first** - Test with port 7497 before live

## Notes

- **IB Gateway must remain running** while fetching data
- **Market data subscriptions** are managed by IBKR, not this app
- **60-day rule**: Log into IBKR at least every 60 days to keep subscriptions active
- **Data accuracy**: IBKR data comes directly from exchanges, more reliable than free sources
