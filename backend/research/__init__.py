"""Research module for quant research workflow.

This module provides:
- DuckDB wrapper for fast SQL queries over Parquet data
- Feature registry with standardized signal definitions
- Backtesting engine using Backtrader
- Experiment tracking integration with MLflow
"""

from backend.research.duckdb_utils import ResearchDB
from backend.research.features import FeatureRegistry, compute_features
from backend.research.backtest import EventDrivenBacktest, BacktestExperiment

__all__ = [
    "ResearchDB",
    "FeatureRegistry", 
    "compute_features",
    "EventDrivenBacktest",
    "BacktestExperiment",
]
