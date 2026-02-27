"""Parquet-based market data lake for persistent historical storage.

Stores daily OHLCV (yfinance) and FRED time-series as Parquet files
organised by asset class.  Supports incremental updates, catalog
queries, and date-range reads.

Directory layout
----------------
data/market_data/
├── prices/
│   ├── equities.parquet
│   ├── fx.parquet
│   ├── commodities.parquet
│   └── rates_yf.parquet
├── fred/
│   ├── treasury_yields.parquet
│   ├── macro_indicators.parquet
│   └── fed_liquidity.parquet
└── catalog.json
"""

import json
import logging
import os
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

_BASE_DIR = Path(__file__).resolve().parent.parent / "data" / "market_data"
_PRICES_DIR = _BASE_DIR / "prices"
_FRED_DIR = _BASE_DIR / "fred"
_CATALOG_PATH = _BASE_DIR / "catalog.json"

_YF_ASSET_FILES = {
    "equities": _PRICES_DIR / "equities.parquet",
    "fx": _PRICES_DIR / "fx.parquet",
    "commodities": _PRICES_DIR / "commodities.parquet",
    "rates_yf": _PRICES_DIR / "rates_yf.parquet",
}

# IBKR-specific parquet files (for higher quality/intraday data from IBKR)
_IBKR_ASSET_FILES = {
    "ibkr_equities": _PRICES_DIR / "ibkr_equities.parquet",
    "ibkr_fx": _PRICES_DIR / "ibkr_fx.parquet",
    "ibkr_futures": _PRICES_DIR / "ibkr_futures.parquet",
    "ibkr_options": _PRICES_DIR / "ibkr_options.parquet",
}

_FRED_CATEGORY_FILES = {
    "treasury_yields": _FRED_DIR / "treasury_yields.parquet",
    "macro_indicators": _FRED_DIR / "macro_indicators.parquet",
    "fed_liquidity": _FRED_DIR / "fed_liquidity.parquet",
}

from backend.market_data_service import (
    COMMODITY_TICKERS,
    EQUITY_TICKERS,
    FED_LIQUIDITY_SERIES,
    FX_TICKERS,
    MACRO_FRED_SERIES,
    RATES_FRED_SERIES,
    RATES_TICKERS,
)

_ASSET_CLASS_TICKERS = {
    "equities": list(EQUITY_TICKERS.keys()),
    "fx": list(FX_TICKERS.keys()),
    "commodities": list(COMMODITY_TICKERS.keys()),
    "rates_yf": list(RATES_TICKERS.keys()),
}

# IBKR ticker lists - commonly traded securities
# These can be extended or loaded from config
_IBKR_ASSET_TICKERS = {
    "ibkr_equities": [
        # US Large Cap
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "JPM", "JNJ",
        "V", "PG", "UNH", "HD", "MA", "DIS", "PYPL", "BAC", "ADBE", "NFLX",
        "CRM", "INTC", "VZ", "T", "PFE", "MRK", "KO", "PEP", "ABT", "TMO",
        # More tickers can be added or loaded from config
    ],
    "ibkr_fx": [
        # Major pairs
        "EURUSD", "GBPUSD", "USDJPY", "USDCAD", "USDCHF", "AUDUSD", "NZDUSD",
        # Minor pairs
        "EURGBP", "EURJPY", "GBPJPY", "EURCHF", "AUDJPY", "CADJPY",
    ],
    "ibkr_futures": [
        # Equity Index Futures
        "ES", "NQ", "YM", "RTY",  # S&P 500, Nasdaq, Dow, Russell
        # Energy
        "CL", "BZ", "NG",  # Crude, Brent, Natural Gas
        # Metals
        "GC", "SI", "HG",  # Gold, Silver, Copper
        # Bonds
        "ZB", "ZN", "ZF", "ZT",  # 30Y, 10Y, 5Y, 2Y Treasury
        # Agriculture
        "ZC", "ZS", "ZL", "ZM", "HE", "LE",  # Corn, Soybeans, Oil, Meal, Hogs, Cattle
    ],
    "ibkr_options": [
        # Options underlyings - same as ibkr_equities
    ],
}

_FRED_CATEGORY_SERIES = {
    "treasury_yields": list(RATES_FRED_SERIES.keys()),
    "macro_indicators": list(MACRO_FRED_SERIES.keys()),
    "fed_liquidity": list(FED_LIQUIDITY_SERIES.keys()),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_dirs():
    _PRICES_DIR.mkdir(parents=True, exist_ok=True)
    _FRED_DIR.mkdir(parents=True, exist_ok=True)


def _read_catalog() -> dict:
    if _CATALOG_PATH.exists():
        try:
            return json.loads(_CATALOG_PATH.read_text())
        except Exception:
            pass
    return {}


def _write_catalog(catalog: dict):
    _CATALOG_PATH.write_text(json.dumps(catalog, indent=2, default=str))


def _append_parquet(filepath: Path, new_df: pd.DataFrame):
    """Merge *new_df* into an existing Parquet file, deduplicating."""
    if new_df.empty:
        return

    if filepath.exists():
        try:
            existing = pd.read_parquet(filepath)
            combined = pd.concat([existing, new_df], ignore_index=True)
        except Exception:
            combined = new_df
    else:
        combined = new_df

    dedup_cols = ["date", "ticker"] if "ticker" in combined.columns else ["date", "series_id"]
    combined = combined.drop_duplicates(subset=dedup_cols, keep="last")
    combined = combined.sort_values("date").reset_index(drop=True)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(filepath, index=False)


# ---------------------------------------------------------------------------
# Pull jobs — lightweight background task tracking
# ---------------------------------------------------------------------------

_jobs: Dict[str, Dict[str, Any]] = {}
_jobs_lock = threading.Lock()


def _create_job(description: str) -> str:
    job_id = str(uuid.uuid4())[:8]
    with _jobs_lock:
        _jobs[job_id] = {
            "id": job_id,
            "description": description,
            "status": "running",
            "started": datetime.utcnow().isoformat(),
            "finished": None,
            "rows_written": 0,
            "error": None,
        }
    return job_id


def _finish_job(job_id: str, rows: int = 0, error: Optional[str] = None):
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id]["status"] = "error" if error else "completed"
            _jobs[job_id]["finished"] = datetime.utcnow().isoformat()
            _jobs[job_id]["rows_written"] = rows
            _jobs[job_id]["error"] = error


def get_job_status(job_id: str) -> Optional[dict]:
    with _jobs_lock:
        return _jobs.get(job_id)


# ---------------------------------------------------------------------------
# MarketDataStore
# ---------------------------------------------------------------------------

class MarketDataStore:
    """Parquet-backed market data lake."""

    def __init__(self):
        _ensure_dirs()

    # -- yfinance pulls -----------------------------------------------------

    def pull_yf_data(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        asset_class: str,
    ) -> int:
        """Bulk-download OHLCV from yfinance and append to Parquet.

        Returns the number of rows written.
        """
        try:
            import yfinance as yf
        except ImportError:
            logger.error("yfinance not installed")
            return 0

        filepath = _YF_ASSET_FILES.get(asset_class)
        if filepath is None:
            logger.error(f"Unknown asset class: {asset_class}")
            return 0

        try:
            df = yf.download(
                tickers,
                start=start_date,
                end=end_date,
                interval="1d",
                progress=False,
                threads=True,
            )
        except Exception as e:
            logger.error(f"yfinance download error: {e}")
            return 0

        if df.empty:
            return 0

        is_multi = isinstance(df.columns, pd.MultiIndex)
        records = []

        for ticker in tickers:
            try:
                if is_multi:
                    if ticker not in df["Close"].columns:
                        continue
                    sub = df.xs(ticker, level=1, axis=1)
                else:
                    sub = df

                for idx, row in sub.iterrows():
                    close_val = row.get("Close")
                    if pd.isna(close_val):
                        continue
                    records.append({
                        "date": idx.date().isoformat(),
                        "ticker": ticker,
                        "open": float(row["Open"]) if pd.notna(row.get("Open")) else None,
                        "high": float(row["High"]) if pd.notna(row.get("High")) else None,
                        "low": float(row["Low"]) if pd.notna(row.get("Low")) else None,
                        "close": float(close_val),
                        "volume": float(row["Volume"]) if pd.notna(row.get("Volume")) else None,
                    })
            except Exception as e:
                logger.debug(f"Error processing {ticker}: {e}")

        if not records:
            return 0

        new_df = pd.DataFrame(records)
        _append_parquet(filepath, new_df)
        self._update_catalog_entry(asset_class, "yfinance", filepath, new_df)
        return len(records)

    # -- FRED pulls ---------------------------------------------------------

    def pull_fred_data(
        self,
        series_ids: List[str],
        start_date: str,
        end_date: str,
        category: str,
    ) -> int:
        """Bulk-download from FRED and append to Parquet."""
        from backend.market_data_service import _get_fred

        fred = _get_fred()
        if fred is None:
            logger.warning("FRED client not available")
            return 0

        filepath = _FRED_CATEGORY_FILES.get(category)
        if filepath is None:
            logger.error(f"Unknown FRED category: {category}")
            return 0

        records = []
        for sid in series_ids:
            try:
                data = fred.get_series(sid, observation_start=start_date, observation_end=end_date)
                if data is None or data.empty:
                    continue
                data = data.dropna()
                for idx, val in data.items():
                    records.append({
                        "date": idx.date().isoformat(),
                        "series_id": sid,
                        "value": float(val),
                    })
            except Exception as e:
                logger.debug(f"FRED fetch error for {sid}: {e}")

        if not records:
            return 0

        new_df = pd.DataFrame(records)
        _append_parquet(filepath, new_df)
        self._update_catalog_entry(category, "fred", filepath, new_df)
        return len(records)

    # -- IBKR pulls ---------------------------------------------------------

    def pull_ibkr_data(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        asset_class: str,
        interval: str = "1 day",
        sec_type: str = "STK",
        exchange: str = "SMART"
    ) -> int:
        """Download OHLCV from IBKR and append to Parquet.
        
        This method connects to IB Gateway/TWS to fetch historical data.
        Requires IB Gateway to be running with API access enabled.
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            asset_class: Asset class key (ibkr_equities, ibkr_fx, ibkr_futures)
            interval: Bar interval (e.g., "1 day", "1 min", "5 mins")
            sec_type: Security type ("STK", "CASH", "FUT")
            exchange: Exchange (e.g., "SMART", "IDEALPRO", "CME")
            
        Returns:
            Number of rows written
        """
        import asyncio
        from datetime import datetime as dt
        
        filepath = _IBKR_ASSET_FILES.get(asset_class)
        if filepath is None:
            logger.error(f"Unknown IBKR asset class: {asset_class}")
            return 0
        
        # Parse dates
        start = dt.strptime(start_date, "%Y-%m-%d")
        end = dt.strptime(end_date, "%Y-%m-%d")
        
        # Calculate duration for IBKR request
        days_diff = (end - start).days
        if days_diff <= 7:
            duration = f"{days_diff + 1} D"
        elif days_diff <= 30:
            duration = "1 M"
        elif days_diff <= 90:
            duration = "3 M"
        elif days_diff <= 365:
            duration = "1 Y"
        else:
            duration = "2 Y"
        
        # Get IBKR client
        try:
            from backend.ibkr_client import IBKRClient
        except ImportError:
            logger.error("IBKR client not available")
            return 0
        
        async def fetch_all():
            client = IBKRClient()
            if not await client.connect():
                logger.error("Could not connect to IBKR")
                return []
            
            records = []
            for ticker in tickers:
                try:
                    # Determine security type and exchange for this ticker
                    ticker_sec_type = sec_type
                    ticker_exchange = exchange
                    
                    # Auto-detect forex
                    if asset_class == "ibkr_fx" or "/" in ticker or ticker in ["EURUSD", "GBPUSD", "USDJPY", "USDCAD", "USDCHF", "AUDUSD", "NZDUSD"]:
                        ticker_sec_type = "CASH"
                        ticker_exchange = "IDEALPRO"
                    # Auto-detect futures
                    elif asset_class == "ibkr_futures":
                        ticker_sec_type = "FUT"
                        ticker_exchange = "CME"
                    
                    df = await client.get_historical_data(
                        symbol=ticker,
                        sec_type=ticker_sec_type,
                        exchange=ticker_exchange,
                        duration=duration,
                        interval=interval,
                        start_date=start,
                        end_date=end
                    )
                    
                    if df.empty:
                        logger.debug(f"No data returned for {ticker}")
                        continue
                    
                    for _, row in df.iterrows():
                        date_val = row['date']
                        if hasattr(date_val, 'date'):
                            date_str = date_val.date().isoformat()
                        else:
                            date_str = str(date_val)[:10]
                        
                        records.append({
                            "date": date_str,
                            "ticker": ticker,
                            "open": float(row['open']) if pd.notna(row.get('open')) else None,
                            "high": float(row['high']) if pd.notna(row.get('high')) else None,
                            "low": float(row['low']) if pd.notna(row.get('low')) else None,
                            "close": float(row['close']) if pd.notna(row.get('close')) else None,
                            "volume": int(row['volume']) if pd.notna(row.get('volume')) else None,
                        })
                    
                    logger.info(f"Fetched {len(df)} bars for {ticker}")
                    
                    # Rate limiting - be nice to IBKR API
                    await asyncio.sleep(0.2)
                    
                except Exception as e:
                    logger.error(f"Error fetching {ticker}: {e}")
            
            await client.disconnect()
            return records
        
        # Run async fetch
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                logger.error("Cannot run IBKR fetch in async context - use separate thread")
                return 0
            records = loop.run_until_complete(fetch_all())
        except Exception as e:
            logger.error(f"IBKR fetch error: {e}")
            return 0
        
        if not records:
            return 0
        
        new_df = pd.DataFrame(records)
        _append_parquet(filepath, new_df)
        self._update_catalog_entry(asset_class, "ibkr", filepath, new_df)
        return len(records)

    # -- Query stored data --------------------------------------------------

    def query(
        self,
        asset_class: str,
        tickers: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """Read stored Parquet data, optionally filtered."""
        filepath = _YF_ASSET_FILES.get(asset_class) or _FRED_CATEGORY_FILES.get(asset_class) or _IBKR_ASSET_FILES.get(asset_class)
        if filepath is None or not filepath.exists():
            return pd.DataFrame()

        df = pd.read_parquet(filepath)

        id_col = "ticker" if "ticker" in df.columns else "series_id"
        if tickers:
            df = df[df[id_col].isin(tickers)]
        if start_date:
            df = df[df["date"] >= start_date]
        if end_date:
            df = df[df["date"] <= end_date]

        return df.sort_values("date").reset_index(drop=True)

    # -- Catalog ------------------------------------------------------------

    def get_catalog(self) -> dict:
        """Return metadata about all stored datasets."""
        catalog = _read_catalog()
        enriched: dict = {}
        for key, entry in catalog.items():
            filepath = Path(entry.get("filepath", ""))
            exists = filepath.exists()
            enriched[key] = {
                **entry,
                "exists": exists,
                "file_size_mb": round(filepath.stat().st_size / 1e6, 2) if exists else 0,
            }
        return enriched

    # -- Incremental update -------------------------------------------------

    def update_all(self) -> str:
        """Incremental update: fetch only data newer than last stored date.

        Returns a job_id that can be polled for status.
        """
        job_id = _create_job("update_all")
        thread = threading.Thread(target=self._run_update_all, args=(job_id,), daemon=True)
        thread.start()
        return job_id

    def _run_update_all(self, job_id: str):
        total_rows = 0
        catalog = _read_catalog()
        today = datetime.utcnow().strftime("%Y-%m-%d")
        default_start = (datetime.utcnow() - timedelta(days=730)).strftime("%Y-%m-%d")

        try:
            for asset_class, tickers in _ASSET_CLASS_TICKERS.items():
                entry = catalog.get(asset_class, {})
                start = entry.get("end_date", default_start)
                rows = self.pull_yf_data(tickers, start, today, asset_class)
                total_rows += rows
                logger.info(f"update_all: {asset_class} +{rows} rows")

            for category, series_ids in _FRED_CATEGORY_SERIES.items():
                entry = catalog.get(category, {})
                start = entry.get("end_date", default_start)
                rows = self.pull_fred_data(series_ids, start, today, category)
                total_rows += rows
                logger.info(f"update_all: {category} +{rows} rows")

            _finish_job(job_id, total_rows)
        except Exception as e:
            logger.error(f"update_all failed: {e}")
            _finish_job(job_id, total_rows, str(e))

    # -- Internal helpers ---------------------------------------------------

    def _update_catalog_entry(
        self,
        key: str,
        source: str,
        filepath: Path,
        new_df: pd.DataFrame,
    ):
        catalog = _read_catalog()
        dates = new_df["date"].tolist()
        existing = catalog.get(key, {})

        start_date = min(dates) if dates else existing.get("start_date", "")
        end_date = max(dates) if dates else existing.get("end_date", "")
        if existing.get("start_date") and existing["start_date"] < start_date:
            start_date = existing["start_date"]
        if existing.get("end_date") and existing["end_date"] > end_date:
            end_date = existing["end_date"]

        id_col = "ticker" if "ticker" in new_df.columns else "series_id"
        new_tickers = set(new_df[id_col].unique())
        old_tickers = set(existing.get("tickers", []))
        all_tickers = sorted(old_tickers | new_tickers)

        row_count = 0
        if filepath.exists():
            try:
                row_count = len(pd.read_parquet(filepath))
            except Exception:
                pass

        catalog[key] = {
            "source": source,
            "filepath": str(filepath),
            "start_date": start_date,
            "end_date": end_date,
            "tickers": all_tickers,
            "row_count": row_count,
            "last_updated": datetime.utcnow().isoformat(),
        }
        _write_catalog(catalog)


# Singleton
market_data_store = MarketDataStore()
