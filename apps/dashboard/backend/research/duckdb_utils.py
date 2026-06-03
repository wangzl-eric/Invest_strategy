"""DuckDB wrapper for fast SQL queries over Parquet market data.

This module provides a unified interface for querying all market data
using DuckDB's ability to read Parquet files directly with SQL.
"""

import logging
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import duckdb
import pandas as pd

from backend.config import settings

logger = logging.getLogger(__name__)

# Default data directory shared across dashboard and workstation flows.
DATA_DIR = Path(__file__).resolve().parents[4] / "data" / "market_data"
PRICES_DIR = DATA_DIR / "prices"
FRED_DIR = DATA_DIR / "fred"


class ResearchDB:
    """DuckDB wrapper for market data research."""

    def __init__(self, memory_limit_mb: int = 4096):
        """Initialize DuckDB connection.

        Args:
            memory_limit_mb: Maximum memory for DuckDB operations
        """
        self.memory_limit_mb = memory_limit_mb
        self._conn: Optional[duckdb.DuckDBPyConnection] = None
        self._setup_database()

    def _setup_database(self):
        """Configure DuckDB with settings and register Parquet files."""
        try:
            # Create connection with memory limit
            self._conn = duckdb.connect(
                config={"memory_limit": f"{self.memory_limit_mb}MB"}
            )

            # Register views for each Parquet file
            self._register_parquet_views()

            logger.info("DuckDB research database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize DuckDB: {e}")
            raise

    def _register_parquet_views(self):
        """Register Parquet files as DuckDB views."""
        if self._conn is None:
            return

        # Register IBKR data views (primary source)
        ibkr_files = {
            "ibkr_equities": PRICES_DIR / "ibkr_equities.parquet",
            "ibkr_fx": PRICES_DIR / "ibkr_fx.parquet",
            "ibkr_futures": PRICES_DIR / "ibkr_futures.parquet",
            "ibkr_options": PRICES_DIR / "ibkr_options.parquet",
        }

        # Register yfinance data views (fallback)
        yf_files = {
            "yf_equities": PRICES_DIR / "equities.parquet",
            "yf_fx": PRICES_DIR / "fx.parquet",
            "yf_commodities": PRICES_DIR / "commodities.parquet",
            "yf_rates": PRICES_DIR / "rates_yf.parquet",
        }

        # Register FRED data views
        fred_files = {
            "fred_treasury": FRED_DIR / "treasury_yields.parquet",
            "fred_macro": FRED_DIR / "macro_indicators.parquet",
            "fred_liquidity": FRED_DIR / "fed_liquidity.parquet",
        }

        all_files = {**ibkr_files, **yf_files, **fred_files}

        for name, filepath in all_files.items():
            if filepath.exists():
                try:
                    # Create view that reads directly from Parquet
                    self._conn.execute(
                        f"""
                        CREATE OR REPLACE VIEW {name} AS
                        SELECT * FROM read_parquet('{filepath}')
                    """
                    )
                    logger.debug(f"Registered view: {name} -> {filepath}")
                except Exception as e:
                    logger.warning(f"Failed to register {name}: {e}")

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        """Get DuckDB connection."""
        if self._conn is None:
            self._setup_database()
        return self._conn

    def execute(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """Execute a SQL query and return results as DataFrame.

        Args:
            query: SQL query string
            params: Optional query parameters

        Returns:
            DataFrame with query results
        """
        try:
            if params:
                # DuckDB uses $1, $2 for positional params or :name for named params
                result = self._conn.execute(query, params).df()
            else:
                result = self._conn.execute(query).df()
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query[:500]}")
            raise

    def query_prices(
        self,
        tickers: Optional[List[str]] = None,
        asset_class: Optional[str] = None,
        start_date: Optional[Union[str, date]] = None,
        end_date: Optional[Union[str, date]] = None,
        source: str = "ibkr",
    ) -> pd.DataFrame:
        """Query price data with filters.

        Args:
            tickers: List of ticker symbols to filter
            asset_class: Asset class to filter (equity, fx, futures, commodity)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            source: Data source (ibkr, yf, fred)

        Returns:
            DataFrame with price data
        """
        # Map source to view name
        source_map = {
            "ibkr": "ibkr_equities",
            "yf": "yf_equities",
            "yfinance": "yf_equities",
            "fred": "fred_treasury",
        }

        # Determine which view to use based on asset class and source
        if asset_class == "fx":
            view = "ibkr_fx" if source == "ibkr" else "yf_fx"
        elif asset_class == "futures":
            view = "ibkr_futures"
        elif asset_class == "commodity":
            view = "yf_commodities"
        elif asset_class == "rate":
            view = "fred_treasury"
        else:
            view = source_map.get(source, "ibkr_equities")

        # Build query
        query = f"SELECT * FROM {view} WHERE 1=1"
        params = {}

        if tickers:
            placeholders = ", ".join([f"'{t}'" for t in tickers])
            query += f" AND ticker IN ({placeholders})"

        if start_date:
            query += " AND date >= $start_date"
            params["start_date"] = str(start_date)

        if end_date:
            query += " AND date <= $end_date"
            params["end_date"] = str(end_date)

        query += " ORDER BY ticker, date"

        return self.execute(query, params)

    def get_returns(
        self,
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        periods: int = 1,
    ) -> pd.DataFrame:
        """Calculate returns for given tickers.

        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            periods: Number of periods for return calculation

        Returns:
            DataFrame with date and return columns per ticker
        """
        query = """
            WITH prices AS (
                SELECT
                    ticker,
                    date,
                    close,
                    ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY date) as rn
                FROM ibkr_equities
                WHERE ticker IN ({tickers})
                {date_filter}
            )
            SELECT
                p1.date,
                p1.ticker,
                (p2.close - p1.close) / p1.close as return
            FROM prices p1
            JOIN prices p2 ON p1.ticker = p2.ticker
                AND p2.rn = p1.rn + {periods}
            ORDER BY p1.ticker, p1.date
        """.format(
            tickers=", ".join([f"'{t}'" for t in tickers]),
            date_filter=f"AND date >= '{start_date}'" if start_date else "",
            periods=periods,
        )

        return self.execute(query)

    def get_volatility(
        self,
        ticker: str,
        window: int = 20,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """Calculate rolling volatility for a ticker.

        Args:
            ticker: Ticker symbol
            window: Rolling window size
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with date, close, and volatility columns
        """
        query = f"""
            WITH returns AS (
                SELECT
                    date,
                    close,
                    (close - LAG(close, 1) OVER (ORDER BY date)) / LAG(close, 1) OVER (ORDER BY date) as ret
                FROM ibkr_equities
                WHERE ticker = '{ticker}'
                {f"AND date >= '{start_date}'" if start_date else ""}
                {f"AND date <= '{end_date}'" if end_date else ""}
            )
            SELECT
                date,
                close,
                STDDEV(ret) OVER (ORDER BY date ROWS BETWEEN {window-1} PRECEDING AND CURRENT ROW) * SQRT(252) as volatility
            FROM returns
            ORDER BY date
        """

        return self.execute(query)

    def get_correlation_matrix(
        self,
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        window: Optional[int] = None,
    ) -> pd.DataFrame:
        """Calculate correlation matrix for given tickers.

        Args:
            tickers: List of ticker symbols
            start_date: Start date
            end_date: End date
            window: Optional rolling window for time-varying correlation

        Returns:
            Correlation matrix as DataFrame
        """
        ticker_list = ", ".join([f"'{t}'" for t in tickers])

        if window:
            # Rolling correlation
            query = f"""
                WITH returns AS (
                    SELECT
                        date,
                        ticker,
                        (close - LAG(close, 1) OVER (PARTITION BY ticker ORDER BY date)) / LAG(close, 1) OVER (PARTITION BY ticker ORDER BY date) as ret
                    FROM ibkr_equities
                    WHERE ticker IN ({ticker_list})
                    {f"AND date >= '{start_date}'" if start_date else ""}
                    {f"AND date <= '{end_date}'" if end_date else ""}
                ),
                pivoted AS (
                    SELECT date, ticker, ret FROM returns
                )
                SELECT * FROM pivoted
                PIVOT (AVG(ret) ON ticker IN ({ticker_list}))
            """
        else:
            # Static correlation
            query = f"""
                WITH returns AS (
                    SELECT
                        date,
                        ticker,
                        (close - LAG(close, 1) OVER (PARTITION BY ticker ORDER BY date)) / LAG(close, 1) OVER (PARTITION BY ticker ORDER BY date) as ret
                    FROM ibkr_equities
                    WHERE ticker IN ({ticker_list})
                    {f"AND date >= '{start_date}'" if start_date else ""}
                    {f"AND date <= '{end_date}'" if end_date else ""}
                )
                SELECT CORR(a.ret, b.ret) as correlation
                FROM returns a
                JOIN returns b ON a.date = b.date
                WHERE a.ticker = '{tickers[0]}' AND b.ticker = '{tickers[1]}'
            """

        return self.execute(query)

    def get_fred_series(
        self,
        series_ids: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """Query FRED economic data.

        Args:
            series_ids: List of FRED series IDs
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with FRED data
        """
        series_list = ", ".join([f"'{s}'" for s in series_ids])

        query = f"""
            SELECT * FROM fred_macro
            WHERE series_id IN ({series_list})
            {f"AND date >= '{start_date}'" if start_date else ""}
            {f"AND date <= '{end_date}'" if end_date else ""}
            ORDER BY series_id, date
        """

        return self.execute(query)

    def get_combined_data(
        self,
        ticker: str,
        fred_series: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """Get price data combined with macro indicators.

        Args:
            ticker: Equity ticker
            fred_series: List of FRED series to join
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with combined price and macro data
        """
        price_query = f"""
            SELECT date, close as price FROM ibkr_equities
            WHERE ticker = '{ticker}'
            {f"AND date >= '{start_date}'" if start_date else ""}
            {f"AND date <= '{end_date}'" if end_date else ""}
        """

        if fred_series:
            series_list = ", ".join([f"'{s}'" for s in fred_series])
            fred_query = f"""
                SELECT date, series_id, value FROM fred_macro
                WHERE series_id IN ({series_list})
                {f"AND date >= '{start_date}'" if start_date else ""}
                {f"AND date <= '{end_date}'" if end_date else ""}
            """

            query = f"""
                WITH prices AS ({price_query}),
                     fred AS ({fred_query})
                SELECT p.date, p.price, f.series_id, f.value
                FROM prices p
                LEFT JOIN fred f ON p.date = f.date
                ORDER BY p.date, f.series_id
            """
        else:
            query = price_query

        return self.execute(query)

    def close(self):
        """Close DuckDB connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ----------------------------------------------------------------------
# Convenience functions
# ----------------------------------------------------------------------


def get_research_db() -> ResearchDB:
    """Get a ResearchDB instance with default settings."""
    memory_limit = getattr(settings.research.duckdb, "memory_limit", 4096)
    return ResearchDB(memory_limit_mb=memory_limit)


def query_prices(**kwargs) -> pd.DataFrame:
    """Convenience function for querying prices."""
    with get_research_db() as db:
        return db.query_prices(**kwargs)


def get_returns(tickers: List[str], **kwargs) -> pd.DataFrame:
    """Convenience function for getting returns."""
    with get_research_db() as db:
        return db.get_returns(tickers, **kwargs)


def get_volatility(ticker: str, **kwargs) -> pd.DataFrame:
    """Convenience function for getting volatility."""
    with get_research_db() as db:
        return db.get_volatility(ticker, **kwargs)
