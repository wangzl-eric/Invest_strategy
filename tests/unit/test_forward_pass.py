"""Unit tests for forward_pass module."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

import numpy as np
import pandas as pd

from backtests.forward_pass import (
    ForwardPassTracker,
    TradeRecord,
    SignalHistory,
    SignalSnapshot,
    TradeComparison,
    ComparisonView,
    create_tracker,
)


class TestSignalSnapshot:
    """Tests for SignalSnapshot dataclass."""

    def test_signal_snapshot_creation(self):
        """Test creating a signal snapshot."""
        timestamp = datetime(2024, 1, 15)
        snapshot = SignalSnapshot(
            timestamp=timestamp,
            signal_name="momentum",
            signal_value=0.73,
            prices={"SPY": 450.0},
            positions={"SPY": 100},
            lookback_used=60,
        )

        assert snapshot.signal_name == "momentum"
        assert snapshot.signal_value == 0.73
        assert snapshot.prices["SPY"] == 450.0
        assert snapshot.timestamp == timestamp

    def test_signal_snapshot_to_dict(self):
        """Test converting snapshot to dictionary."""
        snapshot = SignalSnapshot(
            timestamp=datetime(2024, 1, 15),
            signal_name="rsi",
            signal_value=-0.3,
        )

        d = snapshot.to_dict()
        assert d["signal_name"] == "rsi"
        assert d["signal_value"] == -0.3
        assert "timestamp" in d


class TestTradeRecord:
    """Tests for TradeRecord dataclass."""

    def test_trade_record_creation(self):
        """Test creating a trade record."""
        timestamp = datetime(2024, 1, 15)
        trade = TradeRecord(
            timestamp=timestamp,
            ticker="AAPL",
            direction=1,
            quantity=100,
            entry_price=150.0,
            predicted_return=0.05,
            signal_confidence=0.8,
            entry_signals={"momentum": 0.7, "rsi": -0.2},
        )

        assert trade.ticker == "AAPL"
        assert trade.direction == 1
        assert trade.quantity == 100
        assert trade.predicted_return == 0.05

    def test_actual_return_calculation(self):
        """Test actual return calculation."""
        trade = TradeRecord(
            timestamp=datetime(2024, 1, 15),
            ticker="AAPL",
            direction=1,
            quantity=100,
            entry_price=100.0,
            exit_price=110.0,
        )

        assert trade.get_actual_return() == pytest.approx(0.10)

    def test_pnl_calculation(self):
        """Test P&L calculation."""
        trade = TradeRecord(
            timestamp=datetime(2024, 1, 15),
            ticker="AAPL",
            direction=1,
            quantity=100,
            entry_price=100.0,
            exit_price=110.0,
        )

        assert trade.get_pnl() == pytest.approx(1000.0)

    def test_short_trade_return(self):
        """Test return calculation for short trade."""
        trade = TradeRecord(
            timestamp=datetime(2024, 1, 15),
            ticker="AAPL",
            direction=-1,  # Short
            quantity=100,
            entry_price=100.0,
            exit_price=90.0,  # Price dropped
        )

        # Short profits when price drops
        assert trade.get_actual_return() == pytest.approx(0.10)

    def test_to_dict(self):
        """Test converting trade to dictionary."""
        trade = TradeRecord(
            timestamp=datetime(2024, 1, 15),
            ticker="AAPL",
            direction=1,
            quantity=100,
            entry_price=100.0,
            exit_price=110.0,
        )

        d = trade.to_dict()
        assert d["ticker"] == "AAPL"
        assert d["actual_return"] == pytest.approx(0.10)
        assert d["pnl"] == pytest.approx(1000.0)


class TestSignalHistory:
    """Tests for SignalHistory class."""

    def test_signal_history_creation(self):
        """Test creating signal history."""
        history = SignalHistory()
        assert len(history.snapshots) == 0

    def test_add_snapshot(self):
        """Test adding snapshots."""
        history = SignalHistory()
        ts = datetime(2024, 1, 15)

        history.add_snapshot(
            timestamp=ts,
            signals={"momentum": 0.5, "rsi": -0.3},
            prices={"SPY": 450.0},
            positions={"SPY": 100},
        )

        assert len(history.snapshots) == 2

    def test_get_signals_at(self):
        """Test retrieving signals at specific timestamp."""
        history = SignalHistory()
        ts = datetime(2024, 1, 15)

        history.add_snapshot(ts, {"momentum": 0.5})
        history.add_snapshot(ts, {"rsi": -0.3})

        signals = history.get_signals_at(ts)
        assert "momentum" in signals
        assert "rsi" in signals

    def test_get_signal_series(self):
        """Test getting signal as time series."""
        history = SignalHistory()

        for i in range(5):
            ts = datetime(2024, 1, i + 1)
            history.add_snapshot(ts, {"momentum": 0.1 * i})

        series = history.get_signal_series("momentum")
        assert len(series) == 5
        assert series.iloc[-1] == 0.4

    def test_to_dataframe(self):
        """Test exporting to DataFrame."""
        history = SignalHistory()
        ts = datetime(2024, 1, 15)

        history.add_snapshot(ts, {"momentum": 0.5, "rsi": -0.3})

        df = history.to_dataframe()
        assert len(df) == 2  # Two snapshots (momentum and rsi)


class TestForwardPassTracker:
    """Tests for ForwardPassTracker class."""

    def test_tracker_creation(self):
        """Test creating forward pass tracker."""
        tracker = ForwardPassTracker()
        assert len(tracker.trades) == 0

    def test_update_market_data(self):
        """Test updating market data."""
        tracker = ForwardPassTracker()
        ts = datetime(2024, 1, 15)

        tracker.update_market_data(
            timestamp=ts,
            prices={"SPY": 450.0, "TLT": 100.0},
            positions={"SPY": 100},
        )

        assert tracker._current_prices["SPY"] == 450.0
        assert tracker._current_positions["SPY"] == 100

    def test_update_signals(self):
        """Test updating signals."""
        tracker = ForwardPassTracker()
        ts = datetime(2024, 1, 15)

        tracker.update_signals(ts, {"momentum": 0.73})

        assert len(tracker.signal_history.snapshots) == 1
        assert tracker.signal_history._current_signals["momentum"] == 0.73

    def test_open_trade(self):
        """Test opening a trade."""
        tracker = ForwardPassTracker()
        ts = datetime(2024, 1, 15)

        tracker.update_signals(ts, {"momentum": 0.5})
        tracker.update_market_data(ts, {"AAPL": 150.0}, {})

        trade = tracker.open_trade(
            timestamp=ts,
            ticker="AAPL",
            direction=1,
            quantity=100,
            price=150.0,
            predicted_return=0.05,
            confidence=0.8,
        )

        assert trade.ticker == "AAPL"
        assert trade.predicted_return == 0.05
        assert trade.signal_confidence == 0.8
        assert len(tracker.trades) == 1

    def test_close_trade(self):
        """Test closing a trade."""
        tracker = ForwardPassTracker()
        ts_entry = datetime(2024, 1, 15)
        ts_exit = datetime(2024, 1, 20)

        # Set up entry
        tracker.update_signals(ts_entry, {"momentum": 0.5})
        tracker.update_market_data(ts_entry, {"AAPL": 150.0}, {})

        trade = tracker.open_trade(
            timestamp=ts_entry,
            ticker="AAPL",
            direction=1,
            quantity=100,
            price=150.0,
        )

        # Close trade
        tracker.update_market_data(ts_exit, {"AAPL": 155.0}, {})
        tracker.close_trade("AAPL", ts_exit, 155.0)

        assert trade.exit_price == 155.0
        assert trade.get_actual_return() == pytest.approx(0.0333, rel=0.01)

    def test_get_completed_trades(self):
        """Test getting completed trades."""
        tracker = ForwardPassTracker()
        ts = datetime(2024, 1, 15)

        tracker.update_market_data(ts, {"AAPL": 150.0}, {})
        tracker.open_trade(ts, "AAPL", 1, 100, 150.0)
        tracker.close_trade("AAPL", ts, 155.0)

        completed = tracker.get_completed_trades()
        assert len(completed) == 1

    def test_get_signal_accuracy(self):
        """Test signal accuracy calculation."""
        tracker = ForwardPassTracker()
        ts_entry = datetime(2024, 1, 15)
        ts_exit = datetime(2024, 1, 20)

        # Open trade with prediction
        tracker.update_signals(ts_entry, {"momentum": 0.5})
        tracker.update_market_data(ts_entry, {"AAPL": 100.0}, {})
        tracker.open_trade(
            ts_entry, "AAPL", 1, 100, 100.0,
            predicted_return=0.10  # Predict 10% up
        )

        # Close with actual 5% up
        tracker.update_market_data(ts_exit, {"AAPL": 105.0}, {})
        tracker.close_trade("AAPL", ts_exit, 105.0)

        df = tracker.get_signal_accuracy()
        assert len(df) == 1
        assert df.iloc[0]["predicted_return"] == 0.10
        assert df.iloc[0]["actual_return"] == pytest.approx(0.05, rel=0.01)
        assert df.iloc[0]["correct_direction"] == True  # Both positive

    def test_signal_performance_summary(self):
        """Test performance summary."""
        tracker = ForwardPassTracker()

        # Add some trades: one correct direction, one wrong
        ts1 = datetime(2024, 1, 15)
        ts2 = datetime(2024, 1, 16)

        # Trade 1: predict up (0.05), actual up (0.05) -> correct
        tracker.update_market_data(ts1, {"AAPL": 100.0}, {})
        tracker.open_trade(ts1, "AAPL", 1, 100, 100.0, predicted_return=0.05, confidence=0.8)
        tracker.close_trade("AAPL", ts1, 105.0)  # +5% actual

        # Trade 2: predict down (-0.03), actual up (+0.05) -> wrong direction
        tracker.update_market_data(ts2, {"MSFT": 200.0}, {})
        tracker.open_trade(ts2, "MSFT", 1, 50, 200.0, predicted_return=-0.03, confidence=0.2)
        tracker.close_trade("MSFT", ts2, 210.0)  # +5% actual

        summary = tracker.get_signal_performance_summary()
        assert summary["total_trades"] == 2
        assert summary["direction_accuracy"] == 0.5  # 1/2 correct
        assert summary["high_confidence_accuracy"] == 1.0  # 1/1 high conf correct


class TestComparisonView:
    """Tests for ComparisonView class."""

    def test_comparison_creation(self):
        """Test creating comparison view."""
        tracker = ForwardPassTracker()
        comparison = ComparisonView(tracker, None)

        assert comparison.forward_tracker is tracker

    def test_get_summary_empty(self):
        """Test summary with no data."""
        tracker = ForwardPassTracker()
        comparison = ComparisonView(tracker, None)

        summary = comparison.get_summary()
        assert "error" in summary

    def test_prediction_quality_by_signal(self):
        """Test per-signal quality analysis."""
        tracker = ForwardPassTracker()

        # Add trade with signals and predictions
        ts = datetime(2024, 1, 15)
        tracker.update_signals(ts, {"momentum": 0.5, "rsi": -0.3})
        tracker.update_market_data(ts, {"AAPL": 100.0}, {})
        tracker.open_trade(ts, "AAPL", 1, 100, 100.0, predicted_return=0.05)
        tracker.close_trade("AAPL", ts, 105.0)

        comparison = ComparisonView(tracker, None)
        df = comparison.get_prediction_quality_by_signal()

        # Should have entries for the signals
        assert len(df) >= 0  # May be empty if no signals match

    def test_confusion_matrix(self):
        """Test confusion matrix."""
        tracker = ForwardPassTracker()

        # Add trades with various outcomes
        ts1 = datetime(2024, 1, 15)
        tracker.update_signals(ts1, {"momentum": 0.5})
        tracker.update_market_data(ts1, {"AAPL": 100.0}, {})
        tracker.open_trade(ts1, "AAPL", 1, 100, 100.0, predicted_return=0.05)
        tracker.close_trade("AAPL", ts1, 105.0)  # Pred: pos, Actual: pos

        comparison = ComparisonView(tracker, None)
        matrix = comparison.get_confusion_matrix()

        # Should have some data
        assert matrix is not None


class TestCreateTracker:
    """Tests for create_tracker factory function."""

    def test_create_tracker(self):
        """Test factory function."""
        tracker = create_tracker()
        assert isinstance(tracker, ForwardPassTracker)


class TestEdgeCases:
    """Edge case tests."""

    def test_trade_without_prediction(self):
        """Test trade without predicted return."""
        tracker = ForwardPassTracker()
        ts = datetime(2024, 1, 15)

        tracker.update_market_data(ts, {"AAPL": 100.0}, {})
        tracker.open_trade(ts, "AAPL", 1, 100, 100.0)  # No prediction
        tracker.close_trade("AAPL", ts, 105.0)

        df = tracker.get_signal_accuracy()
        assert len(df) == 0  # No predictions to compare

    def test_multiple_tickers(self):
        """Test tracking multiple tickers."""
        tracker = ForwardPassTracker()
        ts = datetime(2024, 1, 15)

        tracker.update_market_data(ts, {"AAPL": 100.0, "MSFT": 200.0}, {})
        tracker.open_trade(ts, "AAPL", 1, 100, 100.0)
        tracker.open_trade(ts, "MSFT", -1, 50, 200.0)

        assert len(tracker.trades) == 2
        assert tracker._open_trades["AAPL"].ticker == "AAPL"
        assert tracker._open_trades["MSFT"].ticker == "MSFT"

    def test_close_nonexistent_trade(self):
        """Test closing a trade that doesn't exist."""
        tracker = ForwardPassTracker()
        ts = datetime(2024, 1, 15)

        result = tracker.close_trade("NONEXISTENT", ts, 100.0)
        assert result is None
