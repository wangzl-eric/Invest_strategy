"""Unit tests for vectorized backtesting."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from backtests.vectorized import (
    VectorizedBacktestConfig,
    run_vectorized_backtest,
)
from backtests.core import VectorStrategy, CostModel, SlippageModel


class SimpleStrategy(VectorStrategy):
    """Simple test strategy."""
    name = "simple_strategy"
    
    def generate_positions(self, bars: pd.DataFrame) -> pd.Series:
        """Generate simple long positions when close > mean."""
        close = bars["close"].astype(float)
        mean_price = close.rolling(10, min_periods=1).mean()
        return (close > mean_price).astype(float)


class TestVectorizedBacktestConfig:
    """Tests for VectorizedBacktestConfig."""
    
    def test_default_config(self):
        """Test default backtest config."""
        cfg = VectorizedBacktestConfig()
        
        assert cfg.shift_positions_by == 1
        assert cfg.periods_per_year == 252
        assert cfg.cost_model.cost_tps == 0.0
        assert cfg.slippage_model.slippage_bps == 0.0


class TestRunVectorizedBacktest:
    """Tests for run_vectorized_backtest."""
    
    def test_basic_backtest(self, sample_prices_series):
        """Test basic vectorized backtest."""
        bars = pd.DataFrame({
            "timestamp": sample_prices_series.index,
            "close": sample_prices_series.values
        })
        bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
        
        strategy = SimpleStrategy()
        result = run_vectorized_backtest(
            bars=bars,
            strategy=strategy,
            price_col="close"
        )
        
        assert result.equity is not None
        assert result.returns is not None
        assert result.positions is not None
        assert result.turnover is not None
        assert result.stats is not None
        assert "total_return" in result.stats
        assert "sharpe" in result.stats
        assert "max_drawdown" in result.stats
        assert len(result.equity) == len(bars)
    
    def test_backtest_with_costs(self, sample_prices_series):
        """Test backtest with transaction costs."""
        bars = pd.DataFrame({
            "timestamp": sample_prices_series.index,
            "close": sample_prices_series.values
        })
        bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
        
        cfg = VectorizedBacktestConfig(
            cost_model=CostModel(cost_tps=0.001),  # 10 bps
            slippage_model=SlippageModel(slippage_bps=5.0)  # 5 bps
        )
        
        strategy = SimpleStrategy()
        result = run_vectorized_backtest(
            bars=bars,
            strategy=strategy,
            cfg=cfg,
            price_col="close"
        )
        
        assert result.stats is not None
        # With costs, returns should be lower (or same if no trading)
        assert isinstance(result.stats["total_return"], float)
    
    def test_backtest_missing_price_column(self, sample_prices_series):
        """Test backtest with missing price column."""
        bars = pd.DataFrame({
            "timestamp": sample_prices_series.index,
            "open": sample_prices_series.values  # Wrong column
        })
        bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
        
        strategy = SimpleStrategy()
        
        with pytest.raises(ValueError, match="missing.*close"):
            run_vectorized_backtest(
                bars=bars,
                strategy=strategy,
                price_col="close"
            )
    
    def test_backtest_position_shifting(self, sample_prices_series):
        """Test that positions are shifted correctly."""
        bars = pd.DataFrame({
            "timestamp": sample_prices_series.index,
            "close": sample_prices_series.values
        })
        bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
        
        cfg = VectorizedBacktestConfig(shift_positions_by=1)
        strategy = SimpleStrategy()
        result = run_vectorized_backtest(
            bars=bars,
            strategy=strategy,
            cfg=cfg,
            price_col="close"
        )
        
        # Positions should be shifted by 1 period
        assert len(result.positions) == len(bars)
        # First position should be 0 (shifted)
        assert result.positions.iloc[0] == 0.0 or np.isnan(result.positions.iloc[0])
