"""Risk analytics: VaR, CVaR, and portfolio risk metrics."""
from typing import Optional
import numpy as np
import pandas as pd


def historical_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR) using historical simulation.
    
    Args:
        returns: Return time series
        confidence_level: Confidence level (e.g., 0.95 for 95% VaR)
    
    Returns:
        VaR as a negative return (loss)
    """
    if len(returns) == 0:
        return 0.0
    
    percentile = (1 - confidence_level) * 100
    var = np.percentile(returns, percentile)
    return float(var)


def parametric_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR) using parametric method (assumes normal distribution).
    
    Args:
        returns: Return time series
        confidence_level: Confidence level (e.g., 0.95 for 95% VaR)
    
    Returns:
        VaR as a negative return (loss)
    """
    if len(returns) == 0:
        return 0.0
    
    mean = returns.mean()
    std = returns.std()
    
    # Z-score for confidence level
    from scipy import stats
    z_score = stats.norm.ppf(1 - confidence_level)
    
    var = mean + z_score * std
    return float(var)


def conditional_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
    """
    Calculate Conditional VaR (CVaR) / Expected Shortfall.
    
    Average of returns below the VaR threshold.
    
    Args:
        returns: Return time series
        confidence_level: Confidence level (e.g., 0.95 for 95% CVaR)
    
    Returns:
        CVaR as a negative return (loss)
    """
    if len(returns) == 0:
        return 0.0
    
    var = historical_var(returns, confidence_level)
    tail_returns = returns[returns <= var]
    
    if len(tail_returns) == 0:
        return float(var)
    
    cvar = tail_returns.mean()
    return float(cvar)


def portfolio_metrics(
    returns: pd.Series,
    confidence_level: float = 0.95,
    benchmark_returns: Optional[pd.Series] = None,
) -> dict:
    """
    Calculate comprehensive portfolio risk metrics.
    
    Args:
        returns: Portfolio return time series
        confidence_level: Confidence level for VaR/CVaR
        benchmark_returns: Optional benchmark returns for beta calculation
    
    Returns:
        Dictionary of risk metrics
    """
    if len(returns) == 0:
        return {
            'var': 0.0,
            'cvar': 0.0,
            'volatility': 0.0,
            'beta': 0.0,
            'alpha': 0.0,
        }
    
    var = historical_var(returns, confidence_level)
    cvar = conditional_var(returns, confidence_level)
    volatility = float(returns.std() * np.sqrt(252))  # Annualized
    
    beta = 0.0
    alpha = 0.0
    
    if benchmark_returns is not None and len(benchmark_returns) > 0:
        # Align returns
        common_idx = returns.index.intersection(benchmark_returns.index)
        if len(common_idx) > 10:
            aligned_returns = returns.loc[common_idx]
            aligned_benchmark = benchmark_returns.loc[common_idx]
            
            # Calculate beta
            covariance = np.cov(aligned_returns, aligned_benchmark)[0, 1]
            benchmark_variance = aligned_benchmark.var()
            
            if benchmark_variance > 0:
                beta = float(covariance / benchmark_variance)
            
            # Calculate alpha (annualized)
            portfolio_mean = aligned_returns.mean() * 252
            benchmark_mean = aligned_benchmark.mean() * 252
            alpha = float(portfolio_mean - beta * benchmark_mean)
    
    return {
        'var': var,
        'cvar': cvar,
        'volatility': volatility,
        'beta': beta,
        'alpha': alpha,
    }
