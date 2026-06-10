"""Backtesting framework using Backtrader."""

from alpha_research.backtests.cache import SignalCache
from alpha_research.backtests.forward_pass import (
    ComparisonView,
    ForwardPassTracker,
    SignalHistory,
    TradeRecord,
    create_tracker,
)
from alpha_research.backtests.parallel import ParallelBacktester
from alpha_research.backtests.run_manager import BacktestRun, RunManager

__all__ = [
    # Forward pass tracking
    "ForwardPassTracker",
    "TradeRecord",
    "SignalHistory",
    "ComparisonView",
    "create_tracker",
    # Phase 4: scalability
    "ParallelBacktester",
    "SignalCache",
    "RunManager",
    "BacktestRun",
]
