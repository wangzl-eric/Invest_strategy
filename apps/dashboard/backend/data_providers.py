"""Data provider interfaces for market data from multiple sources."""
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class MarketDataProvider(ABC):
    """Abstract interface for market data providers."""

    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Get historical price data."""
        pass

    @abstractmethod
    def get_quote(self, symbol: str) -> Dict:
        """Get current quote for a symbol."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of this provider."""
        pass


class YahooFinanceProvider(MarketDataProvider):
    """Yahoo Finance data provider."""

    def __init__(self):
        try:
            import yfinance as yf

            self.yf = yf
        except ImportError:
            logger.error("yfinance not installed")
            self.yf = None

    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Get historical data from Yahoo Finance."""
        if not self.yf:
            return pd.DataFrame()

        try:
            ticker = self.yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval=interval)
            return data
        except Exception as e:
            logger.error(f"Error fetching data from Yahoo Finance for {symbol}: {e}")
            return pd.DataFrame()

    def get_quote(self, symbol: str) -> Dict:
        """Get current quote from Yahoo Finance."""
        if not self.yf:
            return {}

        try:
            ticker = self.yf.Ticker(symbol)
            info = ticker.info
            quote = {
                "symbol": symbol,
                "price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "change": info.get("regularMarketChange"),
                "change_percent": info.get("regularMarketChangePercent"),
                "volume": info.get("volume"),
                "market_cap": info.get("marketCap"),
            }
            return quote
        except Exception as e:
            logger.error(f"Error fetching quote from Yahoo Finance for {symbol}: {e}")
            return {}

    def get_provider_name(self) -> str:
        return "Yahoo Finance"


class IBKRProvider(MarketDataProvider):
    """Interactive Brokers data provider.

    This provider uses the IBKR API (via ib_insync) to fetch market data.
    It requires IB Gateway or TWS to be running with API access enabled.

    Advantages over Yahoo Finance:
    - More accurate data (direct from exchange)
    - Intraday data (1-minute bars)
    - Forex data (more reliable than yfinance)
    - Futures data
    - Options chains

    Requirements:
    - IB Gateway or TWS running on localhost (port 7497 for paper, 7496 for live)
    - API access enabled in TWS/Gateway settings
    - Market data subscriptions for the requested instruments
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 7497, client_id: int = 1):
        """Initialize IBKR provider.

        Args:
            host: IB Gateway/TWS host (default: 127.0.0.1)
            port: IB Gateway/TWS port (default: 7497 for paper trading)
            client_id: Client ID for API connection (default: 1)
        """
        self.host = host
        self.port = port
        self.client_id = client_id
        self._ib = None
        self._connected = False
        self._client = None

    def _get_client(self):
        """Get or create the IBKR client."""
        if self._client is None:
            from backend.ibkr_client import IBKRClient

            self._client = IBKRClient()
        return self._client

    async def _ensure_connected(self) -> bool:
        """Ensure connection to IBKR."""
        client = self._get_client()
        return await client.ensure_connected()

    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Get historical data from IBKR.

        Args:
            symbol: Ticker symbol (e.g., "AAPL", "EURUSD")
            start_date: Start date
            end_date: End date
            interval: Bar size - "1d", "1h", "5m", "1m", etc.

        Returns:
            DataFrame with OHLCV data
        """
        import asyncio

        # Map interval to IBKR format
        ibkr_interval = self._map_interval(interval)

        # Calculate duration based on date range
        days_diff = (end_date - start_date).days
        if days_diff <= 7:
            duration = f"{days_diff + 1} D"
        elif days_diff <= 30:
            duration = "1 M"
        elif days_diff <= 90:
            duration = "3 M"
        elif days_diff <= 365:
            duration = "1 Y"
        else:
            duration = "2 Y"

        # Determine security type
        sec_type = "STK"
        exchange = "SMART"

        # Check if it's forex (contains / or is a currency pair)
        if "/" in symbol or symbol in [
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "USDCAD",
            "USDCHF",
            "AUDUSD",
            "NZDUSD",
        ]:
            sec_type = "CASH"
            exchange = "IDEALPRO"

        # Check if it's a futures symbol
        futures_symbols = [
            "ES",
            "NQ",
            "YM",
            "RTY",
            "CL",
            "GC",
            "SI",
            "NG",
            "ZB",
            "ZN",
            "ZF",
            "ZT",
            "HE",
            "LE",
            "ZS",
            "ZM",
            "ZO",
        ]
        if symbol in futures_symbols:
            sec_type = "FUT"
            exchange = "CME"

        try:
            # Run async method synchronously
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we need to handle differently
                # For now, return empty and let caller use async version
                logger.warning(
                    "IBKRProvider.get_historical_data called in async context - use async version instead"
                )
                return pd.DataFrame()

            client = self._get_client()
            result = loop.run_until_complete(
                client.get_historical_data(
                    symbol=symbol,
                    sec_type=sec_type,
                    exchange=exchange,
                    duration=duration,
                    interval=ibkr_interval,
                    start_date=start_date,
                    end_date=end_date,
                )
            )
            return result
        except Exception as e:
            logger.error(f"Error fetching IBKR data for {symbol}: {e}")
            return pd.DataFrame()

    def get_quote(self, symbol: str) -> Dict:
        """Get current quote from IBKR.

        Args:
            symbol: Ticker symbol

        Returns:
            Dict with bid, ask, last, volume, etc.
        """
        import asyncio

        sec_type = "STK"
        exchange = "SMART"

        if "/" in symbol or symbol in [
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "USDCAD",
            "USDCHF",
            "AUDUSD",
            "NZDUSD",
        ]:
            sec_type = "CASH"
            exchange = "IDEALPRO"

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                logger.warning(
                    "IBKRProvider.get_quote called in async context - use async version instead"
                )
                return {}

            client = self._get_client()
            result = loop.run_until_complete(
                client.get_quote(symbol, sec_type, exchange)
            )
            return result
        except Exception as e:
            logger.error(f"Error fetching IBKR quote for {symbol}: {e}")
            return {}

    def get_provider_name(self) -> str:
        return "Interactive Brokers"

    def _map_interval(self, interval: str) -> str:
        """Map common interval names to IBKR format."""
        interval_map = {
            "1m": "1 min",
            "2m": "2 mins",
            "3m": "3 mins",
            "5m": "5 mins",
            "10m": "10 mins",
            "15m": "15 mins",
            "30m": "30 mins",
            "1h": "1 hour",
            "2h": "2 hours",
            "3h": "3 hours",
            "4h": "4 hours",
            "8h": "8 hours",
            "1d": "1 day",
            "1w": "1 week",
            "1mo": "1 month",
        }
        return interval_map.get(interval.lower(), "1 day")

    async def get_historical_data_async(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Async version of get_historical_data."""
        if not await self._ensure_connected():
            logger.error("Could not connect to IBKR")
            return pd.DataFrame()

        ibkr_interval = self._map_interval(interval)

        days_diff = (end_date - start_date).days
        if days_diff <= 7:
            duration = f"{days_diff + 1} D"
        elif days_diff <= 30:
            duration = "1 M"
        elif days_diff <= 90:
            duration = "3 M"
        elif days_diff <= 365:
            duration = "1 Y"
        else:
            duration = "2 Y"

        sec_type = "STK"
        exchange = "SMART"

        if "/" in symbol or symbol in [
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "USDCAD",
            "USDCHF",
            "AUDUSD",
            "NZDUSD",
        ]:
            sec_type = "CASH"
            exchange = "IDEALPRO"

        try:
            client = self._get_client()
            return await client.get_historical_data(
                symbol=symbol,
                sec_type=sec_type,
                exchange=exchange,
                duration=duration,
                interval=ibkr_interval,
                start_date=start_date,
                end_date=end_date,
            )
        except Exception as e:
            logger.error(f"Error fetching IBKR data for {symbol}: {e}")
            return pd.DataFrame()

    async def get_quote_async(self, symbol: str) -> Dict:
        """Async version of get_quote."""
        if not await self._ensure_connected():
            return {}

        sec_type = "STK"
        exchange = "SMART"

        if "/" in symbol or symbol in [
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "USDCAD",
            "USDCHF",
            "AUDUSD",
            "NZDUSD",
        ]:
            sec_type = "CASH"
            exchange = "IDEALPRO"

        try:
            client = self._get_client()
            return await client.get_quote(symbol, sec_type, exchange)
        except Exception as e:
            logger.error(f"Error fetching IBKR quote for {symbol}: {e}")
            return {}


class PolygonProvider(MarketDataProvider):
    """Polygon.io data provider."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or None
        # TODO: Implement Polygon.io client

    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Get historical data from Polygon.io."""
        # TODO: Implement
        logger.warning("Polygon.io provider not yet implemented")
        return pd.DataFrame()

    def get_quote(self, symbol: str) -> Dict:
        """Get current quote from Polygon.io."""
        # TODO: Implement
        return {}

    def get_provider_name(self) -> str:
        return "Polygon.io"


class DataProviderManager:
    """Manages multiple market data providers."""

    def __init__(self):
        self.providers: Dict[str, MarketDataProvider] = {}
        self.default_provider: Optional[str] = None

    def register_provider(
        self, provider_id: str, provider: MarketDataProvider, set_default: bool = False
    ):
        """Register a data provider."""
        self.providers[provider_id] = provider
        if set_default or self.default_provider is None:
            self.default_provider = provider_id
        logger.info(
            f"Registered data provider: {provider_id} ({provider.get_provider_name()})"
        )

    def get_provider(
        self, provider_id: Optional[str] = None
    ) -> Optional[MarketDataProvider]:
        """Get a provider by ID, or default if not specified."""
        provider_id = provider_id or self.default_provider
        return self.providers.get(provider_id) if provider_id else None

    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        provider_id: Optional[str] = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Get historical data from specified or default provider."""
        provider = self.get_provider(provider_id)
        if not provider:
            logger.warning(f"No data provider available (requested: {provider_id})")
            return pd.DataFrame()

        return provider.get_historical_data(symbol, start_date, end_date, interval)

    def get_quote(self, symbol: str, provider_id: Optional[str] = None) -> Dict:
        """Get quote from specified or default provider."""
        provider = self.get_provider(provider_id)
        if not provider:
            return {}

        return provider.get_quote(symbol)

    # ---------------------------------------------------------------------------
    # Fallback methods
    # ---------------------------------------------------------------------------

    def get_historical_data_with_fallback(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        asset_class: str,
        interval: str = "1d",
    ) -> Dict:
        """Get historical data with automatic fallback.

        Tries providers in order of priority until one succeeds.

        Args:
            symbol: Ticker symbol
            start_date: Start date
            end_date: End date
            asset_class: Asset class (equity, fx, rates, commodities)
            interval: Data interval (1d, 1h, 5m, etc.)

        Returns:
            Dict with keys: data, source_used, fallback_reason, success
        """
        # Try each provider in order
        for provider_id in self._get_priority_order(asset_class):
            provider = self.providers.get(provider_id)
            if not provider:
                continue

            try:
                data = provider.get_historical_data(
                    symbol, start_date, end_date, interval
                )
                if not data.empty:
                    return {
                        "data": data,
                        "source_used": provider_id,
                        "fallback_reason": None,
                        "success": True,
                    }
            except Exception as e:
                logger.debug(f"Provider {provider_id} failed for {symbol}: {e}")
                continue

        # All providers failed
        return {
            "data": pd.DataFrame(),
            "source_used": None,
            "fallback_reason": f"All providers failed for {symbol}",
            "success": False,
        }

    def get_quote_with_fallback(self, symbol: str, asset_class: str) -> Dict:
        """Get quote with automatic fallback.

        Args:
            symbol: Ticker symbol
            asset_class: Asset class for priority ordering

        Returns:
            Dict with keys: quote, source_used, fallback_reason, success
        """
        for provider_id in self._get_priority_order(asset_class):
            provider = self.providers.get(provider_id)
            if not provider:
                continue

            try:
                quote = provider.get_quote(symbol)
                if quote:
                    return {
                        "quote": quote,
                        "source_used": provider_id,
                        "fallback_reason": None,
                        "success": True,
                    }
            except Exception as e:
                logger.debug(f"Provider {provider_id} failed for quote {symbol}: {e}")
                continue

        return {
            "quote": {},
            "source_used": None,
            "fallback_reason": f"All providers failed for quote {symbol}",
            "success": False,
        }

    def _get_priority_order(self, asset_class: str) -> List[str]:
        """Get provider priority order for an asset class.

        Tries to use the data_source_manager if available, otherwise uses defaults.
        """
        try:
            from backend.data_source_manager import DataSource, data_source_manager

            # Map provider IDs to data sources
            source_to_provider = {
                DataSource.YFINANCE: "yahoo",
                DataSource.IBKR: "ibkr",
            }

            # Get priority sources from manager
            sources = data_source_manager.get_priority_order(asset_class)
            return [
                source_to_provider.get(s, s.value)
                for s in sources
                if s in source_to_provider
            ]
        except ImportError:
            # Fallback to default order
            if asset_class in ["equity", "fx", "commodities"]:
                return ["ibkr", "yahoo"]
            elif asset_class in ["rates", "macro"]:
                return ["yahoo"]
            return ["yahoo"]

    def get_provider_status(self) -> Dict[str, Dict]:
        """Get status of all registered providers."""
        status = {}
        for provider_id, provider in self.providers.items():
            status[provider_id] = {
                "name": provider.get_provider_name(),
                "available": True,  # Would need health check to determine actual status
            }
        return status


# Global data provider manager
data_provider_manager = DataProviderManager()

# Register default providers
try:
    yahoo_provider = YahooFinanceProvider()
    data_provider_manager.register_provider("yahoo", yahoo_provider, set_default=True)
except Exception as e:
    logger.warning(f"Could not register Yahoo Finance provider: {e}")

# Register IBKR provider (requires IB Gateway/TWS to be running)
try:
    from backend.config import settings

    ibkr_provider = IBKRProvider(
        host=settings.ibkr.host,
        port=settings.ibkr.port,
        client_id=settings.ibkr.client_id,
    )
    data_provider_manager.register_provider("ibkr", ibkr_provider)
except Exception as e:
    logger.warning(f"Could not register IBKR provider: {e}")
