from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path("/Users/zelin/Desktop/PA Investment/Invest_strategy")
STUDY_DIR = (
    REPO_ROOT
    / "workstation"
    / "playground"
    / "studies"
    / "2026-03-29_expected_returns_ilmanen"
)
PRICES_DIR = REPO_ROOT / "data" / "market_data" / "prices"
FRED_DIR = REPO_ROOT / "data" / "market_data" / "fred"
CATALOG_PATH = REPO_ROOT / "data" / "market_data" / "catalog.json"
DEFAULT_START = "2024-02-26"
DEFAULT_END = "2026-02-27"


def read_catalog() -> dict:
    with CATALOG_PATH.open() as handle:
        return json.load(handle)


def filter_date(
    frame: pd.DataFrame,
    start: str | None = DEFAULT_START,
    end: str | None = DEFAULT_END,
    date_col: str = "date",
) -> pd.DataFrame:
    out = frame.copy()
    if date_col in out.columns:
        out[date_col] = pd.to_datetime(out[date_col])
        if start is not None:
            out = out[out[date_col] >= pd.Timestamp(start)]
        if end is not None:
            out = out[out[date_col] <= pd.Timestamp(end)]
        return out

    out.index = pd.to_datetime(out.index)
    if start is not None:
        out = out[out.index >= pd.Timestamp(start)]
    if end is not None:
        out = out[out.index <= pd.Timestamp(end)]
    return out


def business_days(
    start: str | None = DEFAULT_START,
    end: str | None = DEFAULT_END,
) -> pd.DatetimeIndex:
    return pd.date_range(start, end, freq="B")


def load_fred_series(
    series_ids: list[str] | tuple[str, ...],
    start: str | None = DEFAULT_START,
    end: str | None = DEFAULT_END,
) -> pd.DataFrame:
    frames = []
    wanted = set(series_ids)
    for parquet_file in sorted(FRED_DIR.glob("*.parquet")):
        df = pd.read_parquet(parquet_file)
        if "series_id" not in df.columns:
            continue
        sub = df[df["series_id"].isin(wanted)]
        if not sub.empty:
            frames.append(filter_date(sub, start=start, end=end))

    if not frames:
        return pd.DataFrame(index=business_days(start, end))

    joined = pd.concat(frames, ignore_index=True).drop_duplicates(["date", "series_id"])
    wide = (
        joined.pivot(index="date", columns="series_id", values="value")
        .sort_index()
        .apply(pd.to_numeric, errors="coerce")
    )
    wide.index = pd.to_datetime(wide.index)
    return wide


def load_price_series(
    tickers: list[str] | tuple[str, ...],
    start: str | None = DEFAULT_START,
    end: str | None = DEFAULT_END,
    value_col: str = "close",
) -> pd.DataFrame:
    frames = []
    wanted = set(tickers)
    for parquet_file in sorted(PRICES_DIR.glob("*.parquet")):
        df = pd.read_parquet(parquet_file)
        if "ticker" not in df.columns or value_col not in df.columns:
            continue
        sub = df[df["ticker"].isin(wanted)]
        if not sub.empty:
            frames.append(filter_date(sub, start=start, end=end))

    if not frames:
        return pd.DataFrame(index=business_days(start, end))

    joined = pd.concat(frames, ignore_index=True).drop_duplicates(["date", "ticker"], keep="last")
    wide = (
        joined.pivot(index="date", columns="ticker", values=value_col)
        .sort_index()
        .apply(pd.to_numeric, errors="coerce")
    )
    wide.index = pd.to_datetime(wide.index)
    return wide


def load_named_price_frame(
    name: str,
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    path = PRICES_DIR / f"{name}.parquet"
    frame = pd.read_parquet(path)
    if "date" not in frame.columns:
        frame = frame.copy()
        frame.index = pd.to_datetime(frame.index)
        frame.index.name = "date"
    else:
        frame = frame.copy()
        frame["date"] = pd.to_datetime(frame["date"])
        frame = frame.set_index("date")
    frame = frame.sort_index()
    frame = filter_date(frame, start=start, end=end)
    frame.index.name = "date"
    return frame


def load_named_price_series(
    name: str,
    value_col: str = "close",
    start: str | None = None,
    end: str | None = None,
) -> pd.Series:
    frame = load_named_price_frame(name, start=start, end=end)
    return pd.to_numeric(frame[value_col], errors="coerce").rename(name)


def simple_returns(prices: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    return prices.pct_change()


def log_returns(prices: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    return np.log(prices).diff()


def forward_return(
    prices: pd.Series,
    horizon: int,
) -> pd.Series:
    return prices.shift(-horizon).div(prices).sub(1.0).rename(f"fwd_{horizon}d")


def annualize_rate(series: pd.Series, basis: float = 100.0) -> pd.Series:
    return pd.to_numeric(series, errors="coerce") / basis


def annualized_realized_vol(
    returns: pd.Series,
    window: int = 21,
    trading_days: int = 252,
) -> pd.Series:
    return returns.rolling(window, min_periods=window).std() * np.sqrt(trading_days)


def rolling_zscore(
    series: pd.Series,
    window: int,
    min_periods: int | None = None,
) -> pd.Series:
    min_periods = min_periods or max(20, window // 3)
    mean = series.rolling(window, min_periods=min_periods).mean()
    std = series.rolling(window, min_periods=min_periods).std()
    return (series - mean) / std.replace(0.0, np.nan)
