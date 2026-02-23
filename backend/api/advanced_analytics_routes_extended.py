"""Extended advanced analytics routes using the new advanced_analytics module."""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
import pandas as pd
import numpy as np

from backend.database import get_db
from backend.models import PnLHistory, AccountSnapshot
from backend.data_processor import DataProcessor
from backend.advanced_analytics import (
    PortfolioOptimizer,
    FactorAnalyzer,
    MonteCarloSimulator,
    AttributionAnalyzer,
    RegimeDetector,
    AnomalyDetector,
)

logger = logging.getLogger(__name__)

router = APIRouter()
data_processor = DataProcessor()
optimizer = PortfolioOptimizer()
factor_analyzer = FactorAnalyzer()
mc_simulator = MonteCarloSimulator()
attribution_analyzer = AttributionAnalyzer()
regime_detector = RegimeDetector()
anomaly_detector = AnomalyDetector()


@router.get("/regime-detection")
async def detect_market_regime(
    account_id: Optional[str] = Query(None, description="Account ID"),
    lookback_window: int = Query(60, description="Lookback window in days"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db)
):
    """Detect current market regime (bull/bear/neutral)."""
    try:
        if not account_id:
            latest = db.query(AccountSnapshot).order_by(desc(AccountSnapshot.timestamp)).first()
            if latest:
                account_id = latest.account_id
        
        if not account_id:
            raise HTTPException(status_code=400, detail="account_id is required")
        
        # Get returns
        returns_df = data_processor.get_returns_series(account_id, start_date, end_date)
        
        if returns_df.empty:
            raise HTTPException(status_code=400, detail="Insufficient data")
        
        returns = pd.Series(
            returns_df['daily_return'].values,
            index=pd.to_datetime(returns_df['date'])
        )
        
        result = regime_detector.detect_regime(returns, lookback_window)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in regime detection: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomaly-detection")
async def detect_anomalies(
    account_id: Optional[str] = Query(None, description="Account ID"),
    threshold_sigma: float = Query(3.0, description="Threshold in standard deviations"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db)
):
    """Detect anomalous returns."""
    try:
        if not account_id:
            latest = db.query(AccountSnapshot).order_by(desc(AccountSnapshot.timestamp)).first()
            if latest:
                account_id = latest.account_id
        
        if not account_id:
            raise HTTPException(status_code=400, detail="account_id is required")
        
        # Get returns
        returns_df = data_processor.get_returns_series(account_id, start_date, end_date)
        
        if returns_df.empty:
            raise HTTPException(status_code=400, detail="Insufficient data")
        
        returns = pd.Series(
            returns_df['daily_return'].values,
            index=pd.to_datetime(returns_df['date'])
        )
        
        result = anomaly_detector.detect_anomalies(returns, threshold_sigma)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in anomaly detection: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stress-test")
async def stress_test_portfolio(
    account_id: Optional[str] = Query(None, description="Account ID"),
    scenarios: Optional[str] = Query(None, description="JSON array of scenario dicts"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db)
):
    """Perform stress testing with various scenarios."""
    try:
        import json
        
        if not account_id:
            latest = db.query(AccountSnapshot).order_by(desc(AccountSnapshot.timestamp)).first()
            if latest:
                account_id = latest.account_id
        
        if not account_id:
            raise HTTPException(status_code=400, detail="account_id is required")
        
        # Get returns
        returns_df = data_processor.get_returns_series(account_id, start_date, end_date)
        
        if returns_df.empty:
            raise HTTPException(status_code=400, detail="Insufficient data")
        
        returns = pd.Series(
            returns_df['daily_return'].values,
            index=pd.to_datetime(returns_df['date'])
        )
        
        # Parse scenarios
        if scenarios:
            scenario_list = json.loads(scenarios)
        else:
            # Default scenarios
            scenario_list = [
                {"name": "Market Crash 2008", "market_shock": -0.20, "volatility_multiplier": 2.0},
                {"name": "Moderate Correction", "market_shock": -0.10, "volatility_multiplier": 1.5},
                {"name": "Volatility Spike", "market_shock": 0.0, "volatility_multiplier": 2.0},
            ]
        
        result = mc_simulator.stress_test(returns, scenario_list)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in stress test: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
