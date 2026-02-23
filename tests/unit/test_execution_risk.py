"""Unit tests for execution/risk.py."""
import pytest
import os
from execution.risk import RiskEngine, RiskLimits, RiskState, RiskDecision
from execution.types import OrderRequest


class TestRiskLimits:
    """Test RiskLimits dataclass."""
    
    def test_risk_limits_defaults(self):
        """Test default risk limits."""
        limits = RiskLimits()
        
        assert limits.max_position_notional == 50_000.0
        assert limits.max_gross_notional == 250_000.0
        assert limits.max_daily_loss == 2_500.0


class TestRiskEngine:
    """Test RiskEngine class."""
    
    def test_risk_engine_init(self):
        """Test RiskEngine initialization."""
        engine = RiskEngine()
        assert engine.limits is not None
    
    def test_risk_engine_custom_limits(self):
        """Test RiskEngine with custom limits."""
        limits = RiskLimits(
            max_position_notional=100_000.0,
            max_gross_notional=500_000.0
        )
        engine = RiskEngine(limits=limits)
        assert engine.limits.max_position_notional == 100_000.0
    
    def test_check_order_allowed(self):
        """Test order check when all limits are satisfied."""
        engine = RiskEngine()
        state = RiskState(
            gross_notional=100_000.0,
            position_notional={'AAPL': 20_000.0},
            daily_pnl=100.0
        )
        order = OrderRequest(
            symbol='GOOGL',
            side='BUY',
            quantity=100.0
        )
        price = 150.0
        
        decision = engine.check_order(state=state, order=order, price=price)
        
        assert decision.allowed is True
        assert decision.reason == ""
    
    def test_check_order_kill_switch(self, monkeypatch):
        """Test order check when kill switch is enabled."""
        monkeypatch.setenv('KILL_SWITCH', 'true')
        
        engine = RiskEngine()
        state = RiskState()
        order = OrderRequest(symbol='AAPL', side='BUY', quantity=100.0)
        
        decision = engine.check_order(state=state, order=order, price=100.0)
        
        assert decision.allowed is False
        assert 'kill switch' in decision.reason.lower()
    
    def test_check_order_max_daily_loss(self):
        """Test order check when daily loss limit is breached."""
        engine = RiskEngine()
        state = RiskState(
            gross_notional=0.0,
            daily_pnl=-3000.0  # Exceeds max_daily_loss of 2500
        )
        order = OrderRequest(symbol='AAPL', side='BUY', quantity=100.0)
        
        decision = engine.check_order(state=state, order=order, price=100.0)
        
        assert decision.allowed is False
        assert 'daily loss' in decision.reason.lower()
    
    def test_check_order_max_position_notional(self):
        """Test order check when position notional limit is exceeded."""
        engine = RiskEngine()
        state = RiskState(
            gross_notional=0.0,
            position_notional={'AAPL': 45_000.0}  # Close to limit
        )
        order = OrderRequest(
            symbol='AAPL',
            side='BUY',
            quantity=100.0  # Would add 10k, exceeding 50k limit
        )
        price = 100.0
        
        decision = engine.check_order(state=state, order=order, price=price)
        
        assert decision.allowed is False
        assert 'position notional' in decision.reason.lower()
    
    def test_check_order_max_gross_notional(self):
        """Test order check when gross notional limit is exceeded."""
        engine = RiskEngine()
        state = RiskState(
            gross_notional=240_000.0  # Close to 250k limit
        )
        order = OrderRequest(
            symbol='AAPL',
            side='BUY',
            quantity=1000.0  # Would add 150k, exceeding limit
        )
        price = 150.0
        
        decision = engine.check_order(state=state, order=order, price=price)
        
        assert decision.allowed is False
        assert 'gross notional' in decision.reason.lower()
    
    def test_check_order_sell_reduces_position(self):
        """Test that selling reduces position notional."""
        engine = RiskEngine()
        state = RiskState(
            gross_notional=50_000.0,
            position_notional={'AAPL': 30_000.0}
        )
        order = OrderRequest(
            symbol='AAPL',
            side='SELL',
            quantity=100.0
        )
        price = 100.0
        
        decision = engine.check_order(state=state, order=order, price=price)
        
        # Selling should be allowed (reduces position)
        assert decision.allowed is True
        # Symbol notional should decrease
        assert decision.context['symbol_notional_after'] < 30_000.0
