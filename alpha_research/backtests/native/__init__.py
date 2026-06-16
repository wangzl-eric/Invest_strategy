"""Native event-driven backtest engine.

A rigorous, user-friendly, share-based portfolio backtester built by adapting
the strongest ideas from vnpy, backtrader, and qlib (see
``docs/guides/backtesting_engine_comparison.md``). It complements the vectorized
``alpha_research.review.engine`` (kept as the fast review path) with realistic
event-driven accounting: real positions, cash, fills, commission, slippage, and
no-look-ahead-by-construction.

Quick start::

    from alpha_research.backtests.native import backtest_weights
    result = backtest_weights(weights, prices, cost_bps=5.0)
    print(result.summary())

See ``docs/guides/native_engine_user_guide.md`` for the full guide.
"""

from .analyzers import (
    AnalysisInput,
    Analyzer,
    DrawdownAnalyzer,
    PerformanceAnalyzer,
    ReturnsAnalyzer,
    SharpeAnalyzer,
    StatsAnalyzer,
    TradeAnalyzer,
    default_analyzers,
)
from .api import backtest_strategy, backtest_weights
from .broker import SimBroker
from .engine import BacktestEngine
from .objects import (
    Account,
    Bar,
    Direction,
    Order,
    OrderStatus,
    OrderType,
    Position,
    Trade,
)
from .results import BacktestResult
from .strategy import CallableStrategy, Context, Strategy, WeightsStrategy

__all__ = [
    # one-call API
    "backtest_weights",
    "backtest_strategy",
    # engine + broker
    "BacktestEngine",
    "SimBroker",
    # strategy API
    "Strategy",
    "Context",
    "WeightsStrategy",
    "CallableStrategy",
    # objects
    "Bar",
    "Order",
    "Trade",
    "Position",
    "Account",
    "Direction",
    "OrderType",
    "OrderStatus",
    # results + analyzers
    "BacktestResult",
    "Analyzer",
    "AnalysisInput",
    "ReturnsAnalyzer",
    "SharpeAnalyzer",
    "DrawdownAnalyzer",
    "TradeAnalyzer",
    "PerformanceAnalyzer",
    "StatsAnalyzer",
    "default_analyzers",
]
