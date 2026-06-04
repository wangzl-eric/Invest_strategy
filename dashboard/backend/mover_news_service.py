"""Market Movers News Service - fetches news for top movers and generates LLM summaries."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.config import settings
from backend.llm_client import MarketMoversLLMClient, generate_movers_news_summary
from backend.news_service import NewsService

logger = logging.getLogger(__name__)

# Cache TTL for mover news summaries (in seconds)
MOVER_NEWS_TTL = 300  # 5 minutes


class MoverNewsService:
    """Service for fetching news on market movers and generating LLM summaries.

    This service:
    1. Takes a list of movers from the "What Changed" panel
    2. Fetches news for each mover via IBKR
    3. Uses LLM to generate a concise market summary
    """

    def __init__(self, news_service: Optional[NewsService] = None):
        """Initialize the mover news service.

        Args:
            news_service: Optional NewsService instance. If not provided,
                         a new one will be created.
        """
        self._news_service = news_service
        self._llm_client = None

        # Check if LLM is configured
        if not settings.llm.is_configured:
            logger.warning(
                "QWEN_API_KEY not configured - LLM summarization will not be available"
            )

    @property
    def news_service(self) -> NewsService:
        """Get or create NewsService instance."""
        if self._news_service is None:
            self._news_service = NewsService()
        return self._news_service

    @property
    def llm_client(self) -> Optional[MarketMoversLLMClient]:
        """Get LLM client if configured."""
        if self._llm_client is None:
            if settings.llm.is_configured:
                self._llm_client = MarketMoversLLMClient()
            else:
                return None
        return self._llm_client

    @property
    def is_llm_configured(self) -> bool:
        """Check if LLM is configured."""
        return settings.llm.is_configured

    async def get_mover_news(
        self,
        movers: List[Dict[str, Any]],
        max_articles_per_ticker: int = 3,
    ) -> Dict[str, Any]:
        """Fetch news for all movers and optionally generate LLM summary.

        Args:
            movers: List of mover dicts with at least 'ticker' key
            max_articles_per_ticker: Max news articles to fetch per ticker

        Returns:
            Dict with:
            - movers: Original movers list
            - news_by_ticker: Dict mapping ticker -> list of news articles
            - llm_summary: Optional LLM-generated summary (if configured)
            - timestamp: ISO timestamp
            - error: Any error message if something failed
        """
        result = {
            "movers": movers,
            "news_by_ticker": {},
            "llm_summary": None,
            "timestamp": datetime.utcnow().isoformat(),
            "error": None,
        }

        if not movers:
            result["error"] = "No movers provided"
            return result

        # Fetch news for each mover in parallel
        tickers = [m.get("ticker") for m in movers if m.get("ticker")]

        if not tickers:
            result["error"] = "No tickers found in movers"
            return result

        # Determine which tickers are equities (for IBKR news)
        equity_tickers = []
        for m in movers:
            ticker = m.get("ticker", "")
            asset_class = m.get("asset_class", "").lower()
            # Only fetch news for stocks/equities via IBKR
            if asset_class in ("equity", "stock", "") and ticker:
                equity_tickers.append(ticker)

        # Fetch news in parallel for equity tickers
        news_tasks = []
        for ticker in equity_tickers[:10]:  # Limit to top 10 movers
            news_tasks.append(self._fetch_ticker_news(ticker, max_articles_per_ticker))

        if news_tasks:
            news_results = await asyncio.gather(*news_tasks, return_exceptions=True)

            for ticker, news in zip(equity_tickers[:10], news_results):
                if isinstance(news, Exception):
                    logger.warning(f"Failed to fetch news for {ticker}: {news}")
                    result["news_by_ticker"][ticker] = []
                else:
                    result["news_by_ticker"][ticker] = news

        # Generate LLM summary if configured
        if self.is_llm_configured and self.llm_client:
            try:
                llm_summary = await self.llm_client.generate_movers_summary(
                    movers=movers,
                    news_articles_by_ticker=result["news_by_ticker"],
                )
                result["llm_summary"] = llm_summary.model_dump()
            except Exception as e:
                logger.error(f"Failed to generate LLM summary: {e}")
                result["error"] = f"LLM summary failed: {str(e)}"
        else:
            result["llm_summary"] = {
                "overall_market_sentiment": "unknown",
                "key_themes": [],
                "top_mover_summaries": [],
                "market_narrative": "LLM not configured - set QWEN_API_KEY in .env",
                "notable_patterns": [],
                "confidence": 0.0,
            }

        return result

    async def _fetch_ticker_news(
        self, ticker: str, max_articles: int = 3
    ) -> List[Dict[str, Any]]:
        """Fetch news for a single ticker.

        Args:
            ticker: Ticker symbol
            max_articles: Max articles to fetch

        Returns:
            List of news articles
        """
        try:
            articles = await self.news_service.get_equity_news(
                symbol=ticker,
                max_articles=max_articles,
            )
            return articles
        except Exception as e:
            logger.debug(f"News fetch error for {ticker}: {e}")
            return []

    def get_mover_news_sync(
        self,
        movers: List[Dict[str, Any]],
        max_articles_per_ticker: int = 3,
    ) -> Dict[str, Any]:
        """Synchronous wrapper for get_mover_news.

        Args:
            movers: List of mover dicts
            max_articles_per_ticker: Max articles per ticker

        Returns:
            Dict with news and optional LLM summary
        """
        try:
            # Try to get existing event loop or create new one
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # We're in an async context, create a new task
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run,
                            self.get_mover_news(movers, max_articles_per_ticker),
                        )
                        return future.result()
                else:
                    return loop.run_until_complete(
                        self.get_mover_news(movers, max_articles_per_ticker)
                    )
            except RuntimeError:
                # No event loop exists
                return asyncio.run(self.get_mover_news(movers, max_articles_per_ticker))
        except Exception as e:
            logger.error(f"Error in get_mover_news_sync: {e}")
            return {
                "movers": movers,
                "news_by_ticker": {},
                "llm_summary": None,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            }


# Global instance
_mover_news_service: Optional[MoverNewsService] = None


def get_mover_news_service() -> MoverNewsService:
    """Get the global MoverNewsService instance."""
    global _mover_news_service
    if _mover_news_service is None:
        _mover_news_service = MoverNewsService()
    return _mover_news_service
