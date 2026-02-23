"""Integration tests for API routes."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from backend.main import app
from backend.models import AccountSnapshot, Position, PnLHistory, Trade


@pytest.fixture
def client(mock_db_session):
    """Create test client with mocked database."""
    return TestClient(app)


@pytest.fixture
def sample_data(mock_db_session):
    """Create sample data in test database."""
    db = mock_db_session
    
    # Create account snapshot
    snapshot = AccountSnapshot(
        account_id='TEST123',
        timestamp=datetime.utcnow(),
        total_cash_value=50000.0,
        net_liquidation=150000.0,
        equity=150000.0,
    )
    db.add(snapshot)
    
    # Create position
    position = Position(
        account_id='TEST123',
        timestamp=datetime.utcnow(),
        symbol='AAPL',
        quantity=100.0,
        market_price=150.0,
        market_value=15000.0,
    )
    db.add(position)
    
    # Create PnL history
    pnl = PnLHistory(
        account_id='TEST123',
        date=datetime.utcnow(),
        realized_pnl=1000.0,
        unrealized_pnl=500.0,
        total_pnl=1500.0,
        net_liquidation=150000.0,
    )
    db.add(pnl)
    
    # Create trade
    trade = Trade(
        account_id='TEST123',
        exec_id='TEST_EXEC_001',
        exec_time=datetime.utcnow(),
        symbol='AAPL',
        side='BUY',
        shares=100.0,
        price=150.0,
        commission=1.0,
    )
    db.add(trade)
    
    db.commit()
    return {'account_id': 'TEST123'}


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_basic_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_api_health_check(self, client):
        """Test API health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "api"
    
    def test_detailed_health_check(self, client):
        """Test detailed health check endpoint."""
        response = client.get("/api/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "components" in data
        assert "database" in data["components"]


class TestAccountEndpoints:
    """Test account-related endpoints."""
    
    def test_get_account_summary(self, client, sample_data):
        """Test getting account summary."""
        response = client.get("/api/account/summary", params={"account_id": "TEST123"})
        assert response.status_code == 200
        data = response.json()
        assert data["account_id"] == "TEST123"
        assert "net_liquidation" in data
    
    def test_get_account_summary_no_data(self, client):
        """Test getting account summary when no data exists."""
        response = client.get("/api/account/summary")
        # Should return 404 or empty result
        assert response.status_code in [200, 404]


class TestPositionEndpoints:
    """Test position-related endpoints."""
    
    def test_get_positions(self, client, sample_data):
        """Test getting positions."""
        response = client.get("/api/positions", params={"account_id": "TEST123"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert data[0]["symbol"] == "AAPL"


class TestPnLEndpoints:
    """Test PnL-related endpoints."""
    
    def test_get_pnl(self, client, sample_data):
        """Test getting PnL history."""
        response = client.get("/api/pnl", params={"account_id": "TEST123"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_pnl_with_date_range(self, client, sample_data):
        """Test getting PnL with date filtering."""
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        response = client.get(
            "/api/pnl",
            params={
                "account_id": "TEST123",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        )
        assert response.status_code == 200
    
    def test_get_pnl_history(self, client, sample_data):
        """Test getting PnL history time series."""
        response = client.get(
            "/api/pnl/history",
            params={"account_id": "TEST123", "freq": "D"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestTradeEndpoints:
    """Test trade-related endpoints."""
    
    def test_get_trades(self, client, sample_data):
        """Test getting trades."""
        response = client.get("/api/trades", params={"account_id": "TEST123"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_trades_with_symbol_filter(self, client, sample_data):
        """Test getting trades filtered by symbol."""
        response = client.get(
            "/api/trades",
            params={"account_id": "TEST123", "symbol": "AAPL"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestPerformanceEndpoints:
    """Test performance metrics endpoints."""
    
    def test_get_performance(self, client, sample_data):
        """Test getting performance metrics."""
        response = client.get("/api/performance", params={"account_id": "TEST123"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
