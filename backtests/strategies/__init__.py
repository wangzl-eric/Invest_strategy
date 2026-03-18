"""Backtest strategies package.

Signal definitions for backtesting and live trading.
All signals extend bt.Indicator for native Backtrader compatibility.
"""
from backtests.strategies.labeling import TripleBarrierLabeler
from backtests.strategies.metadata import SIGNAL_METADATA, get_signal_metadata
from backtests.strategies.signals import (
    BaseSignal,
    BollingerPositionSignal,
    CarrySignal,
    MACDSignal,
    MeanReversionSignal,
    MomentumSignal,
    RSISignal,
    SignalBlender,
    SMACrossoverSignal,
    VolatilitySignal,
    create_blended_strategy,
    create_signal_strategy,
    get_signal,
    list_signals,
    register,
    run_signal_research,
    run_signal_research_ml,
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
    "run_signal_research_ml",
    # Labeling
    "TripleBarrierLabeler",
    # Backtrader integration
    "create_signal_strategy",
    "create_blended_strategy",
    # Metadata
    "SIGNAL_METADATA",
    "get_signal_metadata",
]
