"""Backtrader-compatible signal wrapper.

Provides integration between our signal system and Backtrader's event-driven framework.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Union

import backtrader as bt
import numpy as np
import pandas as pd

from backtests.strategies.signals import BaseSignal, get_signal, list_signals


class BacktraderSignalIndicator(bt.Indicator):
    """
    Wrap our signal classes as Backtrader indicators.

    Usage:
        signal = BacktraderSignalIndicator('SPY', lookback=20)
        # In strategy:
        if signal.lines.signal[0] > 0:
            self.buy()
    """

    lines = ("signal",)
    params = (
        ("lookback", 20),
        ("signal_name", "momentum_12_1"),
        ("skip", 21),
    )

    def __init__(self):
        # Get the signal class
        self.signal_class = get_signal(self.params.signal_name)
        if self.signal_class is None:
            raise ValueError(f"Signal {self.params.signal_name} not found")

        # Store historical data for signal computation
        self._history = []

    def next(self):
        """Called on each new bar - compute signal for current bar."""
        # Get all available data points up to now
        close = self.data.close

        # Build a DataFrame for the signal computation
        # Use data from -lookback to now (excluding current bar to avoid lookahead)
        lookback = self.params.lookback
        if len(close) < lookback + 1:
            self.lines.signal[0] = 0
            return

        # Get historical closes (excluding current bar for proper signal)
        hist = pd.Series([close[-i] for i in range(lookback, 0, -1)])
        prices = pd.DataFrame({"close": hist})

        try:
            sig = self.signal_class.compute(prices)
            if isinstance(sig, pd.DataFrame):
                sig_val = sig.iloc[-1].mean() if len(sig.columns) > 0 else 0
            else:
                sig_val = sig.iloc[-1] if len(sig) > 0 else 0

            # Convert to position: 1 = long, -1 = short, 0 = flat
            self.lines.signal[0] = np.sign(sig_val) if not pd.isna(sig_val) else 0
        except Exception:
            self.lines.signal[0] = 0


def signals_to_backtrader(
    signals: Union[pd.Series, pd.DataFrame],
    data_feed: bt.feeds.DataFeed,
) -> pd.Series:
    """
    Convert our signals format to backtrader-compatible Series.

    Args:
        signals: Signal values (can be raw or positions)
        data_feed: Backtrader data feed to align with

    Returns:
        Series with -1/0/1 values aligned to data_feed dates
    """
    if isinstance(signals, pd.DataFrame):
        # Multi-asset - take mean across columns
        signals = signals.mean(axis=1)

    # Ensure index is datetime
    if not isinstance(signals.index, pd.DatetimeIndex):
        signals.index = pd.to_datetime(signals.index)

    # Convert to positions if needed
    positions = np.sign(signals).fillna(0)

    return positions


def create_signal_strategy(
    signal_name: str,
    lookback: int = 20,
    skip: int = 21,
) -> type:
    """
    Create a Backtrader strategy class from a signal name.

    Args:
        signal_name: Name of signal in registry
        lookback: Lookback period for signal
        skip: Skip days (for momentum)

    Returns:
        Backtrader Strategy class
    """
    signal = get_signal(signal_name)
    if signal is None:
        raise ValueError(f"Signal {signal_name} not found in registry")

    class SignalStrategy(bt.Strategy):
        params = (
            ("lookback", lookback),
            ("skip", skip),
            ("threshold", 0.0),  # Signal threshold for entry
        )

        def __init__(self):
            self.signal_indicator = BacktraderSignalIndicator(
                data=self.data,
                signal_name=signal_name,
                lookback=lookback,
                skip=skip,
            )
            self.order = None

        def notify_order(self, order):
            if order.status in [order.Completed]:
                self.order = None

        def next(self):
            if self.order:
                return

            sig = self.signal_indicator.lines.signal[0]

            if sig > self.params.threshold:
                if not self.position:
                    self.order = self.buy()
            elif sig < -self.params.threshold:
                if self.position:
                    self.order = self.sell()
            elif sig == 0:
                # Exit on zero signal
                if self.position:
                    self.order = self.close()

    SignalStrategy.__name__ = f"SignalStrategy_{signal_name}"
    return SignalStrategy


def run_backtest_with_signals(
    prices: pd.DataFrame,
    signal_names: List[str],
    weights: Optional[List[float]] = None,
    initial_cash: float = 100000,
    commission: float = 0.001,
) -> Dict:
    """
    Run a backtest using our signal system with Backtrader.

    Args:
        prices: Price data with columns [open, high, low, close, volume]
        signal_names: List of signal names to use
        weights: Weights for blending signals (default: equal)
        initial_cash: Starting capital
        commission: Commission rate

    Returns:
        Backtest results dictionary
    """
    from workstation.backtests.event_driven.backtest_engine import (
        BacktestEngine,
        IBKRDataFeed,
    )

    weights = weights or [1.0 / len(signal_names)] * len(signal_names)

    # Compute signals
    all_signals = []
    for sig_name in signal_names:
        sig = get_signal(sig_name)
        if sig is None:
            continue

        # Compute signal on close prices
        close_df = prices[["close"]].copy()
        sig_values = sig.compute(close_df)

        # Convert to positions
        positions = sig.to_positions(sig_values)
        all_signals.append(positions)

    if not all_signals:
        raise ValueError("No valid signals computed")

    # Blend signals
    blended = pd.concat(all_signals, axis=1)
    blended = blended.mean(axis=1).fillna(0)

    # Align to price data
    prices_aligned = prices.loc[blended.index].copy()

    # Prepare data for backtrader
    bt_data = prices_aligned.reset_index()
    bt_data.columns = ["date", "open", "high", "low", "close", "volume"]

    # Run backtest
    engine = BacktestEngine(cash=initial_cash, commission=commission)
    engine.add_data(IBKRDataFeed(dataname=bt_data), name="asset")

    # Use SignalStrategy with blended signals
    from workstation.backtests.event_driven.backtest_engine import (
        create_signal_strategy_class,
    )

    StrategyClass = create_signal_strategy_class(
        signals=blended,
        name="BlendedSignal",
    )
    engine.add_strategy(StrategyClass)

    return engine.run_backtest()


# ============================================================================
# Signal-to-Backtrader Mapping
# ============================================================================

# Mapping from our signal names to backtrader indicators
SIGNAL_TO_BT_INDICATOR: Dict[str, str] = {
    "momentum_12_1": "bt.ind.Momentum",
    "momentum_60_21": "bt.ind.Momentum",
    "mean_reversion": "bt.ind.RSI",  # Approximate
    "rsi": "bt.ind.RSI",
    "macd": "bt.ind.MACD",
    "sma_crossover": "bt.ind.SMA",  # Approximate
    "bollinger_position": "bt.ind.BollingerBands",
    "volatility": "bt.ind.StandardDeviation",
}


def get_backtrader_equivalent(signal_name: str) -> Optional[str]:
    """Get Backtrader indicator equivalent for a signal."""
    return SIGNAL_TO_BT_INDICATOR.get(signal_name)


# ============================================================================
# Event-Driven Signal Computation
# ============================================================================


class EventDrivenSignalComputer:
    """
    Compute signals in an event-driven manner (bar by bar).

    This is useful for live trading where signals need to be
    computed incrementally as new data arrives.
    """

    def __init__(self, signal: BaseSignal, lookback: int = 60):
        self.signal = signal
        self.lookback = lookback
        self._prices: List[float] = []

    def update(self, close: float) -> float:
        """
        Update with new bar and compute signal.

        Args:
            close: Closing price of new bar

        Returns:
            Signal value (-1 to 1)
        """
        self._prices.append(close)

        # Keep only lookback period
        if len(self._prices) > self.lookback:
            self._prices.pop(0)

        if len(self._prices) < self.lookback // 2:
            return 0.0

        # Compute signal
        prices_df = pd.DataFrame({"close": self._prices})
        sig = self.signal.compute(prices_df)

        if isinstance(sig, pd.DataFrame):
            return sig.iloc[-1].mean() if len(sig) > 0 else 0.0
        else:
            return sig.iloc[-1] if len(sig) > 0 else 0.0

    def get_position(self, threshold: float = 0.0) -> int:
        """Get position signal (-1, 0, 1) based on threshold."""
        if len(self._prices) == 0:
            return 0
        sig = self._prices[-1]
        if sig > threshold:
            return 1
        elif sig < -threshold:
            return -1
        return 0


__all__ = [
    "BacktraderSignalIndicator",
    "signals_to_backtrader",
    "create_signal_strategy",
    "run_backtest_with_signals",
    "get_backtrader_equivalent",
    "EventDrivenSignalComputer",
]
