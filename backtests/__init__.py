"""Backtesting framework using Backtrader."""

from backtests.cache import SignalCache
from backtests.forward_pass import (
    ComparisonView,
    ForwardPassTracker,
    SignalHistory,
    TradeRecord,
    create_tracker,
)
from backtests.parallel import ParallelBacktester
from backtests.run_manager import BacktestRun, RunManager

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
