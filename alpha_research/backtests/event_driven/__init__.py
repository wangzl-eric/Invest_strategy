"""Event-driven backtesting — the Backtrader execution-sim adapter.

The native event-driven engine now lives in ``alpha_research.backtests.native``
(the former ``EventDrivenBacktester`` skeleton here was retired in its favour).
What remains is the heavyweight Backtrader adapter (``backtest_engine``), imported
lazily and only re-exported when ``backtrader`` is installed, so importing this
package never hard-requires that optional dependency.
"""

try:  # optional: the Backtrader execution-sim adapter
    from alpha_research.backtests.event_driven.backtest_engine import (  # noqa: F401
        BacktestEngine,
        HistoricalPercentSizer,
        IBKRDataFeed,
        LiveTradingEngine,
        ParquetDataFeed,
        VolatilitySizer,
        create_mean_reversion_strategy,
        create_momentum_strategy,
        create_signal_strategy,
        make_ibkr_dataname,
        quick_backtest,
    )

    _BACKTRADER_AVAILABLE = True
    __all__ = [
        "BacktestEngine",
        "LiveTradingEngine",
        "IBKRDataFeed",
        "ParquetDataFeed",
        "VolatilitySizer",
        "HistoricalPercentSizer",
        "create_momentum_strategy",
        "create_mean_reversion_strategy",
        "create_signal_strategy",
        "quick_backtest",
        "make_ibkr_dataname",
    ]
except ImportError:  # pragma: no cover - exercised only when backtrader absent
    _BACKTRADER_AVAILABLE = False
    __all__ = []
