"""API routes for advanced analytics: optimization, factor analysis, attribution, Monte Carlo."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
import pandas as pd
import numpy as np

from backend.database import get_db
from backend.models import Position, Trade, PnLHistory, AccountSnapshot
from backend.api.schemas import (
    OptimizationResponse,
    OptimizationWeightsResponse,
    FactorAnalysisResponse,
    FactorLoadingResponse,
    StyleAnalysisResponse,
    AttributionResponse,
    MonteCarloResponse,
    MonteCarloPercentilesResponse,
)
from backend.advanced_analytics import (
    PortfolioOptimizer,
    FactorAnalyzer,
    MonteCarloSimulator,
    AttributionAnalyzer,
    RegimeDetector,
    AnomalyDetector,
)
from backend.data_processor import DataProcessor

# Try to import from portfolio.advanced_analytics if available (for compatibility)
try:
    from portfolio.advanced_analytics import (
        markowitz_optimize,
        black_litterman_optimize,
        risk_parity_optimize,
        fama_french_analysis,
        style_analysis,
        factor_attribution,
        sector_attribution,
        security_attribution,
        monte_carlo_simulation,
        monte_carlo_portfolio_simulation,
    )
    HAS_PORTFOLIO_MODULE = True
except ImportError:
    HAS_PORTFOLIO_MODULE = False
    # Use our implementations as fallback
    optimizer = PortfolioOptimizer()
    factor_analyzer = FactorAnalyzer()
    mc_simulator = MonteCarloSimulator()
    attribution_analyzer = AttributionAnalyzer()

logger = logging.getLogger(__name__)

router = APIRouter()
data_processor = DataProcessor()


def get_position_returns(
    account_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = None,
) -> pd.DataFrame:
    """
    Get historical returns for each position from position snapshots.
    
    Returns DataFrame with date index and symbol columns (returns).
    Falls back to trade data if position snapshots are unavailable.
    """
    if db is None:
        from backend.database import get_db_context
        with get_db_context() as db_session:
            return _get_position_returns_impl(account_id, start_date, end_date, db_session)
    else:
        return _get_position_returns_impl(account_id, start_date, end_date, db)


def _get_position_returns_impl(
    account_id: str,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    db: Session,
) -> pd.DataFrame:
    """Internal implementation of get_position_returns."""
    # Try to get returns from position snapshots first
    query = db.query(Position).filter(Position.account_id == account_id)
    
    if start_date:
        query = query.filter(Position.timestamp >= start_date)
    if end_date:
        query = query.filter(Position.timestamp <= end_date)
    
    positions = query.order_by(Position.timestamp).all()
    
    if positions:
        # Group positions by timestamp and symbol
        positions_by_date = {}
        for pos in positions:
            date_key = pos.timestamp.date()
            if date_key not in positions_by_date:
                positions_by_date[date_key] = {}
            positions_by_date[date_key][pos.symbol] = pos
        
        if len(positions_by_date) >= 2:
            # Calculate returns from market price changes
            dates = sorted(positions_by_date.keys())
            all_symbols = set()
            for date_positions in positions_by_date.values():
                all_symbols.update(date_positions.keys())
            
            returns_data = []
            for i in range(1, len(dates)):
                prev_date = dates[i-1]
                curr_date = dates[i]
                
                prev_positions = positions_by_date[prev_date]
                curr_positions = positions_by_date[curr_date]
                
                for symbol in all_symbols:
                    if symbol in prev_positions and symbol in curr_positions:
                        prev_price = prev_positions[symbol].market_price
                        curr_price = curr_positions[symbol].market_price
                        
                        if prev_price and curr_price and prev_price > 0:
                            ret = (curr_price - prev_price) / prev_price
                            returns_data.append({
                                'date': pd.Timestamp(curr_date),
                                'symbol': symbol,
                                'return': ret,
                            })
            
            if returns_data:
                returns_df = pd.DataFrame(returns_data)
                returns_pivot = returns_df.pivot_table(
                    index='date',
                    columns='symbol',
                    values='return',
                    aggfunc='mean'
                )
                # Forward fill missing values, then fill remaining with 0
                returns_pivot = returns_pivot.ffill().fillna(0.0)
                return returns_pivot
    
    # Fallback: use trade data
    query = db.query(Trade).filter(Trade.account_id == account_id)
    
    if start_date:
        query = query.filter(Trade.exec_time >= start_date)
    if end_date:
        query = query.filter(Trade.exec_time <= end_date)
    
    trades = query.order_by(Trade.exec_time).all()
    
    if not trades:
        return pd.DataFrame()
    
    # Group by symbol and calculate approximate returns from price changes
    trades_df = pd.DataFrame([{
        'date': t.exec_time,
        'symbol': t.symbol,
        'price': t.price,
        'side': t.side,
    } for t in trades])
    
    if trades_df.empty:
        return pd.DataFrame()
    
    trades_df['date'] = pd.to_datetime(trades_df['date'])
    trades_df = trades_df.sort_values('date')
    
    # For each symbol, calculate returns from price changes
    returns_data = []
    for symbol in trades_df['symbol'].unique():
        symbol_trades = trades_df[trades_df['symbol'] == symbol].sort_values('date')
        if len(symbol_trades) < 2:
            continue
        
        # Calculate returns from price changes
        prices = symbol_trades['price'].values
        dates = symbol_trades['date'].values
        
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                ret = (prices[i] - prices[i-1]) / prices[i-1]
                returns_data.append({
                    'date': dates[i],
                    'symbol': symbol,
                    'return': ret,
                })
    
    if not returns_data:
        return pd.DataFrame()
    
    returns_df = pd.DataFrame(returns_data)
    returns_df['date'] = pd.to_datetime(returns_df['date'])
    
    # Pivot to get returns by symbol
    returns_pivot = returns_df.pivot_table(
        index='date',
        columns='symbol',
        values='return',
        aggfunc='mean'
    ).fillna(0.0)
    
    return returns_pivot


def get_current_positions_with_weights(
    account_id: str,
    db: Session,
) -> pd.Series:
    """Get current portfolio weights from positions."""
    query = db.query(Position).filter(
        Position.account_id == account_id
    ).order_by(desc(Position.timestamp))
    
    positions = query.all()
    
    if not positions:
        return pd.Series(dtype=float)
    
    # Get latest position for each symbol
    latest_positions = {}
    for pos in positions:
        if pos.symbol not in latest_positions or pos.timestamp > latest_positions[pos.symbol].timestamp:
            latest_positions[pos.symbol] = pos
    
    # Calculate weights
    total_value = sum(p.market_value or 0.0 for p in latest_positions.values())
    
    if total_value == 0:
        return pd.Series(dtype=float)
    
    weights = {}
    for symbol, pos in latest_positions.items():
        if pos.market_value:
            weights[symbol] = pos.market_value / total_value
    
    return pd.Series(weights)


# =============================================================================
# Portfolio Optimization Routes
# =============================================================================

@router.post("/optimization/markowitz", response_model=OptimizationResponse)
async def optimize_markowitz(
    account_id: Optional[str] = Query(None, description="Account ID"),
    risk_free_rate: float = Query(0.0, description="Risk-free rate"),
    target_return: Optional[float] = Query(None, description="Target return (for min variance)"),
    max_weight: float = Query(1.0, description="Maximum weight per asset"),
    min_weight: float = Query(0.0, description="Minimum weight per asset"),
    long_only: bool = Query(True, description="Long-only constraint"),
    start_date: Optional[datetime] = Query(None, description="Start date for returns calculation"),
    end_date: Optional[datetime] = Query(None, description="End date for returns calculation"),
    db: Session = Depends(get_db),
):
    """Markowitz mean-variance portfolio optimization."""
    try:
        if not account_id:
            # Infer from latest snapshot
            latest = db.query(AccountSnapshot).order_by(desc(AccountSnapshot.timestamp)).first()
            if latest:
                account_id = latest.account_id
        
        if not account_id:
            raise HTTPException(status_code=400, detail="account_id is required")
        
        # Get position returns
        returns_df = get_position_returns(account_id, start_date, end_date, db)
        
        if returns_df.empty or len(returns_df.columns) == 0:
            raise HTTPException(
                status_code=400,
                detail="Insufficient position data for optimization"
            )
        
        # Calculate expected returns and covariance
        expected_returns = returns_df.mean() * 252  # Annualized
        cov_matrix = returns_df.cov() * 252  # Annualized
        
        # Optimize
        if HAS_PORTFOLIO_MODULE:
            result = markowitz_optimize(
                expected_returns=expected_returns,
                cov_matrix=cov_matrix,
                risk_free_rate=risk_free_rate,
                target_return=target_return,
                max_weight=max_weight,
                min_weight=min_weight,
                long_only=long_only,
            )
        else:
            # Use our implementation
            result_dict = optimizer.markowitz_optimization(
                returns_df,
                risk_free_rate=risk_free_rate / 252,  # Convert to daily
                target_return=target_return / 252 if target_return else None
            )
            if "error" in result_dict:
                raise HTTPException(status_code=400, detail=result_dict["error"])
            # Convert to expected format
            from types import SimpleNamespace
            result = SimpleNamespace(
                weights=result_dict["weights"],
                expected_return=result_dict["expected_return"] * 252,  # Annualize
                expected_volatility=result_dict["expected_volatility"] * np.sqrt(252),  # Annualize
                sharpe_ratio=result_dict["sharpe_ratio"],
                constraints_satisfied=True,
                optimization_status="success"
            )
        
        weights_list = [
            OptimizationWeightsResponse(asset=asset, weight=float(weight))
            for asset, weight in result.weights.items()
            if abs(weight) > 1e-6
        ]
        
        return OptimizationResponse(
            method="markowitz",
            weights=weights_list,
            expected_return=result.expected_return,
            expected_volatility=result.expected_volatility,
            sharpe_ratio=result.sharpe_ratio,
            constraints_satisfied=result.constraints_satisfied,
            optimization_status=result.optimization_status,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Markowitz optimization: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")


@router.post("/optimization/black-litterman", response_model=OptimizationResponse)
async def optimize_black_litterman(
    account_id: Optional[str] = Query(None, description="Account ID"),
    risk_aversion: float = Query(3.0, description="Risk aversion parameter"),
    risk_free_rate: float = Query(0.0, description="Risk-free rate"),
    tau: float = Query(0.05, description="Uncertainty scaling factor"),
    views: Optional[str] = Query(None, description="JSON dict of {asset: expected_return} views"),
    view_confidences: Optional[str] = Query(None, description="JSON dict of {asset: confidence}"),
    start_date: Optional[datetime] = Query(None, description="Start date for returns calculation"),
    end_date: Optional[datetime] = Query(None, description="End date for returns calculation"),
    db: Session = Depends(get_db),
):
    """Black-Litterman portfolio optimization."""
    try:
        import json
        
        if not account_id:
            latest = db.query(AccountSnapshot).order_by(desc(AccountSnapshot.timestamp)).first()
            if latest:
                account_id = latest.account_id
        
        if not account_id:
            raise HTTPException(status_code=400, detail="account_id is required")
        
        # Get current positions for market cap weights
        current_weights = get_current_positions_with_weights(account_id, db)
        
        if current_weights.empty:
            raise HTTPException(
                status_code=400,
                detail="No current positions found for market equilibrium"
            )
        
        # Get returns for covariance
        returns_df = get_position_returns(account_id, start_date, end_date, db)
        
        if returns_df.empty:
            raise HTTPException(
                status_code=400,
                detail="Insufficient data for optimization"
            )
        
        cov_matrix = returns_df.cov() * 252
        
        # Parse views
        views_dict = json.loads(views) if views else None
        confidences_dict = json.loads(view_confidences) if view_confidences else None
        
        # Optimize
        result = black_litterman_optimize(
            market_caps=current_weights,
            cov_matrix=cov_matrix,
            risk_aversion=risk_aversion,
            views=views_dict,
            view_confidences=confidences_dict,
            tau=tau,
            risk_free_rate=risk_free_rate,
        )
        
        weights_list = [
            OptimizationWeightsResponse(asset=asset, weight=float(weight))
            for asset, weight in result.weights.items()
            if abs(weight) > 1e-6
        ]
        
        return OptimizationResponse(
            method="black_litterman",
            weights=weights_list,
            expected_return=result.expected_return,
            expected_volatility=result.expected_volatility,
            sharpe_ratio=result.sharpe_ratio,
            constraints_satisfied=result.constraints_satisfied,
            optimization_status=result.optimization_status,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Black-Litterman optimization: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")


@router.post("/optimization/risk-parity", response_model=OptimizationResponse)
async def optimize_risk_parity(
    account_id: Optional[str] = Query(None, description="Account ID"),
    target_risk: Optional[float] = Query(None, description="Target portfolio volatility"),
    start_date: Optional[datetime] = Query(None, description="Start date for returns calculation"),
    end_date: Optional[datetime] = Query(None, description="End date for returns calculation"),
    db: Session = Depends(get_db),
):
    """Risk parity portfolio optimization (equal risk contribution)."""
    try:
        if not account_id:
            latest = db.query(AccountSnapshot).order_by(desc(AccountSnapshot.timestamp)).first()
            if latest:
                account_id = latest.account_id
        
        if not account_id:
            raise HTTPException(status_code=400, detail="account_id is required")
        
        # Get position returns
        returns_df = get_position_returns(account_id, start_date, end_date, db)
        
        if returns_df.empty:
            raise HTTPException(
                status_code=400,
                detail="Insufficient data for optimization"
            )
        
        cov_matrix = returns_df.cov() * 252
        
        # Optimize
        result = risk_parity_optimize(
            cov_matrix=cov_matrix,
            target_risk=target_risk,
        )
        
        weights_list = [
            OptimizationWeightsResponse(asset=asset, weight=float(weight))
            for asset, weight in result.weights.items()
            if abs(weight) > 1e-6
        ]
        
        return OptimizationResponse(
            method="risk_parity",
            weights=weights_list,
            expected_return=result.expected_return,
            expected_volatility=result.expected_volatility,
            sharpe_ratio=result.sharpe_ratio,
            constraints_satisfied=result.constraints_satisfied,
            optimization_status=result.optimization_status,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in risk parity optimization: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")


# =============================================================================
# Factor Analysis Routes
# =============================================================================

@router.get("/factor-analysis/fama-french", response_model=FactorAnalysisResponse)
async def analyze_fama_french(
    account_id: Optional[str] = Query(None, description="Account ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db),
):
    """Fama-French factor model analysis."""
    try:
        if not account_id:
            latest = db.query(AccountSnapshot).order_by(desc(AccountSnapshot.timestamp)).first()
            if latest:
                account_id = latest.account_id
        
        if not account_id:
            raise HTTPException(status_code=400, detail="account_id is required")
        
        # Get position returns
        returns_df = get_position_returns(account_id, start_date, end_date, db)
        
        if returns_df.empty:
            raise HTTPException(
                status_code=400,
                detail="Insufficient data for factor analysis"
            )
        
        # Get market returns (S&P 500 proxy)
        from backend.benchmark_service import get_sp500_data
        
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        
        sp500_df = get_sp500_data(start_date, end_date)
        
        if sp500_df.empty:
            raise HTTPException(
                status_code=400,
                detail="Could not fetch market benchmark data"
            )
        
        market_returns = pd.Series(
            sp500_df['daily_return'].values,
            index=pd.to_datetime(sp500_df['date'])
        )
        
        # Run Fama-French analysis
        result = fama_french_analysis(
            returns=returns_df,
            market_returns=market_returns,
        )
        
        # Format response
        loadings_list = []
        for asset in result.factor_loadings.index:
            for factor in result.factor_loadings.columns:
                loadings_list.append(
                    FactorLoadingResponse(
                        asset=asset,
                        factor=factor,
                        loading=float(result.factor_loadings.loc[asset, factor])
                    )
                )
        
        return FactorAnalysisResponse(
            factor_loadings=loadings_list,
            factor_returns=result.factor_returns.to_dict(),
            r_squared=result.r_squared.to_dict(),
            factor_names=result.factor_names,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Fama-French analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.get("/factor-analysis/style", response_model=StyleAnalysisResponse)
async def analyze_style(
    account_id: Optional[str] = Query(None, description="Account ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    constraint_long_only: bool = Query(True, description="Long-only constraint"),
    db: Session = Depends(get_db),
):
    """Style analysis (Sharpe style regression)."""
    try:
        if not account_id:
            latest = db.query(AccountSnapshot).order_by(desc(AccountSnapshot.timestamp)).first()
            if latest:
                account_id = latest.account_id
        
        if not account_id:
            raise HTTPException(status_code=400, detail="account_id is required")
        
        # Get portfolio returns
        returns_df = data_processor.get_returns_series(account_id, start_date, end_date)
        
        if returns_df.empty:
            raise HTTPException(
                status_code=400,
                detail="Insufficient data for style analysis"
            )
        
        portfolio_returns = pd.Series(
            returns_df['daily_return'].values,
            index=pd.to_datetime(returns_df['date'])
        )
        
        # Get style benchmarks (simplified - use S&P 500 sectors or indices)
        # In practice, you'd fetch actual style benchmark data
        from backend.benchmark_service import get_sp500_data
        
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        
        sp500_df = get_sp500_data(start_date, end_date)
        
        if sp500_df.empty:
            raise HTTPException(
                status_code=400,
                detail="Could not fetch benchmark data"
            )
        
        # For now, use S&P 500 as single style benchmark
        # In production, you'd fetch multiple style indices
        style_benchmarks = pd.DataFrame({
            'Market': pd.Series(
                sp500_df['daily_return'].values,
                index=pd.to_datetime(sp500_df['date'])
            )
        })
        
        result = style_analysis(
            portfolio_returns=portfolio_returns,
            style_benchmarks=style_benchmarks,
            constraint_long_only=constraint_long_only,
        )
        
        return StyleAnalysisResponse(
            style_weights=result['style_weights'].to_dict(),
            r_squared=result['r_squared'],
            tracking_error=result['tracking_error'],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in style analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


# =============================================================================
# Attribution Analysis Routes
# =============================================================================

@router.get("/attribution/factor", response_model=AttributionResponse)
async def attribute_factor(
    account_id: Optional[str] = Query(None, description="Account ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db),
):
    """Factor-based performance attribution."""
    try:
        if not account_id:
            latest = db.query(AccountSnapshot).order_by(desc(AccountSnapshot.timestamp)).first()
            if latest:
                account_id = latest.account_id
        
        if not account_id:
            raise HTTPException(status_code=400, detail="account_id is required")
        
        # Get portfolio returns
        returns_df = data_processor.get_returns_series(account_id, start_date, end_date)
        
        if returns_df.empty:
            raise HTTPException(
                status_code=400,
                detail="Insufficient data for attribution"
            )
        
        portfolio_returns = pd.Series(
            returns_df['daily_return'].values,
            index=pd.to_datetime(returns_df['date'])
        )
        
        # Get position returns and run Fama-French to get factor loadings
        position_returns = get_position_returns(account_id, start_date, end_date, db)
        
        if position_returns.empty:
            raise HTTPException(
                status_code=400,
                detail="Insufficient position data"
            )
        
        # Get market returns
        from backend.benchmark_service import get_sp500_data
        
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        
        sp500_df = get_sp500_data(start_date, end_date)
        market_returns = pd.Series(
            sp500_df['daily_return'].values,
            index=pd.to_datetime(sp500_df['date'])
        )
        
        # Run factor analysis
        factor_result = fama_french_analysis(
            returns=position_returns,
            market_returns=market_returns,
        )
        
        # Get portfolio weights
        portfolio_weights = get_current_positions_with_weights(account_id, db)
        
        # Calculate attribution
        result = factor_attribution(
            portfolio_returns=portfolio_returns,
            factor_loadings=factor_result.factor_loadings,
            factor_returns=factor_result.factor_returns,
            portfolio_weights=portfolio_weights,
        )
        
        return AttributionResponse(
            total_attribution=result.total_attribution,
            factor_attribution=result.factor_attribution.to_dict() if len(result.factor_attribution) > 0 else None,
            sector_attribution=None,
            region_attribution=None,
            security_attribution=None,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in factor attribution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Attribution error: {str(e)}")


# =============================================================================
# Monte Carlo Simulation Routes
# =============================================================================

@router.get("/monte-carlo/simple", response_model=MonteCarloResponse)
async def monte_carlo_simple(
    account_id: Optional[str] = Query(None, description="Account ID"),
    initial_value: Optional[float] = Query(None, description="Initial portfolio value"),
    n_simulations: int = Query(10000, description="Number of simulations"),
    n_periods: int = Query(252, description="Number of periods (days)"),
    start_date: Optional[datetime] = Query(None, description="Start date for parameter estimation"),
    end_date: Optional[datetime] = Query(None, description="End date for parameter estimation"),
    random_seed: Optional[int] = Query(None, description="Random seed"),
    db: Session = Depends(get_db),
):
    """Simple Monte Carlo simulation for portfolio value."""
    try:
        if not account_id:
            latest = db.query(AccountSnapshot).order_by(desc(AccountSnapshot.timestamp)).first()
            if latest:
                account_id = latest.account_id
        
        if not account_id:
            raise HTTPException(status_code=400, detail="account_id is required")
        
        # Get portfolio returns to estimate parameters
        returns_df = data_processor.get_returns_series(account_id, start_date, end_date)
        
        if returns_df.empty or len(returns_df) < 10:
            raise HTTPException(
                status_code=400,
                detail="Insufficient data for parameter estimation"
            )
        
        returns = returns_df['daily_return'].dropna()
        
        # Estimate parameters
        expected_return = float(returns.mean() * 252)  # Annualized
        volatility = float(returns.std() * np.sqrt(252))  # Annualized
        
        # Get initial value
        if initial_value is None:
            latest_snapshot = db.query(AccountSnapshot).filter(
                AccountSnapshot.account_id == account_id
            ).order_by(desc(AccountSnapshot.timestamp)).first()
            
            if latest_snapshot:
                initial_value = latest_snapshot.net_liquidation or latest_snapshot.equity or 100000.0
            else:
                initial_value = 100000.0
        
        # Run simulation
        if HAS_PORTFOLIO_MODULE:
            result = monte_carlo_simulation(
                initial_value=initial_value,
                expected_return=expected_return,
                volatility=volatility,
                n_simulations=n_simulations,
                n_periods=n_periods,
                random_seed=random_seed,
            )
        else:
            # Use our implementation
            if random_seed:
                np.random.seed(random_seed)
            result_dict = mc_simulator.simulate_returns(
                returns,
                num_simulations=n_simulations,
                num_periods=n_periods,
                initial_value=initial_value
            )
            if "error" in result_dict:
                raise HTTPException(status_code=400, detail=result_dict["error"])
            # Convert to expected format
            from types import SimpleNamespace
            result = SimpleNamespace(
                expected_final_value=result_dict["mean_final_value"],
                percentiles=result_dict["percentiles"],
                probability_of_loss=float((np.array([result_dict["mean_final_value"]]) < initial_value).mean()) if result_dict["mean_final_value"] < initial_value else 0.0,
                var_95=result_dict["var_95"],
                cvar_95=result_dict.get("cvar_95", result_dict["var_95"]),
            )
        
        return MonteCarloResponse(
            initial_value=initial_value,
            expected_final_value=result.expected_final_value,
            percentiles=MonteCarloPercentilesResponse(**result.percentiles),
            probability_of_loss=result.probability_of_loss,
            var_95=result.var_95,
            cvar_95=result.cvar_95,
            n_simulations=n_simulations,
            n_periods=n_periods,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Monte Carlo simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@router.get("/monte-carlo/portfolio", response_model=MonteCarloResponse)
async def monte_carlo_portfolio(
    account_id: Optional[str] = Query(None, description="Account ID"),
    initial_value: Optional[float] = Query(None, description="Initial portfolio value"),
    n_simulations: int = Query(10000, description="Number of simulations"),
    n_periods: int = Query(252, description="Number of periods (days)"),
    rebalance_frequency: int = Query(21, description="Rebalance frequency (days, 0 = no rebalancing)"),
    start_date: Optional[datetime] = Query(None, description="Start date for parameter estimation"),
    end_date: Optional[datetime] = Query(None, description="End date for parameter estimation"),
    random_seed: Optional[int] = Query(None, description="Random seed"),
    db: Session = Depends(get_db),
):
    """Multi-asset portfolio Monte Carlo simulation."""
    try:
        if not account_id:
            latest = db.query(AccountSnapshot).order_by(desc(AccountSnapshot.timestamp)).first()
            if latest:
                account_id = latest.account_id
        
        if not account_id:
            raise HTTPException(status_code=400, detail="account_id is required")
        
        # Get current positions and weights
        portfolio_weights = get_current_positions_with_weights(account_id, db)
        
        if portfolio_weights.empty:
            raise HTTPException(
                status_code=400,
                detail="No current positions found"
            )
        
        # Get position returns
        position_returns = get_position_returns(account_id, start_date, end_date, db)
        
        if position_returns.empty:
            raise HTTPException(
                status_code=400,
                detail="Insufficient position data"
            )
        
        # Align assets
        common_assets = portfolio_weights.index.intersection(position_returns.columns)
        
        if len(common_assets) == 0:
            raise HTTPException(
                status_code=400,
                detail="No common assets between positions and returns"
            )
        
        portfolio_weights = portfolio_weights.loc[common_assets]
        portfolio_weights = portfolio_weights / portfolio_weights.sum()  # Normalize
        
        position_returns = position_returns[common_assets]
        
        # Estimate parameters
        expected_returns = position_returns.mean() * 252  # Annualized
        cov_matrix = position_returns.cov() * 252  # Annualized
        
        # Get initial value
        if initial_value is None:
            latest_snapshot = db.query(AccountSnapshot).filter(
                AccountSnapshot.account_id == account_id
            ).order_by(desc(AccountSnapshot.timestamp)).first()
            
            if latest_snapshot:
                initial_value = latest_snapshot.net_liquidation or latest_snapshot.equity or 100000.0
            else:
                initial_value = 100000.0
        
        # Run simulation
        result = monte_carlo_portfolio_simulation(
            initial_weights=portfolio_weights,
            expected_returns=expected_returns,
            cov_matrix=cov_matrix,
            initial_value=initial_value,
            n_simulations=n_simulations,
            n_periods=n_periods,
            rebalance_frequency=rebalance_frequency,
            random_seed=random_seed,
        )
        
        return MonteCarloResponse(
            initial_value=initial_value,
            expected_final_value=result.expected_final_value,
            percentiles=MonteCarloPercentilesResponse(**result.percentiles),
            probability_of_loss=result.probability_of_loss,
            var_95=result.var_95,
            cvar_95=result.cvar_95,
            n_simulations=n_simulations,
            n_periods=n_periods,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in portfolio Monte Carlo simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")
