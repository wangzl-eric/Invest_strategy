"""Unified public data interface for research, notebooks, and agents.

Usage::

    from alpha_research.quant_data.api import get_data
    df = get_data(["DGS10", "SPY"], start="2010-01-01")

Local Parquet lake is tried first; on a cache miss the appropriate API
connector is called, the result is written back to disk, and a warning
is emitted so callers know a network fetch occurred.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Optional, Union

import pandas as pd

# Ensure repo root is importable when running from notebooks
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from alpha_research.quant_data.analytics import (  # re-exported for convenience  # noqa: E402
    calculate_returns,
    calculate_volatility,
    compute_correlation_matrix,
    compute_drawdown,
    compute_rolling_sharpe,
)
from alpha_research.quant_data.ticker_map import TickerInfo, resolve_strict  # noqa: E402

log = logging.getLogger(__name__)

_PRICES_DIR = _REPO_ROOT / "data" / "market_data" / "prices"
_CATALOG_PATH = _REPO_ROOT / "data" / "market_data" / "catalog.json"


# ---------------------------------------------------------------------------
# Catalog helpers
# ---------------------------------------------------------------------------


def _load_catalog() -> dict:
    if _CATALOG_PATH.exists():
        try:
            return json.loads(_CATALOG_PATH.read_text())
        except Exception:
            pass
    return {}


def _catalog_coverage(ticker: str) -> Optional[tuple[str, str]]:
    """Return (start, end) from catalog if ticker is locally available."""
    catalog = _load_catalog()
    entry = catalog.get(ticker) or catalog.get(ticker.upper())
    if entry and isinstance(entry, dict):
        return entry.get("start"), entry.get("end")
    return None


# ---------------------------------------------------------------------------
# Local Parquet read
# ---------------------------------------------------------------------------


def _read_parquet_prices(ticker: str, start: str, end: str) -> Optional[pd.DataFrame]:
    """Try to read price data for *ticker* from the local Parquet lake."""
    candidates = list(_PRICES_DIR.glob("*.parquet")) if _PRICES_DIR.exists() else []
    for parquet_file in candidates:
        try:
            df = pd.read_parquet(parquet_file)
            col_ticker = (
                "ticker"
                if "ticker" in df.columns
                else ("symbol" if "symbol" in df.columns else None)
            )
            if col_ticker is None:
                continue
            mask = df[col_ticker].str.upper() == ticker.upper()
            if not mask.any():
                continue
            sub = df[mask].copy()
            date_col = "date" if "date" in sub.columns else "timestamp"
            sub[date_col] = pd.to_datetime(sub[date_col])
            sub = sub[(sub[date_col] >= start) & (sub[date_col] <= end)]
            if not sub.empty:
                return sub
        except Exception:
            continue
    return None


def _read_parquet_macro(series_id: str, start: str, end: str) -> Optional[pd.DataFrame]:
    """Try to read macro/FRED data for *series_id* from the local Parquet lake."""
    candidates = list(_PRICES_DIR.glob("*.parquet")) if _PRICES_DIR.exists() else []
    for parquet_file in candidates:
        try:
            df = pd.read_parquet(parquet_file)
            id_col = "series_id" if "series_id" in df.columns else None
            if id_col is None:
                continue
            mask = df[id_col].str.upper() == series_id.upper()
            if not mask.any():
                continue
            sub = df[mask].copy()
            sub["date"] = pd.to_datetime(sub["date"])
            sub = sub[(sub["date"] >= start) & (sub["date"] <= end)]
            if not sub.empty:
                return sub
        except Exception:
            continue
    return None


# ---------------------------------------------------------------------------
# API fetchers
# ---------------------------------------------------------------------------


def _fetch_yfinance(ticker: str, start: str, end: str) -> pd.DataFrame:
    import yfinance as yf

    raw = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if raw.empty:
        return pd.DataFrame(
            columns=["date", "ticker", "open", "high", "low", "close", "volume"]
        )
    raw = raw.reset_index()
    raw.columns = [
        c[0].lower() if isinstance(c, tuple) else c.lower() for c in raw.columns
    ]
    raw = raw.rename(columns={"date": "date", "index": "date"})
    raw["ticker"] = ticker
    for col in ["open", "high", "low", "close", "volume"]:
        if col not in raw.columns:
            raw[col] = float("nan")
    return raw[["date", "ticker", "open", "high", "low", "close", "volume"]]


def _fetch_fred(series_id: str, start: str, end: str) -> pd.DataFrame:
    import os

    import pandas_datareader.data as web

    api_key = os.getenv("FRED_API_KEY", "")
    kwargs = {"api_key": api_key} if api_key else {}
    raw = web.DataReader(series_id, "fred", start, end, **kwargs)
    raw = raw.reset_index()
    raw.columns = ["date", "value"]
    raw["series_id"] = series_id
    raw["date"] = pd.to_datetime(raw["date"])
    return raw[["date", "series_id", "value"]]


def _fetch_binance(symbol: str, start: str, end: str) -> pd.DataFrame:
    """Pull daily OHLCV from Binance public API."""
    try:
        from alpha_research.quant_data.connectors.binance_public import (
            BinancePublicConnector,  # type: ignore
        )

        connector = BinancePublicConnector()
        return connector.fetch_bars(symbol=symbol, start=start, end=end)
    except Exception:
        pass
    import time

    import requests

    start_ms = int(pd.Timestamp(start).timestamp() * 1000)
    end_ms = int(pd.Timestamp(end).timestamp() * 1000)
    url = "https://api.binance.com/api/v3/klines"
    rows, limit = [], 1000
    while start_ms < end_ms:
        resp = requests.get(
            url,
            params={
                "symbol": symbol,
                "interval": "1d",
                "startTime": start_ms,
                "endTime": end_ms,
                "limit": limit,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        rows.extend(data)
        start_ms = data[-1][0] + 86_400_000
        time.sleep(0.1)
    if not rows:
        return pd.DataFrame(
            columns=["date", "ticker", "open", "high", "low", "close", "volume"]
        )
    df = pd.DataFrame(
        rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_vol",
            "trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ],
    )
    df["date"] = pd.to_datetime(df["open_time"], unit="ms").dt.normalize()
    df["ticker"] = symbol
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = df[c].astype(float)
    return df[["date", "ticker", "open", "high", "low", "close", "volume"]]


# ---------------------------------------------------------------------------
# Core get_data function
# ---------------------------------------------------------------------------


def _today() -> str:
    return date.today().isoformat()


def _fetch_single(
    info: TickerInfo, start: str, end: str, source: Optional[str]
) -> pd.DataFrame:
    """Fetch one instrument: local first, then API fallback."""
    effective_source = source or info.source

    # Try local cache first
    if effective_source == "fred":
        local = _read_parquet_macro(info.canonical_id, start, end)
    else:
        local = _read_parquet_prices(info.canonical_id, start, end)

    if local is not None and not local.empty:
        return local

    # Cache miss — fetch from API
    log.warning(
        "cache miss for %s — fetching from %s",
        info.canonical_id,
        effective_source,
    )

    if effective_source == "fred":
        df = _fetch_fred(info.canonical_id, start, end)
    elif effective_source == "binance":
        df = _fetch_binance(info.canonical_id, start, end)
    else:
        df = _fetch_yfinance(info.canonical_id, start, end)

    if df.empty:
        return df

    # Write back to prices dir so next read hits cache
    _PRICES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = (
        _PRICES_DIR / f"{info.canonical_id.replace('=', '_').replace('/', '_')}.parquet"
    )
    df.to_parquet(out_path, index=False)
    return df


def get_data(
    tickers: Union[str, list[str]],
    start: str,
    end: Optional[str] = None,
    frequency: str = "1d",
    source: Optional[str] = None,
) -> pd.DataFrame:
    """Unified market data interface.

    Args:
        tickers:   Single ticker/alias or list. Natural language accepted
                   (e.g. '10-year yield', 'S&P 500', 'bitcoin').
        start:     ISO date string, e.g. '2010-01-01'.
        end:       ISO date string (default: today).
        frequency: '1d' (default), '1w', or '1m'. Only '1d' is currently
                   fetched from APIs; resampling applied for others.
        source:    Force a specific connector: 'yfinance'|'fred'|'stooq'|
                   'ecb'|'binance'|'polygon'|'ibkr'. Auto-detected if None.

    Returns:
        DataFrame with columns (date, ticker, open, high, low, close, volume)
        for price data, or (date, series_id, value) for macro/FRED data.
    """
    if isinstance(tickers, str):
        tickers = [tickers]
    end = end or _today()

    frames: list[pd.DataFrame] = []
    for query in tickers:
        info = resolve_strict(query)
        df = _fetch_single(info, start, end, source)
        if not df.empty:
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)

    # Resample if non-daily frequency requested
    if frequency in ("1w", "1m") and "date" in result.columns:
        result = _resample(result, frequency)

    return result


def _resample(df: pd.DataFrame, frequency: str) -> pd.DataFrame:
    """Resample a daily price or macro DataFrame to weekly or monthly."""
    freq_map = {"1w": "W-FRI", "1m": "ME"}
    rule = freq_map.get(frequency, "W-FRI")

    out_frames = []
    id_col = "ticker" if "ticker" in df.columns else "series_id"
    for ident, grp in df.groupby(id_col):
        grp = grp.set_index("date").sort_index()
        if "close" in grp.columns:
            resampled = (
                grp[["open", "high", "low", "close", "volume"]]
                .resample(rule)
                .agg(
                    {
                        "open": "first",
                        "high": "max",
                        "low": "min",
                        "close": "last",
                        "volume": "sum",
                    }
                )
            )
        else:
            resampled = grp[["value"]].resample(rule).last()
        resampled = resampled.reset_index().rename(columns={"index": "date"})
        resampled[id_col] = ident
        out_frames.append(resampled)

    return pd.concat(out_frames, ignore_index=True) if out_frames else df


# ---------------------------------------------------------------------------
# Convenience aliases (backward-compat with data_helpers.py)
# ---------------------------------------------------------------------------


def get_prices(
    tickers: Union[str, list[str]],
    start: str,
    end: Optional[str] = None,
    **kwargs,
) -> pd.DataFrame:
    """Alias for get_data() targeting price/equity data."""
    return get_data(tickers, start=start, end=end, **kwargs)


def get_fred(
    series_ids: Union[str, list[str]],
    start: str,
    end: Optional[str] = None,
) -> pd.DataFrame:
    """Alias for get_data() targeting FRED macro series."""
    return get_data(series_ids, start=start, end=end, source="fred")


def get_vix(start: str, end: Optional[str] = None) -> pd.DataFrame:
    """Convenience: fetch VIX (VIXCLS) from FRED."""
    return get_data("VIXCLS", start=start, end=end, source="fred")


def get_spy(start: str, end: Optional[str] = None) -> pd.DataFrame:
    """Convenience: fetch SPY from yfinance."""
    return get_data("SPY", start=start, end=end, source="yfinance")


__all__ = [
    "get_data",
    "get_prices",
    "get_fred",
    "get_vix",
    "get_spy",
    "compute_rolling_sharpe",
    "compute_drawdown",
    "compute_correlation_matrix",
    "calculate_returns",
    "calculate_volatility",
]
