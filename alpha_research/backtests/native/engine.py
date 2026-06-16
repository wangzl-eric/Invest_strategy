"""The native event-driven backtest engine (the "cerebro" of this package).

Design lineage:

* **backtrader (Cerebro)** — one orchestrator wires data + strategy + broker +
  analyzers and drives a single bar loop. Users assemble parts and call
  ``run()``.
* **vnpy** — a strict per-bar event loop: every bar the strategy is *pushed*
  state and *emits* orders that the broker turns into trades; nothing is
  computed across the whole panel at once.
* **qlib** — look-ahead is prevented *structurally*. The strategy only ever sees
  ``history`` sliced to ``[:current_bar]`` and trades execute on a configurable
  delay (decision at close *t*, fill at *t* or *t+1*), so the execution
  convention is explicit rather than implied by a ``.shift()`` buried in vector
  code.

Rigor guarantees:

1. **No look-ahead** — ``Context.history`` never contains rows after the
   decision bar; the engine asserts this.
2. **Reconcilable** — run cost-free with daily rebalancing and the net returns
   match ``review.engine.run_weights_backtest`` (shift_bars=1) to ~1e-9.
3. **Accounting closure** — equity is always ``cash + Σ position value``; costs
   leave the book via cash, never by an ad-hoc subtraction from returns.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from alpha_research.backtests.costs.slippage import SlippageModel
from alpha_research.backtests.costs.transaction_costs import CostModel

from .analyzers import AnalysisInput, Analyzer, default_analyzers
from .broker import SimBroker
from .results import BacktestResult
from .strategy import Context, Strategy

TRADING_DAYS = 252


class BacktestEngine:
    """Assemble data + strategy + broker + analyzers and run a bar loop.

    Args:
        prices: Wide close-price frame (DatetimeIndex x symbol). Used for both
            valuation and (by default) execution.
        initial_cash: Starting cash.
        cost_model: Commission model (default: zero — opt into frictions).
        slippage_model: Fill-impact model (default: zero).
        allow_short: Permit negative positions.
        execution_delay: Bars between a decision (at bar *t*'s close) and its
            fill. 0 = fill at the same close (≡ vectorized ``shift_bars=1``);
            1 = fill at the next bar (≡ ``shift_bars=2``).
        exec_prices: Optional separate execution-price frame (e.g. opens). When
            given, fills use these prices; valuation still uses ``prices``.
        analyzers: Analyzer instances to run (default: the standard four).
    """

    def __init__(
        self,
        prices: pd.DataFrame,
        *,
        initial_cash: float = 100_000.0,
        cost_model: Optional[CostModel] = None,
        slippage_model: Optional[SlippageModel] = None,
        allow_short: bool = True,
        execution_delay: int = 0,
        exec_prices: Optional[pd.DataFrame] = None,
        analyzers: Optional[List[Analyzer]] = None,
    ) -> None:
        if not isinstance(prices.index, pd.DatetimeIndex):
            raise ValueError("prices must have a DatetimeIndex")
        if execution_delay < 0:
            raise ValueError("execution_delay must be >= 0")
        if prices.index.has_duplicates:
            raise ValueError(
                "prices index has duplicate timestamps — de-duplicate before "
                "backtesting (duplicates corrupt the bar loop and turnover)"
            )
        if prices.shape[1] == 0:
            raise ValueError("prices has no columns (no tradable symbols)")
        # Drop columns that are entirely NaN — they can never be traded and only
        # pollute weight/exposure bookkeeping.
        all_nan = prices.columns[prices.isna().all()]
        self.prices = prices.drop(columns=list(all_nan)).sort_index()
        if self.prices.shape[1] == 0:
            raise ValueError("every price column is all-NaN — nothing to trade")
        self.exec_prices = (
            exec_prices.reindex(index=self.prices.index, columns=self.prices.columns)
            if exec_prices is not None
            else self.prices
        )
        self.initial_cash = float(initial_cash)
        self.execution_delay = int(execution_delay)
        self.broker = SimBroker(
            initial_cash=initial_cash,
            cost_model=cost_model,
            slippage_model=slippage_model,
            allow_short=allow_short,
        )
        self.analyzers = analyzers if analyzers is not None else default_analyzers()
        self.strategy: Optional[Strategy] = None

    def set_strategy(self, strategy: Strategy) -> "BacktestEngine":
        self.strategy = strategy
        return self

    # -- main loop ---------------------------------------------------------
    def run(self) -> BacktestResult:
        if self.strategy is None:
            raise ValueError("no strategy set — call set_strategy() first")
        if self.prices.empty:
            raise ValueError("prices frame is empty")

        strat = self.strategy
        strat.on_start()

        index = self.prices.index
        symbols = list(self.prices.columns)
        delay = self.execution_delay

        equity_records: Dict[pd.Timestamp, float] = {}
        weight_rows: Dict[pd.Timestamp, Dict[str, float]] = {}
        position_rows: Dict[pd.Timestamp, Dict[str, float]] = {}
        turnover_records: Dict[pd.Timestamp, float] = {}
        pending: Dict[int, List] = {}

        for i, d in enumerate(index):
            close_row = self.prices.iloc[i]
            close_prices = {s: float(close_row[s]) for s in symbols}
            exec_row = self.exec_prices.iloc[i]
            exec_prices = {s: float(exec_row[s]) for s in symbols}

            # 1. Fill any orders scheduled to execute on this bar (delay > 0).
            traded_notional = 0.0
            for order in pending.pop(i, []):
                trade = self.broker.execute(order, exec_prices.get(order.symbol), d)
                if trade is not None:
                    traded_notional += trade.notional

            # 2. Decision: hand the strategy state through `now` (no future rows).
            #    NO-LOOK-AHEAD GUARANTEE: history is sliced to [:i+1] so its last
            #    row is exactly the decision bar `d`. This is an always-on check
            #    (not `assert`, which `python -O` would strip) — the single most
            #    important invariant of the engine. A target set here only earns
            #    *forward* returns (it is filled at `d`'s close or later and
            #    marked at the next bar), so it can never use information that
            #    was not knowable at `d`.
            history = self.prices.iloc[: i + 1]
            if history.index[-1] != d:  # pragma: no cover - invariant guard
                raise RuntimeError(
                    "look-ahead guard tripped: history extends beyond the "
                    f"decision bar ({history.index[-1]} > {d})"
                )
            pre_equity = self.broker.equity(close_prices)
            ctx = Context(
                now=d,
                history=history,
                prices=close_prices,
                equity=pre_equity,
                weights=self.broker.weights(close_prices),
                positions={
                    s: p.quantity for s, p in self.broker.account.positions.items()
                },
            )
            strat.on_bar(ctx)

            # 3. Route orders: fill now (delay 0) or schedule for bar i+delay.
            if delay == 0:
                for order in ctx.pending_orders:
                    trade = self.broker.execute(order, exec_prices.get(order.symbol), d)
                    if trade is not None:
                        traded_notional += trade.notional
            else:
                exec_idx = i + delay
                if exec_idx < len(index):
                    pending.setdefault(exec_idx, []).extend(ctx.pending_orders)

            # 4. Record post-bar state (marked at this bar's close).
            equity_records[d] = self.broker.equity(close_prices)
            weight_rows[d] = self.broker.weights(close_prices)
            position_rows[d] = {
                s: p.quantity for s, p in self.broker.account.positions.items()
            }
            turnover_records[d] = (
                traded_notional / pre_equity if pre_equity > 0 else 0.0
            )

        strat.on_finish()

        return self._build_result(
            index, symbols, equity_records, weight_rows, position_rows, turnover_records
        )

    # -- assembly ----------------------------------------------------------
    def _build_result(
        self,
        index: pd.DatetimeIndex,
        symbols: List[str],
        equity_records: Dict,
        weight_rows: Dict,
        position_rows: Dict,
        turnover_records: Dict,
    ) -> BacktestResult:
        equity_full = pd.Series(equity_records).reindex(index)
        positions_full = (
            pd.DataFrame(position_rows).T.reindex(index).fillna(0.0)
            if position_rows
            else pd.DataFrame(index=index)
        )

        # Trim warm-up: returns begin the bar AFTER the first non-flat position,
        # matching run_weights_backtest's `valid` mask (first earning day).
        # Returns are computed on the FULL equity series first, then sliced, so
        # the first earning day's return is not lost to pct_change's leading NaN.
        has_pos = (
            positions_full.abs().sum(axis=1) > 1e-12
            if not positions_full.empty
            else pd.Series(False, index=index)
        )
        returns_full = equity_full.pct_change()
        if has_pos.any() and index.get_loc(has_pos.idxmax()) + 1 < len(index):
            first_earn = index[index.get_loc(has_pos.idxmax()) + 1]
            returns = returns_full.loc[first_earn:]
        else:
            returns = returns_full.dropna()

        # Rebase the equity curve to initial_cash over the active window.
        if len(returns) > 0:
            equity = (1.0 + returns).cumprod() * self.initial_cash
        else:
            equity = pd.Series(dtype=float)

        weights_df = (
            pd.DataFrame(weight_rows).T.reindex(returns.index).fillna(0.0)
            if weight_rows
            else pd.DataFrame(index=returns.index)
        )
        positions_df = positions_full.reindex(returns.index).fillna(0.0)
        turnover = pd.Series(turnover_records).reindex(returns.index).fillna(0.0)

        metrics = self._headline_metrics(returns, equity, turnover)

        analysis_in = AnalysisInput(
            returns=returns,
            equity=equity,
            turnover=turnover,
            trades=self.broker.trades,
        )
        analyzer_out = {a.name: a.analyze(analysis_in) for a in self.analyzers}

        equity_curve = pd.DataFrame(
            {"date": equity.index, "portfolio_value": equity.values}
        )
        return BacktestResult(
            daily_returns=returns,
            equity_curve=equity_curve,
            weights=weights_df,
            positions=positions_df,
            turnover=turnover,
            trades=list(self.broker.trades),
            metrics=metrics,
            analyzers=analyzer_out,
        )

    def rebuild_with_returns(
        self, base: BacktestResult, net_returns: pd.Series
    ) -> BacktestResult:
        """Return a new result with ``net_returns`` substituted for the daily
        returns, recomputing the equity curve, headline metrics, and analyzers.

        Used by the parity path (``api._backtest_weights_parity``): the event
        loop supplies the verified gross stream and per-bar weights/positions/
        trades, and this swaps in a net stream derived under a different cost
        convention without re-running the loop.
        """
        net = net_returns.reindex(base.daily_returns.index).astype(float)
        equity = (1.0 + net).cumprod() * self.initial_cash
        turnover = base.turnover
        metrics = self._headline_metrics(net, equity, turnover)
        analysis_in = AnalysisInput(
            returns=net, equity=equity, turnover=turnover, trades=base.trades
        )
        analyzer_out = {a.name: a.analyze(analysis_in) for a in self.analyzers}
        equity_curve = pd.DataFrame(
            {"date": equity.index, "portfolio_value": equity.values}
        )
        return BacktestResult(
            daily_returns=net,
            equity_curve=equity_curve,
            weights=base.weights,
            positions=base.positions,
            turnover=turnover,
            trades=base.trades,
            metrics=metrics,
            analyzers=analyzer_out,
        )

    def _headline_metrics(
        self, returns: pd.Series, equity: pd.Series, turnover: pd.Series
    ) -> Dict[str, float]:
        n = len(returns)
        if n == 0:
            return {"n_days": 0.0}
        total_return = float(equity.iloc[-1] / self.initial_cash - 1.0)
        vol = float(returns.std() * np.sqrt(TRADING_DAYS))
        sharpe = (
            float(returns.mean() / returns.std() * np.sqrt(TRADING_DAYS))
            if returns.std() > 0
            else 0.0
        )
        peak = equity.cummax()
        drawdown = (equity - peak) / peak
        return {
            "total_return": total_return,
            "annualized_return": float((1 + total_return) ** (TRADING_DAYS / n) - 1),
            "volatility": vol,
            "sharpe_ratio": sharpe,
            "max_drawdown": float(drawdown.min()),
            "annual_turnover": float(turnover.mean() * TRADING_DAYS),
            "total_commission": float(self.broker.total_commission),
            "total_slippage": float(self.broker.total_slippage),
            "n_days": float(n),
        }


__all__ = ["BacktestEngine"]
