"""Cross-asset market data service.

Aggregates real-time and macro data from yfinance and FRED API
with TTL caching per asset class.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Instrument definitions
# ---------------------------------------------------------------------------

RATES_TICKERS = {
    "^IRX": {"name": "3-Month T-Bill", "tenor": "3M"},
    "^FVX": {"name": "5-Year Treasury", "tenor": "5Y"},
    "^TNX": {"name": "10-Year Treasury", "tenor": "10Y"},
    "^TYX": {"name": "30-Year Treasury", "tenor": "30Y"},
}

RATES_FRED_SERIES = {
    # Treasury Yields — full curve for charting
    "DGS1MO": {"name": "1-Month Treasury", "tenor": "1M", "category": "treasury", "tenor_years": 1 / 12},
    "DGS3MO": {"name": "3-Month Treasury", "tenor": "3M", "category": "treasury", "tenor_years": 0.25},
    "DGS6MO": {"name": "6-Month Treasury", "tenor": "6M", "category": "treasury", "tenor_years": 0.5},
    "DGS1": {"name": "1-Year Treasury", "tenor": "1Y", "category": "treasury", "tenor_years": 1},
    "DGS2": {"name": "2-Year Treasury", "tenor": "2Y", "category": "treasury", "tenor_years": 2},
    "DGS3": {"name": "3-Year Treasury", "tenor": "3Y", "category": "treasury", "tenor_years": 3},
    "DGS5": {"name": "5-Year Treasury", "tenor": "5Y", "category": "treasury", "tenor_years": 5},
    "DGS7": {"name": "7-Year Treasury", "tenor": "7Y", "category": "treasury", "tenor_years": 7},
    "DGS10": {"name": "10-Year Treasury", "tenor": "10Y", "category": "treasury", "tenor_years": 10},
    "DGS20": {"name": "20-Year Treasury", "tenor": "20Y", "category": "treasury", "tenor_years": 20},
    "DGS30": {"name": "30-Year Treasury", "tenor": "30Y", "category": "treasury", "tenor_years": 30},
    # Yield Curve Spreads
    "T10Y2Y": {"name": "10Y-2Y Spread", "tenor": "2s10s", "category": "curve_spread"},
    "T10Y3M": {"name": "10Y-3M Spread", "tenor": "10Y3M", "category": "curve_spread"},
    # Policy Rates
    "DFEDTARU": {"name": "Fed Funds Target (Upper)", "tenor": "FF", "category": "policy"},
    "SOFR": {"name": "SOFR", "tenor": "O/N", "category": "policy"},
    # Breakeven Inflation & Forward Inflation
    "T5YIE": {"name": "5Y Breakeven Inflation", "tenor": "5Y BEI", "category": "inflation"},
    "T10YIE": {"name": "10Y Breakeven Inflation", "tenor": "10Y BEI", "category": "inflation"},
    "T5YIFR": {"name": "5Y5Y Forward Inflation", "tenor": "5Y5Y Fwd", "category": "inflation"},
    # TIPS Real Yields
    "DFII5": {"name": "5Y Real Yield (TIPS)", "tenor": "5Y Real", "category": "real_yield", "tenor_years": 5},
    "DFII10": {"name": "10Y Real Yield (TIPS)", "tenor": "10Y Real", "category": "real_yield", "tenor_years": 10},
    "DFII30": {"name": "30Y Real Yield (TIPS)", "tenor": "30Y Real", "category": "real_yield", "tenor_years": 30},
}

# USD swap rate series (DSWP*) were discontinued on FRED. If a professional
# data feed becomes available, add swap rates here and uncomment SWAP_SPREAD_PAIRS.
SWAP_SPREAD_PAIRS: dict = {}

MACRO_YF_FALLBACK = {
    "^VIX": {"name": "VIX (Equity Volatility)", "unit": "index", "freq": "real-time"},
    "HYG": {"name": "HY Credit ETF (HYG)", "unit": "$", "freq": "real-time"},
    "LQD": {"name": "IG Credit ETF (LQD)", "unit": "$", "freq": "real-time"},
    "TIP": {"name": "TIPS Bond ETF (TIP)", "unit": "$", "freq": "real-time"},
    "IEF": {"name": "7-10Y Treasury ETF (IEF)", "unit": "$", "freq": "real-time"},
    "GLD": {"name": "Gold ETF (GLD)", "unit": "$", "freq": "real-time"},
}

FX_TICKERS = {
    "DX-Y.NYB": {"name": "US Dollar Index (DXY)", "pair": "DXY"},
    "EURUSD=X": {"name": "EUR/USD", "pair": "EURUSD"},
    "GBPUSD=X": {"name": "GBP/USD", "pair": "GBPUSD"},
    "USDJPY=X": {"name": "USD/JPY", "pair": "USDJPY"},
    "AUDUSD=X": {"name": "AUD/USD", "pair": "AUDUSD"},
    "USDCAD=X": {"name": "USD/CAD", "pair": "USDCAD"},
    "USDCHF=X": {"name": "USD/CHF", "pair": "USDCHF"},
    "NZDUSD=X": {"name": "NZD/USD", "pair": "NZDUSD"},
    "USDSEK=X": {"name": "USD/SEK", "pair": "USDSEK"},
    "USDNOK=X": {"name": "USD/NOK", "pair": "USDNOK"},
}

EQUITY_TICKERS = {
    "^GSPC": {"name": "S&P 500", "region": "US"},
    "^NDX": {"name": "Nasdaq 100", "region": "US"},
    "^RUT": {"name": "Russell 2000", "region": "US"},
    "^STOXX": {"name": "STOXX 600", "region": "EU"},
    "^N225": {"name": "Nikkei 225", "region": "JP"},
    "^VIX": {"name": "VIX", "region": "US"},
}

COMMODITY_TICKERS = {
    "CL=F": {"name": "WTI Crude Oil", "group": "Energy"},
    "BZ=F": {"name": "Brent Crude Oil", "group": "Energy"},
    "NG=F": {"name": "Natural Gas", "group": "Energy"},
    "GC=F": {"name": "Gold", "group": "Metals"},
    "SI=F": {"name": "Silver", "group": "Metals"},
    "HG=F": {"name": "Copper", "group": "Metals"},
}

MACRO_FRED_SERIES = {
    "UNRATE": {"name": "Unemployment Rate", "unit": "%", "freq": "monthly"},
    "CPIAUCSL": {"name": "CPI (All Urban)", "unit": "index", "freq": "monthly"},
    "GDPC1": {"name": "Real GDP", "unit": "B$", "freq": "quarterly"},
    "UMCSENT": {"name": "Consumer Sentiment", "unit": "index", "freq": "monthly"},
    "NFCI": {"name": "Chicago Fed NFCI", "unit": "index", "freq": "weekly"},
    "BAMLH0A0HYM2": {"name": "HY OAS Spread", "unit": "bp", "freq": "daily"},
}

# Fed balance sheet / liquidity series for QE/QT monitoring.
# Units on FRED vary — divisor converts raw value to trillions of USD.
FED_LIQUIDITY_SERIES = {
    "WALCL":     {"name": "Fed Total Assets",                "freq": "weekly", "divisor": 1e6,  "raw_unit": "M$"},
    "RRPONTSYD": {"name": "ON Reverse Repo (RRP)",           "freq": "daily",  "divisor": 1e3,  "raw_unit": "B$"},
    "WRESBAL":   {"name": "Reserve Balances",                "freq": "weekly", "divisor": 1e6,  "raw_unit": "M$"},
    "WTREGEN":   {"name": "Treasury General Account (TGA)",  "freq": "weekly", "divisor": 1e6,  "raw_unit": "M$"},
    "TREAST":    {"name": "Fed Holdings: Treasuries",        "freq": "weekly", "divisor": 1e6,  "raw_unit": "M$"},
    "WSHOMCB":   {"name": "Fed Holdings: MBS",               "freq": "weekly", "divisor": 1e6,  "raw_unit": "M$"},
}

# All yfinance tickers used for the z-score "what changed" scanner
ALL_YF_TICKERS: Dict[str, Dict[str, str]] = {}
for _map, _cls in [
    (RATES_TICKERS, "Rates"),
    (FX_TICKERS, "FX"),
    (EQUITY_TICKERS, "Equities"),
    (COMMODITY_TICKERS, "Commodities"),
]:
    for ticker, meta in _map.items():
        ALL_YF_TICKERS[ticker] = {**meta, "asset_class": _cls}

# ---------------------------------------------------------------------------
# TTL cache
# ---------------------------------------------------------------------------

class _TTLCache:
    """Simple in-memory TTL cache."""

    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._store and time.time() < self._expiry.get(key, 0):
            return self._store[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: float):
        self._store[key] = value
        self._expiry[key] = time.time() + ttl_seconds

    def invalidate(self, key: str):
        self._store.pop(key, None)
        self._expiry.pop(key, None)


_cache = _TTLCache()

# Cache TTLs
REALTIME_TTL = 60       # 60 s for yfinance market data
FRED_TTL = 3600         # 1 h for FRED macro data
ZSCORE_TTL = 120        # 2 min for z-score scanner (heavier computation)
SPARKLINE_TTL = 300     # 5 min for batch sparkline data

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _yf_download(tickers: List[str], period: str = "5d", interval: str = "1d") -> pd.DataFrame:
    """Wrapper around yfinance download with error handling."""
    try:
        import yfinance as yf
        data = yf.download(
            tickers,
            period=period,
            interval=interval,
            progress=False,
            threads=True,
        )
        return data
    except Exception as e:
        logger.error(f"yfinance download failed for {tickers}: {e}")
        return pd.DataFrame()


def _get_fred():
    """Return a Fred client if an API key is configured, else None."""
    try:
        from backend.config import settings
        api_key = settings.market_data.fred_api_key
        if not api_key:
            return None
        from fredapi import Fred
        return Fred(api_key=api_key)
    except Exception as e:
        logger.warning(f"Could not initialize FRED client: {e}")
        return None


def _safe_float(val) -> Optional[float]:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _extract_snapshot(df: pd.DataFrame, tickers_meta: dict) -> List[dict]:
    """Extract latest price / change from a multi-ticker yfinance dataframe."""
    results = []
    if df.empty:
        return results

    is_multi = isinstance(df.columns, pd.MultiIndex)

    for ticker, meta in tickers_meta.items():
        try:
            if is_multi:
                close_col = df["Close"][ticker] if ticker in df["Close"].columns else None
            else:
                close_col = df["Close"] if "Close" in df.columns else None

            if close_col is None or close_col.dropna().empty:
                continue

            close_series = close_col.dropna()
            last_price = _safe_float(close_series.iloc[-1])
            prev_price = _safe_float(close_series.iloc[-2]) if len(close_series) >= 2 else None

            change = None
            change_pct = None
            if last_price is not None and prev_price is not None and prev_price != 0:
                change = last_price - prev_price
                change_pct = (change / prev_price) * 100

            last_date = ""
            try:
                last_date = str(close_series.index[-1].date()) if hasattr(close_series.index[-1], 'date') else ""
            except Exception:
                pass

            results.append({
                "ticker": ticker,
                **meta,
                "price": last_price,
                "change": _safe_float(change),
                "change_pct": _safe_float(change_pct),
                "date": last_date,
            })
        except Exception as e:
            logger.debug(f"Error extracting data for {ticker}: {e}")

    return results


# ---------------------------------------------------------------------------
# MarketDataService
# ---------------------------------------------------------------------------

class MarketDataService:
    """Aggregates cross-asset market data from yfinance and FRED."""

    # -- Rates ---------------------------------------------------------------

    def get_rates_snapshot(self) -> dict:
        cached = _cache.get("rates_snapshot")
        if cached is not None:
            return cached

        # yfinance yields (real-time-ish)
        tickers = list(RATES_TICKERS.keys())
        df = _yf_download(tickers, period="5d")
        yf_rates = _extract_snapshot(df, RATES_TICKERS)

        # FRED series (richer set of yields + spreads)
        fred_rates = self._fetch_fred_rates()

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "yields": yf_rates,
            "fred": fred_rates,
        }
        _cache.set("rates_snapshot", result, REALTIME_TTL)
        return result

    def _fetch_fred_rates(self) -> List[dict]:
        cached = _cache.get("fred_rates")
        if cached is not None:
            return cached

        fred = _get_fred()
        if fred is None:
            return []

        results = []
        values_by_series: Dict[str, float] = {}

        for series_id, meta in RATES_FRED_SERIES.items():
            try:
                data = fred.get_series(series_id, observation_start=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
                if data is not None and not data.empty:
                    data = data.dropna()
                    if data.empty:
                        continue
                    last_val = _safe_float(data.iloc[-1])
                    prev_val = _safe_float(data.iloc[-2]) if len(data) >= 2 else None
                    change = (last_val - prev_val) if (last_val is not None and prev_val is not None) else None
                    if last_val is not None:
                        values_by_series[series_id] = last_val

                    history = [
                        {"date": str(idx.date()), "value": _safe_float(v)}
                        for idx, v in data.items()
                    ]

                    results.append({
                        "series": series_id,
                        **meta,
                        "value": last_val,
                        "change": _safe_float(change),
                        "date": str(data.index[-1].date()),
                        "history": history,
                    })
            except Exception as e:
                logger.debug(f"FRED fetch error for {series_id}: {e}")

        for tenor_label, (tsy_id, swap_id) in SWAP_SPREAD_PAIRS.items():
            tsy_val = values_by_series.get(tsy_id)
            swap_val = values_by_series.get(swap_id)
            if tsy_val is not None and swap_val is not None:
                spread_bp = (swap_val - tsy_val) * 100
                results.append({
                    "series": f"SS_{tenor_label}",
                    "name": f"{tenor_label} Swap Spread",
                    "tenor": f"{tenor_label} SS",
                    "category": "swap_spread",
                    "value": _safe_float(spread_bp),
                    "change": None,
                    "date": "",
                    "unit": "bp",
                })
                results.append({
                    "series": f"ASW_{tenor_label}",
                    "name": f"{tenor_label} Asset Swap Spread",
                    "tenor": f"{tenor_label} ASW",
                    "category": "asset_swap",
                    "value": _safe_float(-spread_bp),
                    "change": None,
                    "date": "",
                    "unit": "bp",
                })

        _cache.set("fred_rates", results, FRED_TTL)
        return results

    # -- FX ------------------------------------------------------------------

    def get_fx_snapshot(self) -> dict:
        cached = _cache.get("fx_snapshot")
        if cached is not None:
            return cached

        tickers = list(FX_TICKERS.keys())
        df = _yf_download(tickers, period="5d")
        pairs = _extract_snapshot(df, FX_TICKERS)

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "pairs": pairs,
        }
        _cache.set("fx_snapshot", result, REALTIME_TTL)
        return result

    # -- Equities ------------------------------------------------------------

    def get_equities_snapshot(self) -> dict:
        cached = _cache.get("equities_snapshot")
        if cached is not None:
            return cached

        tickers = list(EQUITY_TICKERS.keys())
        df = _yf_download(tickers, period="5d")
        indices = _extract_snapshot(df, EQUITY_TICKERS)

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "indices": indices,
        }
        _cache.set("equities_snapshot", result, REALTIME_TTL)
        return result

    # -- Commodities ---------------------------------------------------------

    def get_commodities_snapshot(self) -> dict:
        cached = _cache.get("commodities_snapshot")
        if cached is not None:
            return cached

        tickers = list(COMMODITY_TICKERS.keys())
        df = _yf_download(tickers, period="5d")
        items = _extract_snapshot(df, COMMODITY_TICKERS)

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "commodities": items,
        }
        _cache.set("commodities_snapshot", result, REALTIME_TTL)
        return result

    # -- Macro pulse ---------------------------------------------------------

    def get_macro_pulse(self) -> dict:
        cached = _cache.get("macro_pulse")
        if cached is not None:
            return cached

        fred = _get_fred()
        indicators: List[dict] = []
        note = None

        if fred is not None:
            for series_id, meta in MACRO_FRED_SERIES.items():
                try:
                    data = fred.get_series(
                        series_id,
                        observation_start=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                    )
                    if data is not None and not data.empty:
                        data = data.dropna()
                        if data.empty:
                            continue
                        last_val = _safe_float(data.iloc[-1])
                        prev_val = _safe_float(data.iloc[-2]) if len(data) >= 2 else None
                        change = (last_val - prev_val) if (last_val is not None and prev_val is not None) else None
                        indicators.append({
                            "series": series_id,
                            **meta,
                            "value": last_val,
                            "previous": prev_val,
                            "change": _safe_float(change),
                            "date": str(data.index[-1].date()),
                        })
                except Exception as e:
                    logger.debug(f"FRED macro fetch error for {series_id}: {e}")

        if not indicators:
            indicators = self._fetch_macro_yf_fallback()
            if fred is None:
                note = "Showing market-based macro proxies — set FRED_API_KEY in .env for economic indicators (free at fred.stlouisfed.org/docs/api/api_key.html)"

        ttl = FRED_TTL if fred else REALTIME_TTL
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "indicators": indicators,
            "note": note,
        }
        _cache.set("macro_pulse", result, ttl)
        return result

    def _fetch_macro_yf_fallback(self) -> List[dict]:
        """Market-based macro proxies from yfinance when FRED is unavailable."""
        tickers = list(MACRO_YF_FALLBACK.keys())
        df = _yf_download(tickers, period="5d")
        snapshots = _extract_snapshot(df, MACRO_YF_FALLBACK)
        indicators = []
        for item in snapshots:
            ticker = item.get("ticker", "")
            meta = MACRO_YF_FALLBACK.get(ticker, {})
            indicators.append({
                "series": ticker,
                "name": meta.get("name", ticker),
                "value": item.get("price"),
                "change": item.get("change"),
                "unit": meta.get("unit", ""),
                "freq": meta.get("freq", ""),
                "date": item.get("date", ""),
            })
        return indicators

    # -- What Changed (z-score scanner) --------------------------------------

    def get_what_changed(self, sigma_threshold: float = 1.5) -> dict:
        cached = _cache.get("what_changed")
        if cached is not None:
            return cached

        tickers = list(ALL_YF_TICKERS.keys())
        df = _yf_download(tickers, period="1mo", interval="1d")

        movers: List[dict] = []
        if df.empty:
            return {"timestamp": datetime.utcnow().isoformat(), "movers": [], "threshold": sigma_threshold}

        is_multi = isinstance(df.columns, pd.MultiIndex)

        for ticker, meta in ALL_YF_TICKERS.items():
            try:
                if is_multi:
                    if ticker not in df["Close"].columns:
                        continue
                    close = df["Close"][ticker].dropna()
                else:
                    close = df["Close"].dropna()

                if len(close) < 5:
                    continue

                returns = close.pct_change().dropna()
                if len(returns) < 5:
                    continue

                vol_20d = returns.iloc[-21:].std() if len(returns) >= 21 else returns.std()
                if vol_20d == 0 or np.isnan(vol_20d):
                    continue

                today_return = returns.iloc[-1]
                z_score = today_return / vol_20d

                if abs(z_score) >= sigma_threshold:
                    movers.append({
                        "ticker": ticker,
                        **meta,
                        "price": _safe_float(close.iloc[-1]),
                        "return_pct": _safe_float(today_return * 100),
                        "vol_20d": _safe_float(vol_20d * 100),
                        "z_score": _safe_float(z_score),
                        "direction": "up" if z_score > 0 else "down",
                    })
            except Exception as e:
                logger.debug(f"z-score calc error for {ticker}: {e}")

        movers.sort(key=lambda x: abs(x.get("z_score", 0)), reverse=True)

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "movers": movers,
            "threshold": sigma_threshold,
        }
        _cache.set("what_changed", result, ZSCORE_TTL)
        return result

    # -- Curves data for charting --------------------------------------------

    def get_curves_data(self) -> dict:
        """Yield curve, swap curve, swap spread curve, and forward rates for plotting."""
        cached = _cache.get("curves_data")
        if cached is not None:
            return cached

        fred_rates = self._fetch_fred_rates()
        if not fred_rates:
            return {}

        vals: Dict[str, dict] = {}
        for r in fred_rates:
            vals[r["series"]] = r

        tsy_curve_series = [
            ("DGS1MO", "1M", 1 / 12), ("DGS3MO", "3M", 0.25), ("DGS6MO", "6M", 0.5),
            ("DGS1", "1Y", 1), ("DGS2", "2Y", 2), ("DGS3", "3Y", 3),
            ("DGS5", "5Y", 5), ("DGS7", "7Y", 7), ("DGS10", "10Y", 10),
            ("DGS20", "20Y", 20), ("DGS30", "30Y", 30),
        ]
        swap_curve_series = [
            ("DSWP2", "2Y", 2), ("DSWP5", "5Y", 5),
            ("DSWP10", "10Y", 10), ("DSWP30", "30Y", 30),
        ]

        yc_tenors, yc_years, yc_yields = [], [], []
        for sid, tenor, years in tsy_curve_series:
            v = vals.get(sid, {}).get("value")
            if v is not None:
                yc_tenors.append(tenor)
                yc_years.append(years)
                yc_yields.append(v)

        sc_tenors, sc_years, sc_rates = [], [], []
        for sid, tenor, years in swap_curve_series:
            v = vals.get(sid, {}).get("value")
            if v is not None:
                sc_tenors.append(tenor)
                sc_years.append(years)
                sc_rates.append(v)

        ss_tenors, ss_years, ss_bp = [], [], []
        for tenor_label in ["2Y", "5Y", "10Y", "30Y"]:
            key = f"SS_{tenor_label}"
            v = vals.get(key, {}).get("value")
            if v is not None:
                ss_tenors.append(tenor_label)
                ss_years.append({"2Y": 2, "5Y": 5, "10Y": 10, "30Y": 30}[tenor_label])
                ss_bp.append(v)

        fwd_labels, fwd_rates = [], []
        if len(yc_years) >= 2:
            for i in range(len(yc_years) - 1):
                t1, y1 = yc_years[i], yc_yields[i]
                t2, y2 = yc_years[i + 1], yc_yields[i + 1]
                if t2 > t1 and y1 is not None and y2 is not None:
                    fwd = (y2 * t2 - y1 * t1) / (t2 - t1)
                    fwd_labels.append(f"{yc_tenors[i]}-{yc_tenors[i+1]}")
                    fwd_rates.append(round(fwd, 4))

        latest_date = ""
        for r in fred_rates:
            d = r.get("date", "")
            if d and d > latest_date:
                latest_date = d

        result = {
            "yield_curve": {"tenors": yc_tenors, "tenor_years": yc_years, "yields": yc_yields, "date": latest_date},
            "swap_curve": {"tenors": sc_tenors, "tenor_years": sc_years, "rates": sc_rates, "date": latest_date},
            "swap_spreads": {"tenors": ss_tenors, "tenor_years": ss_years, "spreads_bp": ss_bp, "date": latest_date},
            "forward_rates": {"labels": fwd_labels, "rates": fwd_rates, "date": latest_date},
        }
        _cache.set("curves_data", result, FRED_TTL)
        return result

    # -- Fed Balance Sheet / Liquidity (QE / QT monitor) --------------------

    def get_fed_liquidity_data(self) -> dict:
        """Historical Fed balance sheet components for QE/QT monitoring.

        Returns latest snapshot values (in T$) and 2-year historical time
        series for charting, including a computed Net Liquidity line.
        """
        cached = _cache.get("fed_liquidity")
        if cached is not None:
            return cached

        fred = _get_fred()
        if fred is None:
            return {}

        start = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")

        raw_series: Dict[str, pd.Series] = {}
        snapshot: List[dict] = []

        for series_id, meta in FED_LIQUIDITY_SERIES.items():
            try:
                data = fred.get_series(series_id, observation_start=start)
                if data is not None and not data.empty:
                    data = data.dropna()
                    if data.empty:
                        continue
                    raw_series[series_id] = data
                    last_raw = _safe_float(data.iloc[-1])
                    prev_raw = _safe_float(data.iloc[-2]) if len(data) >= 2 else None
                    divisor = meta["divisor"]
                    last_t = last_raw / divisor if last_raw is not None else None
                    prev_t = prev_raw / divisor if prev_raw is not None else None
                    chg = (last_t - prev_t) if (last_t is not None and prev_t is not None) else None
                    snapshot.append({
                        "series": series_id,
                        "name": meta["name"],
                        "value": _safe_float(last_t),
                        "change": _safe_float(chg),
                        "unit": "T$",
                        "freq": meta["freq"],
                        "date": str(data.index[-1].date()),
                    })
            except Exception as e:
                logger.debug(f"Fed liquidity fetch error for {series_id}: {e}")

        # Build aligned historical dataframe in trillions
        hist: Dict[str, List[dict]] = {}
        for sid, series in raw_series.items():
            divisor = FED_LIQUIDITY_SERIES[sid]["divisor"]
            converted = series / divisor
            hist[sid] = [{"date": str(idx.date()), "value": _safe_float(v)} for idx, v in converted.items()]

        # Compute Net Liquidity = Fed Assets − TGA − RRP
        net_liq_series: List[dict] = []
        if "WALCL" in raw_series and "WTREGEN" in raw_series and "RRPONTSYD" in raw_series:
            walcl = (raw_series["WALCL"] / FED_LIQUIDITY_SERIES["WALCL"]["divisor"]).resample("B").ffill()
            tga = (raw_series["WTREGEN"] / FED_LIQUIDITY_SERIES["WTREGEN"]["divisor"]).resample("B").ffill()
            rrp = (raw_series["RRPONTSYD"] / FED_LIQUIDITY_SERIES["RRPONTSYD"]["divisor"]).resample("B").ffill()
            combined = pd.DataFrame({"walcl": walcl, "tga": tga, "rrp": rrp}).dropna()
            if not combined.empty:
                combined["net_liq"] = combined["walcl"] - combined["tga"] - combined["rrp"]
                net_liq_series = [{"date": str(idx.date()), "value": _safe_float(v)} for idx, v in combined["net_liq"].items()]

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "snapshot": snapshot,
            "history": hist,
            "net_liquidity": net_liq_series,
        }
        _cache.set("fed_liquidity", result, FRED_TTL)
        return result

    # -- Central Bank Meeting Tracker ----------------------------------------

    def get_cb_meeting_tracker(self) -> dict:
        """Central bank meeting countdown with OIS-implied rate context.

        Returns FOMC meeting schedule, countdown, current Fed Funds target,
        SOFR, and 2Y Treasury as proxy for market-implied rate path.
        Meeting-specific probabilities (e.g. CME FedWatch) require CME data.
        """
        cached = _cache.get("cb_meeting_tracker")
        if cached is not None:
            return cached

        from backend.cb_meeting_schedule import get_next_fomc_meeting, get_upcoming_fomc_meetings

        result: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "fed": {},
            "upcoming": [],
        }

        # FOMC schedule
        next_meeting = get_next_fomc_meeting()
        if next_meeting:
            meeting_date, has_sep = next_meeting
            from datetime import date
            days = (meeting_date - date.today()).days
            result["fed"]["next_meeting_date"] = meeting_date.isoformat()
            result["fed"]["days_until"] = days
            result["fed"]["has_sep"] = has_sep
            result["fed"]["label"] = f"{meeting_date.strftime('%b %d')}{' (SEP)' if has_sep else ''}"

        result["upcoming"] = get_upcoming_fomc_meetings(limit=6)

        # Policy rates and implied path proxy from FRED
        fred = _get_fred()
        if fred:
            start = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            series_ids = ["DFEDTARU", "SOFR", "EFFR", "DGS2"]
            for sid in series_ids:
                try:
                    data = fred.get_series(sid, observation_start=start)
                    if data is not None and not data.empty:
                        data = data.dropna()
                        if not data.empty:
                            last_val = _safe_float(data.iloc[-1])
                            if sid == "DFEDTARU":
                                result["fed"]["target_upper"] = last_val
                            elif sid == "SOFR":
                                result["fed"]["sofr"] = last_val
                            elif sid == "EFFR":
                                result["fed"]["effr"] = last_val
                            elif sid == "DGS2":
                                result["fed"]["two_year_yield"] = last_val
                except Exception as e:
                    logger.debug(f"CB tracker FRED fetch error for {sid}: {e}")

        # Compute implied path proxy: 2Y yield vs target (spread = market pricing in cuts/hikes)
        target = result["fed"].get("target_upper")
        two_y = result["fed"].get("two_year_yield")
        if target is not None and two_y is not None:
            result["fed"]["two_y_minus_target"] = round(two_y - target, 2)

        _cache.set("cb_meeting_tracker", result, FRED_TTL)
        return result

    # -- Batch sparklines ----------------------------------------------------

    def get_batch_sparklines(self, days: int = 30) -> Dict[str, List[dict]]:
        """Batch-fetch sparkline data for all yfinance-tracked instruments.

        Returns {ticker: [{date, close}, ...]} for every ticker in
        RATES_TICKERS, FX_TICKERS, EQUITY_TICKERS, and COMMODITY_TICKERS.
        """
        cache_key = f"batch_sparklines_{days}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        tickers = list(ALL_YF_TICKERS.keys())
        df = _yf_download(tickers, period=f"{days}d", interval="1d")

        result: Dict[str, List[dict]] = {}
        if df.empty:
            return result

        is_multi = isinstance(df.columns, pd.MultiIndex)
        for ticker in tickers:
            try:
                if is_multi:
                    if ticker not in df["Close"].columns:
                        continue
                    close = df["Close"][ticker].dropna()
                else:
                    close = df["Close"].dropna()

                if close.empty:
                    continue

                points = [
                    {"date": str(idx.date()), "close": _safe_float(val)}
                    for idx, val in close.items()
                ]
                result[ticker] = points
            except Exception as e:
                logger.debug(f"Sparkline extraction error for {ticker}: {e}")

        _cache.set(cache_key, result, SPARKLINE_TTL)
        return result

    # -- Combined overview ---------------------------------------------------

    def get_overview(self) -> dict:
        """Single call that returns all panels for the dashboard."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "rates": self.get_rates_snapshot(),
            "fx": self.get_fx_snapshot(),
            "equities": self.get_equities_snapshot(),
            "commodities": self.get_commodities_snapshot(),
            "macro": self.get_macro_pulse(),
            "what_changed": self.get_what_changed(),
            "curves": self.get_curves_data(),
            "fed_liquidity": self.get_fed_liquidity_data(),
            "cb_meetings": self.get_cb_meeting_tracker(),
            "sparklines": self.get_batch_sparklines(),
        }

    # -- Historical data for sparklines --------------------------------------

    def get_historical(self, symbol: str, days: int = 30) -> List[dict]:
        cache_key = f"hist_{symbol}_{days}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        df = _yf_download([symbol], period=f"{days}d", interval="1d")
        if df.empty:
            return []

        is_multi = isinstance(df.columns, pd.MultiIndex)
        close = df["Close"][symbol].dropna() if is_multi else df["Close"].dropna()

        points = [
            {"date": str(idx.date()), "close": _safe_float(val)}
            for idx, val in close.items()
        ]
        _cache.set(cache_key, points, REALTIME_TTL)
        return points


# Singleton
market_data_service = MarketDataService()
