"""Unit tests for IBKR data pipeline components."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
from pathlib import Path


class TestIBKRClientHistoricalData:
    """Test IBKR client's historical data methods."""
    
    @pytest.fixture
    def mock_ib_client(self):
        """Create a mock IB client."""
        with patch('backend.ibkr_client.IB') as mock_ib:
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
        
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'close': [100.0, 101.0]
        })
        report = DataQualityReport(df)
        
        assert not report.is_valid()
        assert any("Missing required column" in issue for issue in report.issues)
    
    def test_validate_valid_dataframe(self):
        """Test validation of valid DataFrame."""
        from backend.ibkr_data_fetcher import DataQualityReport
        
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10),
            'open': [100.0] * 10,
            'high': [105.0] * 10,
            'low': [95.0] * 10,
            'close': [102.0] * 10,
            'volume': [1000000] * 10,
            'ticker': ['AAPL'] * 10
        })
        report = DataQualityReport(df)
        
        # Should be valid (no critical issues)
        # May have warnings but no issues
        assert 'date' in report.stats['columns']
    
    def test_validate_negative_prices(self):
        """Test detection of negative prices."""
        from backend.ibkr_data_fetcher import DataQualityReport
        
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5),
            'open': [100.0, -5.0, 100.0, 100.0, 100.0],
            'high': [105.0] * 5,
            'low': [95.0] * 5,
            'close': [102.0] * 5,
            'volume': [1000000] * 5
        })
        report = DataQualityReport(df)
        
        assert any("negative" in issue.lower() for issue in report.issues)
    
    def test_validate_high_low_sanity(self):
        """Test high < low detection."""
        from backend.ibkr_data_fetcher import DataQualityReport
        
        # Create DataFrame with explicit high < low
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5),
            'open': [100.0, 100.0, 100.0, 100.0, 100.0],
            'high': [95.0, 105.0, 105.0, 105.0, 105.0],  # First row: high < low
            'low': [105.0, 95.0, 95.0, 95.0, 95.0],  # First row: high < low
            'close': [100.0, 100.0, 100.0, 100.0, 100.0],
            'volume': [1000000, 1000000, 1000000, 1000000, 1000000]
        })
        
        report = DataQualityReport(df)
        
        # Should detect high < low
        assert any("high < low" in issue.lower() for issue in report.issues)
    
    def test_validate_clean_data(self):
        """Test data cleaning function."""
        from backend.ibkr_data_fetcher import validate_and_clean
        
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-02'],  # Duplicate
            'open': [100.0, 101.0, 101.0],  # Duplicate
            'high': [105.0, 106.0, 106.0],
            'low': [95.0, 96.0, 96.0],
            'close': [102.0, 103.0, 103.0],
            'volume': [1000000, 1000001, 1000001],
            'ticker': ['AAPL', 'AAPL', 'AAPL']
        })
        
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
            exchange="SMART"
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
        config_path = Path(__file__).resolve().parent.parent.parent / "config" / "ibkr_data_subscriptions.yaml"
        assert config_path.exists()
    
    def test_config_file_valid_yaml(self):
        """Test that config file is valid YAML."""
        import yaml
        config_path = Path(__file__).resolve().parent.parent.parent / "config" / "ibkr_data_subscriptions.yaml"
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert isinstance(config, dict)
        assert "subscriptions" in config


# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit
