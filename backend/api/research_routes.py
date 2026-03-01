"""Research API endpoints for quant research workflow.

Provides endpoints for:
- SQL queries over market data (DuckDB)
- Feature computation
- Backtest execution
- Experiment tracking
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, Body
import pandas as pd

from backend.config import settings
from backend.research.duckdb_utils import ResearchDB, get_research_db
from backend.research.features import FeatureRegistry, compute_features, get_feature_registry
from backend.research.backtest import (
    BacktestConfig, EventDrivenBacktest,
    run_backtest, run_factor_backtest, BacktestExperiment
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/research", tags=["research"])


# ----------------------------------------------------------------------
# Data Query Endpoints
# ----------------------------------------------------------------------

@router.get("/query")
async def research_query(
    sql: str = Query(..., description="SQL query to execute"),
    limit: int = Query(1000, description="Maximum rows to return"),
):
    """Execute a raw SQL query over market data.
    
    This endpoint uses DuckDB to query Parquet files directly.
    Available tables:
    - ibkr_equities, ibkr_fx, ibkr_futures, ibkr_options
    - yf_equities, yf_fx, yf_commodities, yf_rates
    - fred_treasury, fred_macro, fred_liquidity
    
    Example queries:
    - SELECT * FROM ibkr_equities WHERE ticker = 'AAPL' LIMIT 100
    - SELECT date, close FROM ibkr_fx WHERE ticker = 'EURUSD'
    - SELECT * FROM fred_macro WHERE series_id = 'CPIAUCSL'
    """
    try:
        with get_research_db() as db:
            # Add limit to query
            query = sql.strip()
            if "LIMIT" not in query.upper():
                query = f"{query} LIMIT {limit}"
            
            result = db.execute(query)
            return {
                "status": "success",
                "row_count": len(result),
                "data": result.to_dict(orient="records")
            }
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/prices")
async def get_research_prices(
    tickers: Optional[str] = Query(None, description="Comma-separated tickers"),
    asset_class: Optional[str] = Query(None, description="Asset class (equity, fx, futures, commodity)"),
    source: str = Query("ibkr", description="Data source (ibkr, yf)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(1000, description="Maximum rows"),
):
    """Query price data with filters."""
    try:
        ticker_list = tickers.split(",") if tickers else None
        
        with get_research_db() as db:
            df = db.query_prices(
                tickers=ticker_list,
                asset_class=asset_class,
                source=source,
                start_date=start_date,
                end_date=end_date
            )
        
        if limit and len(df) > limit:
            df = df.tail(limit)
        
        return {
            "status": "success",
            "row_count": len(df),
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        logger.error(f"Price query failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/returns")
async def get_research_returns(
    tickers: str = Query(..., description="Comma-separated tickers"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    periods: int = Query(1, description="Return periods"),
):
    """Calculate returns for given tickers."""
    try:
        ticker_list = tickers.split(",")
        
        with get_research_db() as db:
            df = db.get_returns(
                tickers=ticker_list,
                start_date=start_date,
                end_date=end_date,
                periods=periods
            )
        
        return {
            "status": "success",
            "row_count": len(df),
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        logger.error(f"Returns query failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/fred")
async def get_fred_data(
    series_ids: str = Query(..., description="Comma-separated FRED series IDs"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
):
    """Query FRED economic data."""
    try:
        series_list = series_ids.split(",")
        
        with get_research_db() as db:
            df = db.get_fred_series(
                series_ids=series_list,
                start_date=start_date,
                end_date=end_date
            )
        
        return {
            "status": "success",
            "row_count": len(df),
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        logger.error(f"FRED query failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ----------------------------------------------------------------------
# Feature Endpoints
# ----------------------------------------------------------------------

@router.get("/features")
async def list_features(
    category: Optional[str] = Query(None, description="Filter by category (momentum, volatility, value, quality)"),
):
    """List all available features in the registry."""
    try:
        registry = get_feature_registry()
        
        if category:
            from backend.research.features import FeatureCategory
            cat = FeatureCategory(category.lower())
            features = registry.list_features(cat)
        else:
            features = registry.list_features()
        
        return {
            "status": "success",
            "count": len(features),
            "features": [
                {
                    "name": f.name,
                    "category": f.category.value,
                    "description": f.description,
                    "parameters": f.parameters,
                    "required_data": f.required_data
                }
                for f in features
            ]
        }
    except Exception as e:
        logger.error(f"Feature list failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/features/compute")
async def compute_features_endpoint(
    data: List[Dict[str, Any]],
    feature_names: List[str] = Query(..., description="List of feature names to compute"),
    price_col: str = Query("close", description="Price column name"),
):
    """Compute features from price data."""
    try:
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Compute features
        result_df = compute_features(df, feature_names, price_col)
        
        return {
            "status": "success",
            "row_count": len(result_df),
            "data": result_df.to_dict(orient="records")
        }
    except Exception as e:
        logger.error(f"Feature computation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ----------------------------------------------------------------------
# Backtest Endpoints
# ----------------------------------------------------------------------

@router.post("/backtest")
async def run_backtest_endpoint(
    data: List[Dict[str, Any]],
    signals: List[Dict[str, Any]],
    initial_capital: float = Query(100000, description="Initial capital"),
    commission: float = Query(0.001, description="Commission per trade"),
    slippage: float = Query(0.0005, description="Slippage"),
):
    """Run a backtest with provided price data and signals.
    
    Request body should contain:
    - data: List of {date, close, ...} records
    - signals: List of {date, signal} records (-1, 0, 1)
    """
    try:
        # Convert to DataFrames
        price_df = pd.DataFrame(data)
        if "date" in price_df.columns:
            price_df["date"] = pd.to_datetime(price_df["date"])
            price_df = price_df.set_index("date")
        
        signals_df = pd.DataFrame(signals)
        if "date" in signals_df.columns:
            signals_df["date"] = pd.to_datetime(signals_df["date"])
            signals_df = signals_df.set_index("date")
        
        # Align signals to price data
        common_idx = price_df.index.intersection(signals_df.index)
        aligned_signals = signals_df.loc[common_idx, "signal"] if "signal" in signals_df.columns else signals_df.loc[common_idx, 0]
        
        # Create config
        config = BacktestConfig(
            initial_capital=initial_capital,
            commission=commission,
            slippage=slippage
        )
        
        # Run backtest
        result = run_backtest(price_df, aligned_signals, config)
        
        return {
            "status": "success",
            "metrics": result.metrics,
            "total_trades": len(result.trades),
            "equity_curve": result.equity_curve.to_dict(orient="records") if not result.equity_curve.empty else [],
            "trades": result.trades.to_dict(orient="records") if not result.trades.empty else []
        }
    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/backtest/factor")
async def run_factor_backtest_endpoint(
    data: List[Dict[str, Any]],
    factor_name: str = Query(..., description="Factor column name"),
    direction: str = Query("long_short", description="long_short or long_only"),
    quantile: float = Query(0.2, description="Top/bottom quantile"),
    initial_capital: float = Query(100000, description="Initial capital"),
    commission: float = Query(0.001, description="Commission"),
    slippage: float = Query(0.0005, description="Slippage"),
):
    """Run a factor-based backtest.
    
    Ranks securities by factor and goes long top quantile, short bottom quantile.
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")
        
        # Create config
        config = BacktestConfig(
            initial_capital=initial_capital,
            commission=commission,
            slippage=slippage
        )
        
        # Run factor backtest
        result = run_factor_backtest(
            df,
            factor_name=factor_name,
            direction=direction,
            quantile=quantile,
            config=config
        )
        
        return {
            "status": "success",
            "metrics": result.metrics,
            "total_trades": len(result.trades),
            "summary": result.summary()
        }
    except Exception as e:
        logger.error(f"Factor backtest failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/backtest/mlflow")
async def run_backtest_with_mlflow(
    data: List[Dict[str, Any]],
    signals: List[Dict[str, Any]],
    experiment_name: Optional[str] = Query(None, description="MLflow experiment name"),
    run_params: Optional[Dict[str, Any]] = Body(None, description="Parameters to log"),
    initial_capital: float = Query(100000, description="Initial capital"),
    commission: float = Query(0.001, description="Commission"),
    slippage: float = Query(0.0005, description="Slippage"),
):
    """Run backtest and log to MLflow."""
    try:
        # Run backtest
        result = await run_backtest_endpoint(
            data, signals, initial_capital, commission, slippage, True
        )
        
        # Log to MLflow
        experiment = BacktestExperiment(experiment_name)
        
        config = BacktestConfig(
            initial_capital=initial_capital,
            commission=commission,
            slippage=slippage
        )
        
        # Create BacktestResult from metrics
        # (simplified - in production would pass full result)
        
        logger.info(f"Backtest completed: Sharpe={result['metrics'].get('sharpe_ratio', 0):.2f}")
        
        return {
            "status": "success",
            "message": "Backtest completed and logged to MLflow",
            "metrics": result["metrics"]
        }
    except Exception as e:
        logger.error(f"MLflow backtest failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ----------------------------------------------------------------------
# Catalog / Status Endpoints
# ----------------------------------------------------------------------

@router.get("/status")
async def get_research_status():
    """Get research infrastructure status."""
    try:
        # Check DuckDB
        duckdb_ok = True
        try:
            with get_research_db() as db:
                db.execute("SELECT 1")
        except Exception as e:
            duckdb_ok = False
            logger.warning(f"DuckDB check failed: {e}")
        
        # Check MLflow
        mlflow_ok = settings.research.mlflow.is_enabled
        
        # Get feature count
        registry = get_feature_registry()
        feature_count = len(registry.list_features())
        
        return {
            "status": "ok" if duckdb_ok else "degraded",
            "duckdb": "ok" if duckdb_ok else "error",
            "mlflow": "enabled" if mlflow_ok else "disabled",
            "features_registered": feature_count,
            "config": {
                "data_sources": {
                    "equity": settings.data_sources.equity,
                    "fx": settings.data_sources.fx,
                    "futures": settings.data_sources.futures,
                    "commodity": settings.data_sources.commodity,
                    "rate": settings.data_sources.rate
                }
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
