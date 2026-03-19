"""
Playground Data Helpers

Simplified local-first data access wrappers for the Market Study Playground.
They use the unified backend data pipeline so notebooks can:
- read from the local research cache first
- optionally start a refresh job to update the cache from source APIs
- keep exploratory work aligned with the main research storage model
"""

from __future__ import annotations

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Sequence, Union

import numpy as np
import pandas as pd

# Add repo root to path so playground notebooks can import backend modules
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.data_pipeline import data_pipeline  # noqa: E402

DEFAULT_PRICE_DATASET = "equities"
DEFAULT_MACRO_DATASET = "macro_indicators"


def _today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _normalize_identifiers(values: Union[str, Sequence[str]]) -> list[str]:
    if isinstance(values, str):
        value = values.strip()
        return [value] if value else []
    return [str(v).strip() for v in values if str(v).strip()]


def _require_identifiers(kind: str, identifiers: Sequence[str]) -> None:
    if not identifiers:
        raise ValueError(f"{kind} requires at least one identifier")


def _empty_price_frame() -> pd.DataFrame:
    return pd.DataFrame(
        columns=["date", "ticker", "open", "high", "low", "close", "volume"]
    )


def _empty_macro_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=["date", "series_id", "value"])


def _price_dataset_candidates(source: str, dataset: Optional[str]) -> list[str]:
    if dataset:
        return [dataset]

    source_key = source.lower()
    if source_key == "ibkr":
        return ["ibkr_equities"]
    if source_key in {"yfinance", "yf"}:
        return ["equities"]
    if source_key in {"auto", "local", "parquet"}:
        return ["ibkr_equities", "equities"]

    raise ValueError(f"Unknown price source: {source}")


def _macro_dataset_candidates(source: str, dataset: Optional[str]) -> list[str]:
    if dataset:
        return [dataset]

    source_key = source.lower()
    if source_key in {"fred", "auto", "local", "parquet"}:
        return ["macro_indicators", "treasury_yields", "fed_liquidity"]

    raise ValueError(f"Unknown macro source: {source}")


def _query_local_dataset(
    *,
    dataset: str,
    identifiers: Sequence[str],
    start: str,
    end: str,
    refresh_if_missing: bool = False,
) -> pd.DataFrame:
    req = data_pipeline.build_local_request(
        dataset=dataset,
        identifiers=identifiers,
        start_date=start,
        end_date=end,
        refresh_if_missing=refresh_if_missing,
    )
    return data_pipeline.query_local(req)


def start_refresh_job(
    *,
    dataset: str,
    identifiers: Union[str, Sequence[str]],
    start: str,
    end: Optional[str] = None,
    interval: str = "1 day",
    sec_type: Optional[str] = None,
    exchange: Optional[str] = None,
) -> str:
    """Start a local data refresh job and return the job id."""
    normalized = _normalize_identifiers(identifiers)
    _require_identifiers("Refresh job", normalized)
    job_req = data_pipeline.build_refresh_request(
        dataset=dataset,
        identifiers=normalized,
        start_date=start,
        end_date=end or _today_str(),
        interval=interval,
        sec_type=sec_type,
        exchange=exchange,
    )
    return data_pipeline.start_refresh_job(job_req)


def wait_for_refresh_job(
    job_id: str,
    *,
    timeout_seconds: float = 60.0,
    poll_interval: float = 0.25,
) -> dict:
    """Poll a refresh job until it completes or times out."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        status = data_pipeline.get_job_status(job_id)
        if status and status.get("status") != "running":
            return status
        time.sleep(poll_interval)

    raise TimeoutError(f"Timed out waiting for refresh job {job_id}")


def refresh_prices(
    tickers: Union[str, Sequence[str]],
    *,
    start: str,
    end: Optional[str] = None,
    dataset: str = DEFAULT_PRICE_DATASET,
    interval: str = "1 day",
    sec_type: Optional[str] = None,
    exchange: Optional[str] = None,
    wait: bool = True,
) -> Union[str, dict]:
    """Start a refresh job for local price data."""
    job_id = start_refresh_job(
        dataset=dataset,
        identifiers=tickers,
        start=start,
        end=end,
        interval=interval,
        sec_type=sec_type,
        exchange=exchange,
    )
    return wait_for_refresh_job(job_id) if wait else job_id


def refresh_macro_series(
    series_ids: Union[str, Sequence[str]],
    *,
    start: str,
    end: Optional[str] = None,
    dataset: str = DEFAULT_MACRO_DATASET,
    wait: bool = True,
) -> Union[str, dict]:
    """Start a refresh job for local macro/FRED data."""
    job_id = start_refresh_job(
        dataset=dataset,
        identifiers=series_ids,
        start=start,
        end=end,
    )
    return wait_for_refresh_job(job_id) if wait else job_id


def get_prices(
    tickers: Union[str, List[str]],
    start: str,
    end: Optional[str] = None,
    source: str = "auto",
    dataset: Optional[str] = None,
    refresh_if_missing: bool = False,
) -> Union[pd.DataFrame, dict]:
    """
    Load price data from the local research cache.

    Args:
        tickers: Single ticker string or list of tickers
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD), defaults to today
        source: 'auto', 'local', 'parquet', 'yfinance', 'yf', or 'ibkr'
        dataset: Explicit dataset key such as 'equities', 'ibkr_equities', 'fx'
        refresh_if_missing: If True, refresh the final candidate dataset on cache miss

    Returns:
        If single ticker: DataFrame with columns [date, ticker, open, high, low, close, volume]
        If multiple tickers: dict of {ticker: DataFrame}
    """
    end = end or _today_str()
    identifiers = _normalize_identifiers(tickers)
    _require_identifiers("Price lookup", identifiers)
    single_ticker = isinstance(tickers, str)
    candidates = _price_dataset_candidates(source, dataset)

    result: dict[str, pd.DataFrame] = {}
    remaining = identifiers.copy()

    for idx, dataset_name in enumerate(candidates):
        if not remaining:
            break

        allow_refresh = refresh_if_missing and idx == len(candidates) - 1
        df = _query_local_dataset(
            dataset=dataset_name,
            identifiers=remaining,
            start=start,
            end=end,
            refresh_if_missing=allow_refresh,
        )
        if df.empty or "ticker" not in df.columns:
            continue

        for ticker in remaining.copy():
            sub = df[df["ticker"] == ticker].sort_values("date").reset_index(drop=True)
            if not sub.empty:
                result[ticker] = sub
                remaining.remove(ticker)

    for ticker in remaining:
        result[ticker] = _empty_price_frame()

    return result[identifiers[0]] if single_ticker else result


def get_macro_series(
    series_ids: Union[str, List[str]],
    start: str,
    end: Optional[str] = None,
    source: str = "auto",
    dataset: Optional[str] = None,
    refresh_if_missing: bool = False,
) -> pd.DataFrame:
    """
    Load FRED or macro data from the local research cache.

    If `dataset` is not provided, local reads scan the common macro datasets.
    Refresh-on-miss requires an explicit dataset so the helper knows which local
    store to update.
    """
    end = end or _today_str()
    identifiers = _normalize_identifiers(series_ids)
    _require_identifiers("Macro series lookup", identifiers)
    single_series = isinstance(series_ids, str)
    candidates = _macro_dataset_candidates(source, dataset)

    if refresh_if_missing and len(candidates) > 1:
        raise ValueError(
            "Refreshing macro data requires an explicit dataset. "
            "Use dataset='macro_indicators', 'treasury_yields', or 'fed_liquidity'."
        )

    frames = []
    for idx, dataset_name in enumerate(candidates):
        df = _query_local_dataset(
            dataset=dataset_name,
            identifiers=identifiers,
            start=start,
            end=end,
            refresh_if_missing=refresh_if_missing and idx == len(candidates) - 1,
        )
        if not df.empty:
            frames.append(df)

    if not frames:
        return _empty_macro_frame()

    result = (
        pd.concat(frames, ignore_index=True)
        .drop_duplicates(subset=["date", "series_id"], keep="last")
        .sort_values(["series_id", "date"])
        .reset_index(drop=True)
    )

    if single_series:
        return result[result["series_id"] == identifiers[0]].reset_index(drop=True)

    if len(identifiers) > 1:
        wide = result.pivot(index="date", columns="series_id", values="value")
        wide = wide.reset_index()
        return wide

    return result


def load_market_data(
    tickers: Union[str, Sequence[str]],
    start: Optional[str] = None,
    end: Optional[str] = None,
    dataset: str = DEFAULT_PRICE_DATASET,
    refresh_if_missing: bool = False,
) -> Union[pd.DataFrame, dict]:
    """Backward-compatible alias for playground notebooks."""
    start = start or (datetime.now() - timedelta(days=365 * 5)).strftime("%Y-%m-%d")
    return get_prices(
        tickers,
        start=start,
        end=end,
        dataset=dataset,
        refresh_if_missing=refresh_if_missing,
    )


def load_fred_data(
    series_ids: Union[str, Sequence[str]],
    start: Optional[str] = None,
    end: Optional[str] = None,
    dataset: str = DEFAULT_MACRO_DATASET,
    refresh_if_missing: bool = False,
) -> pd.DataFrame:
    """Backward-compatible alias for playground notebooks."""
    start = start or (datetime.now() - timedelta(days=365 * 5)).strftime("%Y-%m-%d")
    return get_macro_series(
        series_ids,
        start=start,
        end=end,
        dataset=dataset,
        refresh_if_missing=refresh_if_missing,
    )


def get_market_snapshot() -> dict:
    """
    Get current market overview snapshot from locally cached data.

    Returns:
        dict with current values for major indices and rates
    """
    end = _today_str()
    start = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

    snapshot = {}

    for ticker in ["SPY", "QQQ", "IWM"]:
        try:
            df = get_prices(ticker, start=start, end=end)
            if len(df) > 0:
                snapshot[ticker.lower()] = df["close"].iloc[-1]
        except Exception:
            pass

    for series_id in ["DGS10", "DGS2", "DFF"]:
        try:
            df = get_macro_series(
                series_id,
                start=start,
                end=end,
                dataset="treasury_yields"
                if series_id.startswith("DGS")
                else "macro_indicators",
            )
            if len(df) > 0:
                snapshot[series_id.lower()] = df["value"].iloc[-1]
        except Exception:
            pass

    return snapshot


def get_correlation_matrix(
    tickers: List[str],
    window: int = 60,
    start: Optional[str] = None,
    end: Optional[str] = None,
    dataset: str = DEFAULT_PRICE_DATASET,
) -> pd.DataFrame:
    """
    Calculate correlation matrix for multiple assets.
    """
    if start is None:
        start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    prices_dict = get_prices(tickers, start=start, end=end, dataset=dataset)

    close_prices = pd.DataFrame()
    for ticker, df in prices_dict.items():
        if len(df) > 0 and "close" in df.columns:
            close_prices[ticker] = df.set_index("date")["close"]

    if close_prices.empty:
        return pd.DataFrame()

    returns = close_prices.pct_change().dropna()

    if window > 0:
        corr = returns.rolling(window).corr().iloc[-len(tickers) :]
        corr.index = corr.index.droplevel(0)
    else:
        corr = returns.corr()

    return corr


def calculate_returns(
    prices: pd.DataFrame, method: str = "simple", periods: int = 1
) -> pd.Series:
    """
    Calculate returns from price series.
    """
    if isinstance(prices, pd.DataFrame):
        prices = prices["close"]

    if method == "simple":
        return prices.pct_change(periods=periods)
    if method == "log":
        return np.log(prices / prices.shift(periods))
    raise ValueError(f"Unknown method: {method}. Use 'simple' or 'log'")


def calculate_volatility(
    returns: pd.Series,
    window: int = 20,
    annualize: bool = True,
    method: str = "rolling",
) -> pd.Series:
    """
    Calculate volatility from returns.
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
    """
    if isinstance(prices, pd.DataFrame):
        prices = prices["close"]

    cum_returns = prices / prices.iloc[0]
    running_max = cum_returns.expanding().max()
    drawdown = (cum_returns - running_max) / running_max

    return drawdown


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
    """
    if shortcut not in FRED_SERIES:
        raise ValueError(
            f"Unknown shortcut: {shortcut}. Available: {list(FRED_SERIES.keys())}"
        )

    series_id = FRED_SERIES[shortcut]
    dataset = (
        "treasury_yields" if series_id.startswith("DGS") else DEFAULT_MACRO_DATASET
    )
    return get_macro_series(series_id, start=start, end=end, dataset=dataset)
