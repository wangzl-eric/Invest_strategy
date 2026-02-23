"""Benchmark data service for fetching market index data.

Fetches S&P 500 (^GSPC) and other benchmark data via yfinance
for portfolio performance comparison.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from functools import lru_cache
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Cache TTL in seconds (1 hour)
CACHE_TTL = 3600

# In-memory cache for benchmark data
_benchmark_cache: Dict[str, Any] = {}
_cache_timestamp: Dict[str, datetime] = {}


def _is_cache_valid(cache_key: str) -> bool:
    """Check if cached data is still valid."""
    if cache_key not in _cache_timestamp:
        return False
    age = (datetime.now() - _cache_timestamp[cache_key]).total_seconds()
    return age < CACHE_TTL


def get_sp500_data(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    use_cache: bool = True
) -> pd.DataFrame:
    """Fetch S&P 500 historical data.
    
    Args:
        start_date: Start date for data (defaults to 1 year ago)
        end_date: End date for data (defaults to today)
        use_cache: Whether to use cached data if available
        
    Returns:
        DataFrame with columns: date, close, daily_return, cumulative_return
    """
    try:
        import yfinance as yf
    except ImportError:
        logger.error("yfinance not installed. Run: pip install yfinance")
        return pd.DataFrame()
    
    # Default date range
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=365)
    
    # Create cache key
    cache_key = f"sp500_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
    
    # Check cache
    if use_cache and cache_key in _benchmark_cache and _is_cache_valid(cache_key):
        logger.debug(f"Using cached S&P 500 data for {cache_key}")
        return _benchmark_cache[cache_key]
    
    logger.info(f"Fetching S&P 500 data from {start_date.date()} to {end_date.date()}")
    
    try:
        # Fetch data from yfinance
        ticker = yf.Ticker("^GSPC")
        hist = ticker.history(start=start_date, end=end_date)
        
        if hist.empty:
            logger.warning("No S&P 500 data returned from yfinance")
            return pd.DataFrame()
        
        # Process data
        df = pd.DataFrame({
            'date': hist.index,
            'close': hist['Close'].values,
        })
        df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
        df = df.sort_values('date').reset_index(drop=True)
        
        # Calculate returns
        df['daily_return'] = df['close'].pct_change()
        df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
        
        # Cache the result
        _benchmark_cache[cache_key] = df
        _cache_timestamp[cache_key] = datetime.now()
        
        logger.info(f"Fetched {len(df)} days of S&P 500 data")
        return df
        
    except Exception as e:
        logger.error(f"Error fetching S&P 500 data: {e}")
        return pd.DataFrame()


def get_benchmark_comparison(
    portfolio_returns: pd.Series,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """Compare portfolio returns against S&P 500 benchmark.
    
    Args:
        portfolio_returns: Series of daily portfolio returns (index should be dates)
        start_date: Start date for comparison
        end_date: End date for comparison
        
    Returns:
        Dictionary with comparison metrics and aligned data
    """
    # Get S&P 500 data
    sp500_df = get_sp500_data(start_date, end_date)
    
    if sp500_df.empty:
        return {
            'error': 'Could not fetch benchmark data',
            'portfolio_sharpe': None,
            'benchmark_sharpe': None,
            'alpha': None,
            'beta': None,
        }
    
    # Align dates
    sp500_df = sp500_df.set_index('date')
    
    # Convert portfolio returns to DataFrame if needed
    if isinstance(portfolio_returns.index, pd.DatetimeIndex):
        portfolio_dates = portfolio_returns.index
    else:
        portfolio_dates = pd.to_datetime(portfolio_returns.index)
    
    portfolio_df = pd.DataFrame({
        'portfolio_return': portfolio_returns.values
    }, index=portfolio_dates)
    
    # Merge on date
    merged = portfolio_df.join(sp500_df[['daily_return']], how='inner')
    merged = merged.rename(columns={'daily_return': 'benchmark_return'})
    merged = merged.dropna()
    
    if len(merged) < 10:
        return {
            'error': 'Insufficient overlapping data points',
            'data_points': len(merged),
        }
    
    # Calculate metrics
    portfolio_ret = merged['portfolio_return']
    benchmark_ret = merged['benchmark_return']
    
    # Sharpe ratios (assuming 0 risk-free rate for simplicity)
    portfolio_sharpe = np.sqrt(252) * portfolio_ret.mean() / portfolio_ret.std() if portfolio_ret.std() > 0 else 0
    benchmark_sharpe = np.sqrt(252) * benchmark_ret.mean() / benchmark_ret.std() if benchmark_ret.std() > 0 else 0
    
    # Beta and Alpha (CAPM)
    cov_matrix = np.cov(portfolio_ret, benchmark_ret)
    beta = cov_matrix[0, 1] / cov_matrix[1, 1] if cov_matrix[1, 1] > 0 else 0
    alpha = (portfolio_ret.mean() - beta * benchmark_ret.mean()) * 252  # Annualized
    
    # Information Ratio
    tracking_error = (portfolio_ret - benchmark_ret).std() * np.sqrt(252)
    excess_return = (portfolio_ret.mean() - benchmark_ret.mean()) * 252
    information_ratio = excess_return / tracking_error if tracking_error > 0 else 0
    
    # Cumulative returns for charting
    portfolio_cumulative = (1 + portfolio_ret).cumprod() - 1
    benchmark_cumulative = (1 + benchmark_ret).cumprod() - 1
    
    return {
        'portfolio_sharpe': float(portfolio_sharpe),
        'benchmark_sharpe': float(benchmark_sharpe),
        'beta': float(beta),
        'alpha': float(alpha),
        'information_ratio': float(information_ratio),
        'tracking_error': float(tracking_error),
        'correlation': float(portfolio_ret.corr(benchmark_ret)),
        'data_points': len(merged),
        'portfolio_cumulative_return': float(portfolio_cumulative.iloc[-1]) if len(portfolio_cumulative) > 0 else 0,
        'benchmark_cumulative_return': float(benchmark_cumulative.iloc[-1]) if len(benchmark_cumulative) > 0 else 0,
        'time_series': {
            'dates': merged.index.strftime('%Y-%m-%d').tolist(),
            'portfolio_cumulative': portfolio_cumulative.tolist(),
            'benchmark_cumulative': benchmark_cumulative.tolist(),
        }
    }


def calculate_rolling_metrics(
    returns: pd.Series,
    window: int = 30
) -> Dict[str, List[float]]:
    """Calculate rolling performance metrics.
    
    Args:
        returns: Series of daily returns
        window: Rolling window size in days
        
    Returns:
        Dictionary with rolling metrics time series
    """
    if len(returns) < window:
        return {
            'dates': [],
            'rolling_sharpe': [],
            'rolling_volatility': [],
            'rolling_return': [],
        }
    
    # Rolling calculations
    rolling_mean = returns.rolling(window=window).mean()
    rolling_std = returns.rolling(window=window).std()
    
    # Annualized metrics
    rolling_sharpe = np.sqrt(252) * rolling_mean / rolling_std
    rolling_volatility = rolling_std * np.sqrt(252)
    rolling_return = rolling_mean * 252
    
    # Drop NaN values
    valid_idx = ~rolling_sharpe.isna()
    
    dates = returns.index[valid_idx]
    if hasattr(dates, 'strftime'):
        date_strings = dates.strftime('%Y-%m-%d').tolist()
    else:
        date_strings = [str(d) for d in dates]
    
    return {
        'dates': date_strings,
        'rolling_sharpe': rolling_sharpe[valid_idx].tolist(),
        'rolling_volatility': rolling_volatility[valid_idx].tolist(),
        'rolling_return': rolling_return[valid_idx].tolist(),
    }


def get_returns_distribution(
    returns: pd.Series,
    bins: int = 50
) -> Dict[str, Any]:
    """Calculate returns distribution statistics.
    
    Args:
        returns: Series of daily returns
        bins: Number of histogram bins
        
    Returns:
        Dictionary with distribution data and statistics
    """
    returns = returns.dropna()
    
    if len(returns) < 2:
        return {
            'histogram': {'bins': [], 'counts': []},
            'statistics': {},
        }
    
    # Histogram
    counts, bin_edges = np.histogram(returns, bins=bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Statistics
    mean_ret = float(returns.mean())
    std_ret = float(returns.std())
    skewness = float(returns.skew()) if len(returns) > 2 else 0
    kurtosis = float(returns.kurtosis()) if len(returns) > 3 else 0
    
    # VaR and CVaR at 95% confidence
    var_95 = float(np.percentile(returns, 5))
    cvar_95 = float(returns[returns <= var_95].mean()) if len(returns[returns <= var_95]) > 0 else var_95
    
    # Percentiles
    percentiles = {
        'p1': float(np.percentile(returns, 1)),
        'p5': float(np.percentile(returns, 5)),
        'p25': float(np.percentile(returns, 25)),
        'p50': float(np.percentile(returns, 50)),
        'p75': float(np.percentile(returns, 75)),
        'p95': float(np.percentile(returns, 95)),
        'p99': float(np.percentile(returns, 99)),
    }
    
    return {
        'histogram': {
            'bins': bin_centers.tolist(),
            'counts': counts.tolist(),
        },
        'statistics': {
            'mean': mean_ret,
            'std': std_ret,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'min': float(returns.min()),
            'max': float(returns.max()),
            'positive_days': int((returns > 0).sum()),
            'negative_days': int((returns < 0).sum()),
            'total_days': len(returns),
        },
        'percentiles': percentiles,
    }


def clear_cache():
    """Clear the benchmark data cache."""
    global _benchmark_cache, _cache_timestamp
    _benchmark_cache = {}
    _cache_timestamp = {}
    logger.info("Benchmark cache cleared")
