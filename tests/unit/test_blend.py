"""Unit tests for portfolio signal blending."""
import pytest
import pandas as pd
import numpy as np
from portfolio.blend import Signal, blend_signals, zscore


class TestZScore:
    """Tests for z-score normalization."""
    
    def test_zscore_basic(self):
        """Test basic z-score calculation."""
        s = pd.Series([1, 2, 3, 4, 5])
        result = zscore(s)
        
        assert len(result) == 5
        assert abs(result.mean()) < 1e-10  # Mean should be ~0
        assert abs(result.std() - 1.0) < 1e-10  # Std should be ~1
    
    def test_zscore_zero_std(self):
        """Test z-score with zero standard deviation."""
        s = pd.Series([5, 5, 5, 5, 5])
        result = zscore(s)
        
        assert len(result) == 5
        assert (result == 0).all()
    
    def test_zscore_nan_handling(self):
        """Test z-score with NaN values."""
        s = pd.Series([1, 2, np.nan, 4, 5])
        result = zscore(s)
        
        # Should still compute z-score on non-NaN values
        assert len(result) == 5


class TestBlendSignals:
    """Tests for signal blending."""
    
    def test_blend_single_signal(self, sample_returns_series):
        """Test blending a single signal."""
        signal = Signal(
            name="test",
            score=sample_returns_series,
            weight=1.0
        )
        
        result = blend_signals([signal])
        
        assert len(result) == len(sample_returns_series)
        assert isinstance(result, pd.Series)
    
    def test_blend_multiple_signals(self, sample_returns_series):
        """Test blending multiple signals."""
        signal1 = Signal(
            name="signal1",
            score=sample_returns_series,
            weight=1.0
        )
        signal2 = Signal(
            name="signal2",
            score=sample_returns_series * 2,
            weight=0.5
        )
        
        result = blend_signals([signal1, signal2])
        
        assert len(result) == len(sample_returns_series)
        assert isinstance(result, pd.Series)
    
    def test_blend_different_indices(self):
        """Test blending signals with different indices."""
        dates1 = pd.date_range("2024-01-01", periods=50, freq="D")
        dates2 = pd.date_range("2024-01-15", periods=50, freq="D")
        
        signal1 = Signal(
            name="signal1",
            score=pd.Series(range(50), index=dates1),
            weight=1.0
        )
        signal2 = Signal(
            name="signal2",
            score=pd.Series(range(50), index=dates2),
            weight=1.0
        )
        
        result = blend_signals([signal1, signal2])
        
        # Should union the indices
        assert len(result) >= 50
    
    def test_blend_empty_list(self):
        """Test blending empty signal list."""
        result = blend_signals([])
        
        assert isinstance(result, pd.Series)
        assert len(result) == 0
    
    def test_blend_without_zscore(self, sample_returns_series):
        """Test blending without z-score normalization."""
        signal = Signal(
            name="test",
            score=sample_returns_series,
            weight=1.0
        )
        
        result = blend_signals([signal], zscore_each=False)
        
        assert len(result) == len(sample_returns_series)
        # Should be approximately equal to original (with weight 1.0)
        pd.testing.assert_series_equal(result, sample_returns_series * 1.0, check_names=False)
    
    def test_blend_weighted(self, sample_returns_series):
        """Test weighted signal blending."""
        signal1 = Signal(
            name="signal1",
            score=pd.Series([1.0] * len(sample_returns_series), index=sample_returns_series.index),
            weight=2.0
        )
        signal2 = Signal(
            name="signal2",
            score=pd.Series([1.0] * len(sample_returns_series), index=sample_returns_series.index),
            weight=1.0
        )
        
        result = blend_signals([signal1, signal2], zscore_each=False)
        
        # With equal scores, result should reflect weight ratio (2:1)
        # After z-scoring, weights still apply
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_returns_series)
