"""Forward Pass: Track signal evolution during backtesting.

This module provides dual-tracking for P&L attribution:
1. Forward-pass: What the strategy predicted/saw at decision time
2. Post-trade: What actually happened (with hindsight)

Usage:
    from backtests.forward_pass import ForwardPassTracker, ComparisonView
    
    # Track predictions during backtest
    tracker = ForwardPassTracker()
    tracker.open_trade(timestamp, ticker, direction, price, predicted_return=0.05)
    tracker.close_trade(ticker, exit_price)
    
    # Compare with attribution
    comparison = ComparisonView(tracker, attribution_df)
    summary = comparison.get_summary()
"""

from backtests.forward_pass.trade_tracker import (
    SignalSnapshot,
    TradeRecord,
    SignalHistory,
    ForwardPassTracker,
    create_tracker,
)
from backtests.forward_pass.comparison import (
    TradeComparison,
    ComparisonView,
    create_comparison_view,
)

__all__ = [
    # Trade tracking
    "SignalSnapshot",
    "TradeRecord",
    "SignalHistory",
    "ForwardPassTracker",
    "create_tracker",
    # Comparison
    "TradeComparison",
    "ComparisonView",
    "create_comparison_view",
]
