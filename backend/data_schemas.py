"""Unified data schemas for cross-asset market data.

This module defines canonical schemas that work across all asset classes
(equities, FX, futures, commodities, rates) with asset-class-specific extensions.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict, Any
import pandas as pd


class AssetClass(str, Enum):
    """Asset class enumeration."""
    EQUITY = "equity"
    FX = "fx"
    FUTURES = "futures"
    COMMODITY = "commodity"
    RATE = "rate"
    CREDIT = "credit"
    OPTION = "option"
    CRYPTO = "crypto"


class DataSource(str, Enum):
    """Data source enumeration."""
    IBKR = "ibkr"
    YFINANCE = "yfinance"
    FRED = "fred"
    MANUAL = "manual"


@dataclass
class TimeSeriesBar:
    """Canonical time-series bar schema for all asset classes.
    
    This is the core schema that all market data conforms to.
    Asset-class-specific fields are stored in the extensions dict.
    """
    # Core fields
    date: date
    ticker: str
    asset_class: AssetClass
    
    # OHLCV fields
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None
    
    # Metadata
    source: DataSource = DataSource.IBKR
    interval: str = "1d"  # 1d, 1h, 15m, 5m, 1m, etc.
    currency: str = "USD"
    exchange: Optional[str] = None
    
    # Extensions for asset-class-specific data
    # Examples:
    #   - equity: dividend, split_ratio
    #   - fx: bid, ask, mid
    #   - futures: expiry, contract_multiplier
    #   - option: strike, expiry, option_type, underlying
    extensions: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "date": self.date.isoformat() if isinstance(self.date, date) else str(self.date),
            "ticker": self.ticker,
            "asset_class": self.asset_class.value,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "source": self.source.value,
            "interval": self.interval,
            "currency": self.currency,
            "exchange": self.exchange,
            **self.extensions
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TimeSeriesBar":
        """Create from dictionary."""
        date_val = data.get("date")
        if isinstance(date_val, str):
            date_val = pd.to_datetime(date_val).date()
        
        # Extract extensions (everything not in core fields)
        core_fields = {"date", "ticker", "asset_class", "open", "high", "low", "close", 
                      "volume", "source", "interval", "currency", "exchange"}
        extensions = {k: v for k, v in data.items() if k not in core_fields}
        
        asset_class = data.get("asset_class", "equity")
        if isinstance(asset_class, str):
            asset_class = AssetClass(asset_class)
        
        source = data.get("source", "ibkr")
        if isinstance(source, str):
            source = DataSource(source)
        
        return cls(
            date=date_val,
            ticker=data.get("ticker", ""),
            asset_class=asset_class,
            open=data.get("open"),
            high=data.get("high"),
            low=data.get("low"),
            close=data.get("close"),
            volume=data.get("volume"),
            source=source,
            interval=data.get("interval", "1d"),
            currency=data.get("currency", "USD"),
            exchange=data.get("exchange"),
            extensions=extensions
        )


@dataclass
class FredSeries:
    """Schema for FRED economic time series."""
    date: date
    series_id: str
    value: Optional[float]
    source: DataSource = DataSource.FRED
    
    # FRED-specific metadata
    units: Optional[str] = None
    frequency: Optional[str] = None  # daily, weekly, monthly, quarterly
    category: Optional[str] = None  # treasury_yield, macro_indicator, liquidity
    
    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat() if isinstance(self.date, date) else str(self.date),
            "series_id": self.series_id,
            "value": self.value,
            "source": self.source.value,
            "units": self.units,
            "frequency": self.frequency,
            "category": self.category
        }


@dataclass 
class MarketSnapshot:
    """Real-time or near-real-time market quote."""
    ticker: str
    asset_class: AssetClass
    
    # Price fields
    bid: Optional[float] = None
    ask: Optional[float] = None
    last: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    prev_close: Optional[float] = None
    
    # Volume
    volume: Optional[int] = None
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None
    
    # Metadata
    timestamp: Optional[datetime] = None
    exchange: Optional[str] = None
    currency: str = "USD"
    
    # Calculated fields
    change: Optional[float] = None
    change_pct: Optional[float] = None
    
    def compute_change(self):
        """Compute change from prev_close."""
        if self.last and self.prev_close:
            self.change = self.last - self.prev_close
            if self.prev_close != 0:
                self.change_pct = (self.change / self.prev_close) * 100
    
    def to_dict(self) -> dict:
        result = {
            "ticker": self.ticker,
            "asset_class": self.asset_class.value,
            "bid": self.bid,
            "ask": self.ask,
            "last": self.last,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "prev_close": self.prev_close,
            "volume": self.volume,
            "bid_size": self.bid_size,
            "ask_size": self.ask_size,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "exchange": self.exchange,
            "currency": self.currency,
            "change": self.change,
            "change_pct": self.change_pct
        }
        return {k: v for k, v in result.items() if v is not None}


# ----------------------------------------------------------------------
# Schema converters for Parquet
# ----------------------------------------------------------------------

def time_series_bar_to_df(bars: List[TimeSeriesBar]) -> pd.DataFrame:
    """Convert list of TimeSeriesBar to DataFrame."""
    if not bars:
        return pd.DataFrame()
    
    records = [bar.to_dict() for bar in bars]
    df = pd.DataFrame(records)
    
    # Ensure date is string for Parquet
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    
    return df


def fred_series_to_df(series: List[FredSeries]) -> pd.DataFrame:
    """Convert list of FredSeries to DataFrame."""
    if not series:
        return pd.DataFrame()
    
    records = [s.to_dict() for s in series]
    df = pd.DataFrame(records)
    
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    
    return df


# ----------------------------------------------------------------------
# Asset class mappings
# ----------------------------------------------------------------------

# Default asset class by ticker pattern
TICKER_TO_ASSET_CLASS: Dict[str, AssetClass] = {
    # Equities
    "^GSPC": AssetClass.EQUITY,
    "^NDX": AssetClass.EQUITY,
    "^RUT": AssetClass.EQUITY,
    "^VIX": AssetClass.EQUITY,
    # FX (typically has =X suffix or is forex pair)
    "EURUSD": AssetClass.FX,
    "GBPUSD": AssetClass.FX,
    "USDJPY": AssetClass.FX,
    # Futures (typically has =F suffix)
    "ES=F": AssetClass.FUTURES,
    "CL=F": AssetClass.FUTURES,
    "GC=F": AssetClass.FUTURES,
    # Commodities
    "CL": AssetClass.COMMODITY,
    "GC": AssetClass.COMMODITY,
    # Rates
    "^IRX": AssetClass.RATE,
    "^FVX": AssetClass.RATE,
    "^TNX": AssetClass.RATE,
    "^TYX": AssetClass.RATE,
}


def get_asset_class(ticker: str) -> AssetClass:
    """Determine asset class from ticker."""
    # Check exact match first
    if ticker in TICKER_TO_ASSET_CLASS:
        return TICKER_TO_ASSET_CLASS[ticker]
    
    # Check patterns
    ticker_upper = ticker.upper()
    if "=X" in ticker_upper:
        if ticker_upper.startswith(("EUR", "GBP", "USD", "AUD", "NZD", "CAD", "CHF")):
            return AssetClass.FX
    if "=F" in ticker_upper:
        return AssetClass.FUTURES
    if ticker_upper.startswith(("^", "DGS", "T")) and any(t in ticker_upper for t in ["YIELD", "TREASURY", "SPREAD"]):
        return AssetClass.RATE
    
    # Default to equity
    return AssetClass.EQUITY


# ----------------------------------------------------------------------
# Common ticker mappings (IBKR <-> yfinance)
# ----------------------------------------------------------------------

# yfinance to IBKR ticker mapping
YF_TO_IBKR: Dict[str, str] = {
    "^GSPC": "SPX",
    "^NDX": "NDX",
    "^RUT": "RUT",
    "^VIX": "VIX",
    "EURUSD=X": "EURUSD",
    "GBPUSD=X": "GBPUSD",
    "USDJPY=X": "USDJPY",
    "CL=F": "CL",
    "BZ=F": "BZ",
    "GC=F": "GC",
    "NG=F": "NG",
    "HG=F": "HG",
    "SI=F": "SI",
}

# IBKR to yfinance ticker mapping
IBKR_TO_YF: Dict[str, str] = {v: k for k, v in YF_TO_IBKR.items()}


def to_ibkr_ticker(ticker: str) -> str:
    """Convert yfinance ticker to IBKR format."""
    return YF_TO_IBKR.get(ticker, ticker)


def to_yf_ticker(ticker: str) -> str:
    """Convert IBKR ticker to yfinance format."""
    return IBKR_TO_YF.get(ticker, ticker)
