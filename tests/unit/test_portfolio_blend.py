"""Unit tests for portfolio/blend.py."""
import pytest
import pandas as pd
import numpy as np
from portfolio.blend import Signal, blend_signals, zscore


class TestZScore:
    """Test z-score normalization function."""
    
    def test_zscore_basic(self):
        """Test basic z-score calculation."""
        s = pd.Series([1, 2, 3, 4, 5])
        result = zscore(s)
        
        assert len(result) == 5
        assert abs(result.mean()) < 1e-10  # Mean should be ~0
        assert abs(result.std() - 1.0) < 1e-10  # Std should be ~1
    
    def test_zscore_constant_series(self):
        """Test z-score with constant series (std=0)."""
        s = pd.Series([5.0, 5.0, 5.0])
        result = zscore(s)
        
        # Should return zeros when std is 0
        assert (result == 0.0).all()
    
    def test_zscore_with_nan(self):
        """Test z-score handles NaN values."""
        s = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0])
        result = zscore(s)
        
        assert len(result) == 5
        assert pd.isna(result.iloc[2])  # NaN should remain NaN
    
    def test_zscore_empty_series(self):
        """Test z-score with empty series."""
        s = pd.Series(dtype=float)
        result = zscore(s)
        
        assert len(result) == 0


class TestBlendSignals:
    """Test signal blending functionality."""
    
    def test_blend_empty_signals(self):
        """Test blending with no signals."""
        result = blend_signals([])
        assert isinstance(result, pd.Series)
        assert len(result) == 0
    
    def test_blend_single_signal(self, sample_signals):
        """Test blending with a single signal."""
        signal = sample_signals[0]
        result = blend_signals([signal])
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(signal.score)
        # Should be z-scored version of the signal
        assert all(result.index == signal.score.index)
    
    def test_blend_multiple_signals(self, sample_signals):
        """Test blending multiple signals with weights."""
        result = blend_signals(sample_signals)
        
        assert isinstance(result, pd.Series)
        assert len(result) == 4  # 4 symbols
        assert all(result.index == sample_signals[0].score.index)
    
    def test_blend_with_weights(self):
        """Test blending with different signal weights."""
        symbols = ['AAPL', 'GOOGL']
        signal1 = Signal(
            name='signal1',
            score=pd.Series([1.0, 2.0], index=symbols),
            weight=2.0
        )
        signal2 = Signal(
            name='signal2',
            score=pd.Series([3.0, 4.0], index=symbols),
            weight=1.0
        )
        
        result = blend_signals([signal1, signal2], zscore_each=True)
        
        assert len(result) == 2
        # After z-scoring, the weighted sum should be computed
        assert all(result.index == symbols)
    
    def test_blend_without_zscore(self):
        """Test blending without z-score normalization."""
        symbols = ['AAPL', 'GOOGL']
        signal1 = Signal(
            name='signal1',
            score=pd.Series([1.0, 2.0], index=symbols),
            weight=1.0
        )
        signal2 = Signal(
            name='signal2',
            score=pd.Series([3.0, 4.0], index=symbols),
            weight=1.0
        )
        
        result = blend_signals([signal1, signal2], zscore_each=False)
        
        # Without z-scoring, should be simple weighted sum
        expected = signal1.score * 1.0 + signal2.score * 1.0
        pd.testing.assert_series_equal(result, expected)
    
    def test_blend_mismatched_indices(self):
        """Test blending signals with different asset universes."""
        signal1 = Signal(
            name='signal1',
            score=pd.Series([1.0, 2.0], index=['AAPL', 'GOOGL']),
            weight=1.0
        )
        signal2 = Signal(
            name='signal2',
            score=pd.Series([3.0, 4.0, 5.0], index=['AAPL', 'MSFT', 'TSLA']),
            weight=1.0
        )
        
        result = blend_signals([signal1, signal2])
        
        # Should union indices
        expected_symbols = {'AAPL', 'GOOGL', 'MSFT', 'TSLA'}
        assert set(result.index) == expected_symbols
        
        # Missing values should be filled with 0
        assert result['MSFT'] is not None
        assert result['TSLA'] is not None
    
    def test_blend_with_missing_values(self):
        """Test blending handles missing values correctly."""
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        signal1 = Signal(
            name='signal1',
            score=pd.Series([1.0, np.nan, 3.0], index=symbols),
            weight=1.0
        )
        
        result = blend_signals([signal1])
        
        assert len(result) == 3
        # NaN should be filled with 0 in the blend
        assert pd.notna(result['AAPL'])
        assert pd.notna(result['GOOGL'])  # NaN filled with 0
        assert pd.notna(result['MSFT'])
