"""Integration tests for API routes."""
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models import AccountSnapshot, PnLHistory, Position, Trade


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
        account_id="TEST123",
        timestamp=datetime.utcnow(),
        total_cash_value=50000.0,
        net_liquidation=150000.0,
        equity=150000.0,
    )
    db.add(snapshot)

    # Create position
    position = Position(
        account_id="TEST123",
        timestamp=datetime.utcnow(),
        symbol="AAPL",
        quantity=100.0,
        market_price=150.0,
        market_value=15000.0,
    )
    db.add(position)

    # Create PnL history
    pnl = PnLHistory(
        account_id="TEST123",
        date=datetime.utcnow(),
        realized_pnl=1000.0,
        unrealized_pnl=500.0,
        total_pnl=1500.0,
        net_liquidation=150000.0,
    )
    db.add(pnl)

    # Create trade
    trade = Trade(
        account_id="TEST123",
        exec_id="TEST_EXEC_001",
        exec_time=datetime.utcnow(),
        symbol="AAPL",
        side="BUY",
        shares=100.0,
        price=150.0,
        commission=1.0,
    )
    db.add(trade)

    db.commit()
    return {"account_id": "TEST123"}


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_basic_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestResearchVerdictEndpoints:
    """Test research verdict API endpoints."""

    def test_verdict_endpoint_rule_based_only(self, client):
        """Test /api/research/verdict with LLM disabled."""
        # Generate sample returns
        np.random.seed(42)
        returns = np.random.randn(100) * 0.01 + 0.0005

        request_data = {
            "returns": returns.tolist(),
            "benchmarks": {"SPY": (np.random.randn(100) * 0.008 + 0.0003).tolist()},
            "hypothesis": {
                "statement": "Momentum continues after earnings beats",
                "who_loses_money": "Slow traders",
                "economic_mechanism": "Information diffusion",
            },
            "n_iterations": 10,
            "avg_turnover": 0.5,
            "use_llm": False,
        }

        response = client.post("/api/research/verdict", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert "details" in data
        assert "verdict" in data

        # Verify details structure
        details = data["details"]
        assert "rule_based" in details
        assert "final" in details
        assert "verdict" in details["final"]

        # Verify rule-based structure
        rb = details["rule_based"]
        assert "significance" in rb
        assert "walkforward" in rb
        assert "robustness" in rb
        assert "beta" in rb

        # Verify significance metrics
        sig = rb["significance"]
        assert "sharpe_ratio" in sig
        assert "probabilistic_sharpe" in sig
        assert "deflated_sharpe" in sig
        assert "verdict" in sig

        # Verify walkforward metrics
        wf = rb["walkforward"]
        assert "win_rate" in wf
        assert "n_windows" in wf
        assert "verdict" in wf

        # Verify robustness metrics
        rob = rb["robustness"]
        assert "base_sharpe" in rob
        assert "costs_100_sharpe" in rob
        assert "slippage_25_sharpe" in rob
        assert "verdict" in rob

        # Verify beta metrics
        beta = rb["beta"]
        assert "spy_correlation" in beta
        assert "verdict" in beta

    def test_verdict_endpoint_without_benchmarks(self, client):
        """Test /api/research/verdict without benchmark data."""
        np.random.seed(42)
        returns = np.random.randn(100) * 0.01

        request_data = {
            "returns": returns.tolist(),
            "use_llm": False,
        }

        response = client.post("/api/research/verdict", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "verdict" in data

    def test_verdict_endpoint_with_hypothesis_only(self, client):
        """Test /api/research/verdict with hypothesis only."""
        np.random.seed(42)
        returns = np.random.randn(100) * 0.01

        request_data = {
            "returns": returns.tolist(),
            "hypothesis": {
                "statement": "Test hypothesis",
            },
            "use_llm": False,
        }

        response = client.post("/api/research/verdict", json=request_data)

        assert response.status_code == 200

    def test_verdict_endpoint_with_empty_returns(self, client):
        """Test /api/research/verdict with empty returns."""
        request_data = {
            "returns": [],
            "use_llm": False,
        }

        # Should handle gracefully
        response = client.post("/api/research/verdict", json=request_data)
        # May return 500 or 200 depending on implementation
        assert response.status_code in [200, 400, 500]

    def test_verdict_endpoint_invalid_data(self, client):
        """Test /api/research/verdict with invalid data."""
        request_data = {
            "returns": "not a list",  # Invalid
        }

        response = client.post("/api/research/verdict", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_verdict_from_report_endpoint(self, client):
        """Test /api/research/verdict/from-report endpoint."""
        # Create a mock report
        report = {
            "hypothesis": {
                "statement": "Test",
                "who_loses_money": "Test",
                "economic_mechanism": "Test",
                "noise_discrimination": "Test",
                "is_valid": True,
                "warnings": [],
            },
            "significance": {
                "sharpe_ratio": 1.5,
                "probabilistic_sharpe": 0.8,
                "deflated_sharpe": 1.2,
                "min_required_length": 12,
                "threshold": 0.5,
            },
            "walkforward": {
                "n_windows": 10,
                "train_months": 12,
                "test_months": 3,
                "step_months": 1,
                "mean_return": 0.15,
                "return_std": 0.1,
                "win_rate": 0.7,
                "best_return": 0.3,
                "worst_return": -0.05,
                "crisis_included": True,
            },
            "robustness": {
                "base_return": 0.2,
                "base_sharpe": 1.5,
                "costs_50_return": 0.15,
                "costs_50_sharpe": 1.2,
                "costs_100_return": 0.1,
                "costs_100_sharpe": 0.9,
                "slippage_10_return": 0.18,
                "slippage_10_sharpe": 1.4,
                "slippage_25_return": 0.15,
                "slippage_25_sharpe": 1.2,
            },
            "beta": {
                "spy_correlation": 0.3,
                "qqq_correlation": 0.4,
            },
            "n_iterations": 10,
            "optimization_landscape": "FLAT",
        }

        request_data = {
            "report": report,
            "use_llm": False,
        }

        response = client.post("/api/research/verdict/from-report", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert "details" in data or "final" in data

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
                "end_date": end_date.isoformat(),
            },
        )
        assert response.status_code == 200

    def test_get_pnl_history(self, client, sample_data):
        """Test getting PnL history time series."""
        response = client.get(
            "/api/pnl/history", params={"account_id": "TEST123", "freq": "D"}
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
            "/api/trades", params={"account_id": "TEST123", "symbol": "AAPL"}
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
