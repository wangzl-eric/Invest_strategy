"""Statistical analytics helpers for research and backtesting.

Moved from workstation/playground/shared/data_helpers.py so all layers
can import without depending on the playground package.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_rolling_sharpe(
    returns: pd.Series,
    window: int = 252,
    annualize: bool = True,
) -> pd.Series:
    """Rolling annualised Sharpe ratio.

    Args:
        returns: Daily return series.
        window:  Look-back window in trading days.
        annualize: Multiply by sqrt(252) when True.

    Returns:
        pd.Series with same index as *returns*.
    """
    roll_mean = returns.rolling(window).mean()
    roll_std = returns.rolling(window).std()
    sharpe = roll_mean / roll_std
    if annualize:
        sharpe = sharpe * np.sqrt(252)
    return sharpe


def compute_drawdown(prices: pd.Series) -> pd.Series:
    """Drawdown series from a price (or NAV) series.

    Args:
        prices: Price or cumulative-return series. If a DataFrame is passed,
                the 'close' column is used.

    Returns:
        pd.Series of drawdown values (0 to -1).
    """
    if isinstance(prices, pd.DataFrame):
        prices = prices["close"]
    cum = prices / prices.iloc[0]
    running_max = cum.expanding().max()
    return (cum - running_max) / running_max


def compute_correlation_matrix(returns_df: pd.DataFrame) -> pd.DataFrame:
    """Pearson correlation matrix of a multi-column returns DataFrame.

    Args:
        returns_df: DataFrame where each column is a return series.

    Returns:
        Square correlation DataFrame.
    """
    return returns_df.corr()


def calculate_returns(
    prices: pd.Series | pd.DataFrame,
    method: str = "simple",
    periods: int = 1,
) -> pd.Series:
    """Percentage or log returns from a price series."""
    if isinstance(prices, pd.DataFrame):
        prices = prices["close"]
    if method == "simple":
        return prices.pct_change(periods=periods)
    if method == "log":
        return np.log(prices / prices.shift(periods))
    raise ValueError(f"Unknown method: {method!r}. Use 'simple' or 'log'.")


def calculate_volatility(
    returns: pd.Series,
    window: int = 20,
    annualize: bool = True,
    method: str = "rolling",
) -> pd.Series:
    """Rolling or EWM volatility, optionally annualised."""
    if method == "rolling":
        vol = returns.rolling(window).std()
    elif method == "ewm":
        vol = returns.ewm(span=window).std()
    else:
        raise ValueError(f"Unknown method: {method!r}. Use 'rolling' or 'ewm'.")
    if annualize:
        vol = vol * np.sqrt(252)
    return vol
