"""Forward Pass: Track signal evolution during backtesting.

This module captures what the strategy "saw" at each decision point,
without look-ahead bias. Used for comparing predictions vs actual outcomes.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd


@dataclass
class SignalSnapshot:
    """A single signal snapshot at a point in time."""

    timestamp: datetime
    signal_name: str
    signal_value: float

    # Context
    prices: Dict[str, float] = field(default_factory=dict)  # {ticker: price}
    positions: Dict[str, float] = field(default_factory=dict)  # Current positions

    # Metadata
    lookback_used: int = 0
    data_available: bool = True

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "signal_name": self.signal_name,
            "signal_value": self.signal_value,
            "prices": self.prices,
            "positions": self.positions,
            "lookback_used": self.lookback_used,
            "data_available": self.data_available,
        }


@dataclass
class TradeRecord:
    """A single trade with forward-pass context."""

    trade_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Trade details
    timestamp: datetime = None  # When trade was executed
    ticker: str = ""
    direction: int = 0  # 1 = long, -1 = short, 0 = flat
    quantity: float = 0
    entry_price: float = 0
    exit_price: Optional[float] = None

    # Forward-pass context (what strategy saw)
    entry_signals: Dict[str, float] = field(
        default_factory=dict
    )  # Signal values at entry
    signal_names: List[str] = field(default_factory=list)  # Which signals used
    predicted_return: Optional[float] = None  # Model's predicted return
    signal_confidence: Optional[float] = None  # Confidence score

    # Forward-pass prices (what was available)
    prices_at_entry: Dict[str, float] = field(default_factory=dict)
    prices_at_exit: Optional[Dict[str, float]] = None

    # Position state
    position_held_days: int = 0

    def to_dict(self) -> dict:
        return {
            "trade_id": self.trade_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "ticker": self.ticker,
            "direction": self.direction,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "entry_signals": self.entry_signals,
            "signal_names": self.signal_names,
            "predicted_return": self.predicted_return,
            "signal_confidence": self.signal_confidence,
            "prices_at_entry": self.prices_at_entry,
            "prices_at_exit": self.prices_at_exit,
            "position_held_days": self.position_held_days,
            # Computed fields
            "actual_return": self.get_actual_return(),
            "pnl": self.get_pnl(),
        }

    def get_actual_return(self) -> Optional[float]:
        """Calculate actual return after exit."""
        if self.exit_price is None or self.entry_price == 0:
            return None
        return (
            (self.exit_price - self.entry_price)
            / self.entry_price
            * np.sign(self.direction)
        )

    def get_pnl(self) -> Optional[float]:
        """Calculate P&L in dollars."""
        if self.exit_price is None:
            return None
        return (
            (self.exit_price - self.entry_price)
            * self.quantity
            * np.sign(self.direction)
        )


class SignalHistory:
    """Track signal history over time for analysis."""

    def __init__(self):
        self.snapshots: List[SignalSnapshot] = []
        self._current_signals: Dict[str, float] = {}

    def add_snapshot(
        self,
        timestamp: datetime,
        signals: Dict[str, float],
        prices: Optional[Dict[str, float]] = None,
        positions: Optional[Dict[str, float]] = None,
    ) -> None:
        """Add a signal snapshot at a point in time."""
        for name, value in signals.items():
            self.snapshots.append(
                SignalSnapshot(
                    timestamp=timestamp,
                    signal_name=name,
                    signal_value=value,
                    prices=prices or {},
                    positions=positions or {},
                )
            )
        self._current_signals.update(signals)

    def get_signals_at(self, timestamp: datetime) -> Dict[str, float]:
        """Get all signal values at a specific timestamp."""
        result = {}
        for snapshot in self.snapshots:
            if snapshot.timestamp == timestamp:
                result[snapshot.signal_name] = snapshot.signal_value
        return result

    def get_signal_series(self, signal_name: str) -> pd.Series:
        """Get time series for a specific signal."""
        data = [
            (s.timestamp, s.signal_value)
            for s in self.snapshots
            if s.signal_name == signal_name
        ]
        if not data:
            return pd.Series(dtype=float)

        df = pd.DataFrame(data, columns=["timestamp", "value"])
        return df.set_index("timestamp")["value"]

    def to_dataframe(self) -> pd.DataFrame:
        """Export all snapshots to DataFrame."""
        if not self.snapshots:
            return pd.DataFrame()

        data = [s.to_dict() for s in self.snapshots]
        return pd.DataFrame(data)


class ForwardPassTracker:
    """
    Track forward-pass context for each trade.

    This captures what the strategy saw at decision time:
    - Signal values
    - Prices available
    - Predicted returns
    - Confidence levels

    Used for:
    - Signal quality analysis
    - Prediction vs actual comparison
    - Strategy debugging
    """

    def __init__(self):
        self.signal_history = SignalHistory()
        self.trades: List[TradeRecord] = []
        self._current_positions: Dict[str, float] = {}
        self._current_prices: Dict[str, float] = {}
        self._open_trades: Dict[str, TradeRecord] = {}  # ticker -> TradeRecord

    def update_market_data(
        self,
        timestamp: datetime,
        prices: Dict[str, float],
        positions: Dict[str, float],
    ) -> None:
        """Update current market state (called each bar)."""
        self._current_prices = prices
        self._current_positions = positions

    def update_signals(
        self,
        timestamp: datetime,
        signals: Dict[str, float],
    ) -> None:
        """Update current signal values (called each bar)."""
        # Add to history
        self.signal_history.add_snapshot(
            timestamp=timestamp,
            signals=signals,
            prices=self._current_prices,
            positions=self._current_positions,
        )

    def open_trade(
        self,
        timestamp: datetime,
        ticker: str,
        direction: int,
        quantity: float,
        price: float,
        predicted_return: Optional[float] = None,
        confidence: Optional[float] = None,
    ) -> TradeRecord:
        """Record trade opening with forward-pass context."""
        trade = TradeRecord(
            timestamp=timestamp,
            ticker=ticker,
            direction=direction,
            quantity=quantity,
            entry_price=price,
            prices_at_entry=self._current_prices.copy(),
            entry_signals=self.signal_history._current_signals.copy(),
            predicted_return=predicted_return,
            signal_confidence=confidence,
            signal_names=list(self.signal_history._current_signals.keys()),
        )

        self.trades.append(trade)
        self._open_trades[ticker] = trade

        return trade

    def close_trade(
        self,
        ticker: str,
        timestamp: datetime,
        price: float,
    ) -> Optional[TradeRecord]:
        """Record trade closing."""
        trade = self._open_trades.get(ticker)
        if trade is None:
            return None

        trade.exit_price = price
        trade.prices_at_exit = self._current_prices.copy()

        # Calculate holding period
        if trade.timestamp:
            trade.position_held_days = (timestamp - trade.timestamp).days

        del self._open_trades[ticker]

        return trade

    def get_trades(self, ticker: Optional[str] = None) -> List[TradeRecord]:
        """Get all trades, optionally filtered by ticker."""
        if ticker:
            return [t for t in self.trades if t.ticker == ticker]
        return self.trades

    def get_completed_trades(self) -> List[TradeRecord]:
        """Get trades that have been closed."""
        return [t for t in self.trades if t.exit_price is not None]

    def get_open_trades(self) -> List[TradeRecord]:
        """Get currently open trades."""
        return list(self._open_trades.values())

    def get_signal_accuracy(self) -> pd.DataFrame:
        """
        Compare predicted vs actual returns.

        Returns DataFrame with:
        - predicted_return: What the signal predicted
        - actual_return: What actually happened
        - error: Difference
        - correct_direction: Did we get direction right?
        """
        completed = self.get_completed_trades()
        if not completed:
            return pd.DataFrame()

        data = []
        for trade in completed:
            if trade.predicted_return is None or trade.get_actual_return() is None:
                continue

            data.append(
                {
                    "trade_id": trade.trade_id,
                    "timestamp": trade.timestamp,
                    "ticker": trade.ticker,
                    "predicted_return": trade.predicted_return,
                    "actual_return": trade.get_actual_return(),
                    "error": trade.get_actual_return() - trade.predicted_return,
                    "correct_direction": (
                        np.sign(trade.predicted_return)
                        == np.sign(trade.get_actual_return())
                    ),
                    "signal_confidence": trade.signal_confidence,
                }
            )

        return pd.DataFrame(data)

    def get_signal_performance_summary(self) -> Dict[str, Any]:
        """
        Summarize signal prediction quality.
        """
        df = self.get_signal_accuracy()
        if df.empty:
            return {"error": "No completed trades with predictions"}

        # Overall accuracy
        direction_accuracy = df["correct_direction"].mean()

        # By confidence level
        if "signal_confidence" in df.columns:
            high_conf = df[df["signal_confidence"] > 0.7]
            low_conf = df[df["signal_confidence"] <= 0.3]

            high_conf_acc = (
                high_conf["correct_direction"].mean() if len(high_conf) > 0 else None
            )
            low_conf_acc = (
                low_conf["correct_direction"].mean() if len(low_conf) > 0 else None
            )
        else:
            high_conf_acc = None
            low_conf_acc = None

        # Prediction bias
        mean_predicted = df["predicted_return"].mean()
        mean_actual = df["actual_return"].mean()
        bias = mean_actual - mean_predicted

        return {
            "total_trades": len(df),
            "direction_accuracy": direction_accuracy,
            "high_confidence_accuracy": high_conf_acc,
            "low_confidence_accuracy": low_conf_acc,
            "mean_predicted_return": mean_predicted,
            "mean_actual_return": mean_actual,
            "prediction_bias": bias,
            "mae": (df["error"].abs()).mean(),
            "rmse": np.sqrt((df["error"] ** 2).mean()),
        }

    def export_trades(self) -> pd.DataFrame:
        """Export all trades to DataFrame."""
        if not self.trades:
            return pd.DataFrame()

        data = [t.to_dict() for t in self.trades]
        return pd.DataFrame(data)


# ============================================================================
# Integration helpers
# ============================================================================


def create_tracker() -> ForwardPassTracker:
    """Create a new forward pass tracker."""
    return ForwardPassTracker()


__all__ = [
    "SignalSnapshot",
    "TradeRecord",
    "SignalHistory",
    "ForwardPassTracker",
    "create_tracker",
]
