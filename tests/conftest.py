"""Pytest configuration and shared fixtures."""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from backend.models import Base
from backend.config import settings


@pytest.fixture(scope="function")
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def mock_ibkr_client():
    """Mock IBKR client for testing."""
    client = Mock()
    client.connected = True
    client.connect = AsyncMock(return_value=True)
    client.disconnect = AsyncMock(return_value=None)
    client.ensure_connected = AsyncMock(return_value=True)
    client.ib = Mock()
    client.ib.isConnected = Mock(return_value=True)
    client.ib.accountValues = AsyncMock(return_value=[])
    client.ib.positions = AsyncMock(return_value=[])
    client.ib.trades = AsyncMock(return_value=[])
    client.ib.reqAccountSummary = AsyncMock(return_value=[])
    return client


@pytest.fixture
def sample_returns_series():
    """Sample returns series for testing."""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, 100)  # Mean 0.1%, std 2%
    return pd.Series(returns, index=dates)


@pytest.fixture
def sample_prices_series():
    """Sample prices series for testing."""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, 100)
    prices = 100 * (1 + returns).cumprod()
    return pd.Series(prices, index=dates)


@pytest.fixture
def sample_returns_df():
    """Sample returns DataFrame for testing (multi-asset)."""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, (100, 3))
    return pd.DataFrame(returns, index=dates, columns=["AAPL", "MSFT", "GOOGL"])


@pytest.fixture
def sample_equity_series():
    """Sample equity series for testing."""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, 100)
    equity = 100000 * (1 + returns).cumprod()
    return pd.Series(equity, index=dates)
