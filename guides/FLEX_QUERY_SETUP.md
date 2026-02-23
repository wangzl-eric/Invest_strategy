# IBKR Flex Query Setup Guide

This guide explains how to set up and use IBKR Flex Queries to fetch historical trade data.

## Why Flex Queries?

The TWS API (`ib_insync`) only returns trades from the **current session**. For historical trade data beyond today, you need Flex Queries.

| Method | Data Available |
|--------|---------------|
| TWS API | Current session trades only |
| Flex Queries | Up to 365 days of trade history |

## Quick Start

### Step 1: Create a Flex Query in IBKR

1. **Log into IBKR Account Management**
   - Go to: https://www.interactivebrokers.com/sso/Login

2. **Navigate to Flex Queries**
   - Menu: **Performance & Reports → Flex Queries → Activity Flex Query**

3. **Create New Query**
   - Click **"Create"** or **"+"**
   - Give it a name: e.g., `TradeHistory`
   - Set date period: Last 365 days (or custom)
   
4. **Configure Query Sections**
   Enable these sections:
   - ✅ **Trades** (required for trade history)
   - ✅ **Open Positions** (optional)
   - ✅ **Cash Transactions** (optional, for dividends/deposits)
   
5. **Save and Note the Query ID**
   - After saving, you'll see a **Query ID** (e.g., `123456`)
   - Note this down

### Step 2: Generate a Flex Web Service Token

1. In Flex Queries page, click **"Configure Flex Web Service"**
2. Click **"Generate Token"**
3. Set token validity to **365 days**
4. **Copy the token** (shown only once!)

### Step 3: Configure Your App

Edit `config/app_config.yaml`:

```yaml
flex_query:
  token: "your_flex_token_here"  # The token you generated
  trade_query_id: "123456"       # Your Query ID for trades
  position_query_id: ""          # Optional: separate query for positions
  activity_query_id: ""          # Optional: combined query
```

### Step 4: Fetch Trade History

**Option A: Via API (Recommended)**

```bash
# Check if configured
curl http://localhost:8000/api/flex-query/status

# Fetch trades
curl -X POST "http://localhost:8000/api/flex-query/fetch-trades"

# Fetch all data (trades + positions + cash)
curl -X POST "http://localhost:8000/api/flex-query/fetch-all"
```

**Option B: Via Swagger UI**

1. Open http://localhost:8000/docs
2. Find `/api/flex-query/fetch-trades`
3. Click "Try it out" → "Execute"

**Option C: Via Python Script**

```python
import asyncio
from backend.flex_query_client import FlexQueryClient
from backend.flex_importer import import_flex_query_result

async def fetch_trades():
    client = FlexQueryClient(token="your_token")
    result = await client.fetch_statement(query_id="123456")
    
    # Import to database
    import_result = import_flex_query_result(result)
    print(f"Imported {import_result['trades_imported']} trades")
    
    # Or access directly
    for trade in result.trades:
        print(f"{trade.trade_date}: {trade.side} {trade.quantity} {trade.symbol} @ {trade.price}")

asyncio.run(fetch_trades())
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/flex-query/status` | GET | Check if Flex Query is configured |
| `/api/flex-query/fetch-trades` | POST | Fetch and import trade history |
| `/api/flex-query/fetch-all` | POST | Fetch trades, positions, and cash transactions |

### Query Parameters

Both fetch endpoints accept optional parameters:

- `query_id` - Override the configured Query ID
- `token` - Override the configured token (useful for testing)

Example:
```bash
curl -X POST "http://localhost:8000/api/flex-query/fetch-trades?query_id=789012"
```

## Data Retrieved

### Trades (FlexTrade)
- Account ID, Trade ID, Execution ID
- Symbol, Description, Security Type
- Trade Date/Time, Settlement Date
- Side (BUY/SELL), Quantity, Price
- Proceeds, Commission, Tax
- Realized P&L

### Positions (FlexPosition)
- Symbol, Quantity
- Cost Basis (price and money)
- Market Price, Market Value
- Unrealized P&L, Realized P&L

### Cash Transactions (FlexCashTransaction)
- Date, Amount, Currency
- Type (Dividend, Deposit, Withdrawal, etc.)
- Description

## Recommended Flex Query Configuration

For a comprehensive trade history query, enable these fields in IBKR:

**Trade Section:**
- accountId, tradeID, ibExecID
- symbol, description, assetCategory
- tradeDate, tradeTime, settleDateTarget
- buySell, quantity, tradePrice
- proceeds, ibCommission, taxes
- cost, fifoPnlRealized
- currency, exchange, orderType

**Open Positions Section:**
- symbol, position, markPrice
- positionValue, costBasisPrice, costBasisMoney
- fifoPnlUnrealized, fifoPnlRealized

## Troubleshooting

### "Flex Query request failed"
- Verify your token is valid and not expired
- Check the Query ID is correct
- Ensure the query is active in IBKR

### "Statement still generating"
- Large date ranges take longer to generate
- The system will retry automatically (up to 10 times)

### "No trades found"
- Verify the query includes the "Trades" section
- Check the date range in your query configuration
- Make sure you have trades in that period

### Token Expired
- Tokens are valid for 1 year by default
- Generate a new token in IBKR Account Management
- Update `config/app_config.yaml`

## Security Notes

⚠️ **Keep your Flex token secure!**
- Don't commit it to version control
- Consider using environment variables: `FLEX_TOKEN=xxx`
- The token allows read-only access to your account data

## Example: Scheduled Daily Import

Add to your scheduler or cron job:

```python
# scripts/daily_flex_import.py
import asyncio
import logging
from backend.flex_query_client import FlexQueryClient
from backend.flex_importer import import_flex_query_result
from backend.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def daily_import():
    if not settings.flex_query.is_configured:
        logger.error("Flex Query not configured")
        return
    
    client = FlexQueryClient(token=settings.flex_query.token)
    query_id = settings.flex_query.trade_query_id or settings.flex_query.activity_query_id
    
    try:
        result = await client.fetch_statement(query_id)
        import_result = import_flex_query_result(result)
        logger.info(f"Daily import complete: {import_result}")
    except Exception as e:
        logger.error(f"Daily import failed: {e}")

if __name__ == "__main__":
    asyncio.run(daily_import())
```

Run daily:
```bash
# Add to crontab
0 6 * * * cd /path/to/project && conda run -n ibkr-analytics python scripts/daily_flex_import.py
```
