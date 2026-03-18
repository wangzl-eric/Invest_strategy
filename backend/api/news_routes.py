"""News API routes for fetching news from IBKR.

Reference: https://www.interactivebrokers.com/en/trading/ib-api.php
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ibkr_client import NEWS_PROVIDERS, IBKRClient
from backend.news_service import NewsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/news", tags=["news"])


# ============== Request/Response Models ==============


class EquityNewsRequest(BaseModel):
    """Request model for equity news."""

    symbol: str
    max_articles: int = 10
    provider_code: str = "IBKR"


class ForexNewsRequest(BaseModel):
    """Request model for forex news."""

    pair: str  # e.g., "EURUSD"
    max_articles: int = 10
    provider_code: str = "IBKR"


class FuturesNewsRequest(BaseModel):
    """Request model for futures news."""

    symbol: str  # e.g., "ES", "CL", "GC"
    exchange: str = "CME"
    currency: str = "USD"
    max_articles: int = 10
    provider_code: str = "IBKR"


class IndexNewsRequest(BaseModel):
    """Request model for index news."""

    symbol: str  # e.g., "SPX", "NDX", "VIX"
    exchange: str = "CME"
    currency: str = "USD"
    max_articles: int = 10
    provider_code: str = "IBKR"


class PortfolioNewsRequest(BaseModel):
    """Request model for portfolio news."""

    symbols: List[str]
    max_articles_per_symbol: int = 3
    provider_code: str = "IBKR"


class NewsResponse(BaseModel):
    """Response model for news articles."""

    articles: List[dict]
    symbol: str
    count: int


class BulletinResponse(BaseModel):
    """Response model for market bulletins."""

    bulletins: List[dict]
    count: int


class ProvidersResponse(BaseModel):
    """Response model for available news providers."""

    providers: dict


# ============== API Endpoints ==============


@router.post("/equity", response_model=NewsResponse)
async def get_equity_news(request: EquityNewsRequest):
    """Get news for an equity symbol.

    Example:
        ```json
        {
            "symbol": "AAPL",
            "max_articles": 10,
            "provider_code": "IBKR"
        }
        ```
    """
    client = IBKRClient()
    try:
        await client.connect()
        articles = await client.get_news_articles(
            symbol=request.symbol,
            sec_type="STK",
            exchange="SMART",
            currency="USD",
            provider_code=request.provider_code,
            max_articles=request.max_articles,
        )
        return NewsResponse(
            articles=articles,
            symbol=request.symbol,
            count=len(articles),
        )
    except Exception as e:
        logger.error(f"Error fetching equity news for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.disconnect()


@router.post("/equity/df")
async def get_equity_news_df(request: EquityNewsRequest):
    """Get news for an equity symbol as a DataFrame (JSON format).

    Returns news in a flat DataFrame format with columns:
    [date, title, source, url]
    """
    client = IBKRClient()
    try:
        await client.connect()
        df = await client.get_news_for_contract(
            symbol=request.symbol,
            sec_type="STK",
            exchange="SMART",
            currency="USD",
        )
        # Convert DataFrame to records
        records = df.to_dict(orient="records")
        return {
            "symbol": request.symbol,
            "count": len(records),
            "data": records,
        }
    except Exception as e:
        logger.error(f"Error fetching equity news for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.disconnect()


@router.post("/forex", response_model=NewsResponse)
async def get_forex_news(request: ForexNewsRequest):
    """Get news for a forex pair.

    Example:
        ```json
        {
            "pair": "EURUSD",
            "max_articles": 10,
            "provider_code": "IBKR"
        }
        ```
    """
    client = IBKRClient()
    try:
        await client.connect()
        # Extract quote currency from pair
        quote = request.pair[3:] if len(request.pair) > 3 else "USD"
        articles = await client.get_news_articles(
            symbol=request.pair,
            sec_type="CASH",
            exchange="IDEALPRO",
            currency=quote,
            provider_code=request.provider_code,
            max_articles=request.max_articles,
        )
        return NewsResponse(
            articles=articles,
            symbol=request.pair,
            count=len(articles),
        )
    except Exception as e:
        logger.error(f"Error fetching forex news for {request.pair}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.disconnect()


@router.post("/futures", response_model=NewsResponse)
async def get_futures_news(request: FuturesNewsRequest):
    """Get news for a futures contract.

    Example:
        ```json
        {
            "symbol": "ES",
            "exchange": "CME",
            "currency": "USD",
            "max_articles": 10,
            "provider_code": "IBKR"
        }
        ```
    """
    client = IBKRClient()
    try:
        await client.connect()
        articles = await client.get_news_articles(
            symbol=request.symbol,
            sec_type="FUT",
            exchange=request.exchange,
            currency=request.currency,
            provider_code=request.provider_code,
            max_articles=request.max_articles,
        )
        return NewsResponse(
            articles=articles,
            symbol=request.symbol,
            count=len(articles),
        )
    except Exception as e:
        logger.error(f"Error fetching futures news for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.disconnect()


@router.post("/index", response_model=NewsResponse)
async def get_index_news(request: IndexNewsRequest):
    """Get news for an index.

    Example:
        ```json
        {
            "symbol": "SPX",
            "exchange": "CME",
            "currency": "USD",
            "max_articles": 10,
            "provider_code": "IBKR"
        }
        ```
    """
    client = IBKRClient()
    try:
        await client.connect()
        articles = await client.get_news_articles(
            symbol=request.symbol,
            sec_type="IND",
            exchange=request.exchange,
            currency=request.currency,
            provider_code=request.provider_code,
            max_articles=request.max_articles,
        )
        return NewsResponse(
            articles=articles,
            symbol=request.symbol,
            count=len(articles),
        )
    except Exception as e:
        logger.error(f"Error fetching index news for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.disconnect()


@router.get("/bulletins", response_model=BulletinResponse)
async def get_market_bulletins(all_messages: bool = True):
    """Get IBKR market bulletins.

    These are system-wide news messages from Interactive Brokers
    including market events, trading halts, exchange notices, etc.

    Query Parameters:
        - all_messages: If true, get all messages; if false, only new ones
    """
    client = IBKRClient()
    try:
        await client.connect()
        bulletins = await client.get_market_bulletins(all_messages)
        return BulletinResponse(
            bulletins=bulletins,
            count=len(bulletins),
        )
    except Exception as e:
        logger.error(f"Error fetching market bulletins: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.disconnect()


@router.post("/portfolio")
async def get_portfolio_news(request: PortfolioNewsRequest):
    """Get news for multiple symbols (portfolio holdings).

    Example:
        ```json
        {
            "symbols": ["AAPL", "MSFT", "GOOGL", "AMZN"],
            "max_articles_per_symbol": 3,
            "provider_code": "IBKR"
        }
        ```
    """
    client = IBKRClient()
    try:
        await client.connect()
        service = NewsService(ib_client=client)
        results = await service.get_portfolio_news(
            symbols=request.symbols,
            max_articles_per_symbol=request.max_articles_per_symbol,
            provider_code=request.provider_code,
        )

        # Flatten results for response
        all_articles = []
        for symbol, articles in results.items():
            for article in articles:
                article["symbol"] = symbol
                all_articles.append(article)

        return {
            "symbols": request.symbols,
            "news": results,
            "total_articles": len(all_articles),
        }
    except Exception as e:
        logger.error(f"Error fetching portfolio news: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.disconnect()


@router.get("/providers", response_model=ProvidersResponse)
async def get_news_providers():
    """Get available news providers.

    Returns a dictionary of provider codes and their descriptions.

    Note:
        - "IBKR" is free and available to all clients
        - Some premium providers may require specific market data subscriptions
    """
    return ProvidersResponse(providers=NEWS_PROVIDERS)


# ============== Health Check ==============


@router.get("/health")
async def news_health_check():
    """Health check for news service."""
    return {
        "status": "available",
        "service": "IBKR News API",
        "reference": "https://www.interactivebrokers.com/en/trading/ib-api.php",
    }
