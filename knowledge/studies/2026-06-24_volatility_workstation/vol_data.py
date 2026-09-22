"""Volatility workstation — data loaders (akshare-first, high-resolution).

Self-contained loaders for the instruments this workstation studies:

    VIX        CBOE Volatility Index
    USDX       US Dollar Index (DXY)
    GOLD_SPOT  Gold spot price
    GOLD_FUT   Gold futures price
    SP500      S&P 500 Index
    OIS        Overnight Index Swap rates (SOFR + EFFR)
    ON_RRP     Overnight Reverse Repurchase Agreements (Fed facility)

Design notes (verified live against akshare 1.18.x on 2026-06-24)
-----------------------------------------------------------------
akshare's reliability is **source-dependent**. From outside mainland China the
EastMoney history endpoints (``push2his.eastmoney.com``) are frequently blocked
and will *hang*, while Sina / the foreign-futures feed / the Shanghai Gold
Exchange feed are reliable. So every akshare call here is wrapped in
``_guarded`` (hard wall-clock timeout + bounded retry); on failure the loader
falls back to the platform's `get_data` (yfinance / FRED) and records which
source actually served the data in a ``source`` column.

Resolution available per instrument via akshare:
  - GOLD_FUT  : **1-minute** (SHFE `AU0` via `futures_zh_minute_sina`) — highest.
  - GOLD_SPOT : daily (intl `XAU` USD via `futures_foreign_hist`; or SGE `Au99.99` CNY).
  - SP500     : daily (`index_us_stock_sina('.INX')`, Sina — reliable, back to 2004).
  - USDX      : daily (`index_global_hist_em('美元指数')`, EastMoney — region-gated).
  - VIX       : akshare carries **no CBOE VIX**. Use FRED `VIXCLS`.
  - OIS       : FRED only (SOFR from 2018-04, EFFR from 2000-07).
  - ON_RRP    : FRED only (RRPONTSYD from 2003-02).

Every loader returns a tidy DataFrame and caches to ``data/<key>__<res>.parquet``.
This is a playground module (no rigor gates) — fast iteration, learning-focused.
"""

from __future__ import annotations

import concurrent.futures as _cf
import sys
import time
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

_HERE = Path(__file__).resolve().parent
_DATA = _HERE / "data"
_DATA.mkdir(exist_ok=True)

# Make the repo importable so we can reuse the platform's unified data layer.
# .../knowledge/studies/<study>/vol_data.py -> parents[3] is the repo root.
_REPO_ROOT = _HERE.parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


# ---------------------------------------------------------------------------
# Robust akshare call wrapper: hard timeout + bounded retry
# ---------------------------------------------------------------------------

_TRANSIENT = (
    "RemoteDisconnected",
    "Connection aborted",
    "Connection reset",
    "timed out",
    "Read timed out",
    "Max retries exceeded",
    "Remote end closed",
    "Socket is not connected",
)


def _guarded(
    fn: Callable[[], pd.DataFrame],
    *,
    timeout: float = 12.0,
    attempts: int = 2,
    label: str = "akshare",
) -> pd.DataFrame:
    """Run *fn* with a hard wall-clock *timeout* and a couple of retries.

    EastMoney history endpoints can hang for 30-60s when region-blocked;
    the timeout turns that into a fast, catchable failure so callers fall back.
    """
    last: Optional[Exception] = None
    for i in range(attempts):
        # NB: do NOT use `with ThreadPoolExecutor(...)` — its __exit__ joins the
        # worker, which blocks forever on a hung network call and defeats the
        # timeout. Create explicitly and shut down with wait=False so a stuck
        # request is abandoned (the daemon-ish thread dies with the kernel).
        ex = _cf.ThreadPoolExecutor(max_workers=1)
        fut = ex.submit(fn)
        try:
            res = fut.result(timeout=timeout)
            ex.shutdown(wait=False)
            return res
        except _cf.TimeoutError:
            ex.shutdown(wait=False, cancel_futures=True)
            last = TimeoutError(f"{label} exceeded {timeout:.0f}s")
        except Exception as exc:  # noqa: BLE001
            ex.shutdown(wait=False, cancel_futures=True)
            last = exc
            msg = f"{type(exc).__name__}: {exc}"
            if not any(m in msg for m in _TRANSIENT):
                break
        if i < attempts - 1:
            time.sleep(0.8 * (2**i))
    raise last if last else RuntimeError(f"{label} failed")


# ---------------------------------------------------------------------------
# OHLC normalization (handles akshare's English + Chinese column variants)
# ---------------------------------------------------------------------------

_COLMAP = {
    # timestamps
    "date": "date",
    "日期": "date",
    "datetime": "datetime",
    "交易时间": "date",
    "时间": "datetime",
    # ohlc (en)
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume",
    "hold": "open_interest",
    "position": "open_interest",
    # ohlc (cn)
    "开盘": "open",
    "开盘价": "open",
    "今开": "open",
    "最高": "high",
    "最高价": "high",
    "最低": "low",
    "最低价": "low",
    "收盘": "close",
    "收盘价": "close",
    "最新价": "close",
    "晚盘价": "close",
    "成交量": "volume",
    "持仓量": "open_interest",
}


def _normalize_ohlc(df: pd.DataFrame, *, symbol: str, source: str) -> pd.DataFrame:
    """Map a raw akshare frame to tidy [date|datetime, OHLC, volume, symbol, source]."""
    out = df.rename(columns={c: _COLMAP.get(c, c) for c in df.columns})
    ts = "datetime" if "datetime" in out.columns else "date"
    out[ts] = pd.to_datetime(out[ts])
    keep = [ts] + [
        c
        for c in ("open", "high", "low", "close", "volume", "open_interest")
        if c in out.columns
    ]
    out = out[keep].copy()
    for c in keep[1:]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out["symbol"] = symbol
    out["source"] = source
    return out.sort_values(ts).reset_index(drop=True)


def _cache_path(key: str, res: str) -> Path:
    return _DATA / f"{key}__{res}.parquet"


def _maybe_cache(df: pd.DataFrame, key: str, res: str, use_cache: bool) -> pd.DataFrame:
    if use_cache and not df.empty:
        df.to_parquet(_cache_path(key, res), index=False)
    return df


def _read_cache(key: str, res: str) -> Optional[pd.DataFrame]:
    p = _cache_path(key, res)
    if p.exists():
        return pd.read_parquet(p)
    return None


def _window(df: pd.DataFrame, start: Optional[str], end: Optional[str]) -> pd.DataFrame:
    ts = "datetime" if "datetime" in df.columns else "date"
    if start:
        df = df[df[ts] >= pd.Timestamp(start)]
    if end:
        df = df[df[ts] <= pd.Timestamp(end) + pd.Timedelta(days=1)]
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 1) CBOE VIX  — akshare has none; FRED VIXCLS is the real thing
# ---------------------------------------------------------------------------


def load_vix(
    start: str = "1990-01-01", end: Optional[str] = None, use_cache: bool = True
) -> pd.DataFrame:
    """CBOE VIX (daily OHLC). akshare does not carry CBOE VIX.

    Primary: yfinance ``^VIX`` — full OHLC back to 1990-01-02.
    Fallback: FRED ``VIXCLS`` (close only, also back to 1990) via direct fetch
    (bypasses the ``get_data`` resolver which truncates the series).

    Returns tidy [date, open, high, low, close, symbol, source].
    """
    cached = _read_cache("VIX", "1d") if use_cache else None
    if cached is not None and not _stale(cached, end):
        return _window(cached, start, end)

    end_str = end or pd.Timestamp.today().strftime("%Y-%m-%d")

    # Primary: yfinance ^VIX — full OHLC back to 1990
    try:
        from alpha_research.quant_data import api as _api

        df = _api._fetch_yfinance("^VIX", start, end_str)
        if not df.empty:
            out = df[["date", "open", "high", "low", "close"]].copy()
            out["date"] = pd.to_datetime(out["date"])
            out["symbol"] = "VIX"
            out["source"] = "yfinance:^VIX"
            out = out.sort_values("date").reset_index(drop=True)
            _maybe_cache(out, "VIX", "1d", use_cache)
            return _window(out, start, end)
    except Exception as exc:  # noqa: BLE001
        print(f"[vix] yfinance ^VIX failed ({exc}); trying FRED VIXCLS")

    # Fallback: FRED VIXCLS — close only, also back to 1990
    from alpha_research.quant_data.api import _fetch_fred

    df = _fetch_fred("VIXCLS", start, end_str)
    if df.empty:
        return cached if cached is not None else df
    out = df.rename(columns={"value": "close"})[["date", "close"]].copy()
    out["date"] = pd.to_datetime(out["date"])
    out["symbol"] = "VIX"
    out["source"] = "fred:VIXCLS"
    out = out.sort_values("date").reset_index(drop=True)
    _maybe_cache(out, "VIX", "1d", use_cache)
    return _window(out, start, end)


def load_china_qvix(underlying: str = "300etf", minute: bool = False) -> pd.DataFrame:
    """akshare-native vol gauge: China option-implied volatility (QVIX).

    NOT CBOE VIX — it is the implied-vol index of a Chinese ETF option
    (e.g. 300ETF). ``minute=True`` returns intraday resolution. Best-effort:
    the QVIX host is flaky from some networks.
    """
    import akshare as ak

    fn_name = f"index_option_{underlying}_{'min_' if minute else ''}qvix"
    fn = getattr(ak, fn_name)
    raw = _guarded(fn, label=fn_name, timeout=15.0)
    ts = (
        "time"
        if "time" in raw.columns
        else ("datetime" if "datetime" in raw.columns else "date")
    )
    raw = raw.rename(columns={ts: "datetime" if minute else "date", "qvix": "close"})
    raw["symbol"] = f"QVIX_{underlying}"
    raw["source"] = f"akshare:{fn_name}"
    return raw


# ---------------------------------------------------------------------------
# 2) US Dollar Index (DXY)
# ---------------------------------------------------------------------------


def load_usd_index(
    start: str = "2015-01-01", end: Optional[str] = None, use_cache: bool = True
) -> pd.DataFrame:
    """US Dollar Index (daily).

    akshare-first: ``index_global_hist_em('美元指数')`` (EastMoney; region-gated).
    Fallback: FRED broad dollar index ``DTWEXBGS``. ``source`` records which won.
    """
    cached = _read_cache("USDX", "1d") if use_cache else None
    if cached is not None and not _stale(cached, end):
        return _window(cached, start, end)

    # Primary: akshare EastMoney global index (region-gated; may hang/fail offshore).
    try:
        import akshare as ak

        raw = _guarded(
            lambda: ak.index_global_hist_em(symbol="美元指数"),
            label="index_global_hist_em(美元指数)",
            timeout=12.0,
        )
        out = _normalize_ohlc(raw, symbol="USDX", source="akshare:美元指数")
        _maybe_cache(out, "USDX", "1d", use_cache)
        return _window(out, start, end)
    except Exception as exc:  # noqa: BLE001 — fall back transparently
        print(
            f"[usd_index] akshare unavailable ({exc}); falling back to ICE DXY (yfinance DX-Y.NYB)"
        )

    # Fallback: the actual ICE US Dollar Index via yfinance, fetched directly
    # (bypasses the NL ticker resolver, which doesn't carry this symbol).
    from alpha_research.quant_data import api as _api

    df = _api._fetch_yfinance(
        "DX-Y.NYB", start, end or pd.Timestamp.today().strftime("%Y-%m-%d")
    )
    if df.empty:
        return cached if cached is not None else df
    out = df[["date", "open", "high", "low", "close", "volume"]].copy()
    out["date"] = pd.to_datetime(out["date"])
    out["symbol"] = "USDX"
    out["source"] = "yfinance:DX-Y.NYB"
    out = out.sort_values("date").reset_index(drop=True)
    _maybe_cache(out, "USDX", "1d", use_cache)
    return _window(out, start, end)


# ---------------------------------------------------------------------------
# 3) Gold spot
# ---------------------------------------------------------------------------


def load_gold_spot(
    start: str = "2015-01-01",
    end: Optional[str] = None,
    market: str = "intl",
    use_cache: bool = True,
) -> pd.DataFrame:
    """Gold spot (daily).

    market='intl' : XAU/USD international spot (akshare ``futures_foreign_hist('XAU')``), USD/oz.
    market='cn'   : Shanghai Gold Exchange ``Au99.99`` (akshare ``spot_hist_sge``), CNY/gram.
    """
    import akshare as ak

    key = f"GOLD_SPOT_{market}"
    cached = _read_cache(key, "1d") if use_cache else None
    if cached is not None and not _stale(cached, end):
        return _window(cached, start, end)

    if market == "cn":
        raw = _guarded(
            lambda: ak.spot_hist_sge(symbol="Au99.99"), label="spot_hist_sge"
        )
        out = _normalize_ohlc(raw, symbol="XAU_CNY", source="akshare:spot_hist_sge")
    else:
        raw = _guarded(
            lambda: ak.futures_foreign_hist(symbol="XAU"),
            label="futures_foreign_hist(XAU)",
        )
        out = _normalize_ohlc(
            raw, symbol="XAU_USD", source="akshare:futures_foreign_hist:XAU"
        )
    _maybe_cache(out, key, "1d", use_cache)
    return _window(out, start, end)


# ---------------------------------------------------------------------------
# 4) Gold futures  (daily intl + high-res domestic minute)
# ---------------------------------------------------------------------------


def load_gold_futures(
    start: str = "2015-01-01",
    end: Optional[str] = None,
    market: str = "comex",
    use_cache: bool = True,
) -> pd.DataFrame:
    """Gold futures, **daily**.

    market='comex' : COMEX continuous (akshare ``futures_foreign_hist('GC')``), USD/oz.
    market='shfe'  : Shanghai (SHFE) continuous ``AU0`` (akshare ``futures_main_sina``), CNY/gram.

    For the highest resolution available, see :func:`load_gold_futures_minute`.
    """
    import akshare as ak

    key = f"GOLD_FUT_{market}"
    cached = _read_cache(key, "1d") if use_cache else None
    if cached is not None and not _stale(cached, end):
        return _window(cached, start, end)

    if market == "shfe":
        s = pd.Timestamp(start).strftime("%Y%m%d")
        e = pd.Timestamp(end or pd.Timestamp.today()).strftime("%Y%m%d")
        raw = _guarded(
            lambda: ak.futures_main_sina(symbol="AU0", start_date=s, end_date=e),
            label="futures_main_sina(AU0)",
        )
        out = _normalize_ohlc(
            raw, symbol="AU_SHFE", source="akshare:futures_main_sina:AU0"
        )
    else:
        raw = _guarded(
            lambda: ak.futures_foreign_hist(symbol="GC"),
            label="futures_foreign_hist(GC)",
        )
        out = _normalize_ohlc(
            raw, symbol="GC_COMEX", source="akshare:futures_foreign_hist:GC"
        )
    _maybe_cache(out, key, "1d", use_cache)
    return _window(out, start, end)


def load_gold_futures_minute(period: str = "1", use_cache: bool = True) -> pd.DataFrame:
    """**Highest-resolution gold available via akshare**: SHFE gold futures intraday.

    akshare ``futures_zh_minute_sina('AU0', period)`` (Sina, reliable). ``period`` ∈
    {'1','5','15','30','60'} minutes. Returns the most recent ~1000+ bars the feed
    exposes (it is a rolling window, not full history). CNY/gram.
    """
    import akshare as ak

    raw = _guarded(
        lambda: ak.futures_zh_minute_sina(symbol="AU0", period=period),
        label=f"futures_zh_minute_sina(AU0,{period})",
        timeout=20.0,
    )
    out = _normalize_ohlc(
        raw, symbol="AU_SHFE", source=f"akshare:futures_zh_minute_sina:AU0:{period}m"
    )
    _maybe_cache(out, "GOLD_FUT_shfe", f"{period}m", use_cache)
    return out


# ---------------------------------------------------------------------------
# 5) S&P 500
# ---------------------------------------------------------------------------


def load_sp500(
    start: str = "2004-01-01",
    end: Optional[str] = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    """S&P 500 index (daily OHLCV).

    akshare-first: ``index_us_stock_sina('.INX')`` (Sina, reliable, back to 2004).
    Fallback: yfinance ``^GSPC`` (back to ~1928).
    """
    cached = _read_cache("SP500", "1d") if use_cache else None
    if cached is not None and not _stale(cached, end):
        return _window(cached, start, end)

    try:
        import akshare as ak

        raw = _guarded(
            lambda: ak.index_us_stock_sina(symbol=".INX"),
            label="index_us_stock_sina(.INX)",
            timeout=15.0,
        )
        out = _normalize_ohlc(
            raw, symbol="SP500", source="akshare:index_us_stock_sina:.INX"
        )
        _maybe_cache(out, "SP500", "1d", use_cache)
        return _window(out, start, end)
    except Exception as exc:  # noqa: BLE001
        print(f"[sp500] akshare unavailable ({exc}); falling back to yfinance ^GSPC")

    from alpha_research.quant_data import api as _api

    df = _api._fetch_yfinance(
        "^GSPC", start, end or pd.Timestamp.today().strftime("%Y-%m-%d")
    )
    if df.empty:
        return cached if cached is not None else df
    out = df[["date", "open", "high", "low", "close", "volume"]].copy()
    out["date"] = pd.to_datetime(out["date"])
    out["symbol"] = "SP500"
    out["source"] = "yfinance:^GSPC"
    out = out.sort_values("date").reset_index(drop=True)
    _maybe_cache(out, "SP500", "1d", use_cache)
    return _window(out, start, end)


# ---------------------------------------------------------------------------
# 6) OIS rates (SOFR + EFFR)
# ---------------------------------------------------------------------------


def load_ois(
    start: str = "2000-01-01",
    end: Optional[str] = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Overnight Index Swap benchmark rates (daily).

    Loads both FRED ``SOFR`` (from 2018-04) and ``EFFR`` (from 2000-07) and
    merges them on date. SOFR is the post-LIBOR OIS benchmark; EFFR extends the
    history back further.

    Returns [date, sofr, effr, symbol, source].
    """
    cached = _read_cache("OIS", "1d") if use_cache else None
    if cached is not None and not _stale(cached, end):
        return _window(cached, start, end)

    from alpha_research.quant_data.api import _fetch_fred

    sofr = _fetch_fred("SOFR", start, end or pd.Timestamp.today().strftime("%Y-%m-%d"))
    effr = _fetch_fred("EFFR", start, end or pd.Timestamp.today().strftime("%Y-%m-%d"))

    sofr = sofr.rename(columns={"value": "sofr"})[["date", "sofr"]].copy()
    effr = effr.rename(columns={"value": "effr"})[["date", "effr"]].copy()
    sofr["date"] = pd.to_datetime(sofr["date"])
    effr["date"] = pd.to_datetime(effr["date"])

    out = (
        effr.merge(sofr, on="date", how="outer")
        .sort_values("date")
        .reset_index(drop=True)
    )
    out["symbol"] = "OIS"
    out["source"] = "fred:SOFR+EFFR"
    _maybe_cache(out, "OIS", "1d", use_cache)
    return _window(out, start, end)


# ---------------------------------------------------------------------------
# 7) Overnight Reverse Repurchase Agreements (ON RRP)
# ---------------------------------------------------------------------------


def load_on_rrp(
    start: str = "2003-01-01",
    end: Optional[str] = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Fed ON RRP facility usage (daily, billions USD).

    Source: FRED ``RRPONTSYD`` — Treasury Securities Sold by the Federal Reserve
    in Overnight Reverse Repurchase Agreements. Available from 2003-02.

    Returns [date, close (=amount in billions), symbol, source].
    """
    cached = _read_cache("ON_RRP", "1d") if use_cache else None
    if cached is not None and not _stale(cached, end):
        return _window(cached, start, end)

    from alpha_research.quant_data.api import _fetch_fred

    df = _fetch_fred(
        "RRPONTSYD", start, end or pd.Timestamp.today().strftime("%Y-%m-%d")
    )
    if df.empty:
        return cached if cached is not None else df
    out = df.rename(columns={"value": "close"})[["date", "close"]].copy()
    out["date"] = pd.to_datetime(out["date"])
    out["symbol"] = "ON_RRP"
    out["source"] = "fred:RRPONTSYD"
    out = out.sort_values("date").reset_index(drop=True)
    _maybe_cache(out, "ON_RRP", "1d", use_cache)
    return _window(out, start, end)


# ---------------------------------------------------------------------------
# Convenience: load everything + a coverage summary
# ---------------------------------------------------------------------------


def _stale(df: pd.DataFrame, end: Optional[str], tol_days: int = 5) -> bool:
    if df is None or df.empty:
        return True
    ts = "datetime" if "datetime" in df.columns else "date"
    target = pd.Timestamp(end) if end else pd.Timestamp.today()
    return pd.to_datetime(df[ts]).max() < target - pd.Timedelta(days=tol_days)


def load_all(
    start: str = "2018-01-01", end: Optional[str] = None
) -> dict[str, pd.DataFrame]:
    """Load all headline instruments (daily) + the high-res gold minute feed.

    Returns a dict keyed by instrument. Each loader degrades gracefully; a failed
    instrument maps to an empty DataFrame rather than raising.
    """
    out: dict[str, pd.DataFrame] = {}
    jobs = {
        "VIX": lambda: load_vix(start, end),
        "USDX": lambda: load_usd_index(start, end),
        "GOLD_SPOT": lambda: load_gold_spot(start, end, market="intl"),
        "GOLD_FUT": lambda: load_gold_futures(start, end, market="comex"),
        "SP500": lambda: load_sp500(start, end),
        "OIS": lambda: load_ois(start, end),
        "ON_RRP": lambda: load_on_rrp(start, end),
        "GOLD_FUT_1MIN": lambda: load_gold_futures_minute("1"),
    }
    for k, fn in jobs.items():
        try:
            out[k] = fn()
        except Exception as exc:  # noqa: BLE001
            print(f"[load_all] {k} failed: {exc}")
            out[k] = pd.DataFrame()
    return out


def coverage(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """One-row-per-instrument summary: source, resolution, rows, date range."""
    rows = []
    for k, df in frames.items():
        if df is None or df.empty:
            rows.append(
                {
                    "instrument": k,
                    "rows": 0,
                    "source": "—",
                    "start": "—",
                    "end": "—",
                    "resolution": "—",
                }
            )
            continue
        ts = "datetime" if "datetime" in df.columns else "date"
        res = "intraday" if ts == "datetime" else "daily"
        rows.append(
            {
                "instrument": k,
                "rows": len(df),
                "source": df["source"].iloc[0] if "source" in df.columns else "?",
                "start": str(pd.to_datetime(df[ts]).min())[:16],
                "end": str(pd.to_datetime(df[ts]).max())[:16],
                "resolution": res,
            }
        )
    return pd.DataFrame(rows)
