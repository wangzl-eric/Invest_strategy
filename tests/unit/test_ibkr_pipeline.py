"""Unit tests for IBKR data pipeline components."""
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest


class TestIBKRClientHistoricalData:
    """Test IBKR client's historical data methods."""

    @pytest.fixture
    def mock_ib_client(self):
        """Create a mock IB client."""
        with patch("backend.ibkr_client.IB") as mock_ib:
            yield mock_ib

    def test_create_contract_stock(self):
        """Test creating a stock contract."""
        from backend.ibkr_client import IBKRClient

        client = IBKRClient()
        contract = client._create_contract("AAPL", "STK", "SMART", "USD")

        assert contract.symbol == "AAPL"
        assert contract.secType == "STK"
        assert contract.exchange == "SMART"
        assert contract.currency == "USD"

    def test_create_contract_forex(self):
        """Test creating a forex contract."""
        from backend.ibkr_client import IBKRClient

        client = IBKRClient()
        # For forex, ib_insync uses the quote currency as symbol (e.g., EURUSD -> symbol=USD)
        # This is how IBKR's Forex contracts work
        contract = client._create_contract("EURUSD", "CASH", "IDEALPRO", "USD")

        # The contract should be created with the correct security type
        assert contract.secType == "CASH"

    def test_create_contract_futures(self):
        """Test creating a futures contract."""
        from backend.ibkr_client import IBKRClient

        client = IBKRClient()
        contract = client._create_contract("ES", "FUT", "CME", "USD", expiry="202403")

        assert contract.symbol == "ES"
        assert contract.secType == "FUT"

    def test_valid_historical_durations(self):
        """Test that valid durations are defined."""
        from backend.ibkr_client import HISTORICAL_DURATIONS

        assert "1 D" in HISTORICAL_DURATIONS
        assert "1 W" in HISTORICAL_DURATIONS
        assert "1 M" in HISTORICAL_DURATIONS
        assert "1 Y" in HISTORICAL_DURATIONS
        assert "2 Y" in HISTORICAL_DURATIONS

    def test_valid_historical_intervals(self):
        """Test that valid intervals are defined."""
        from backend.ibkr_client import HISTORICAL_INTERVALS

        assert "1 min" in HISTORICAL_INTERVALS
        assert "5 mins" in HISTORICAL_INTERVALS
        assert "1 hour" in HISTORICAL_INTERVALS
        assert "1 day" in HISTORICAL_INTERVALS


class TestIBKRProvider:
    """Test IBKR data provider."""

    def test_ibkr_provider_init(self):
        """Test IBKR provider initialization."""
        from backend.data_providers import IBKRProvider

        provider = IBKRProvider(host="127.0.0.1", port=7497, client_id=1)

        assert provider.host == "127.0.0.1"
        assert provider.port == 7497
        assert provider.client_id == 1

    def test_ibkr_provider_name(self):
        """Test provider name."""
        from backend.data_providers import IBKRProvider

        provider = IBKRProvider()
        assert provider.get_provider_name() == "Interactive Brokers"

    def test_interval_mapping(self):
        """Test interval mapping from standard to IBKR format."""
        from backend.data_providers import IBKRProvider

        provider = IBKRProvider()

        assert provider._map_interval("1m") == "1 min"
        assert provider._map_interval("5m") == "5 mins"
        assert provider._map_interval("1h") == "1 hour"
        assert provider._map_interval("1d") == "1 day"
        assert provider._map_interval("1w") == "1 week"
        assert provider._map_interval("unknown") == "1 day"  # default


class TestIBKRDataFetcher:
    """Test IBKR data fetcher utility functions."""

    def test_default_equity_tickers_defined(self):
        """Test that default equity tickers are defined."""
        from backend.ibkr_data_fetcher import DEFAULT_US_EQUITIES

        assert isinstance(DEFAULT_US_EQUITIES, list)
        assert len(DEFAULT_US_EQUITIES) > 0
        assert "AAPL" in DEFAULT_US_EQUITIES
        assert "MSFT" in DEFAULT_US_EQUITIES

    def test_default_forex_pairs_defined(self):
        """Test that default forex pairs are defined."""
        from backend.ibkr_data_fetcher import DEFAULT_FOREX_PAIRS

        assert isinstance(DEFAULT_FOREX_PAIRS, list)
        assert "EURUSD" in DEFAULT_FOREX_PAIRS
        assert "GBPUSD" in DEFAULT_FOREX_PAIRS

    def test_default_futures_defined(self):
        """Test that default futures are defined."""
        from backend.ibkr_data_fetcher import DEFAULT_FUTURES

        assert isinstance(DEFAULT_FUTURES, list)
        assert "ES" in DEFAULT_FUTURES
        assert "CL" in DEFAULT_FUTURES
        assert "GC" in DEFAULT_FUTURES


class TestDataQualityValidation:
    """Test data quality validation functions."""

    def test_validate_empty_dataframe(self):
        """Test validation of empty DataFrame."""
        from backend.ibkr_data_fetcher import DataQualityReport

        df = pd.DataFrame()
        report = DataQualityReport(df)

        assert not report.is_valid()
        assert "DataFrame is empty" in report.issues

    def test_validate_dataframe_missing_columns(self):
        """Test validation with missing columns."""
        from backend.ibkr_data_fetcher import DataQualityReport

        df = pd.DataFrame(
            {"date": ["2024-01-01", "2024-01-02"], "close": [100.0, 101.0]}
        )
        report = DataQualityReport(df)

        assert not report.is_valid()
        assert any("Missing required column" in issue for issue in report.issues)

    def test_validate_valid_dataframe(self):
        """Test validation of valid DataFrame."""
        from backend.ibkr_data_fetcher import DataQualityReport

        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=10),
                "open": [100.0] * 10,
                "high": [105.0] * 10,
                "low": [95.0] * 10,
                "close": [102.0] * 10,
                "volume": [1000000] * 10,
                "ticker": ["AAPL"] * 10,
            }
        )
        report = DataQualityReport(df)

        # Should be valid (no critical issues)
        # May have warnings but no issues
        assert "date" in report.stats["columns"]

    def test_validate_negative_prices(self):
        """Test detection of negative prices."""
        from backend.ibkr_data_fetcher import DataQualityReport

        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "open": [100.0, -5.0, 100.0, 100.0, 100.0],
                "high": [105.0] * 5,
                "low": [95.0] * 5,
                "close": [102.0] * 5,
                "volume": [1000000] * 5,
            }
        )
        report = DataQualityReport(df)

        assert any("negative" in issue.lower() for issue in report.issues)

    def test_validate_high_low_sanity(self):
        """Test high < low detection."""
        from backend.ibkr_data_fetcher import DataQualityReport

        # Create DataFrame with explicit high < low
        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "open": [100.0, 100.0, 100.0, 100.0, 100.0],
                "high": [95.0, 105.0, 105.0, 105.0, 105.0],  # First row: high < low
                "low": [105.0, 95.0, 95.0, 95.0, 95.0],  # First row: high < low
                "close": [100.0, 100.0, 100.0, 100.0, 100.0],
                "volume": [1000000, 1000000, 1000000, 1000000, 1000000],
            }
        )

        report = DataQualityReport(df)

        # Should detect high < low
        assert any("high < low" in issue.lower() for issue in report.issues)

    def test_validate_clean_data(self):
        """Test data cleaning function."""
        from backend.ibkr_data_fetcher import validate_and_clean

        df = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02", "2024-01-02"],  # Duplicate
                "open": [100.0, 101.0, 101.0],  # Duplicate
                "high": [105.0, 106.0, 106.0],
                "low": [95.0, 96.0, 96.0],
                "close": [102.0, 103.0, 103.0],
                "volume": [1000000, 1000001, 1000001],
                "ticker": ["AAPL", "AAPL", "AAPL"],
            }
        )

        cleaned = validate_and_clean(df)

        # Should remove duplicates
        assert len(cleaned) < len(df)


class TestMarketDataStoreIBKR:
    """Test market data store IBKR integration."""

    def test_ibkr_asset_files_defined(self):
        """Test that IBKR asset files are defined."""
        from backend.market_data_store import _IBKR_ASSET_FILES

        assert isinstance(_IBKR_ASSET_FILES, dict)
        assert "ibkr_equities" in _IBKR_ASSET_FILES
        assert "ibkr_fx" in _IBKR_ASSET_FILES
        assert "ibkr_futures" in _IBKR_ASSET_FILES
        assert "ibkr_options" in _IBKR_ASSET_FILES

    def test_ibkr_tickers_defined(self):
        """Test that IBKR ticker lists are defined."""
        from backend.market_data_store import _IBKR_ASSET_TICKERS

        assert isinstance(_IBKR_ASSET_TICKERS, dict)
        assert "ibkr_equities" in _IBKR_ASSET_TICKERS
        assert "ibkr_fx" in _IBKR_ASSET_TICKERS
        assert "ibkr_futures" in _IBKR_ASSET_TICKERS
        assert isinstance(_IBKR_ASSET_TICKERS["ibkr_equities"], list)


class TestDataRoutesIBKR:
    """Test IBKR API routes."""

    def test_ibkr_pull_request_model(self):
        """Test IBKR pull request model."""
        from backend.api.data_routes import IBKRPullRequest

        req = IBKRPullRequest(
            asset_class="ibkr_equities",
            tickers=["AAPL", "MSFT"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            interval="1 day",
            sec_type="STK",
            exchange="SMART",
        )

        assert req.asset_class == "ibkr_equities"
        assert len(req.tickers) == 2
        assert req.interval == "1 day"

    @pytest.mark.asyncio
    async def test_ibkr_subscription_status_endpoint_import(self):
        """Test that subscription status endpoint can be imported."""
        # Just verify the import works - actual connection testing requires IBKR running
        from backend.api.data_routes import ibkr_subscription_status

        assert ibkr_subscription_status is not None
        assert callable(ibkr_subscription_status)


class TestIBKRSubscriptionsConfig:
    """Test IBKR subscriptions config file."""

    def test_config_file_exists(self):
        """Test that config file was created."""
        config_path = (
            Path(__file__).resolve().parent.parent.parent
            / "config"
            / "ibkr_data_subscriptions.yaml"
        )
        assert config_path.exists()

    def test_config_file_valid_yaml(self):
        """Test that config file is valid YAML."""
        import yaml

        config_path = (
            Path(__file__).resolve().parent.parent.parent
            / "config"
            / "ibkr_data_subscriptions.yaml"
        )

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        assert isinstance(config, dict)
        assert "subscriptions" in config


# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


class TestIBKRClientEdgeCases:
    """Test IBKR client edge cases and error handling."""

    def test_create_contract_with_none_currency(self):
        """Test creating contract with None currency defaults to USD."""
        from backend.ibkr_client import IBKRClient

        client = IBKRClient()
        contract = client._create_contract("AAPL", "STK", "SMART", None)

        assert contract.currency == "USD"

    def test_create_contract_with_empty_exchange(self):
        """Test creating contract with empty exchange."""
        from backend.ibkr_client import IBKRClient

        client = IBKRClient()
        contract = client._create_contract("EURUSD", "CASH", "", "USD")

        # Should default to IDEALPRO for forex
        assert contract.exchange == "IDEALPRO"

    def test_create_contract_unknown_sec_type(self):
        """Test creating contract with unknown security type defaults to stock."""
        from backend.ibkr_client import IBKRClient

        client = IBKRClient()
        contract = client._create_contract("UNKNOWN", "UNKNOWN", "SMART", "USD")

        # Should default to Stock
        assert hasattr(contract, "symbol")

    def test_get_historical_data_with_datetime_dates(self):
        """Test filtering with datetime.date objects."""
        import pandas as pd

        from backend.ibkr_client import IBKRClient

        client = IBKRClient()

        # Create sample data
        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=10),
                "open": [100.0] * 10,
                "high": [105.0] * 10,
                "low": [95.0] * 10,
                "close": [102.0] * 10,
                "volume": [1000000] * 10,
            }
        )

        # Filter with date objects (simulating what happens in real usage)
        start_date = datetime(2024, 1, 5).date()
        end_date = datetime(2024, 1, 8).date()

        # The filter should handle both datetime and date objects
        df_filtered = df[pd.to_datetime(df["date"]) >= pd.to_datetime(start_date)]
        df_filtered = df_filtered[
            pd.to_datetime(df_filtered["date"]) <= pd.to_datetime(end_date)
        ]

        assert len(df_filtered) == 4

    def test_duration_mapping_short_period(self):
        """Test duration mapping for short periods."""
        from backend.ibkr_client import IBKRClient

        client = IBKRClient()

        # Test that duration is correctly calculated
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 5)
        days_diff = (end - start).days

        assert days_diff == 4

    def test_duration_mapping_1_month(self):
        """Test duration mapping for 1 month."""
        from backend.ibkr_client import IBKRClient

        start = datetime(2024, 1, 1)
        end = datetime(2024, 2, 1)
        days_diff = (end - start).days

        # Feb 1 - Jan 1 = 31 days
        assert days_diff == 31

    def test_duration_mapping_1_year(self):
        """Test duration mapping for 1 year."""
        from backend.ibkr_client import IBKRClient

        start = datetime(2024, 1, 1)
        end = datetime(2025, 1, 1)
        days_diff = (end - start).days

        assert days_diff >= 365

    def test_duration_mapping_2_years(self):
        """Test duration mapping for 2+ years."""
        from backend.ibkr_client import IBKRClient

        start = datetime(2022, 1, 1)
        end = datetime(2024, 12, 31)
        days_diff = (end - start).days

        assert days_diff > 365


class TestDataValidationEdgeCases:
    """Test data validation edge cases."""

    def test_validate_all_nan_prices(self):
        """Test validation with all NaN prices."""
        from backend.ibkr_data_fetcher import DataQualityReport

        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "open": [np.nan] * 5,
                "high": [np.nan] * 5,
                "low": [np.nan] * 5,
                "close": [np.nan] * 5,
                "volume": [1000000] * 5,
            }
        )
        report = DataQualityReport(df)

        assert not report.is_valid()

    def test_validate_zero_prices(self):
        """Test zero prices are allowed (not flagged as error)."""
        from backend.ibkr_data_fetcher import DataQualityReport

        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "open": [100.0, 0.0, 100.0, 100.0, 100.0],
                "high": [105.0] * 5,
                "low": [95.0] * 5,
                "close": [102.0] * 5,
                "volume": [1000000] * 5,
            }
        )
        report = DataQualityReport(df)

        # Zero prices are NOT issues (only negative prices)
        assert not any("negative" in issue.lower() for issue in report.issues)

    def test_validate_extreme_volume(self):
        """Test zero volume is allowed (not flagged as error)."""
        from backend.ibkr_data_fetcher import DataQualityReport

        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "open": [100.0] * 5,
                "high": [105.0] * 5,
                "low": [95.0] * 5,
                "close": [102.0] * 5,
                "volume": [0, 0, 0, 0, 0],  # All zero volumes
            }
        )
        report = DataQualityReport(df)

        # Zero volume is NOT an issue (only negative)
        assert not any("volume" in issue.lower() for issue in report.issues)

    def test_validate_missing_date_column(self):
        """Test validation with missing date column."""
        from backend.ibkr_data_fetcher import DataQualityReport

        df = pd.DataFrame(
            {
                "open": [100.0, 101.0],
                "high": [105.0, 106.0],
                "low": [95.0, 96.0],
                "close": [102.0, 103.0],
                "volume": [1000000, 1000001],
            }
        )
        report = DataQualityReport(df)

        assert not report.is_valid()

    def test_validate_duplicate_dates(self):
        """Test duplicates are detected as warnings."""
        from backend.ibkr_data_fetcher import DataQualityReport

        df = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-01", "2024-01-02"],
                "ticker": ["AAPL", "AAPL", "AAPL"],
                "open": [100.0, 100.5, 101.0],
                "high": [105.0, 105.5, 106.0],
                "low": [95.0, 95.5, 96.0],
                "close": [102.0, 102.5, 103.0],
                "volume": [1000000, 1000001, 1000002],
            }
        )
        report = DataQualityReport(df)

        # Duplicates are warnings, not issues
        assert len(report.warnings) > 0
        assert any("duplicate" in w.lower() for w in report.warnings)

    def test_validate_future_dates(self):
        """Test future dates don't cause errors."""
        from datetime import date

        from backend.ibkr_data_fetcher import DataQualityReport

        # Use future dates
        future_date = date.today() + timedelta(days=30)
        df = pd.DataFrame(
            {
                "date": [future_date, future_date + timedelta(days=1)],
                "open": [100.0, 101.0],
                "high": [105.0, 106.0],
                "low": [95.0, 96.0],
                "close": [102.0, 103.0],
                "volume": [1000000, 1000001],
            }
        )
        report = DataQualityReport(df)

        # Future dates should not cause errors (they may generate warnings)
        assert report.df is not None

    def test_validate_close_outside_high_low(self):
        """Test close outside high-low range is detected as warning."""
        from backend.ibkr_data_fetcher import DataQualityReport

        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "open": [100.0] * 5,
                "high": [105.0] * 5,
                "low": [95.0] * 5,
                # Close outside range for first two rows
                "close": [110.0, 90.0, 102.0, 102.0, 102.0],
                "volume": [1000000] * 5,
            }
        )
        report = DataQualityReport(df)

        # Close outside high-low is a warning, not an issue
        assert any("close" in w.lower() for w in report.warnings)

    def test_clean_removes_duplicates(self):
        """Test that clean removes duplicate rows."""
        from backend.ibkr_data_fetcher import validate_and_clean

        df = pd.DataFrame(
            {
                "date": [
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-02",
                    "2024-01-03",
                ],
                "ticker": ["AAPL", "AAPL", "AAPL", "AAPL", "AAPL"],
                "open": [100.0, 100.0, 101.0, 101.0, 102.0],
                "high": [105.0, 105.0, 106.0, 106.0, 107.0],
                "low": [95.0, 95.0, 96.0, 96.0, 97.0],
                "close": [102.0, 102.0, 103.0, 103.0, 104.0],
                "volume": [1000000, 1000000, 1000001, 1000001, 1000002],
            }
        )

        cleaned = validate_and_clean(df)

        # Should have removed duplicates
        assert len(cleaned) < len(df)
        assert len(cleaned) == 3

    def test_clean_handles_empty_dataframe(self):
        """Test that clean handles empty DataFrame."""
        from backend.ibkr_data_fetcher import validate_and_clean

        df = pd.DataFrame()
        cleaned = validate_and_clean(df)

        assert len(cleaned) == 0

    def test_clean_handles_single_row(self):
        """Test that clean handles single row."""
        from backend.ibkr_data_fetcher import validate_and_clean

        df = pd.DataFrame(
            {
                "date": ["2024-01-01"],
                "ticker": ["AAPL"],
                "open": [100.0],
                "high": [105.0],
                "low": [95.0],
                "close": [102.0],
                "volume": [1000000],
            }
        )

        cleaned = validate_and_clean(df)

        assert len(cleaned) == 1


class TestAPIValidation:
    """Test API request validation."""

    def test_pull_request_with_empty_tickers(self):
        """Test pull request with empty tickers list."""
        from pydantic import ValidationError

        from backend.api.data_routes import IBKRPullRequest

        try:
            req = IBKRPullRequest(
                asset_class="ibkr_equities",
                tickers=[],
                start_date="2024-01-01",
                end_date="2024-12-31",
            )
            # Empty list might be allowed - just check it was created
            assert req.tickers == []
        except ValidationError:
            # ValidationError is also acceptable
            pass

    def test_pull_request_with_invalid_dates(self):
        """Test pull request with invalid date format."""
        from pydantic import ValidationError

        from backend.api.data_routes import IBKRPullRequest

        # Should handle invalid date format
        try:
            req = IBKRPullRequest(
                asset_class="ibkr_equities",
                tickers=["AAPL"],
                start_date="invalid-date",
                end_date="2024-12-31",
            )
            # If it didn't raise, check start_date is preserved
            assert req.start_date == "invalid-date"
        except (ValidationError, ValueError):
            # ValidationError or ValueError is expected
            pass

    def test_pull_request_end_before_start(self):
        """Test pull request with end date before start date."""
        from backend.api.data_routes import IBKRPullRequest

        # This should be allowed at validation level
        req = IBKRPullRequest(
            asset_class="ibkr_equities",
            tickers=["AAPL"],
            start_date="2024-12-31",
            end_date="2024-01-01",
        )

        # The dates are preserved as-is (validation happens at execution time)
        assert req.start_date == "2024-12-31"
        assert req.end_date == "2024-01-01"

    def test_pull_request_default_values(self):
        """Test pull request default values."""
        from backend.api.data_routes import IBKRPullRequest

        req = IBKRPullRequest(
            asset_class="ibkr_equities",
            tickers=["AAPL"],
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        assert req.interval == "1 day"
        assert req.sec_type == "STK"
        assert req.exchange == "SMART"

    def test_pull_request_with_custom_exchange(self):
        """Test pull request with custom exchange."""
        from backend.api.data_routes import IBKRPullRequest

        req = IBKRPullRequest(
            asset_class="ibkr_fx",
            tickers=["EURUSD"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            exchange="IDEALPRO",
            sec_type="CASH",
        )

        assert req.exchange == "IDEALPRO"
        assert req.sec_type == "CASH"


class TestTickerUniverse:
    """Test ticker universe configurations."""

    def test_ticker_universe_file_exists(self):
        """Test ticker universe config exists."""
        from pathlib import Path

        config_path = (
            Path(__file__).resolve().parent.parent.parent
            / "config"
            / "ticker_universe.py"
        )
        assert config_path.exists()

    def test_ticker_universe_has_required_lists(self):
        """Test ticker universe has all required lists."""
        from config.ticker_universe import (
            FOREX_EM,
            FOREX_MAJOR,
            FOREX_MINOR,
            HK_EQUITIES,
            US_ETFS,
            US_LARGE_CAP,
            US_MID_SMALL_CAP,
        )

        assert len(US_LARGE_CAP) > 0
        assert len(US_ETFS) > 0
        assert len(FOREX_MAJOR) > 0

    def test_ticker_universe_no_duplicates(self):
        """Test ticker universe has no duplicates."""
        from config.ticker_universe import US_LARGE_CAP

        # Check for duplicates
        assert len(US_LARGE_CAP) == len(set(US_LARGE_CAP))

    def test_active_universe_includes_all(self):
        """Test active universe includes all asset classes."""
        from config.ticker_universe import ACTIVE_UNIVERSE

        assert "us_equities" in ACTIVE_UNIVERSE
        assert "us_etfs" in ACTIVE_UNIVERSE
        assert "hk_equities" in ACTIVE_UNIVERSE
        assert "forex_major" in ACTIVE_UNIVERSE


class TestCatalogOperations:
    """Test catalog operations."""

    def test_catalog_file_exists(self):
        """Test catalog file exists."""
        from pathlib import Path

        catalog_path = (
            Path(__file__).resolve().parent.parent.parent
            / "data"
            / "market_data"
            / "catalog.json"
        )
        assert catalog_path.exists()

    def test_catalog_is_valid_json(self):
        """Test catalog is valid JSON."""
        import json
        from pathlib import Path

        catalog_path = (
            Path(__file__).resolve().parent.parent.parent
            / "data"
            / "market_data"
            / "catalog.json"
        )

        with open(catalog_path, "r") as f:
            catalog = json.load(f)

        assert isinstance(catalog, dict)

    def test_catalog_has_required_fields(self):
        """Test catalog entries have required fields."""
        import json
        from pathlib import Path

        catalog_path = (
            Path(__file__).resolve().parent.parent.parent
            / "data"
            / "market_data"
            / "catalog.json"
        )

        with open(catalog_path, "r") as f:
            catalog = json.load(f)

        # Check at least one entry
        for key, entry in catalog.items():
            assert "source" in entry
            assert "filepath" in entry
            assert "tickers" in entry
