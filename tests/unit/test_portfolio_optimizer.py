"""Unit tests for portfolio/optimizer.py."""
import pytest
import pandas as pd
import numpy as np
from portfolio.optimizer import mean_variance_optimize, weights_from_alpha, OptimizationConfig


class TestMeanVarianceOptimize:
    """Test mean-variance optimization."""
    
    @pytest.mark.slow
    def test_mean_variance_optimize_basic(self):
        """Test basic mean-variance optimization."""
        assets = ['AAPL', 'GOOGL', 'MSFT']
        expected_returns = pd.Series([0.001, 0.0008, 0.0012], index=assets)
        
        # Create a simple covariance matrix
        cov = pd.DataFrame(
            [[0.0004, 0.0002, 0.0001],
             [0.0002, 0.0005, 0.00015],
             [0.0001, 0.00015, 0.0003]],
            index=assets,
            columns=assets
        )
        
        weights = mean_variance_optimize(
            expected_returns=expected_returns,
            cov=cov
        )
        
        assert isinstance(weights, pd.Series)
        assert len(weights) == 3
        assert all(weights.index == assets)
        # Weights should sum to 1
        assert abs(weights.sum() - 1.0) < 1e-6
        # All weights should be within bounds (default: -0.1 to 0.1)
        assert all(weights >= -0.1)
        assert all(weights <= 0.1)
    
    @pytest.mark.slow
    def test_mean_variance_optimize_with_prev_weights(self):
        """Test optimization with previous weights (turnover penalty)."""
        assets = ['AAPL', 'GOOGL', 'MSFT']
        expected_returns = pd.Series([0.001, 0.0008, 0.0012], index=assets)
        cov = pd.DataFrame(
            np.eye(3) * 0.0004,
            index=assets,
            columns=assets
        )
        prev_weights = pd.Series([0.05, 0.03, 0.02], index=assets)
        
        weights = mean_variance_optimize(
            expected_returns=expected_returns,
            cov=cov,
            prev_weights=prev_weights
        )
        
        assert isinstance(weights, pd.Series)
        assert abs(weights.sum() - 1.0) < 1e-6
    
    @pytest.mark.slow
    def test_mean_variance_optimize_with_custom_config(self):
        """Test optimization with custom configuration."""
        assets = ['AAPL', 'GOOGL']
        expected_returns = pd.Series([0.001, 0.0008], index=assets)
        cov = pd.DataFrame(
            [[0.0004, 0.0002],
             [0.0002, 0.0005]],
            index=assets,
            columns=assets
        )
        
        cfg = OptimizationConfig(
            max_weight=0.2,
            min_weight=-0.05,
            risk_aversion=2.0
        )
        
        weights = mean_variance_optimize(
            expected_returns=expected_returns,
            cov=cov,
            cfg=cfg
        )
        
        assert abs(weights.sum() - 1.0) < 1e-6
        assert all(weights <= 0.2)
        assert all(weights >= -0.05)
    
    @pytest.mark.slow
    def test_mean_variance_optimize_with_gross_constraint(self):
        """Test optimization with gross notional constraint."""
        assets = ['AAPL', 'GOOGL', 'MSFT']
        expected_returns = pd.Series([0.001, 0.0008, 0.0012], index=assets)
        cov = pd.DataFrame(
            np.eye(3) * 0.0004,
            index=assets,
            columns=assets
        )
        
        cfg = OptimizationConfig(target_gross=1.5)  # 150% gross exposure
        
        weights = mean_variance_optimize(
            expected_returns=expected_returns,
            cov=cov,
            cfg=cfg
        )
        
        # Gross notional should be <= 1.5
        gross = weights.abs().sum()
        assert gross <= 1.5 + 1e-6


class TestWeightsFromAlpha:
    """Test convenience function for converting alpha to weights."""
    
    @pytest.mark.slow
    def test_weights_from_alpha_basic(self, sample_returns_data):
        """Test converting alpha signal to weights."""
        assets = sample_returns_data.columns
        alpha = pd.Series([0.5, 0.3, -0.2, 0.1], index=assets)
        
        weights = weights_from_alpha(
            alpha=alpha,
            returns=sample_returns_data,
            cov_method='sample'
        )
        
        assert isinstance(weights, pd.Series)
        assert len(weights) == len(assets)
        assert abs(weights.sum() - 1.0) < 1e-6
    
    @pytest.mark.slow
    def test_weights_from_alpha_ledoit_wolf(self, sample_returns_data):
        """Test weights from alpha using Ledoit-Wolf covariance."""
        assets = sample_returns_data.columns
        alpha = pd.Series([0.5, 0.3, -0.2, 0.1], index=assets)
        
        weights = weights_from_alpha(
            alpha=alpha,
            returns=sample_returns_data,
            cov_method='ledoit_wolf'
        )
        
        assert isinstance(weights, pd.Series)
        assert abs(weights.sum() - 1.0) < 1e-6
    
    def test_weights_from_alpha_invalid_method(self, sample_returns_data):
        """Test error handling for invalid covariance method."""
        assets = sample_returns_data.columns
        alpha = pd.Series([0.5, 0.3, -0.2, 0.1], index=assets)
        
        with pytest.raises(ValueError, match="Unknown cov_method"):
            weights_from_alpha(
                alpha=alpha,
                returns=sample_returns_data,
                cov_method='invalid_method'
            )
