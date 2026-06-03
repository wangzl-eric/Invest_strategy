# IBKR News Pipeline Guide

This guide documents the news data pipeline integrated with Interactive Brokers' TWS API.

## Overview

The platform now supports fetching news data through IBKR's API, providing a free alternative to third-party news services like NewsAPI. This integration is available for equities, forex, futures, and indices, plus market-wide bulletins.

**Reference:** [IBKR API Documentation](https://www.interactivebrokers.com/en/trading/ib-api.php)

---

## IBKR News API

### Available News Data

| Data Type | Description | Example Symbols |
|-----------|-------------|-----------------|
| **Equity News** | Stock-specific news | AAPL, MSFT, GOOGL |
| **Forex News** | Currency pair news | EURUSD, GBPUSD, USDJPY |
| **Futures News** | Futures contract news | ES (S&P 500), CL (Oil), GC (Gold) |
| **Index News** | Index-related news | SPX, NDX, VIX |
| **Market Bulletins** | System-wide announcements | Trading halts, exchange notices |

### News Providers

IBKR supports multiple news providers. The default provider is **IBKR** (free).

| Provider Code | Provider Name | Notes |
|---------------|---------------|-------|
| `IBKR` | IBKR News | **Free** - Available to all clients |
| `DJ` | Dow Jones | Requires market data subscription |
| `BZ` | Benzinga | Requires market data subscription |
| `YA` | Yahoo | Requires market data subscription |
| `X` / `R` | Reuters | Requires market data subscription |
| `NEO` | AEX (Netherlands) | Requires market data subscription |
| `MII` | Merrill | Requires market data subscription |
| `FLY` | Fly (Graham) | Requires market data subscription |
| `RB` | RBC | Requires market data subscription |
| `DK` | Danske | Requires market data subscription |

**Note:** Some premium providers require specific IBKR market data subscriptions. The default `IBKR` provider is free.

---

## API Endpoints

### Get Equity News

```bash
POST /api/news/equity
```

Request:
```json
{
    "symbol": "AAPL",
    "max_articles": 10,
    "provider_code": "IBKR"
}
```

Response:
```json
{
    "articles": [
        {
            "id": "...",
            "title": "Apple Reports Record Q4 Earnings",
            "source": "IBKR",
            "timestamp": 1706832000,
            "summary": "...",
            "url": "..."
        }
    ],
    "symbol": "AAPL",
    "count": 10
}
```

### Get Forex News

```bash
POST /api/news/forex
```

Request:
```json
{
    "pair": "EURUSD",
    "max_articles": 10,
    "provider_code": "IBKR"
}
```

### Get Futures News

```bash
POST /api/news/futures
```

Request:
```json
{
    "symbol": "ES",
    "exchange": "CME",
    "currency": "USD",
    "max_articles": 10
}
```

### Get Index News

```bash
POST /api/news/index
```

Request:
```json
{
    "symbol": "SPX",
    "exchange": "CME",
    "currency": "USD"
}
```

### Get Market Bulletins

```bash
GET /api/news/bulletins?all_messages=true
```

Returns system-wide announcements including:
- Trading halts
- Exchange notices
- Regulatory updates
- Market events

### Get Portfolio News

```bash
POST /api/news/portfolio
```

Request:
```json
{
    "symbols": ["AAPL", "MSFT", "GOOGL", "AMZN"],
    "max_articles_per_symbol": 3
}
```

### Get Available Providers

```bash
GET /api/news/providers
```

---

## Python Usage

### Using the NewsService

```python
from backend.news_service import NewsService

# Create service
service = NewsService()

# Get news for a stock
articles = await service.get_equity_news("AAPL", max_articles=5)

# Get news as DataFrame
df = await service.get_equity_news_df("AAPL")

# Get forex news
forex_articles = await service.get_forex_news("EURUSD")

# Get futures news
futures_articles = await service.get_futures_news("ES", exchange="CME")

# Get market bulletins
bulletins = await service.get_market_bulletins()

# Get portfolio news
portfolio_news = await service.get_portfolio_news(
    symbols=["AAPL", "MSFT", "GOOGL"],
    max_articles_per_symbol=3
)

# Using context manager
async with NewsService() as service:
    articles = await service.get_equity_news("AAPL")
```

### Using IBKRClient Directly

```python
from backend.ibkr_client import IBKRClient

client = IBKRClient()

# Connect
await client.connect()

# Get news for a symbol
articles = await client.get_news_articles(
    symbol="AAPL",
    sec_type="STK",
    exchange="SMART",
    currency="USD",
    provider_code="IBKR",
    max_articles=10
)

# Get market bulletins
bulletins = await client.get_market_bulletins(all_messages=True)

# Disconnect
await client.disconnect()
```

---

## Integration with Drawdown Analyzer

The existing `DrawdownAnalyzer` can be extended to use IBKR news:

```python
from backend.news_service import NewsService
from backend.drawdown_analyzer import DrawdownAnalyzer

# Get portfolio positions
positions = ["AAPL", "MSFT", "GOOGL"]

# Get news for portfolio
service = NewsService()
news = await service.get_portfolio_news(positions)

# Use with drawdown analyzer
analyzer = DrawdownAnalyzer()
# ... existing drawdown analysis ...
```

---

## Known Limitations

1. **Provider Availability**: Not all providers may be available to all account types
2. **Rate Limits**: IBKR may impose rate limits on news requests
3. **Data Freshness**: News may have a slight delay compared to direct news services
4. **Content**: Some articles may have truncated summaries depending on provider

---

## Troubleshooting

### No News Returned
- Verify IBKR connection is active
- Check if the symbol has available news
- Try a different provider code

### Connection Issues
- Ensure TWS or IB Gateway is running
- Verify API port configuration matches IBKR settings
- Check that "Enable ActiveX and Socket Clients" is enabled in TWS

### Premium Providers Not Working
- Verify market data subscription for the provider
- Some providers require specific market data subscriptions

---

## References

- [IBKR API Documentation](https://www.interactivebrokers.com/en/trading/ib-api.php)
- [IBKR API GitHub](https://github.com/InteractiveBrokers/ib-api)
- [ib_insync Documentation](https://ib-insync.readthedocs.io/)
- [IBKR Traders' Academy - API Courses](https://www.interactivebrokers.com/en/trading/ib-api.php)

---

## Files Modified

| File | Description |
|------|-------------|
| `backend/ibkr_client.py` | Added `get_news_articles()`, `get_news_for_contract()`, `get_market_bulletins()` methods + `NEWS_PROVIDERS` constant |
| `backend/news_service.py` | New high-level news service with asset-class-specific methods |
| `backend/api/news_routes.py` | New REST API endpoints for news |
| `backend/main.py` | Registered news routes |
