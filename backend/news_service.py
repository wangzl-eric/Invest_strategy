"""News service using IBKR API as primary source.

This module provides a high-level interface for fetching news data through
Interactive Brokers' TWS API. It supports equity, forex, futures, and index
news, as well as market-wide bulletins.

Reference: https://www.interactivebrokers.com/en/trading/ib-api.php
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

import pandas as pd

from backend.ibkr_client import IBKRClient, NEWS_PROVIDERS

logger = logging.getLogger(__name__)


class NewsService:
    """Service for fetching news from IBKR API.

    This service provides a unified interface for retrieving news data
    across different asset classes via Interactive Brokers' TWS API.

    Example:
        >>> service = NewsService()
        >>> articles = await service.get_equity_news("AAPL", max_articles=5)
        >>> for article in articles:
        ...     print(f"{article['title']} - {article['source']}")
    """

    def __init__(self, ib_client: Optional[IBKRClient] = None):
        """Initialize news service.

        Args:
            ib_client: IBKRClient instance. If not provided, a new one
                      will be created when needed.
        """
        self._ib_client = ib_client

    @property
    def ib_client(self) -> IBKRClient:
        """Get or create IBKR client."""
        if self._ib_client is None:
            self._ib_client = IBKRClient()
        return self._ib_client

    async def get_equity_news(
        self,
        symbol: str,
        max_articles: int = 10,
        provider_code: str = "IBKR",
    ) -> List[Dict[str, Any]]:
        """Get news for an equity symbol.

        Args:
            symbol: Stock ticker (e.g., "AAPL", "MSFT", "GOOGL")
            max_articles: Maximum number of articles to return
            provider_code: News provider code (default: "IBKR")

        Returns:
            List of news articles with keys:
            - id: Article ID
            - title: Article headline
            - source: News source
            - timestamp: Publication timestamp
            - summary: Article summary
            - url: Link to full article
        """
        return await self.ib_client.get_news_articles(
            symbol=symbol,
            sec_type="STK",
            exchange="SMART",
            currency="USD",
            provider_code=provider_code,
            max_articles=max_articles,
        )

    async def get_equity_news_df(
        self,
        symbol: str,
        max_articles: int = 10,
        provider_code: str = "IBKR",
    ) -> pd.DataFrame:
        """Get news for an equity symbol as a DataFrame.

        Args:
            symbol: Stock ticker (e.g., "AAPL", "MSFT")
            max_articles: Maximum number of articles to return
            provider_code: News provider code (default: "IBKR")

        Returns:
            DataFrame with columns: [date, title, source, url]
        """
        return await self.ib_client.get_news_for_contract(
            symbol=symbol,
            sec_type="STK",
            exchange="SMART",
            currency="USD",
        )

    async def get_forex_news(
        self,
        pair: str,
        max_articles: int = 10,
        provider_code: str = "IBKR",
    ) -> List[Dict[str, Any]]:
        """Get news for a forex pair.

        Args:
            pair: Forex pair (e.g., "EURUSD", "GBPUSD", "USDJPY")
            max_articles: Maximum number of articles to return
            provider_code: News provider code (default: "IBKR")

        Returns:
            List of news articles
        """
        # Extract currencies from pair
        base = pair[:3]
        quote = pair[3:] if len(pair) > 3 else "USD"

        return await self.ib_client.get_news_articles(
            symbol=pair,
            sec_type="CASH",
            exchange="IDEALPRO",
            currency=quote,
            provider_code=provider_code,
            max_articles=max_articles,
        )

    async def get_futures_news(
        self,
        symbol: str,
        exchange: str = "CME",
        currency: str = "USD",
        max_articles: int = 10,
        provider_code: str = "IBKR",
    ) -> List[Dict[str, Any]]:
        """Get news for a futures contract.

        Args:
            symbol: Futures symbol (e.g., "ES" (E-mini S&P 500),
                   "CL" (Crude Oil), "GC" (Gold))
            exchange: Exchange (CME, NYMEX, COMEX, EUREX, etc.)
            currency: Contract currency
            max_articles: Maximum number of articles to return
            provider_code: News provider code (default: "IBKR")

        Returns:
            List of news articles
        """
        return await self.ib_client.get_news_articles(
            symbol=symbol,
            sec_type="FUT",
            exchange=exchange,
            currency=currency,
            provider_code=provider_code,
            max_articles=max_articles,
        )

    async def get_index_news(
        self,
        symbol: str,
        exchange: str = "CME",
        currency: str = "USD",
        max_articles: int = 10,
        provider_code: str = "IBKR",
    ) -> List[Dict[str, Any]]:
        """Get news for an index.

        Args:
            symbol: Index symbol (e.g., "SPX" (S&P 500), "NDX" (Nasdaq 100),
                   "DJI" (Dow Jones), "VIX")
            exchange: Exchange where index is traded
            currency: Contract currency
            max_articles: Maximum number of articles to return
            provider_code: News provider code (default: "IBKR")

        Returns:
            List of news articles
        """
        return await self.ib_client.get_news_articles(
            symbol=symbol,
            sec_type="IND",
            exchange=exchange,
            currency=currency,
            provider_code=provider_code,
            max_articles=max_articles,
        )

    async def get_market_bulletins(
        self,
        all_messages: bool = True,
    ) -> List[Dict[str, Any]]:
        """Get IBKR market bulletins.

        These are system-wide news messages from Interactive Brokers
        including market events, trading halts, exchange notices,
        regulatory updates, etc.

        Args:
            all_messages: If True, get all messages; if False, only new ones

        Returns:
            List of bulletins with keys:
            - msg_id: Bulletin ID
            - timestamp: Bulletin timestamp
            - headline: Bulletin headline
            - message: Bulletin content
            - exchange: Affected exchange
        """
        return await self.ib_client.get_market_bulletins(all_messages)

    async def get_portfolio_news(
        self,
        symbols: List[str],
        max_articles_per_symbol: int = 3,
        provider_code: str = "IBKR",
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get news for multiple symbols (e.g., portfolio holdings).

        Args:
            symbols: List of ticker symbols
            max_articles_per_symbol: Max articles per symbol
            provider_code: News provider code (default: "IBKR")

        Returns:
            Dictionary mapping symbols to their news articles
        """
        results = {}

        for symbol in symbols:
            try:
                articles = await self.get_equity_news(
                    symbol,
                    max_articles=max_articles_per_symbol,
                    provider_code=provider_code,
                )
                results[symbol] = articles
            except Exception as e:
                logger.warning(f"Failed to get news for {symbol}: {e}")
                results[symbol] = []

        return results

    def get_available_providers(self) -> Dict[str, str]:
        """Get list of available news providers.

        Returns:
            Dictionary of provider codes to descriptions

        Note:
            Some providers may require specific IBKR market data subscriptions.
            The "IBKR" provider is free and available to all IBKR clients.
        """
        return NEWS_PROVIDERS.copy()

    async def connect(self) -> bool:
        """Connect to IBKR.

        Returns:
            True if connected successfully
        """
        return await self.ib_client.connect()

    async def disconnect(self):
        """Disconnect from IBKR."""
        await self.ib_client.disconnect()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
