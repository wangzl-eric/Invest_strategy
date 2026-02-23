"""Data provider interfaces for market data from multiple sources."""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime, timedelta
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
        interval: str = "1d"
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
        interval: str = "1d"
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
        interval: str = "1d"
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
    
    def register_provider(self, provider_id: str, provider: MarketDataProvider, set_default: bool = False):
        """Register a data provider."""
        self.providers[provider_id] = provider
        if set_default or self.default_provider is None:
            self.default_provider = provider_id
        logger.info(f"Registered data provider: {provider_id} ({provider.get_provider_name()})")
    
    def get_provider(self, provider_id: Optional[str] = None) -> Optional[MarketDataProvider]:
        """Get a provider by ID, or default if not specified."""
        provider_id = provider_id or self.default_provider
        return self.providers.get(provider_id) if provider_id else None
    
    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        provider_id: Optional[str] = None,
        interval: str = "1d"
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


# Global data provider manager
data_provider_manager = DataProviderManager()

# Register default providers
try:
    yahoo_provider = YahooFinanceProvider()
    data_provider_manager.register_provider("yahoo", yahoo_provider, set_default=True)
except Exception as e:
    logger.warning(f"Could not register Yahoo Finance provider: {e}")
