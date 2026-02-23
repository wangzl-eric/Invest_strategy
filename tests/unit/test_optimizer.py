"""Unit tests for portfolio optimizer."""
import pytest
import pandas as pd
import numpy as np
from portfolio.optimizer import (
    OptimizationConfig,
    mean_variance_optimize,
    weights_from_alpha,
)


class TestOptimizationConfig:
    """Tests for OptimizationConfig."""
    
    def test_default_config(self):
        """Test default optimization config."""
        cfg = OptimizationConfig()
        
        assert cfg.risk_aversion == 1.0
        assert cfg.turnover_aversion == 0.0
        assert cfg.max_weight == 0.10
        assert cfg.min_weight == -0.10
        assert cfg.target_gross is None
    
    def test_custom_config(self):
        """Test custom optimization config."""
        cfg = OptimizationConfig(
            risk_aversion=2.0,
            turnover_aversion=0.1,
            max_weight=0.20,
            min_weight=-0.20,
            target_gross=1.5
        )
        
        assert cfg.risk_aversion == 2.0
        assert cfg.turnover_aversion == 0.1
        assert cfg.max_weight == 0.20
        assert cfg.min_weight == -0.20
        assert cfg.target_gross == 1.5


class TestMeanVarianceOptimize:
    """Tests for mean-variance optimization."""
    
    def test_basic_optimization(self):
        """Test basic mean-variance optimization."""
        assets = ["AAPL", "MSFT", "GOOGL"]
        expected_returns = pd.Series([0.001, 0.0015, 0.0008], index=assets)
        
        # Simple covariance matrix
        cov = pd.DataFrame(
            [[0.0004, 0.0001, 0.0001],
             [0.0001, 0.0004, 0.0001],
             [0.0001, 0.0001, 0.0004]],
            index=assets,
            columns=assets
        )
        
        weights = mean_variance_optimize(
            expected_returns=expected_returns,
            cov=cov
        )
        
        assert isinstance(weights, pd.Series)
        assert len(weights) == 3
        assert all(asset in weights.index for asset in assets)
        # Weights should sum to 1 (or very close due to numerical precision)
        assert abs(weights.sum() - 1.0) < 1e-6
        # Weights should be within bounds
        assert all(weights >= -0.10)
        assert all(weights <= 0.10)
    
    def test_optimization_with_prev_weights(self):
        """Test optimization with previous weights (turnover penalty)."""
        assets = ["AAPL", "MSFT", "GOOGL"]
        expected_returns = pd.Series([0.001, 0.0015, 0.0008], index=assets)
        cov = pd.DataFrame(
            [[0.0004, 0.0001, 0.0001],
             [0.0001, 0.0004, 0.0001],
             [0.0001, 0.0001, 0.0004]],
            index=assets,
            columns=assets
        )
        prev_weights = pd.Series([0.33, 0.33, 0.34], index=assets)
        
        cfg = OptimizationConfig(turnover_aversion=0.5)
        weights = mean_variance_optimize(
            expected_returns=expected_returns,
            cov=cov,
            prev_weights=prev_weights,
            cfg=cfg
        )
        
        assert isinstance(weights, pd.Series)
        assert abs(weights.sum() - 1.0) < 1e-6
    
    def test_optimization_with_target_gross(self):
        """Test optimization with target gross exposure constraint."""
        assets = ["AAPL", "MSFT", "GOOGL"]
        expected_returns = pd.Series([0.001, 0.0015, 0.0008], index=assets)
        cov = pd.DataFrame(
            [[0.0004, 0.0001, 0.0001],
             [0.0001, 0.0004, 0.0001],
             [0.0001, 0.0001, 0.0004]],
            index=assets,
            columns=assets
        )
        
        cfg = OptimizationConfig(target_gross=1.5)
        weights = mean_variance_optimize(
            expected_returns=expected_returns,
            cov=cov,
            cfg=cfg
        )
        
        assert isinstance(weights, pd.Series)
        gross_exposure = weights.abs().sum()
        assert gross_exposure <= 1.5 + 1e-6  # Allow small numerical error
    
    def test_optimization_requires_cvxpy(self, monkeypatch):
        """Test that optimization requires cvxpy."""
        # This test would require mocking cvxpy import
        # For now, we assume cvxpy is available
        pass


class TestWeightsFromAlpha:
    """Tests for weights_from_alpha convenience function."""
    
    def test_weights_from_alpha_ledoit_wolf(self, sample_returns_df):
        """Test weights from alpha using Ledoit-Wolf covariance."""
        alpha = pd.Series([0.001, 0.0015, 0.0008], index=sample_returns_df.columns)
        
        weights = weights_from_alpha(
            alpha=alpha,
            returns=sample_returns_df,
            cov_method="ledoit_wolf"
        )
        
        assert isinstance(weights, pd.Series)
        assert len(weights) == len(alpha)
        assert abs(weights.sum() - 1.0) < 1e-6
    
    def test_weights_from_alpha_sample_cov(self, sample_returns_df):
        """Test weights from alpha using sample covariance."""
        alpha = pd.Series([0.001, 0.0015, 0.0008], index=sample_returns_df.columns)
        
        weights = weights_from_alpha(
            alpha=alpha,
            returns=sample_returns_df,
            cov_method="sample"
        )
        
        assert isinstance(weights, pd.Series)
        assert len(weights) == len(alpha)
        assert abs(weights.sum() - 1.0) < 1e-6
    
    def test_weights_from_alpha_invalid_method(self, sample_returns_df):
        """Test weights_from_alpha with invalid covariance method."""
        alpha = pd.Series([0.001, 0.0015, 0.0008], index=sample_returns_df.columns)
        
        with pytest.raises(ValueError, match="Unknown cov_method"):
            weights_from_alpha(
                alpha=alpha,
                returns=sample_returns_df,
                cov_method="invalid_method"
            )
