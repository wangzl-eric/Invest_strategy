"""Compatibility shim for the event-driven backtest engine.

The canonical implementation now lives in
`workstation.backtests.event_driven.backtest_engine`. Keep this module in
place so existing imports like `backend.backtest_engine` continue to work
during the layout transition.
"""

from workstation.backtests.event_driven.backtest_engine import *  # noqa: F401,F403
