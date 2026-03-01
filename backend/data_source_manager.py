"""Data source manager for unified fallback logic across yfinance, FRED, and IBKR.

This module provides a centralized way to determine the best available data source
for any given data request, with automatic fallback to secondary sources when
the primary source is unavailable.
"""

import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Available data source types."""
    YFINANCE = "yfinance"
    FRED = "fred"
    IBKR = "ibkr"
    PARQUET_STORE = "parquet"
    NONE = "none"


class SourceStatus(Enum):
    """Health status of a data source."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


# Asset class to source mapping with priority order
DEFAULT_PRIORITY_ORDER = {
    "equity": [DataSource.IBKR, DataSource.PARQUET_STORE, DataSource.YFINANCE],
    "equity_index": [DataSource.YFINANCE, DataSource.PARQUET_STORE, DataSource.IBKR],
    "fx": [DataSource.IBKR, DataSource.PARQUET_STORE, DataSource.YFINANCE],
    "commodities": [DataSource.IBKR, DataSource.PARQUET_STORE, DataSource.YFINANCE],
    "rates": [DataSource.FRED, DataSource.PARQUET_STORE, DataSource.YFINANCE],
    "macro": [DataSource.FRED, DataSource.PARQUET_STORE],
    "fed_liquidity": [DataSource.FRED, DataSource.PARQUET_STORE],
}

# Which asset classes support which sources
SOURCE_CAPABILITIES = {
    DataSource.YFINANCE: ["equity", "equity_index", "fx", "commodities", "rates"],
    DataSource.FRED: ["rates", "macro", "fed_liquidity"],
    DataSource.IBKR: ["equity", "fx", "commodities"],
    DataSource.PARQUET_STORE: ["equity", "equity_index", "fx", "commodities", "rates", "macro", "fed_liquidity"],
}


class SourceHealthTracker:
    """Tracks health status of each data source with circuit breaker pattern."""

    def __init__(self):
        self._health: Dict[DataSource, Dict[str, Any]] = {}
        self._failure_count: Dict[DataSource, int] = {}
        self._failure_threshold = 3  # Fail after 3 consecutive failures
        self._recovery_time = 60  # seconds to wait before retry after failure

    def record_success(self, source: DataSource):
        """Record a successful call."""
        self._failure_count[source] = 0
        if source not in self._health:
            self._health[source] = {"status": SourceStatus.HEALTHY, "last_success": time.time()}
        else:
            self._health[source]["status"] = SourceStatus.HEALTHY
            self._health[source]["last_success"] = time.time()

    def record_failure(self, source: DataSource):
        """Record a failed call."""
        self._failure_count[source] = self._failure_count.get(source, 0) + 1

        if source not in self._health:
            self._health[source] = {"status": SourceStatus.UNKNOWN, "last_failure": time.time()}

        if self._failure_count[source] >= self._failure_threshold:
            self._health[source]["status"] = SourceStatus.UNAVAILABLE
            self._health[source]["failure_time"] = time.time()
            logger.warning(f"Data source {source.value} marked as unavailable after {self._failure_count[source]} failures")

    def get_status(self, source: DataSource) -> SourceStatus:
        """Get current status of a source."""
        if source not in self._health:
            return SourceStatus.UNKNOWN

        health_info = self._health[source]
        status = health_info.get("status", SourceStatus.UNKNOWN)

        # Check if source should recover
        if status == SourceStatus.UNAVAILABLE:
            last_failure = health_info.get("failure_time", 0)
            if time.time() - last_failure > self._recovery_time:
                self._health[source]["status"] = SourceStatus.DEGRADED
                return SourceStatus.DEGRADED

        return status

    def is_available(self, source: DataSource) -> bool:
        """Check if a source is currently available."""
        status = self.get_status(source)
        return status in [SourceStatus.HEALTHY, SourceStatus.DEGRADED]


# Global health tracker
_health_tracker = SourceHealthTracker()


class DataSourceManager:
    """Manages data source selection and fallback logic."""

    def __init__(self):
        self._priority_order = DEFAULT_PRIORITY_ORDER.copy()
        self._custom_priorities: Dict[str, List[DataSource]] = {}

    def set_priority_order(self, asset_class: str, sources: List[DataSource]):
        """Set custom priority order for an asset class."""
        self._custom_priorities[asset_class] = sources

    def get_priority_order(self, asset_class: str) -> List[DataSource]:
        """Get the priority order for an asset class."""
        return self._custom_priorities.get(asset_class, self._priority_order.get(asset_class, [DataSource.YFINANCE]))

    def get_best_source(
        self,
        asset_class: str,
        symbol: Optional[str] = None,
        check_health: bool = True
    ) -> Tuple[DataSource, str]:
        """Get the best available data source for an asset class.

        Args:
            asset_class: The asset class (equity, fx, rates, macro, etc.)
            symbol: Optional symbol to check specific availability
            check_health: Whether to check source health status

        Returns:
            Tuple of (best_source, reason)
        """
        priority = self.get_priority_order(asset_class)

        for source in priority:
            if check_health and not _health_tracker.is_available(source):
                continue

            # Check if source supports this asset class
            if asset_class not in SOURCE_CAPABILITIES.get(source, []):
                continue

            # Check if source can handle this specific symbol
            if symbol and not self._source_can_handle_symbol(source, symbol, asset_class):
                continue

            return source, f"Primary source for {asset_class}"

        # If all preferred sources fail, try any available source
        for source in DataSource:
            if source == DataSource.NONE:
                continue
            if asset_class in SOURCE_CAPABILITIES.get(source, []):
                if check_health and not _health_tracker.is_available(source):
                    continue
                return source, f"Fallback: preferred sources unavailable"

        return DataSource.NONE, "No available data source"

    def _source_can_handle_symbol(self, source: DataSource, symbol: str, asset_class: str) -> bool:
        """Check if a source can handle a specific symbol."""
        # Check symbol-specific limitations
        if source == DataSource.FRED:
            # FRED only handles series IDs, not tickers
            return asset_class in ["rates", "macro", "fed_liquidity"]
        elif source == DataSource.IBKR:
            # IBKR can handle most symbols but needs subscription
            # For now, assume it can handle equities and fx
            return asset_class in ["equity", "fx", "commodities"]
        elif source == DataSource.YFINANCE:
            # yfinance handles most symbols
            return True
        elif source == DataSource.PARQUET_STORE:
            # Parquet store has whatever we've stored
            return True
        return False

    def get_with_fallback(
        self,
        asset_class: str,
        symbol: str,
        fetch_funcs: Dict[DataSource, callable],
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch data with automatic fallback through sources.

        Args:
            asset_class: The asset class to fetch
            symbol: Symbol or series ID to fetch
            fetch_funcs: Dict mapping DataSource to fetch function
            **kwargs: Arguments to pass to fetch functions

        Returns:
            Dict with keys: data, source_used, fallback_reason, success
        """
        priority = self.get_priority_order(asset_class)

        for source in priority:
            if source not in fetch_funcs:
                continue

            if not _health_tracker.is_available(source):
                logger.debug(f"Skipping {source.value} - health check failed")
                continue

            try:
                fetch_func = fetch_funcs[source]
                data = fetch_func(source, symbol, **kwargs)

                # Check if data is valid
                if self._is_valid_data(data):
                    _health_tracker.record_success(source)
                    return {
                        "data": data,
                        "source_used": source.value,
                        "fallback_reason": None,
                        "success": True
                    }
                else:
                    logger.debug(f"Invalid data from {source.value} for {symbol}")

            except Exception as e:
                logger.warning(f"Error fetching {symbol} from {source.value}: {e}")
                _health_tracker.record_failure(source)
                continue

        # All sources failed
        return {
            "data": pd.DataFrame(),
            "source_used": None,
            "fallback_reason": "All data sources failed",
            "success": False
        }

    def _is_valid_data(self, data) -> bool:
        """Check if fetched data is valid."""
        if data is None:
            return False
        if isinstance(data, pd.DataFrame):
            return not data.empty
        if isinstance(data, (list, dict)):
            return len(data) > 0
        return bool(data)

    def get_source_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all data sources and their status."""
        info = {}
        for source in DataSource:
            if source == DataSource.NONE:
                continue
            info[source.value] = {
                "status": _health_tracker.get_status(source).value,
                "supported_asset_classes": SOURCE_CAPABILITIES.get(source, []),
            }
        return info


# Global singleton
data_source_manager = DataSourceManager()


# Convenience functions
def get_best_source(asset_class: str, symbol: Optional[str] = None) -> DataSource:
    """Get the best available data source for an asset class."""
    source, _ = data_source_manager.get_best_source(asset_class, symbol)
    return source


def get_with_fallback(
    asset_class: str,
    symbol: str,
    fetch_funcs: Dict[DataSource, callable],
    **kwargs
) -> Dict[str, Any]:
    """Fetch data with automatic fallback."""
    return data_source_manager.get_with_fallback(asset_class, symbol, fetch_funcs, **kwargs)


def record_success(source: DataSource):
    """Record a successful data fetch."""
    _health_tracker.record_success(source)


def record_failure(source: DataSource):
    """Record a failed data fetch."""
    _health_tracker.record_failure(source)
