"""Unit tests for data processor."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backend.data_processor import DataProcessor


class TestDataProcessor:
    """Tests for DataProcessor class."""
    
    def test_sharpe_ratio_basic(self, sample_returns_series):
        """Test basic Sharpe ratio calculation."""
        processor = DataProcessor()
        sharpe = processor.calculate_sharpe_ratio(sample_returns_series)
        
        assert isinstance(sharpe, float)
        assert not np.isnan(sharpe)
        assert not np.isinf(sharpe)
    
    def test_sharpe_ratio_zero_std(self):
        """Test Sharpe ratio with zero standard deviation."""
        processor = DataProcessor()
        returns = pd.Series([0.001] * 100)
        sharpe = processor.calculate_sharpe_ratio(returns)
        
        assert sharpe == 0.0
    
    def test_sharpe_ratio_empty(self):
        """Test Sharpe ratio with empty series."""
        processor = DataProcessor()
        returns = pd.Series(dtype=float)
        sharpe = processor.calculate_sharpe_ratio(returns)
        
        assert sharpe == 0.0
    
    def test_sharpe_ratio_single_value(self):
        """Test Sharpe ratio with single value."""
        processor = DataProcessor()
        returns = pd.Series([0.001])
        sharpe = processor.calculate_sharpe_ratio(returns)
        
        assert sharpe == 0.0
    
    def test_sortino_ratio_basic(self, sample_returns_series):
        """Test basic Sortino ratio calculation."""
        processor = DataProcessor()
        sortino = processor.calculate_sortino_ratio(sample_returns_series)
        
        assert isinstance(sortino, float)
        assert not np.isnan(sortino)
        assert not np.isinf(sortino)
    
    def test_sortino_ratio_no_downside(self):
        """Test Sortino ratio with no negative returns."""
        processor = DataProcessor()
        returns = pd.Series([0.001, 0.002, 0.0015, 0.002])
        sortino = processor.calculate_sortino_ratio(returns)
        
        # Should return 0.0 if no downside returns
        assert sortino == 0.0
    
    def test_max_drawdown_basic(self, sample_equity_series):
        """Test basic max drawdown calculation."""
        processor = DataProcessor()
        max_dd = processor.calculate_max_drawdown(sample_equity_series)
        
        assert isinstance(max_dd, float)
        assert max_dd <= 0.0  # Drawdown should be negative or zero
        assert not np.isnan(max_dd)
        assert not np.isinf(max_dd)
    
    def test_max_drawdown_monotonic_increase(self):
        """Test max drawdown with monotonically increasing equity."""
        processor = DataProcessor()
        equity = pd.Series(range(100, 200))
        max_dd = processor.calculate_max_drawdown(equity)
        
        assert max_dd == 0.0  # No drawdown if always increasing
    
    def test_max_drawdown_zero_starting_equity(self):
        """Test max drawdown with zero starting equity."""
        processor = DataProcessor()
        equity = pd.Series([0, 100, 200, 150])
        max_dd = processor.calculate_max_drawdown(equity)
        
        # Should handle gracefully
        assert not np.isnan(max_dd)
        assert not np.isinf(max_dd)
    
    def test_max_drawdown_negative_values(self):
        """Test max drawdown with negative equity values."""
        processor = DataProcessor()
        equity = pd.Series([100, 50, 25, 30])
        max_dd = processor.calculate_max_drawdown(equity)
        
        assert max_dd <= 0.0
        assert not np.isnan(max_dd)
    
    def test_daily_returns_empty(self):
        """Test daily returns with no data."""
        processor = DataProcessor()
        returns_df = processor.calculate_daily_returns("NONEXISTENT_ACCOUNT")
        
        assert returns_df.empty
    
    def test_calculate_sharpe_ratio_with_risk_free_rate(self, sample_returns_series):
        """Test Sharpe ratio with risk-free rate."""
        processor = DataProcessor()
        sharpe = processor.calculate_sharpe_ratio(sample_returns_series, risk_free_rate=0.02)
        
        assert isinstance(sharpe, float)
        assert not np.isnan(sharpe)
