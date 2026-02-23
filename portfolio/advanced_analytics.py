"""Advanced analytics: ML portfolio optimization, factor analysis, attribution, Monte Carlo."""
from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

logger = logging.getLogger(__name__)


# =============================================================================
# Portfolio Optimization Models
# =============================================================================

@dataclass
class OptimizationResult:
    """Result of portfolio optimization."""
    weights: pd.Series
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    optimization_method: str
    constraints_satisfied: bool
    optimization_status: str


def markowitz_optimize(
    expected_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_free_rate: float = 0.0,
    target_return: Optional[float] = None,
    max_weight: float = 1.0,
    min_weight: float = 0.0,
    long_only: bool = True,
) -> OptimizationResult:
    """
    Markowitz mean-variance optimization.
    
    Maximizes Sharpe ratio or minimizes variance for target return.
    
    Args:
        expected_returns: Expected returns for each asset
        cov_matrix: Covariance matrix
        risk_free_rate: Risk-free rate for Sharpe calculation
        target_return: If provided, optimize for this return (min variance)
        max_weight: Maximum weight per asset
        min_weight: Minimum weight per asset
        long_only: If True, min_weight >= 0
    
    Returns:
        OptimizationResult with optimal weights
    """
    try:
        import cvxpy as cp
    except ImportError:
        raise ImportError("cvxpy is required for portfolio optimization")
    
    assets = expected_returns.index
    n = len(assets)
    
    # Ensure covariance matrix is aligned
    cov_matrix = cov_matrix.reindex(index=assets, columns=assets)
    
    # Add small ridge for numerical stability
    cov_matrix = cov_matrix + 1e-8 * np.eye(n)
    
    w = cp.Variable(n)
    mu = expected_returns.values
    Sigma = cov_matrix.values
    
    # Portfolio return and variance
    portfolio_return = mu @ w
    portfolio_variance = cp.quad_form(w, Sigma)
    portfolio_volatility = cp.sqrt(portfolio_variance)
    
    # Sharpe ratio
    sharpe = (portfolio_return - risk_free_rate) / portfolio_volatility
    
    # Constraints
    constraints = [cp.sum(w) == 1.0]
    
    if long_only:
        constraints.append(w >= max(min_weight, 0.0))
    else:
        constraints.append(w >= min_weight)
    
    constraints.append(w <= max_weight)
    
    if target_return is not None:
        # Minimize variance for target return
        constraints.append(portfolio_return >= target_return)
        objective = cp.Minimize(portfolio_variance)
    else:
        # Maximize Sharpe ratio
        objective = cp.Maximize(sharpe)
    
    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.OSQP, verbose=False)
    
    if w.value is None:
        raise RuntimeError(f"Optimization failed: {prob.status}")
    
    weights = pd.Series(w.value, index=assets)
    weights[abs(weights) < 1e-8] = 0.0  # Clean numerical noise
    
    # Calculate metrics
    exp_return = float(weights @ expected_returns)
    exp_vol = float(np.sqrt(weights @ cov_matrix @ weights))
    sharpe_ratio = float((exp_return - risk_free_rate) / exp_vol) if exp_vol > 0 else 0.0
    
    return OptimizationResult(
        weights=weights,
        expected_return=exp_return,
        expected_volatility=exp_vol,
        sharpe_ratio=sharpe_ratio,
        optimization_method="markowitz",
        constraints_satisfied=prob.status == "optimal",
        optimization_status=prob.status,
    )


def black_litterman_optimize(
    market_caps: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_aversion: float = 3.0,
    views: Optional[Dict[str, float]] = None,
    view_confidences: Optional[Dict[str, float]] = None,
    tau: float = 0.05,
    risk_free_rate: float = 0.0,
) -> OptimizationResult:
    """
    Black-Litterman portfolio optimization.
    
    Combines market equilibrium with investor views.
    
    Args:
        market_caps: Market capitalization weights (equilibrium portfolio)
        cov_matrix: Covariance matrix
        risk_aversion: Risk aversion parameter (typically 2-4)
        views: Dict of {asset: expected_return} for views
        view_confidences: Dict of {asset: confidence} (0-1, higher = more confident)
        tau: Scaling factor for uncertainty (typically 0.01-0.05)
        risk_free_rate: Risk-free rate
    
    Returns:
        OptimizationResult with optimal weights
    """
    try:
        import cvxpy as cp
    except ImportError:
        raise ImportError("cvxpy is required for portfolio optimization")
    
    assets = market_caps.index
    n = len(assets)
    
    # Ensure covariance matrix is aligned
    cov_matrix = cov_matrix.reindex(index=assets, columns=assets)
    cov_matrix = cov_matrix + 1e-8 * np.eye(n)
    
    # Market equilibrium returns (reverse optimization)
    market_weights = market_caps / market_caps.sum()
    pi = risk_aversion * cov_matrix @ market_weights  # Implied returns
    
    # If no views, return market portfolio
    if not views:
        weights = market_weights
        exp_return = float(weights @ pi)
        exp_vol = float(np.sqrt(weights @ cov_matrix @ weights))
        sharpe = float((exp_return - risk_free_rate) / exp_vol) if exp_vol > 0 else 0.0
        
        return OptimizationResult(
            weights=weights,
            expected_return=exp_return,
            expected_volatility=exp_vol,
            sharpe_ratio=sharpe,
            optimization_method="black_litterman",
            constraints_satisfied=True,
            optimization_status="optimal",
        )
    
    # Build view matrix P and view vector Q
    view_assets = list(views.keys())
    k = len(view_assets)
    
    P = np.zeros((k, n))
    Q = np.zeros(k)
    Omega = np.zeros((k, k))  # Uncertainty matrix
    
    for i, asset in enumerate(view_assets):
        if asset not in assets:
            continue
        idx = assets.get_loc(asset)
        P[i, idx] = 1.0
        Q[i] = views[asset]
        
        # Confidence: higher confidence = lower uncertainty
        confidence = view_confidences.get(asset, 0.5) if view_confidences else 0.5
        # Omega diagonal: lower confidence = higher uncertainty
        Omega[i, i] = tau * (1.0 - confidence) * (P[i] @ cov_matrix @ P[i])
    
    # Black-Litterman formula
    tau_Sigma = tau * cov_matrix
    M1 = np.linalg.inv(tau_Sigma)
    M2 = P.T @ np.linalg.inv(Omega) @ P
    M3 = M1 @ pi
    M4 = P.T @ np.linalg.inv(Omega) @ Q
    
    mu_bl = np.linalg.inv(M1 + M2) @ (M3 + M4)
    mu_bl = pd.Series(mu_bl, index=assets)
    
    # Now optimize with BL expected returns
    return markowitz_optimize(
        expected_returns=mu_bl,
        cov_matrix=cov_matrix,
        risk_free_rate=risk_free_rate,
    )


def risk_parity_optimize(
    cov_matrix: pd.DataFrame,
    target_risk: Optional[float] = None,
) -> OptimizationResult:
    """
    Risk parity optimization (equal risk contribution).
    
    Each asset contributes equally to portfolio risk.
    
    Args:
        cov_matrix: Covariance matrix
        target_risk: Target portfolio volatility (if None, unconstrained)
    
    Returns:
        OptimizationResult with optimal weights
    """
    assets = cov_matrix.index
    n = len(assets)
    
    # Add small ridge for numerical stability
    cov_matrix = cov_matrix + 1e-8 * np.eye(n)
    Sigma = cov_matrix.values
    
    def risk_contribution(w):
        """Calculate risk contribution of each asset."""
        w = np.array(w)
        portfolio_vol = np.sqrt(w @ Sigma @ w)
        if portfolio_vol < 1e-8:
            return np.ones(n) / n
        
        # Marginal contribution to risk
        marginal_contrib = Sigma @ w / portfolio_vol
        # Risk contribution
        contrib = w * marginal_contrib
        return contrib / contrib.sum()
    
    def objective(w):
        """Minimize sum of squared differences from equal contribution."""
        contrib = risk_contribution(w)
        target = np.ones(n) / n
        return np.sum((contrib - target) ** 2)
    
    # Constraints
    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},  # Sum to 1
    ]
    
    if target_risk is not None:
        constraints.append({
            'type': 'eq',
            'fun': lambda w: np.sqrt(w @ Sigma @ w) - target_risk
        })
    
    # Bounds: long-only
    bounds = [(0.0, 1.0) for _ in range(n)]
    
    # Initial guess: equal weights
    w0 = np.ones(n) / n
    
    # Optimize
    result = minimize(
        objective,
        w0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'maxiter': 1000}
    )
    
    if not result.success:
        raise RuntimeError(f"Risk parity optimization failed: {result.message}")
    
    weights = pd.Series(result.x, index=assets)
    weights[abs(weights) < 1e-8] = 0.0
    
    # Calculate metrics (use sample mean for expected return)
    exp_vol = float(np.sqrt(weights @ cov_matrix @ weights))
    # For risk parity, we don't optimize return, so use zero or sample mean
    exp_return = 0.0  # Risk parity doesn't optimize return
    
    return OptimizationResult(
        weights=weights,
        expected_return=exp_return,
        expected_volatility=exp_vol,
        sharpe_ratio=0.0,  # Not applicable for risk parity
        optimization_method="risk_parity",
        constraints_satisfied=result.success,
        optimization_status=result.message,
    )


# =============================================================================
# Factor Analysis
# =============================================================================

@dataclass
class FactorAnalysisResult:
    """Result of factor analysis."""
    factor_loadings: pd.DataFrame  # Assets x Factors
    factor_returns: pd.Series  # Time series of factor returns
    r_squared: pd.Series  # R-squared per asset
    residuals: pd.DataFrame  # Residual returns
    factor_names: List[str]


def fama_french_analysis(
    returns: pd.DataFrame,
    market_returns: pd.Series,
    hml: Optional[pd.Series] = None,  # High minus Low (value)
    smb: Optional[pd.Series] = None,  # Small minus Big (size)
    umd: Optional[pd.Series] = None,  # Up minus Down (momentum)
) -> FactorAnalysisResult:
    """
    Fama-French factor model analysis.
    
    Regresses asset returns on market, HML, SMB, and optionally UMD factors.
    
    Args:
        returns: Asset returns (time x assets)
        market_returns: Market returns (time series)
        hml: HML factor returns (optional)
        smb: SMB factor returns (optional)
        umd: UMD factor returns (optional)
    
    Returns:
        FactorAnalysisResult with loadings and statistics
    """
    from sklearn.linear_model import LinearRegression
    
    # Align time indices
    common_idx = returns.index.intersection(market_returns.index)
    if len(common_idx) < 10:
        raise ValueError("Insufficient overlapping data for factor analysis")
    
    returns_aligned = returns.loc[common_idx]
    market_aligned = market_returns.loc[common_idx]
    
    # Build factor matrix
    factors = pd.DataFrame({'Market': market_aligned}, index=common_idx)
    
    if hml is not None:
        hml_aligned = hml.reindex(common_idx).dropna()
        if len(hml_aligned) > 0:
            factors['HML'] = hml_aligned
    
    if smb is not None:
        smb_aligned = smb.reindex(common_idx).dropna()
        if len(smb_aligned) > 0:
            factors['SMB'] = smb_aligned
    
    if umd is not None:
        umd_aligned = umd.reindex(common_idx).dropna()
        if len(umd_aligned) > 0:
            factors['UMD'] = umd_aligned
    
    # Remove rows with any NaN
    factors = factors.dropna()
    returns_aligned = returns_aligned.loc[factors.index]
    
    if len(factors) < 10:
        raise ValueError("Insufficient data after alignment")
    
    # Regress each asset on factors
    loadings = {}
    r_squared = {}
    residuals_dict = {}
    
    for asset in returns_aligned.columns:
        y = returns_aligned[asset].values
        X = factors.values
        
        model = LinearRegression()
        model.fit(X, y)
        
        loadings[asset] = pd.Series(model.coef_, index=factors.columns)
        r_squared[asset] = model.score(X, y)
        
        y_pred = model.predict(X)
        residuals_dict[asset] = y - y_pred
    
    factor_loadings = pd.DataFrame(loadings).T
    r_squared_series = pd.Series(r_squared)
    residuals = pd.DataFrame(residuals_dict, index=factors.index)
    
    # Factor returns (average of factor values over time)
    factor_returns = factors.mean()
    
    return FactorAnalysisResult(
        factor_loadings=factor_loadings,
        factor_returns=factor_returns,
        r_squared=r_squared_series,
        residuals=residuals,
        factor_names=list(factors.columns),
    )


def style_analysis(
    portfolio_returns: pd.Series,
    style_benchmarks: pd.DataFrame,
    constraint_long_only: bool = True,
) -> Dict[str, Any]:
    """
    Style analysis (Sharpe style regression).
    
    Decomposes portfolio returns into style benchmark exposures.
    
    Args:
        portfolio_returns: Portfolio return time series
        style_benchmarks: Style benchmark returns (time x styles)
        constraint_long_only: If True, weights sum to 1 and are non-negative
    
    Returns:
        Dict with style weights, R-squared, and statistics
    """
    from sklearn.linear_model import LinearRegression
    
    # Align indices
    common_idx = portfolio_returns.index.intersection(style_benchmarks.index)
    if len(common_idx) < 10:
        raise ValueError("Insufficient overlapping data")
    
    y = portfolio_returns.loc[common_idx].values
    X = style_benchmarks.loc[common_idx].values
    
    if constraint_long_only:
        # Constrained regression: weights sum to 1, all >= 0
        from scipy.optimize import minimize
        
        def objective(w):
            """Minimize sum of squared residuals."""
            return np.sum((y - X @ w) ** 2)
        
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}
        ]
        bounds = [(0.0, 1.0) for _ in range(X.shape[1])]
        
        w0 = np.ones(X.shape[1]) / X.shape[1]
        result = minimize(objective, w0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if not result.success:
            raise RuntimeError(f"Style analysis optimization failed: {result.message}")
        
        weights = result.x
    else:
        # Unconstrained regression
        model = LinearRegression()
        model.fit(X, y)
        weights = model.coef_
        # Normalize to sum to 1
        weights = weights / weights.sum() if weights.sum() != 0 else weights
    
    style_weights = pd.Series(weights, index=style_benchmarks.columns)
    
    # Calculate R-squared
    y_pred = X @ weights
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    
    # Tracking error
    tracking_error = np.std(y - y_pred) * np.sqrt(252)  # Annualized
    
    return {
        'style_weights': style_weights,
        'r_squared': r_squared,
        'tracking_error': tracking_error,
        'residuals': pd.Series(y - y_pred, index=common_idx),
    }


# =============================================================================
# Attribution Analysis
# =============================================================================

@dataclass
class AttributionResult:
    """Result of performance attribution."""
    total_attribution: float
    factor_attribution: pd.Series  # Attribution by factor
    sector_attribution: Optional[pd.Series] = None
    region_attribution: Optional[pd.Series] = None
    security_attribution: Optional[pd.Series] = None


def factor_attribution(
    portfolio_returns: pd.Series,
    factor_loadings: pd.DataFrame,
    factor_returns: pd.Series,
    portfolio_weights: Optional[pd.Series] = None,
) -> AttributionResult:
    """
    Factor-based performance attribution.
    
    Attributes portfolio returns to factor exposures.
    
    Args:
        portfolio_returns: Portfolio return time series
        factor_loadings: Factor loadings (assets x factors)
        factor_returns: Factor returns (time x factors)
        portfolio_weights: Portfolio weights (if None, equal weights assumed)
    
    Returns:
        AttributionResult with factor contributions
    """
    # Align data
    common_assets = portfolio_returns.index.intersection(factor_loadings.index)
    if len(common_assets) == 0:
        common_assets = factor_loadings.index
    
    if portfolio_weights is None:
        portfolio_weights = pd.Series(1.0 / len(common_assets), index=common_assets)
    else:
        portfolio_weights = portfolio_weights.reindex(common_assets).fillna(0.0)
    
    # Portfolio factor exposure = weighted sum of asset loadings
    portfolio_exposure = (factor_loadings.loc[common_assets].T * portfolio_weights).T.sum()
    
    # Factor attribution = exposure * factor return
    factor_attrib = portfolio_exposure * factor_returns
    
    # Total attribution
    total_attrib = factor_attrib.sum()
    
    return AttributionResult(
        total_attribution=total_attrib,
        factor_attribution=factor_attrib,
        sector_attribution=None,
        region_attribution=None,
        security_attribution=None,
    )


def sector_attribution(
    portfolio_returns: pd.Series,
    sector_weights: pd.Series,
    sector_returns: pd.Series,
) -> AttributionResult:
    """
    Sector-based performance attribution.
    
    Attributes portfolio returns to sector exposures.
    
    Args:
        portfolio_returns: Portfolio return time series
        sector_weights: Portfolio weights by sector
        sector_returns: Sector returns
    
    Returns:
        AttributionResult with sector contributions
    """
    # Align sectors
    common_sectors = sector_weights.index.intersection(sector_returns.index)
    
    sector_attrib = sector_weights.loc[common_sectors] * sector_returns.loc[common_sectors]
    total_attrib = sector_attrib.sum()
    
    return AttributionResult(
        total_attribution=total_attrib,
        factor_attribution=pd.Series(),  # Not applicable
        sector_attribution=sector_attrib,
        region_attribution=None,
        security_attribution=None,
    )


def security_attribution(
    portfolio_returns: pd.Series,
    security_returns: pd.DataFrame,
    portfolio_weights: pd.Series,
) -> AttributionResult:
    """
    Security-level performance attribution.
    
    Attributes portfolio returns to individual security contributions.
    
    Args:
        portfolio_returns: Portfolio return time series
        security_returns: Security returns (time x securities)
        portfolio_weights: Portfolio weights by security
    
    Returns:
        AttributionResult with security contributions
    """
    # Align securities
    common_securities = portfolio_weights.index.intersection(security_returns.columns)
    
    # Calculate contribution = weight * return
    security_contrib = portfolio_weights.loc[common_securities] * security_returns[common_securities].mean()
    total_attrib = security_contrib.sum()
    
    return AttributionResult(
        total_attribution=total_attrib,
        factor_attribution=pd.Series(),
        sector_attribution=None,
        region_attribution=None,
        security_attribution=security_contrib,
    )


# =============================================================================
# Monte Carlo Simulations
# =============================================================================

@dataclass
class MonteCarloResult:
    """Result of Monte Carlo simulation."""
    simulated_returns: np.ndarray  # n_simulations x n_periods
    simulated_equity: np.ndarray  # n_simulations x n_periods
    percentiles: Dict[str, float]  # Percentiles of final equity
    probability_of_loss: float
    expected_final_value: float
    var_95: float
    cvar_95: float


def monte_carlo_simulation(
    initial_value: float,
    expected_return: float,
    volatility: float,
    n_simulations: int = 10000,
    n_periods: int = 252,
    random_seed: Optional[int] = None,
) -> MonteCarloResult:
    """
    Monte Carlo simulation for portfolio value.
    
    Simulates future portfolio values using geometric Brownian motion.
    
    Args:
        initial_value: Starting portfolio value
        expected_return: Annual expected return
        volatility: Annual volatility
        n_simulations: Number of simulation paths
        n_periods: Number of periods (days) to simulate
        random_seed: Random seed for reproducibility
    
    Returns:
        MonteCarloResult with simulation results
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # Daily parameters
    dt = 1.0 / 252.0  # Daily time step
    mu_daily = expected_return * dt
    sigma_daily = volatility * np.sqrt(dt)
    
    # Generate random shocks
    shocks = np.random.normal(0, 1, size=(n_simulations, n_periods))
    
    # Simulate returns (geometric Brownian motion)
    returns = mu_daily + sigma_daily * shocks
    
    # Calculate equity paths
    equity = np.zeros((n_simulations, n_periods + 1))
    equity[:, 0] = initial_value
    
    for t in range(n_periods):
        equity[:, t + 1] = equity[:, t] * np.exp(returns[:, t])
    
    # Calculate statistics
    final_values = equity[:, -1]
    
    percentiles = {
        'p5': float(np.percentile(final_values, 5)),
        'p25': float(np.percentile(final_values, 25)),
        'p50': float(np.percentile(final_values, 50)),
        'p75': float(np.percentile(final_values, 75)),
        'p95': float(np.percentile(final_values, 95)),
    }
    
    probability_of_loss = float(np.mean(final_values < initial_value))
    expected_final_value = float(np.mean(final_values))
    
    # VaR and CVaR (loss relative to initial)
    losses = initial_value - final_values
    var_95 = float(np.percentile(losses, 95))
    cvar_95 = float(np.mean(losses[losses >= var_95]))
    
    return MonteCarloResult(
        simulated_returns=returns,
        simulated_equity=equity,
        percentiles=percentiles,
        probability_of_loss=probability_of_loss,
        expected_final_value=expected_final_value,
        var_95=var_95,
        cvar_95=cvar_95,
    )


def monte_carlo_portfolio_simulation(
    initial_weights: pd.Series,
    expected_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    initial_value: float,
    n_simulations: int = 10000,
    n_periods: int = 252,
    rebalance_frequency: int = 21,  # Monthly rebalancing
    random_seed: Optional[int] = None,
) -> MonteCarloResult:
    """
    Monte Carlo simulation for multi-asset portfolio.
    
    Simulates portfolio value with multiple assets and rebalancing.
    
    Args:
        initial_weights: Initial portfolio weights
        expected_returns: Expected returns per asset
        cov_matrix: Covariance matrix
        initial_value: Starting portfolio value
        n_simulations: Number of simulation paths
        n_periods: Number of periods (days) to simulate
        rebalance_frequency: Rebalance every N periods (0 = no rebalancing)
        random_seed: Random seed for reproducibility
    
    Returns:
        MonteCarloResult with simulation results
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    assets = initial_weights.index
    n_assets = len(assets)
    
    # Ensure alignment
    expected_returns = expected_returns.reindex(assets).fillna(0.0)
    cov_matrix = cov_matrix.reindex(index=assets, columns=assets).fillna(0.0)
    cov_matrix = cov_matrix + 1e-8 * np.eye(n_assets)  # Add ridge
    
    # Daily parameters
    dt = 1.0 / 252.0
    mu_daily = expected_returns.values * dt
    Sigma_daily = cov_matrix.values * dt
    
    # Generate correlated random shocks
    L = np.linalg.cholesky(Sigma_daily)
    
    # Simulate
    equity = np.zeros((n_simulations, n_periods + 1))
    equity[:, 0] = initial_value
    
    weights = np.tile(initial_weights.values, (n_simulations, 1))
    
    for t in range(n_periods):
        # Generate correlated returns
        z = np.random.normal(0, 1, size=(n_simulations, n_assets))
        returns = mu_daily + (L @ z.T).T
        
        # Update equity
        portfolio_returns = np.sum(weights * returns, axis=1)
        equity[:, t + 1] = equity[:, t] * (1 + portfolio_returns)
        
        # Rebalance if needed
        if rebalance_frequency > 0 and (t + 1) % rebalance_frequency == 0:
            weights = np.tile(initial_weights.values, (n_simulations, 1))
    
    # Calculate statistics
    final_values = equity[:, -1]
    
    percentiles = {
        'p5': float(np.percentile(final_values, 5)),
        'p25': float(np.percentile(final_values, 25)),
        'p50': float(np.percentile(final_values, 50)),
        'p75': float(np.percentile(final_values, 75)),
        'p95': float(np.percentile(final_values, 95)),
    }
    
    probability_of_loss = float(np.mean(final_values < initial_value))
    expected_final_value = float(np.mean(final_values))
    
    losses = initial_value - final_values
    var_95 = float(np.percentile(losses, 95))
    cvar_95 = float(np.mean(losses[losses >= var_95]))
    
    # Average returns across simulations
    avg_returns = np.mean(equity[:, 1:] / equity[:, :-1] - 1, axis=0)
    
    return MonteCarloResult(
        simulated_returns=avg_returns.reshape(1, -1),  # Average path
        simulated_equity=equity,
        percentiles=percentiles,
        probability_of_loss=probability_of_loss,
        expected_final_value=expected_final_value,
        var_95=var_95,
        cvar_95=cvar_95,
    )
