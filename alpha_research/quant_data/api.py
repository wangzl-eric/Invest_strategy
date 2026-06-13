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
from alpha_research.quant_data.pit import apply_publication_lag  # noqa: E402
from alpha_research.quant_data.ticker_map import (  # noqa: E402
    TickerInfo,
    resolve_strict,
)

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
    """Try to read macro/FRED data for *series_id* from the local Parquet lake.

    Searches both the prices dir and the FRED store
    (``data/market_data/fred/*.parquet``, long format date/series_id/value).
    """
    candidates = list(_PRICES_DIR.glob("*.parquet")) if _PRICES_DIR.exists() else []
    fred_dir = _PRICES_DIR.parent / "fred"
    if fred_dir.exists():
        candidates += list(fred_dir.glob("*.parquet"))

    # Multiple files can hold the same series (stale bundles vs refreshed
    # per-series caches) — return the match with the freshest end date.
    best: Optional[pd.DataFrame] = None
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
            if sub.empty:
                continue
            if best is None or sub["date"].max() > best["date"].max():
                best = sub
        except Exception:
            continue
    return best


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

    try:
        import pandas_datareader.data as web
    except ImportError:
        return _fetch_fred_csv(series_id, start, end)

    api_key = os.getenv("FRED_API_KEY", "")
    kwargs = {"api_key": api_key} if api_key else {}
    raw = web.DataReader(series_id, "fred", start, end, **kwargs)
    raw = raw.reset_index()
    raw.columns = ["date", "value"]
    raw["series_id"] = series_id
    raw["date"] = pd.to_datetime(raw["date"])
    return raw[["date", "series_id", "value"]]


def _fetch_fred_csv(series_id: str, start: str, end: str) -> pd.DataFrame:
    """Keyless fallback: FRED's public fredgraph CSV endpoint."""
    import io

    import requests

    url = (
        "https://fred.stlouisfed.org/graph/fredgraph.csv"
        f"?id={series_id}&cosd={start}&coed={end}"
    )
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    raw = pd.read_csv(io.StringIO(resp.text))
    date_col = "observation_date" if "observation_date" in raw.columns else "DATE"
    raw = raw.rename(columns={date_col: "date", series_id: "value"})
    raw["value"] = pd.to_numeric(raw["value"], errors="coerce")
    raw = raw.dropna(subset=["value"])
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
    """Fetch one instrument: local first, then API fallback.

    The local cache is used only when it covers the requested *end* within
    a per-source staleness tolerance (prices: 7 days, macro: 75 days to
    accommodate monthly publication lags); otherwise the API is queried and
    the cache refreshed. Start-side gaps are left to the QC layer — they
    are usually genuine instrument inception, not cache problems.
    """
    effective_source = source or info.source

    # Try local cache first
    if effective_source == "fred":
        local = _read_parquet_macro(info.canonical_id, start, end)
        staleness_tolerance_days = 75
    else:
        local = _read_parquet_prices(info.canonical_id, start, end)
        staleness_tolerance_days = 7

    if local is not None and not local.empty:
        cached_end = pd.to_datetime(local["date"]).max()
        if cached_end >= pd.Timestamp(end) - pd.Timedelta(
            days=staleness_tolerance_days
        ):
            return local
        log.warning(
            "local cache for %s ends %s but %s requested — refreshing from %s",
            info.canonical_id,
            cached_end.date(),
            end,
            effective_source,
        )

    if local is None or local.empty:
        # Cache miss — fetch from API
        log.warning(
            "cache miss for %s — fetching from %s",
            info.canonical_id,
            effective_source,
        )

    try:
        if effective_source == "fred":
            df = _fetch_fred(info.canonical_id, start, end)
        elif effective_source == "binance":
            df = _fetch_binance(info.canonical_id, start, end)
        else:
            df = _fetch_yfinance(info.canonical_id, start, end)
    except Exception as exc:
        if local is not None and not local.empty:
            log.warning(
                "API refresh for %s failed (%s) — using stale local cache",
                info.canonical_id,
                exc,
            )
            return local
        raise

    if df.empty:
        if local is not None and not local.empty:
            log.warning(
                "API refresh for %s returned no rows — using stale local cache",
                info.canonical_id,
            )
            return local
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
    pit: bool = True,
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
        pit:       Point-in-time mode (default True). Macro/FRED results
                   have their dates shifted from reference date to a
                   conservative availability date (publication lag), with
                   the original kept in a ``reference_date`` column. Price
                   data is unaffected. Passing pit=False returns raw
                   reference-dated macro data and logs a look-ahead warning.

    Returns:
        DataFrame with columns (date, ticker, open, high, low, close, volume)
        for price data, or (date, series_id, value[, reference_date]) for
        macro/FRED data.
    """
    if isinstance(tickers, str):
        tickers = [tickers]
    end = end or _today()

    frames: list[pd.DataFrame] = []
    for query in tickers:
        info = resolve_strict(query)
        df = _fetch_single(info, start, end, source)
        if df.empty:
            continue
        if "series_id" in df.columns:
            if pit:
                df = apply_publication_lag(df)
                # Availability-dating can push observations past `end`;
                # keep the window the caller asked for.
                df = df[df["date"] <= pd.Timestamp(end)]
            else:
                log.warning(
                    "get_data(pit=False): macro series %s returned with raw "
                    "reference dates — look-ahead biased if used in a backtest.",
                    df["series_id"].iloc[0],
                )
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
    # pandas renamed the month-end alias "M" -> "ME" in 2.2
    monthly = "ME" if pd.__version__ >= "2.2" else "M"
    freq_map = {"1w": "W-FRI", "1m": monthly}
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
