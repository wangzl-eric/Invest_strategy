"""API routes for backtesting functionality."""
import logging
from typing import Any, Dict, Optional

import pandas as pd
from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel

# Note: Vectorized backtest has been deprecated. Use BacktestEngine with Backtrader.
from portfolio.blend import Signal, blend_signals

logger = logging.getLogger(__name__)

router = APIRouter()


class BacktestRequest(BaseModel):
    """Request model for backtest endpoint."""

    strategy_name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    symbols: list[str] = []
    parameters: Dict[str, Any] = {}


class SimpleMomentumStrategy:
    """Simple momentum strategy for testing."""

    name = "simple_momentum"

    def __init__(self, lookback: int = 60):
        self.lookback = lookback

    def generate_positions(self, bars: pd.DataFrame) -> pd.Series:
        """Generate positions based on momentum signal."""
        close = bars["close"].astype(float)
        mean_price = close.rolling(self.lookback, min_periods=1).mean()
        return (close > mean_price).astype(float)


@router.post("/backtest/run")
async def run_backtest(request: BacktestRequest = Body(...)):
    """Run a backtest using BacktestEngine.

    Note: This is a simplified endpoint. In production, you would:
    - Load historical data from data lake
    - Support multiple strategy types
    - Handle parameter sweeps
    - Store results in database/MLflow
    """
    try:
        # For now, return a placeholder response
        # In a full implementation, this would:
        # 1. Load historical data for requested symbols
        # 2. Initialize strategy with parameters
        # 3. Run backtest
        # 4. Return results

        return {
            "status": "success",
            "message": "Backtest endpoint created. Full implementation requires data lake integration.",
            "strategy": request.strategy_name,
            "parameters": request.parameters,
            "note": "This endpoint requires historical data from the data lake. "
            "Use research/experiments/run_example_momentum.py for full backtesting.",
        }

    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/backtest/strategies")
async def list_backtest_strategies():
    """List available backtest strategies."""
    return {
        "strategies": [
            {
                "name": "simple_momentum",
                "description": "Simple momentum strategy",
                "parameters": {
                    "lookback": {
                        "type": "int",
                        "default": 60,
                        "description": "Lookback period in days",
                    }
                },
            }
        ]
    }
