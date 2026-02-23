"""Unit tests for execution risk controls."""
import pytest
from execution.risk import RiskEngine, RiskLimits, RiskState, RiskDecision
from execution.types import OrderRequest


class TestRiskLimits:
    """Tests for RiskLimits dataclass."""
    
    def test_default_limits(self):
        """Test default risk limits."""
        limits = RiskLimits()
        
        assert limits.max_position_notional == 50_000.0
        assert limits.max_gross_notional == 250_000.0
        assert limits.max_daily_loss == 2_500.0


class TestRiskState:
    """Tests for RiskState."""
    
    def test_default_state(self):
        """Test default risk state."""
        state = RiskState()
        
        assert state.gross_notional == 0.0
        assert state.position_notional == {}
        assert state.daily_pnl == 0.0
    
    def test_state_initialization(self):
        """Test risk state initialization with values."""
        state = RiskState(
            gross_notional=1000.0,
            position_notional={"AAPL": 500.0},
            daily_pnl=-100.0
        )
        
        assert state.gross_notional == 1000.0
        assert state.position_notional == {"AAPL": 500.0}
        assert state.daily_pnl == -100.0


class TestRiskEngine:
    """Tests for RiskEngine."""
    
    def test_allowed_order(self):
        """Test that valid orders are allowed."""
        limits = RiskLimits(
            max_position_notional=10_000.0,
            max_gross_notional=50_000.0,
            max_daily_loss=1_000.0
        )
        engine = RiskEngine(limits)
        state = RiskState()
        
        order = OrderRequest(
            symbol="AAPL",
            side="BUY",
            quantity=10.0,
            order_type="MKT"
        )
        price = 150.0
        
        decision = engine.check_order(state=state, order=order, price=price)
        
        assert decision.allowed is True
        assert decision.reason == ""
    
    def test_block_position_limit(self):
        """Test that orders exceeding position limit are blocked."""
        limits = RiskLimits(max_position_notional=1_000.0)
        engine = RiskEngine(limits)
        state = RiskState(position_notional={"AAPL": 500.0})
        
        order = OrderRequest(
            symbol="AAPL",
            side="BUY",
            quantity=10.0,
            order_type="MKT"
        )
        price = 100.0  # Notional = 1000, plus existing 500 = 1500 > limit
        
        decision = engine.check_order(state=state, order=order, price=price)
        
        assert decision.allowed is False
        assert "position notional" in decision.reason.lower()
    
    def test_block_gross_limit(self):
        """Test that orders exceeding gross notional limit are blocked."""
        limits = RiskLimits(max_gross_notional=1_000.0)
        engine = RiskEngine(limits)
        state = RiskState(gross_notional=500.0)
        
        order = OrderRequest(
            symbol="AAPL",
            side="BUY",
            quantity=10.0,
            order_type="MKT"
        )
        price = 100.0  # Notional = 1000, plus existing 500 = 1500 > limit
        
        decision = engine.check_order(state=state, order=order, price=price)
        
        assert decision.allowed is False
        assert "gross notional" in decision.reason.lower()
    
    def test_block_daily_loss(self):
        """Test that orders are blocked when daily loss limit is breached."""
        limits = RiskLimits(max_daily_loss=1_000.0)
        engine = RiskEngine(limits)
        state = RiskState(daily_pnl=-1_500.0)  # Exceeded loss limit
        
        order = OrderRequest(
            symbol="AAPL",
            side="BUY",
            quantity=10.0,
            order_type="MKT"
        )
        price = 150.0
        
        decision = engine.check_order(state=state, order=order, price=price)
        
        assert decision.allowed is False
        assert "daily loss" in decision.reason.lower()
    
    def test_kill_switch(self, monkeypatch):
        """Test kill switch via environment variable."""
        limits = RiskLimits(kill_switch_env="TEST_KILL_SWITCH")
        engine = RiskEngine(limits)
        state = RiskState()
        
        monkeypatch.setenv("TEST_KILL_SWITCH", "true")
        
        order = OrderRequest(
            symbol="AAPL",
            side="BUY",
            quantity=10.0,
            order_type="MKT"
        )
        price = 150.0
        
        decision = engine.check_order(state=state, order=order, price=price)
        
        assert decision.allowed is False
        assert "kill switch" in decision.reason.lower()
    
    def test_sell_order_position(self):
        """Test that sell orders reduce position notional."""
        limits = RiskLimits(max_position_notional=10_000.0)
        engine = RiskEngine(limits)
        state = RiskState(position_notional={"AAPL": 2_000.0})
        
        order = OrderRequest(
            symbol="AAPL",
            side="SELL",
            quantity=5.0,
            order_type="MKT"
        )
        price = 100.0  # Notional = 500, new position = 2000 - 500 = 1500
        
        decision = engine.check_order(state=state, order=order, price=price)
        
        assert decision.allowed is True  # Should be allowed
