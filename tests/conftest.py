"""Pytest configuration and shared fixtures."""
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock

import numpy as np
import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.config import settings
from backend.models import Base


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
def mock_db_session():
    """Create a mock database session for API testing."""
    session = MagicMock()
    return session


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


@pytest.fixture
def sample_signals():
    """Sample Signal objects for testing signal blending."""
    from portfolio.blend import Signal

    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN"]
    np.random.seed(42)

    # Create 3 sample signals with different scores
    signal1 = Signal(
        name="momentum_1m",
        score=pd.Series(np.random.randn(4), index=symbols),
        weight=1.0,
    )
    signal2 = Signal(
        name="mean_reversion",
        score=pd.Series(np.random.randn(4), index=symbols),
        weight=0.5,
    )
    signal3 = Signal(
        name="value_score",
        score=pd.Series(np.random.randn(4), index=symbols),
        weight=0.75,
    )

    return [signal1, signal2, signal3]


@pytest.fixture
def sample_positions():
    """Sample positions dictionary for testing."""
    return {
        "AAPL": {"quantity": 100, "avg_cost": 150.0, "market_value": 155.0},
        "MSFT": {"quantity": 50, "avg_cost": 300.0, "market_value": 320.0},
        "GOOGL": {"quantity": 25, "avg_cost": 2800.0, "market_value": 2900.0},
    }


@pytest.fixture
def sample_trades():
    """Sample trades list for testing."""
    return [
        {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 100,
            "price": 150.0,
            "commission": 1.0,
            "date": datetime(2024, 1, 15),
        },
        {
            "symbol": "MSFT",
            "action": "BUY",
            "quantity": 50,
            "price": 300.0,
            "commission": 1.0,
            "date": datetime(2024, 1, 20),
        },
    ]


@pytest.fixture
def sample_returns_data():
    """Sample returns data for optimization tests."""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, (100, 4))
    return pd.DataFrame(returns, index=dates, columns=["AAPL", "MSFT", "GOOGL", "AMZN"])


# ============== News Service Fixtures ==============


@pytest.fixture
def mock_news_articles():
    """Mock news articles for testing."""
    return [
        {
            "id": "news-001",
            "title": "Apple Reports Record Q4 Earnings",
            "source": "Reuters",
            "timestamp": "2024-01-15T14:30:00",
            "summary": "Apple Inc. reported record quarterly earnings...",
            "url": "https://example.com/news/001",
        },
        {
            "id": "news-002",
            "title": "Apple Announces New Product Line",
            "source": "Bloomberg",
            "timestamp": "2024-01-14T10:00:00",
            "summary": "Apple unveiled a new line of products...",
            "url": "https://example.com/news/002",
        },
        {
            "id": "news-003",
            "title": "Analysts Upgrade Apple to Buy",
            "source": "CNBC",
            "timestamp": "2024-01-13T16:00:00",
            "summary": "Multiple analysts upgraded Apple's rating...",
            "url": "https://example.com/news/003",
        },
    ]


@pytest.fixture
def mock_forex_news_articles():
    """Mock forex news articles for testing."""
    return [
        {
            "id": "fx-001",
            "title": "EUR/USD Rises on ECB Rate Decision",
            "source": "Reuters",
            "timestamp": "2024-01-15T12:00:00",
            "summary": "The Euro strengthened against the Dollar...",
            "url": "https://example.com/fx/001",
        },
    ]


@pytest.fixture
def mock_market_bulletins():
    """Mock market bulletins for testing."""
    return [
        {
            "msg_id": "msg-001",
            "timestamp": "2024-01-15T09:00:00",
            "headline": "Market Trading Hours Notice",
            "message": "US markets will close early today...",
            "exchange": "NYSE",
        },
        {
            "msg_id": "msg-002",
            "timestamp": "2024-01-14T15:30:00",
            "headline": "Trading Halt: AAPL",
            "message": "Trading halted pending news release...",
            "exchange": "NASDAQ",
        },
    ]


@pytest.fixture
def mock_news_df():
    """Mock news DataFrame for testing."""
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-15", "2024-01-14", "2024-01-13"]),
            "title": [
                "Apple Reports Record Q4 Earnings",
                "Apple Announces New Product Line",
                "Analysts Upgrade Apple to Buy",
            ],
            "source": ["Reuters", "Bloomberg", "CNBC"],
            "url": [
                "https://example.com/news/001",
                "https://example.com/news/002",
                "https://example.com/news/003",
            ],
        }
    )
