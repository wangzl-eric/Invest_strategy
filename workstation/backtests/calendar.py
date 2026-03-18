"""Trading calendar utilities using exchange_calendars.

Provides aligned trading-day schedules to prevent look-ahead artifacts
from non-trading days (holidays, early closes) in daily price data.

Primary use: ``align_to_trading_days()`` filters a DataFrame index to only
keep dates that are genuine trading days for the given exchange.  This
prevents 1-3 day look-ahead artifacts that arise when weekend or holiday
rows are included in resampled data.

Usage::

    from backtests.calendar import align_to_trading_days, get_trading_days

    aligned_prices = align_to_trading_days(prices_df, exchange="XNYS")
    days = get_trading_days("2020-01-01", "2024-12-31", exchange="XNYS")
"""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)

# Default exchange: NYSE (covers most US equity strategies)
DEFAULT_EXCHANGE = "XNYS"


def get_trading_days(
    start: str,
    end: str,
    exchange: str = DEFAULT_EXCHANGE,
) -> pd.DatetimeIndex:
    """Return the set of trading days for ``exchange`` between ``start`` and ``end``.

    Args:
        start: Start date, ISO format YYYY-MM-DD.
        end: End date, ISO format YYYY-MM-DD (inclusive).
        exchange: exchange_calendars exchange code.  Default is ``"XNYS"`` (NYSE).
            Other common codes: ``"XNAS"`` (NASDAQ), ``"XLON"`` (LSE),
            ``"XTSE"`` (TSX).

    Returns:
        DatetimeIndex of valid trading days (timezone-naive, midnight UTC).

    Raises:
        ImportError: If exchange_calendars is not installed.
    """
    try:
        import exchange_calendars as xcals
    except ImportError as exc:
        raise ImportError(
            "exchange_calendars is required for trading-day alignment. "
            "Install with: pip install exchange-calendars"
        ) from exc

    cal = xcals.get_calendar(exchange)
    schedule = cal.schedule.loc[start:end]
    return pd.DatetimeIndex(schedule.index).tz_localize(None)


def align_to_trading_days(
    df: pd.DataFrame,
    exchange: str = DEFAULT_EXCHANGE,
    method: str = "filter",
) -> pd.DataFrame:
    """Filter a DataFrame to keep only rows that fall on trading days.

    Non-trading days (weekends, public holidays, early closes with no open)
    are removed.  This is a lightweight alternative to full calendar
    alignment — it does not forward-fill missing prices.

    Args:
        df: DataFrame with a DatetimeIndex.
        exchange: exchange_calendars exchange code (default NYSE).
        method: ``"filter"`` (drop non-trading rows) is the only supported
            method.  Future versions may support ``"reindex"`` with
            forward-fill.

    Returns:
        A new DataFrame with only trading-day rows.  The original ``df`` is
        not modified.
    """
    if df.empty:
        return df.copy()

    try:
        start = str(df.index[0].date())
        end = str(df.index[-1].date())
        trading_days = get_trading_days(start, end, exchange=exchange)
    except Exception as exc:
        logger.warning(
            "Trading-day alignment failed (%s). Returning original data.", exc
        )
        return df.copy()

    # Build a timezone-naive index from the DataFrame for intersection
    df_dates = df.index.normalize().tz_localize(None)
    mask = df_dates.isin(trading_days)
    return df.loc[mask].copy()


def is_trading_day(
    date: str,
    exchange: str = DEFAULT_EXCHANGE,
) -> bool:
    """Return True if ``date`` is a trading day on ``exchange``."""
    try:
        import exchange_calendars as xcals
    except ImportError:
        return True  # Fail open: assume trading day if calendar unavailable

    cal = xcals.get_calendar(exchange)
    return bool(cal.is_session(date))


__all__ = [
    "get_trading_days",
    "align_to_trading_days",
    "is_trading_day",
    "DEFAULT_EXCHANGE",
]
