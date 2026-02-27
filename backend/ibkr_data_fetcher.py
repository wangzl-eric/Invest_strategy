"""IBKR Data Fetcher - Utility scripts for pulling market data from IBKR.

This module provides convenient functions for fetching market data from IBKR
and storing it in the parquet data lake.

Usage:
    # Fetch equities
    from backend.ibkr_data_fetcher import fetch_equities, fetch_forex, fetch_futures
    
    # Pull data for a few symbols
    result = await fetch_equities(["AAPL", "MSFT", "GOOGL"], "1 Y")
    
    # Pull forex data
    result = await fetch_forex(["EURUSD", "GBPUSD"], "1 Y")
    
    # Bulk fetch
    result = await batch_fetch("ibkr_equities", ["AAPL", "MSFT"], "1 Y")
    
    # Validate data quality
    from backend.ibkr_data_fetcher import validate_data, DataQualityReport
    report = validate_data(df)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Default ticker lists
DEFAULT_US_EQUITIES = [
    # Large Cap Tech
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
    # Financials
    "JPM", "BAC", "WFC", "GS", "MS",
    # Healthcare
    "JNJ", "UNH", "PFE", "MRK", "ABT",
    # Consumer
    "PG", "KO", "PEP", "COST", "WMT",
    # Energy
    "XOM", "CVX", "COP",
    # Industrials
    "BA", "CAT", "GE", "MMM",
    # More Tech
    "NFLX", "ADBE", "CRM", "ORCL", "INTC",
    # ETFs
    "SPY", "QQQ", "IWM", "DIA",
]

DEFAULT_FOREX_PAIRS = [
    # Major pairs
    "EURUSD", "GBPUSD", "USDJPY", "USDCAD", "USDCHF", "AUDUSD", "NZDUSD",
    # Minor pairs
    "EURGBP", "EURJPY", "GBPJPY", "EURCHF", "AUDJPY", "CADJPY",
]

DEFAULT_FUTURES = [
    # Equity Index
    "ES", "NQ", "YM", "RTY",
    # Energy
    "CL", "BZ", "NG",
    # Metals
    "GC", "SI", "HG",
    # Bonds
    "ZB", "ZN", "ZF", "ZT",
]


# ---------------------------------------------------------------------------
# IBKR Client Wrapper
# ---------------------------------------------------------------------------

class IBKRDataFetcher:
    """Wrapper for fetching data from IBKR."""
    
    def __init__(self):
        self._client = None
    
    async def _get_client(self):
        if self._client is None:
            from backend.ibkr_client import IBKRClient
            self._client = IBKRClient()
        return self._client
    
    async def fetch_equities(
        self,
        symbols: List[str],
        duration: str = "1 Y",
        interval: str = "1 day",
        exchange: str = "SMART"
    ) -> Dict[str, pd.DataFrame]:
        """Fetch equity data.
        
        Args:
            symbols: List of stock symbols
            duration: How far back (e.g., "1 Y", "6 M", "30 D")
            interval: Bar interval (e.g., "1 day", "1 min", "5 mins")
            exchange: Exchange (default: SMART)
            
        Returns:
            Dict mapping symbol to DataFrame with OHLCV data
        """
        client = await self._get_client()
        
        if not await client.ensure_connected():
            raise ConnectionError("Could not connect to IBKR")
        
        results = {}
        
        for symbol in symbols:
            try:
                df = await client.get_historical_data(
                    symbol=symbol,
                    sec_type="STK",
                    exchange=exchange,
                    duration=duration,
                    interval=interval
                )
                
                if not df.empty:
                    results[symbol] = df
                    logger.info(f"Fetched {len(df)} bars for {symbol}")
                else:
                    logger.warning(f"No data returned for {symbol}")
                
                # Rate limiting
                await asyncio.sleep(0.2)
                
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
        
        return results
    
    async def fetch_forex(
        self,
        pairs: List[str],
        duration: str = "1 Y",
        interval: str = "1 day"
    ) -> Dict[str, pd.DataFrame]:
        """Fetch forex data.
        
        Args:
            pairs: List of forex pairs (e.g., "EURUSD", "GBPUSD")
            duration: How far back
            interval: Bar interval
            
        Returns:
            Dict mapping pair to DataFrame
        """
        client = await self._get_client()
        
        if not await client.ensure_connected():
            raise ConnectionError("Could not connect to IBKR")
        
        results = {}
        
        for pair in pairs:
            try:
                df = await client.get_historical_data(
                    symbol=pair,
                    sec_type="CASH",
                    exchange="IDEALPRO",
                    duration=duration,
                    interval=interval
                )
                
                if not df.empty:
                    results[pair] = df
                    logger.info(f"Fetched {len(df)} bars for {pair}")
                
                await asyncio.sleep(0.2)
                
            except Exception as e:
                logger.error(f"Error fetching {pair}: {e}")
        
        return results
    
    async def fetch_futures(
        self,
        symbols: List[str],
        duration: str = "1 Y",
        interval: str = "1 day",
        exchange: str = "CME"
    ) -> Dict[str, pd.DataFrame]:
        """Fetch futures data.
        
        Args:
            symbols: List of futures symbols (e.g., "ES", "CL", "GC")
            duration: How far back
            interval: Bar interval
            exchange: Exchange (default: CME)
            
        Returns:
            Dict mapping symbol to DataFrame
        """
        client = await self._get_client()
        
        if not await client.ensure_connected():
            raise ConnectionError("Could not connect to IBKR")
        
        results = {}
        
        for symbol in symbols:
            try:
                df = await client.get_historical_data(
                    symbol=symbol,
                    sec_type="FUT",
                    exchange=exchange,
                    duration=duration,
                    interval=interval
                )
                
                if not df.empty:
                    results[symbol] = df
                    logger.info(f"Fetched {len(df)} bars for {symbol}")
                
                await asyncio.sleep(0.3)  # Futures need more delay
                
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
        
        return results
    
    async def fetch_options_chain(
        self,
        underlying: str,
        exchange: str = "SMART"
    ) -> Dict:
        """Fetch options chain for an underlying.
        
        Args:
            underlying: Stock symbol
            exchange: Exchange
            
        Returns:
            Dict with expirations and strikes
        """
        client = await self._get_client()
        
        if not await client.ensure_connected():
            raise ConnectionError("Could not connect to IBKR")
        
        return await client.get_options_chain(underlying, exchange)
    
    async def disconnect(self):
        """Disconnect from IBKR."""
        if self._client:
            await self._client.disconnect()
            self._client = None


# ---------------------------------------------------------------------------
# Convenience Functions
# ---------------------------------------------------------------------------

async def fetch_equities(
    symbols: List[str],
    duration: str = "1 Y",
    interval: str = "1 day",
    exchange: str = "SMART"
) -> Dict[str, pd.DataFrame]:
    """Fetch equity data from IBKR.
    
    Wrapper function for quick access.
    """
    fetcher = IBKRDataFetcher()
    try:
        return await fetcher.fetch_equities(symbols, duration, interval, exchange)
    finally:
        await fetcher.disconnect()


async def fetch_forex(
    pairs: List[str],
    duration: str = "1 Y",
    interval: str = "1 day"
) -> Dict[str, pd.DataFrame]:
    """Fetch forex data from IBKR.
    
    Wrapper function for quick access.
    """
    fetcher = IBKRDataFetcher()
    try:
        return await fetcher.fetch_forex(pairs, duration, interval)
    finally:
        await fetcher.disconnect()


async def fetch_futures(
    symbols: List[str],
    duration: str = "1 Y",
    interval: str = "1 day",
    exchange: str = "CME"
) -> Dict[str, pd.DataFrame]:
    """Fetch futures data from IBKR.
    
    Wrapper function for quick access.
    """
    fetcher = IBKRDataFetcher()
    try:
        return await fetcher.fetch_futures(symbols, duration, interval, exchange)
    finally:
        await fetcher.disconnect()


async def fetch_options_chain(
    underlying: str,
    exchange: str = "SMART"
) -> Dict:
    """Fetch options chain from IBKR."""
    fetcher = IBKRDataFetcher()
    try:
        return await fetcher.fetch_options_chain(underlying, exchange)
    finally:
        await fetcher.disconnect()


async def batch_fetch(
    asset_class: str,
    symbols: Optional[List[str]] = None,
    duration: str = "1 Y",
    interval: str = "1 day"
) -> Dict[str, pd.DataFrame]:
    """Batch fetch data for an asset class.
    
    Args:
        asset_class: "ibkr_equities", "ibkr_fx", "ibkr_futures"
        symbols: Optional list of symbols (uses defaults if not provided)
        duration: How far back
        interval: Bar interval
        
    Returns:
        Dict mapping symbol to DataFrame
    """
    # Use default tickers if not provided
    if symbols is None:
        if asset_class == "ibkr_equities":
            symbols = DEFAULT_US_EQUITIES
        elif asset_class == "ibkr_fx":
            symbols = DEFAULT_FOREX_PAIRS
        elif asset_class == "ibkr_futures":
            symbols = DEFAULT_FUTURES
        else:
            raise ValueError(f"Unknown asset class: {asset_class}")
    
    if asset_class == "ibkr_equities":
        return await fetch_equities(symbols, duration, interval)
    elif asset_class == "ibkr_fx":
        return await fetch_forex(symbols, duration, interval)
    elif asset_class == "ibkr_futures":
        return await fetch_futures(symbols, duration, interval)
    else:
        raise ValueError(f"Unknown asset class: {asset_class}")


# ---------------------------------------------------------------------------
# Data Validation
# ---------------------------------------------------------------------------

class DataQualityReport:
    """Data quality report for a DataFrame."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.stats: Dict = {}
        
        self._analyze()
    
    def _analyze(self):
        """Run all validation checks."""
        if self.df.empty:
            self.issues.append("DataFrame is empty")
            return
        
        # Basic stats
        self.stats = {
            "rows": len(self.df),
            "columns": list(self.df.columns),
            "date_range": {
                "start": str(self.df['date'].min()) if 'date' in self.df.columns else None,
                "end": str(self.df['date'].max()) if 'date' in self.df.columns else None,
            }
        }
        
        # Check for required columns
        required = ['date', 'open', 'high', 'low', 'close']
        for col in required:
            if col not in self.df.columns:
                self.issues.append(f"Missing required column: {col}")
        
        if 'date' not in self.df.columns:
            return
        
        # Check for missing values
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in self.df.columns:
                missing = self.df[col].isna().sum()
                if missing > 0:
                    pct = (missing / len(self.df)) * 100
                    if pct > 10:
                        self.issues.append(f"Column '{col}' has {missing} missing values ({pct:.1f}%)")
                    else:
                        self.warnings.append(f"Column '{col}' has {missing} missing values ({pct:.1f}%)")
        
        # Check for negative prices
        for col in ['open', 'high', 'low', 'close']:
            if col in self.df.columns:
                neg_count = (self.df[col] < 0).sum()
                if neg_count > 0:
                    self.issues.append(f"Column '{col}' has {neg_count} negative values")
        
        # Check for negative volume
        if 'volume' in self.df.columns:
            neg_vol = (self.df['volume'] < 0).sum()
            if neg_vol > 0:
                self.issues.append(f"Column 'volume' has {neg_vol} negative values")
        
        # Check for high/low sanity
        if all(col in self.df.columns for col in ['high', 'low', 'open', 'close']):
            invalid_hl = ((self.df['high'] < self.df['low'])).sum()
            if invalid_hl > 0:
                self.issues.append(f"High < Low in {invalid_hl} rows")
            
            invalid_h = ((self.df['high'] < self.df['open']) | (self.df['high'] < self.df['close'])).sum()
            if invalid_h > 0:
                self.warnings.append(f"High < Open or Close in {invalid_h} rows")
            
            invalid_l = ((self.df['low'] > self.df['open']) | (self.df['low'] > self.df['close'])).sum()
            if invalid_l > 0:
                self.warnings.append(f"Low > Open or Close in {invalid_l} rows")
        
        # Check for gaps in data
        if 'date' in self.df.columns:
            dates = pd.to_datetime(self.df['date'])
            date_diff = dates.diff().max()
            if date_diff and hasattr(date_diff, 'days'):
                max_gap = date_diff.days
                if max_gap > 7:
                    self.warnings.append(f"Maximum gap in data: {max_gap} days")
        
        # Check for duplicates
        if 'date' in self.df.columns and 'ticker' in self.df.columns:
            dups = self.df.duplicated(subset=['date', 'ticker']).sum()
            if dups > 0:
                self.warnings.append(f"Found {dups} duplicate date/ticker combinations")
    
    def is_valid(self) -> bool:
        """Return True if no critical issues found."""
        return len(self.issues) == 0
    
    def to_dict(self) -> dict:
        """Convert report to dict."""
        return {
            "valid": self.is_valid(),
            "issues": self.issues,
            "warnings": self.warnings,
            "stats": self.stats
        }


def validate_data(df: pd.DataFrame) -> DataQualityReport:
    """Validate data quality and return a report.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataQualityReport with validation results
    """
    return DataQualityReport(df)


def validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean data, fixing common issues.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        Cleaned DataFrame
    """
    report = validate_data(df)
    
    if not report.is_valid():
        logger.warning(f"Data quality issues found: {report.issues}")
    
    # Make a copy
    cleaned = df.copy()
    
    # Remove rows with all NaN OHLC
    if all(col in cleaned.columns for col in ['open', 'high', 'low', 'close']):
        cleaned = cleaned.dropna(subset=['open', 'high', 'low', 'close'], how='all')
    
    # Remove duplicates
    if 'date' in cleaned.columns and 'ticker' in cleaned.columns:
        cleaned = cleaned.drop_duplicates(subset=['date', 'ticker'], keep='last')
    
    # Sort by date
    if 'date' in cleaned.columns:
        cleaned = cleaned.sort_values('date').reset_index(drop=True)
    
    return cleaned


# ---------------------------------------------------------------------------
# Incremental Updates
# ---------------------------------------------------------------------------

def get_last_date_for_ticker(
    parquet_path: Path,
    ticker: str
) -> Optional[datetime]:
    """Get the last date for a specific ticker in a parquet file.
    
    Args:
        parquet_path: Path to parquet file
        ticker: Ticker symbol
        
    Returns:
        Last date as datetime, or None if not found
    """
    if not parquet_path.exists():
        return None
    
    try:
        df = pd.read_parquet(parquet_path)
        if 'ticker' in df.columns and 'date' in df.columns:
            ticker_data = df[df['ticker'] == ticker]
            if not ticker_data.empty:
                last_date = ticker_data['date'].max()
                return pd.to_datetime(last_date)
    except Exception as e:
        logger.error(f"Error reading parquet: {e}")
    
    return None


def get_ibkr_data_path(asset_class: str) -> Path:
    """Get the parquet file path for an IBKR asset class."""
    from backend.market_data_store import _IBKR_ASSET_FILES
    return _IBKR_ASSET_FILES.get(asset_class)


async def incremental_update(
    asset_class: str,
    symbols: Optional[List[str]] = None,
    interval: str = "1 day",
    force_refresh: bool = False
) -> Dict[str, int]:
    """Incrementally update data for an asset class.
    
    Only fetches data newer than the last stored date for each ticker.
    
    Args:
        asset_class: "ibkr_equities", "ibkr_fx", "ibkr_futures"
        symbols: Optional list of symbols (uses defaults if not provided)
        interval: Bar interval
        force_refresh: If True, ignore existing data and fetch all
        
    Returns:
        Dict mapping symbol to number of new rows fetched
    """
    # Get the parquet path
    parquet_path = get_ibkr_data_path(asset_class)
    if not parquet_path:
        raise ValueError(f"Unknown asset class: {asset_class}")
    
    # Use default tickers if not provided
    if symbols is None:
        if asset_class == "ibkr_equities":
            symbols = DEFAULT_US_EQUITIES
        elif asset_class == "ibkr_fx":
            symbols = DEFAULT_FOREX_PAIRS
        elif asset_class == "ibkr_futures":
            symbols = DEFAULT_FUTURES
    
    # Determine start date
    if force_refresh:
        start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
    else:
        # Find the earliest last date across all tickers
        start_date = None
        for symbol in symbols:
            last_date = get_last_date_for_ticker(parquet_path, symbol)
            if last_date:
                if start_date is None or last_date < pd.to_datetime(start_date):
                    start_date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    # Calculate appropriate duration
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    days = (end_dt - start_dt).days
    
    if days <= 7:
        duration = f"{days + 1} D"
    elif days <= 30:
        duration = "1 M"
    elif days <= 90:
        duration = "3 M"
    elif days <= 365:
        duration = "1 Y"
    else:
        duration = "2 Y"
    
    # Fetch the data
    if asset_class == "ibkr_equities":
        results = await fetch_equities(symbols, duration, interval)
    elif asset_class == "ibkr_fx":
        results = await fetch_forex(symbols, duration, interval)
    elif asset_class == "ibkr_futures":
        results = await fetch_futures(symbols, duration, interval)
    else:
        raise ValueError(f"Unknown asset class: {asset_class}")
    
    # Count new rows
    new_rows = {}
    for symbol, df in results.items():
        if df.empty:
            new_rows[symbol] = 0
            continue
        
        if not force_refresh:
            last_date = get_last_date_for_ticker(parquet_path, symbol)
            if last_date:
                df = df[pd.to_datetime(df['date']) > last_date]
        
        new_rows[symbol] = len(df)
        
        # Append to parquet if there are new rows
        if len(df) > 0:
            parquet_path.parent.mkdir(parents=True, exist_ok=True)
            if parquet_path.exists():
                existing = pd.read_parquet(parquet_path)
                combined = pd.concat([existing, df], ignore_index=True)
                combined = combined.drop_duplicates(subset=['date', 'ticker'], keep='last')
                combined = combined.sort_values('date').reset_index(drop=True)
                combined.to_parquet(parquet_path, index=False)
            else:
                df.to_parquet(parquet_path, index=False)
    
    return new_rows


# ---------------------------------------------------------------------------
# Sync wrapper (for non-async use)
# ---------------------------------------------------------------------------

def fetch_equities_sync(
    symbols: List[str],
    duration: str = "1 Y",
    interval: str = "1 day"
) -> Dict[str, pd.DataFrame]:
    """Synchronous version of fetch_equities."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            raise RuntimeError("Cannot use sync version in async context")
        return loop.run_until_complete(fetch_equities(symbols, duration, interval))
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(fetch_equities(symbols, duration, interval))


def fetch_forex_sync(
    pairs: List[str],
    duration: str = "1 Y",
    interval: str = "1 day"
) -> Dict[str, pd.DataFrame]:
    """Synchronous version of fetch_forex."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            raise RuntimeError("Cannot use sync version in async context")
        return loop.run_until_complete(fetch_forex(pairs, duration, interval))
    except RuntimeError:
        return asyncio.run(fetch_forex(pairs, duration, interval))


# ---------------------------------------------------------------------------
# CLI Helper
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        if len(sys.argv) < 3:
            print("Usage: python -m backend.ibkr_data_fetcher <equities|forex|futures> <duration>")
            print("Example: python -m backend.ibkr_data_fetcher equities '1 Y'")
            sys.exit(1)
        
        asset_type = sys.argv[1]
        duration = sys.argv[2] if len(sys.argv) > 2 else "1 Y"
        
        if asset_type == "equities":
            results = await fetch_equities(DEFAULT_US_EQUITIES[:5], duration)
        elif asset_type == "forex":
            results = await fetch_forex(DEFAULT_FOREX_PAIRS, duration)
        elif asset_type == "futures":
            results = await fetch_futures(DEFAULT_FUTURES, duration)
        else:
            print(f"Unknown asset type: {asset_type}")
            sys.exit(1)
        
        for symbol, df in results.items():
            print(f"{symbol}: {len(df)} rows")
    
    asyncio.run(main())
