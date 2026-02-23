"""Advanced analytics including ML models, factor analysis, and Monte Carlo simulations."""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import scipy.optimize as sco
from scipy import stats

logger = logging.getLogger(__name__)


class PortfolioOptimizer:
    """Portfolio optimization using various methods."""
    
    @staticmethod
    def markowitz_optimization(
        returns: pd.DataFrame,
        risk_free_rate: float = 0.0,
        target_return: Optional[float] = None
    ) -> Dict:
        """
        Markowitz mean-variance optimization.
        
        Returns optimal portfolio weights that maximize Sharpe ratio.
        """
        try:
            mean_returns = returns.mean()
            cov_matrix = returns.cov()
            n_assets = len(mean_returns)
            
            # Objective function: negative Sharpe ratio (to minimize)
            def negative_sharpe(weights):
                portfolio_return = np.dot(weights, mean_returns)
                portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                sharpe = (portfolio_return - risk_free_rate) / portfolio_std if portfolio_std > 0 else 0
                return -sharpe
            
            # Constraints
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})  # Weights sum to 1
            
            # Bounds: weights between 0 and 1 (long-only)
            bounds = tuple((0, 1) for _ in range(n_assets))
            
            # Initial guess: equal weights
            initial_weights = np.array([1.0 / n_assets] * n_assets)
            
            # Optimize
            result = sco.minimize(
                negative_sharpe,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if not result.success:
                logger.warning("Markowitz optimization did not converge")
                return {"error": "Optimization failed"}
            
            optimal_weights = result.x
            portfolio_return = np.dot(optimal_weights, mean_returns)
            portfolio_std = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
            sharpe = (portfolio_return - risk_free_rate) / portfolio_std if portfolio_std > 0 else 0
            
            return {
                "weights": dict(zip(returns.columns, optimal_weights)),
                "expected_return": float(portfolio_return),
                "expected_volatility": float(portfolio_std),
                "sharpe_ratio": float(sharpe),
                "method": "markowitz"
            }
        except Exception as e:
            logger.error(f"Error in Markowitz optimization: {e}", exc_info=True)
            return {"error": str(e)}
    
    @staticmethod
    def risk_parity_optimization(returns: pd.DataFrame) -> Dict:
        """
        Risk parity optimization - equal risk contribution from each asset.
        """
        try:
            cov_matrix = returns.cov()
            n_assets = len(cov_matrix)
            
            def risk_contribution(weights):
                portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                marginal_contrib = np.dot(cov_matrix, weights) / portfolio_vol if portfolio_vol > 0 else np.zeros(n_assets)
                contrib = weights * marginal_contrib
                return contrib
            
            def objective(weights):
                contrib = risk_contribution(weights)
                # Minimize sum of squared differences from equal contribution
                target_contrib = np.ones(n_assets) / n_assets
                return np.sum((contrib - target_contrib) ** 2)
            
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            bounds = tuple((0, 1) for _ in range(n_assets))
            initial_weights = np.array([1.0 / n_assets] * n_assets)
            
            result = sco.minimize(
                objective,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if not result.success:
                return {"error": "Optimization failed"}
            
            optimal_weights = result.x
            portfolio_return = np.dot(optimal_weights, returns.mean())
            portfolio_std = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
            
            return {
                "weights": dict(zip(returns.columns, optimal_weights)),
                "expected_return": float(portfolio_return),
                "expected_volatility": float(portfolio_std),
                "method": "risk_parity"
            }
        except Exception as e:
            logger.error(f"Error in risk parity optimization: {e}", exc_info=True)
            return {"error": str(e)}


class FactorAnalyzer:
    """Factor analysis and attribution."""
    
    @staticmethod
    def fama_french_analysis(
        portfolio_returns: pd.Series,
        market_returns: pd.Series,
        risk_free_rate: pd.Series
    ) -> Dict:
        """
        Fama-French three-factor model analysis.
        
        Returns alpha, beta, and factor loadings.
        """
        try:
            # Calculate excess returns
            portfolio_excess = portfolio_returns - risk_free_rate
            market_excess = market_returns - risk_free_rate
            
            # Simple regression: portfolio = alpha + beta * market
            # For full Fama-French, you'd need SMB and HML factors
            X = market_excess.values.reshape(-1, 1)
            y = portfolio_excess.values
            
            # Add intercept
            X = np.column_stack([np.ones(len(X)), X])
            
            # OLS regression
            coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
            alpha = coeffs[0]
            beta = coeffs[1]
            
            # Calculate R-squared
            y_pred = X @ coeffs
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            return {
                "alpha": float(alpha),
                "beta": float(beta),
                "r_squared": float(r_squared),
                "alpha_annualized": float(alpha * 252),
            }
        except Exception as e:
            logger.error(f"Error in Fama-French analysis: {e}", exc_info=True)
            return {"error": str(e)}
    
    @staticmethod
    def style_analysis(
        portfolio_returns: pd.Series,
        style_returns: pd.DataFrame
    ) -> Dict:
        """
        Style analysis - determine portfolio style based on factor returns.
        
        Returns style weights (e.g., growth vs value, large cap vs small cap).
        """
        try:
            # Constrained regression: portfolio = sum(weights * style_factors)
            # Constraints: weights sum to 1, all >= 0
            
            n_styles = len(style_returns.columns)
            
            def objective(weights):
                portfolio_pred = np.dot(style_returns.values, weights)
                return np.sum((portfolio_returns.values - portfolio_pred) ** 2)
            
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            bounds = tuple((0, 1) for _ in range(n_styles))
            initial_weights = np.array([1.0 / n_styles] * n_styles)
            
            result = sco.minimize(
                objective,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if not result.success:
                return {"error": "Style analysis failed"}
            
            style_weights = result.x
            tracking_error = np.sqrt(result.fun / len(portfolio_returns))
            
            return {
                "style_weights": dict(zip(style_returns.columns, style_weights)),
                "tracking_error": float(tracking_error),
                "r_squared": float(1 - (result.fun / np.var(portfolio_returns.values)))
            }
        except Exception as e:
            logger.error(f"Error in style analysis: {e}", exc_info=True)
            return {"error": str(e)}


class MonteCarloSimulator:
    """Monte Carlo simulation for scenario analysis."""
    
    @staticmethod
    def simulate_returns(
        historical_returns: pd.Series,
        num_simulations: int = 10000,
        num_periods: int = 252,
        initial_value: float = 100000
    ) -> Dict:
        """
        Monte Carlo simulation of portfolio returns.
        
        Returns distribution of final values and statistics.
        """
        try:
            mean_return = historical_returns.mean()
            std_return = historical_returns.std()
            
            # Generate random returns
            random_returns = np.random.normal(
                mean_return,
                std_return,
                (num_simulations, num_periods)
            )
            
            # Calculate cumulative returns
            cumulative_returns = (1 + random_returns).cumprod(axis=1)
            final_values = initial_value * cumulative_returns[:, -1]
            
            # Calculate statistics
            mean_final = np.mean(final_values)
            median_final = np.median(final_values)
            std_final = np.std(final_values)
            var_95 = np.percentile(final_values, 5)
            var_99 = np.percentile(final_values, 1)
            
            return {
                "mean_final_value": float(mean_final),
                "median_final_value": float(median_final),
                "std_final_value": float(std_final),
                "var_95": float(var_95),
                "var_99": float(var_99),
                "percentiles": {
                    "p1": float(np.percentile(final_values, 1)),
                    "p5": float(np.percentile(final_values, 5)),
                    "p25": float(np.percentile(final_values, 25)),
                    "p50": float(np.percentile(final_values, 50)),
                    "p75": float(np.percentile(final_values, 75)),
                    "p95": float(np.percentile(final_values, 95)),
                    "p99": float(np.percentile(final_values, 99)),
                },
                "num_simulations": num_simulations,
                "num_periods": num_periods
            }
        except Exception as e:
            logger.error(f"Error in Monte Carlo simulation: {e}", exc_info=True)
            return {"error": str(e)}
    
    @staticmethod
    def stress_test(
        portfolio_returns: pd.Series,
        stress_scenarios: List[Dict[str, float]]
    ) -> Dict:
        """
        Stress testing with historical or hypothetical scenarios.
        
        stress_scenarios: List of dicts with keys like {"market_shock": -0.20, "volatility_spike": 0.50}
        """
        try:
            results = {}
            
            for scenario in stress_scenarios:
                scenario_name = scenario.get("name", "scenario")
                market_shock = scenario.get("market_shock", 0.0)
                volatility_multiplier = scenario.get("volatility_multiplier", 1.0)
                
                # Apply shock to returns
                shocked_returns = portfolio_returns * (1 + market_shock)
                shocked_volatility = shocked_returns.std() * volatility_multiplier
                
                # Calculate impact
                portfolio_value = 100000  # Base value
                final_value = portfolio_value * (1 + shocked_returns.mean()) ** 252
                
                results[scenario_name] = {
                    "final_value": float(final_value),
                    "return_impact": float(shocked_returns.mean() * 252),
                    "volatility_impact": float(shocked_volatility * np.sqrt(252)),
                    "drawdown_estimate": float(abs(market_shock))
                }
            
            return results
        except Exception as e:
            logger.error(f"Error in stress test: {e}", exc_info=True)
            return {"error": str(e)}


class AttributionAnalyzer:
    """Performance attribution analysis."""
    
    @staticmethod
    def sector_attribution(
        positions: pd.DataFrame,
        sector_returns: pd.DataFrame
    ) -> Dict:
        """
        Analyze performance attribution by sector.
        
        positions: DataFrame with columns: symbol, quantity, market_value, sector
        sector_returns: DataFrame with sector returns indexed by date
        """
        try:
            # Group positions by sector
            sector_allocation = positions.groupby('sector')['market_value'].sum()
            total_value = sector_allocation.sum()
            sector_weights = sector_allocation / total_value
            
            # Calculate sector contributions
            sector_contributions = {}
            for sector, weight in sector_weights.items():
                if sector in sector_returns.columns:
                    sector_return = sector_returns[sector].mean()
                    contribution = weight * sector_return
                    sector_contributions[sector] = {
                        "weight": float(weight),
                        "return": float(sector_return),
                        "contribution": float(contribution)
                    }
            
            return {
                "sector_allocations": dict(sector_weights),
                "sector_contributions": sector_contributions,
                "total_attributed": sum(c["contribution"] for c in sector_contributions.values())
            }
        except Exception as e:
            logger.error(f"Error in sector attribution: {e}", exc_info=True)
            return {"error": str(e)}
    
    @staticmethod
    def factor_attribution(
        portfolio_returns: pd.Series,
        factor_returns: pd.DataFrame
    ) -> Dict:
        """
        Factor-based performance attribution.
        
        Decomposes portfolio returns into factor contributions.
        """
        try:
            # Regression: portfolio = sum(factor_loadings * factors) + alpha
            X = factor_returns.values
            y = portfolio_returns.values
            
            # Add intercept for alpha
            X = np.column_stack([np.ones(len(X)), X])
            
            # OLS regression
            coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
            alpha = coeffs[0]
            factor_loadings = coeffs[1:]
            
            # Calculate factor contributions
            factor_contributions = {}
            for i, factor_name in enumerate(factor_returns.columns):
                factor_contribution = factor_loadings[i] * factor_returns[factor_name].mean()
                factor_contributions[factor_name] = {
                    "loading": float(factor_loadings[i]),
                    "contribution": float(factor_contribution)
                }
            
            return {
                "alpha": float(alpha),
                "alpha_annualized": float(alpha * 252),
                "factor_contributions": factor_contributions,
                "total_factor_contribution": sum(c["contribution"] for c in factor_contributions.values())
            }
        except Exception as e:
            logger.error(f"Error in factor attribution: {e}", exc_info=True)
            return {"error": str(e)}


class RegimeDetector:
    """Detect market regimes (bull/bear markets)."""
    
    @staticmethod
    def detect_regime(
        returns: pd.Series,
        lookback_window: int = 60
    ) -> Dict:
        """
        Detect current market regime based on recent returns.
        
        Returns: "bull", "bear", or "neutral"
        """
        try:
            recent_returns = returns.tail(lookback_window)
            mean_return = recent_returns.mean()
            volatility = recent_returns.std()
            
            # Simple classification
            if mean_return > 0.001 and volatility < 0.02:  # Positive returns, low vol
                regime = "bull"
            elif mean_return < -0.001:  # Negative returns
                regime = "bear"
            else:
                regime = "neutral"
            
            return {
                "regime": regime,
                "mean_return": float(mean_return),
                "volatility": float(volatility),
                "confidence": float(abs(mean_return) / volatility) if volatility > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error in regime detection: {e}", exc_info=True)
            return {"error": str(e)}


class AnomalyDetector:
    """Detect anomalies in trading patterns."""
    
    @staticmethod
    def detect_anomalies(
        returns: pd.Series,
        threshold_sigma: float = 3.0
    ) -> Dict:
        """
        Detect anomalous returns using statistical methods.
        
        Returns outliers beyond threshold_sigma standard deviations.
        """
        try:
            mean_return = returns.mean()
            std_return = returns.std()
            
            # Z-scores
            z_scores = (returns - mean_return) / std_return if std_return > 0 else pd.Series([0] * len(returns))
            
            # Find anomalies
            anomalies = abs(z_scores) > threshold_sigma
            anomaly_dates = returns[anomalies].index.tolist()
            anomaly_values = returns[anomalies].values.tolist()
            
            return {
                "num_anomalies": int(anomalies.sum()),
                "anomaly_dates": [str(d) for d in anomaly_dates],
                "anomaly_values": [float(v) for v in anomaly_values],
                "threshold_sigma": threshold_sigma,
                "mean": float(mean_return),
                "std": float(std_return)
            }
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}", exc_info=True)
            return {"error": str(e)}
