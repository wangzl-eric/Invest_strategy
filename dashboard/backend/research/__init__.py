"""Research module for quant research workflow.

This module provides:
- DuckDB wrapper for fast SQL queries over Parquet data
- Feature registry with standardized signal definitions
- Optional backtesting integrations when installed
- Experiment tracking integration with MLflow
"""

from backend.research.duckdb_utils import ResearchDB
from backend.research.features import FeatureRegistry, compute_features

try:
    from backend.research.backtest import BacktestExperiment, EventDrivenBacktest
except ModuleNotFoundError:
    BacktestExperiment = None
    EventDrivenBacktest = None

__all__ = [
    "ResearchDB",
    "FeatureRegistry",
    "compute_features",
]

if EventDrivenBacktest is not None:
    __all__.extend(["EventDrivenBacktest", "BacktestExperiment"])
