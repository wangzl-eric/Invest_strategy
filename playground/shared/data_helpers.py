"""
Playground Data Helpers

Simplified data access wrappers for the Market Study Playground.
Leverages existing infrastructure (quant_data/, market_data_store, market_data_service)
with relaxed validation for exploratory use.
"""

import sys
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def get_prices(
    tickers: Union[str, List[str]],
    start: str,
    end: Optional[str] = None,
    source: str = "auto",
) -> Union[pd.DataFrame, dict]:
    """
    Load price data for one or more tickers.

    Args:
        tickers: Single ticker string or list of tickers
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD), defaults to today
        source: 'auto', 'parquet', 'yfinance', or 'ibkr'

    Returns:
        If single ticker: DataFrame with columns [date, open, high, low, close, volume]
        If multiple tickers: dict of {ticker: DataFrame}

    Example:
        >>> spy = get_prices('SPY', start='2020-01-01')
        >>> prices = get_prices(['SPY', 'TLT', 'GLD'], start='2020-01-01')
    """
    from datetime import datetime

    import yfinance as yf

    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")

    single_ticker = isinstance(tickers, str)
    if single_ticker:
        tickers = [tickers]

    result = {}

    for ticker in tickers:
        # Try Parquet lake first if source is auto
        if source in ["auto", "parquet"]:
            try:
                from backend.market_data_store import MarketDataStore

                store = MarketDataStore()
                df = store.get_prices(ticker, start_date=start, end_date=end)
                if df is not None and len(df) > 0:
                    result[ticker] = df
                    continue
            except Exception:
                pass

        # Fallback to yfinance
        if source in ["auto", "yfinance"]:
            try:
                df = yf.download(ticker, start=start, end=end, progress=False)
                if len(df) > 0:
                    # Normalize column names
                    df = df.reset_index()
                    df.columns = [c.lower() for c in df.columns]

                    # Handle multi-level columns from yfinance
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)

                    # Ensure standard columns
                    required = ["date", "open", "high", "low", "close", "volume"]
                    if "date" not in df.columns and df.index.name == "date":
                        df = df.reset_index()

                    result[ticker] = (
                        df[required] if all(c in df.columns for c in required) else df
                    )
            except Exception as e:
                print(f"Warning: Failed to load {ticker}: {e}")
                result[ticker] = pd.DataFrame()

    return result[tickers[0]] if single_ticker else result


def get_macro_series(
    series_ids: Union[str, List[str]], start: str, end: Optional[str] = None
) -> pd.DataFrame:
    """
    Load FRED macro series.

    Args:
        series_ids: Single series ID or list of series IDs
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD), defaults to today

    Returns:
        DataFrame with columns [date, series_id, value] (long format)
        or [date, series1, series2, ...] (wide format if multiple series)

    Example:
        >>> vix = get_macro_series('VIXCLS', start='2020-01-01')
        >>> yields = get_macro_series(['DGS10', 'DGS2'], start='2020-01-01')
    """
    from datetime import datetime

    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")

    single_series = isinstance(series_ids, str)
    if single_series:
        series_ids = [series_ids]

    try:
        from backend.market_data_service import MarketDataService

        service = MarketDataService()

        dfs = []
        for series_id in series_ids:
            df = service.get_fred_series(series_id, start_date=start, end_date=end)
            if df is not None and len(df) > 0:
                df["series_id"] = series_id
                dfs.append(df)

        if not dfs:
            return pd.DataFrame()

        result = pd.concat(dfs, ignore_index=True)

        # Convert to wide format if multiple series
        if not single_series and len(series_ids) > 1:
            result = result.pivot(index="date", columns="series_id", values="value")
            result = result.reset_index()

        return result

    except Exception as e:
        print(f"Warning: Failed to load FRED series: {e}")
        print("Tip: Check that FRED_API_KEY is set in .env")
        return pd.DataFrame()


def get_market_snapshot() -> dict:
    """
    Get current market overview snapshot.

    Returns:
        dict with current values for major indices, rates, volatility, etc.

    Example:
        >>> snapshot = get_market_snapshot()
        >>> print(f"VIX: {snapshot['vix']:.2f}")
    """
    from datetime import datetime, timedelta

    # Get recent data (last 5 days to ensure we have latest)
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

    snapshot = {}

    # Equities
    for ticker in ["SPY", "QQQ", "IWM"]:
        try:
            df = get_prices(ticker, start=start, end=end)
            if len(df) > 0:
                snapshot[ticker.lower()] = df["close"].iloc[-1]
        except Exception:
            pass

    # Rates
    for series_id in ["DGS10", "DGS2", "DFF"]:
        try:
            df = get_macro_series(series_id, start=start, end=end)
            if len(df) > 0:
                snapshot[series_id.lower()] = df["value"].iloc[-1]
        except Exception:
            pass

    # Volatility
    try:
        vix = get_macro_series("VIXCLS", start=start, end=end)
        if len(vix) > 0:
            snapshot["vix"] = vix["value"].iloc[-1]
    except Exception:
        pass

    return snapshot


def get_correlation_matrix(
    tickers: List[str],
    window: int = 60,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> pd.DataFrame:
    """
    Calculate correlation matrix for multiple assets.

    Args:
        tickers: List of ticker symbols
        window: Rolling window for correlation (days)
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)

    Returns:
        Correlation matrix DataFrame

    Example:
        >>> corr = get_correlation_matrix(['SPY', 'TLT', 'GLD'], window=60)
    """
    from datetime import datetime, timedelta

    if start is None:
        start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    # Load prices
    prices_dict = get_prices(tickers, start=start, end=end)

    # Extract close prices
    close_prices = pd.DataFrame()
    for ticker, df in prices_dict.items():
        if len(df) > 0 and "close" in df.columns:
            close_prices[ticker] = df.set_index("date")["close"]

    if close_prices.empty:
        return pd.DataFrame()

    # Calculate returns
    returns = close_prices.pct_change().dropna()

    # Calculate correlation
    if window > 0:
        # Rolling correlation (return latest)
        corr = returns.rolling(window).corr().iloc[-len(tickers) :]
        corr.index = corr.index.droplevel(0)
    else:
        # Full period correlation
        corr = returns.corr()

    return corr


def calculate_returns(
    prices: pd.DataFrame, method: str = "simple", periods: int = 1
) -> pd.Series:
    """
    Calculate returns from price series.

    Args:
        prices: DataFrame or Series with price data
        method: 'simple' or 'log'
        periods: Number of periods for return calculation

    Returns:
        Series of returns

    Example:
        >>> returns = calculate_returns(spy['close'], method='simple')
        >>> log_returns = calculate_returns(spy['close'], method='log')
    """
    if isinstance(prices, pd.DataFrame):
        prices = prices["close"]

    if method == "simple":
        return prices.pct_change(periods=periods)
    elif method == "log":
        return np.log(prices / prices.shift(periods))
    else:
        raise ValueError(f"Unknown method: {method}. Use 'simple' or 'log'")


def calculate_volatility(
    returns: pd.Series,
    window: int = 20,
    annualize: bool = True,
    method: str = "rolling",
) -> pd.Series:
    """
    Calculate volatility from returns.

    Args:
        returns: Series of returns
        window: Rolling window size
        annualize: Whether to annualize (multiply by sqrt(252))
        method: 'rolling' or 'ewm' (exponentially weighted)

    Returns:
        Series of volatility values

    Example:
        >>> vol = calculate_volatility(returns, window=20, annualize=True)
    """
    if method == "rolling":
        vol = returns.rolling(window).std()
    elif method == "ewm":
        vol = returns.ewm(span=window).std()
    else:
        raise ValueError(f"Unknown method: {method}. Use 'rolling' or 'ewm'")

    if annualize:
        vol = vol * np.sqrt(252)

    return vol


def calculate_drawdown(prices: pd.Series) -> pd.Series:
    """
    Calculate drawdown from price series.

    Args:
        prices: Series of prices

    Returns:
        Series of drawdown values (negative percentages)

    Example:
        >>> dd = calculate_drawdown(spy['close'])
        >>> max_dd = dd.min()
    """
    if isinstance(prices, pd.DataFrame):
        prices = prices["close"]

    cum_returns = prices / prices.iloc[0]
    running_max = cum_returns.expanding().max()
    drawdown = (cum_returns - running_max) / running_max

    return drawdown


# Convenience function for common FRED series
FRED_SERIES = {
    "vix": "VIXCLS",
    "vvix": "VVIX",
    "dgs10": "DGS10",
    "dgs2": "DGS2",
    "dff": "DFF",
    "yield_curve": "T10Y2Y",
    "hy_spread": "BAMLH0A0HYM2",
    "ig_spread": "BAMLC0A0CM",
    "unemployment": "UNRATE",
    "cpi": "CPIAUCSL",
    "gdp": "GDP",
    "fed_balance_sheet": "WALCL",
}


def get_fred_shortcut(
    shortcut: str, start: str, end: Optional[str] = None
) -> pd.DataFrame:
    """
    Load FRED series using shortcut names.

    Args:
        shortcut: Shortcut name (see FRED_SERIES dict)
        start: Start date
        end: End date

    Returns:
        DataFrame with series data

    Example:
        >>> vix = get_fred_shortcut('vix', start='2020-01-01')
        >>> yield_curve = get_fred_shortcut('yield_curve', start='2020-01-01')
    """
    if shortcut not in FRED_SERIES:
        raise ValueError(
            f"Unknown shortcut: {shortcut}. Available: {list(FRED_SERIES.keys())}"
        )

    series_id = FRED_SERIES[shortcut]
    return get_macro_series(series_id, start=start, end=end)
