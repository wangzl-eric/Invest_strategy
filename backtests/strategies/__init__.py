"""Backtest strategies package.

Signal definitions for backtesting and live trading.
All signals extend bt.Indicator for native Backtrader compatibility.
"""
from backtests.strategies.signals import (
    BaseSignal,
    MomentumSignal,
    CarrySignal,
    MeanReversionSignal,
    VolatilitySignal,
    RSISignal,
    MACDSignal,
    SMACrossoverSignal,
    BollingerPositionSignal,
    SignalBlender,
    register,
    get_signal,
    list_signals,
    run_signal_research,
    create_signal_strategy,
    create_blended_strategy,
)
from backtests.strategies.metadata import (
    SIGNAL_METADATA,
    get_signal_metadata,
)

__all__ = [
    # Base classes
    "BaseSignal",
    # Signal classes
    "MomentumSignal",
    "CarrySignal",
    "MeanReversionSignal",
    "VolatilitySignal",
    "RSISignal",
    "MACDSignal",
    "SMACrossoverSignal",
    "BollingerPositionSignal",
    # Blending
    "SignalBlender",
    # Registry
    "register",
    "get_signal",
    "list_signals",
    # Research
    "run_signal_research",
    # Backtrader integration
    "create_signal_strategy",
    "create_blended_strategy",
    # Metadata
    "SIGNAL_METADATA",
    "get_signal_metadata",
]
