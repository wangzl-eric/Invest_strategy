"""Research workstation utilities for signal development and backtesting."""

from research.helpers import (
    load_prices,
    load_fred,
    evaluate_signal,
    plot_backtest,
)
from research.signals import (
    BaseSignal,
    MomentumSignal,
    CarrySignal,
    MeanReversionSignal,
    register,
    get_signal,
    list_signals,
)

__all__ = [
    "load_prices",
    "load_fred",
    "evaluate_signal",
    "plot_backtest",
    "BaseSignal",
    "MomentumSignal",
    "CarrySignal",
    "MeanReversionSignal",
    "register",
    "get_signal",
    "list_signals",
]
