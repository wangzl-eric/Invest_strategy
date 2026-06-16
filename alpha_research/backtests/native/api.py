"""User-friendly one-call entry points for the native engine.

These wrap the ``BacktestEngine`` for the two most common workflows so a
researcher never has to touch the broker/analyzer plumbing for a basic run:

* ``backtest_weights`` — backtest a precomputed target-weights frame (the repo
  "weights contract"). The signature deliberately mirrors
  ``review.engine.run_weights_backtest`` (``cost_bps`` / ``shift_bars`` /
  ``initial_cash``) so it is a drop-in alternative with realistic share-based
  accounting.
* ``backtest_strategy`` — backtest a ``Strategy`` subclass or a
  ``fn(ctx) -> {symbol: weight}`` closure.

``shift_bars`` maps to the engine's ``execution_delay`` as ``shift_bars - 1`` so
the execution convention lines up exactly with the vectorized engine and the
manifest ``ExecutionConvention``.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional, Union

import pandas as pd

from alpha_research.backtests.costs.slippage import FixedSlippageModel, SlippageModel
from alpha_research.backtests.costs.transaction_costs import (
    CostModel,
    ProportionalCostModel,
)

from .analyzers import default_analyzers
from .engine import BacktestEngine
from .results import BacktestResult
from .strategy import CallableStrategy, Context, Strategy, WeightsStrategy


def backtest_weights(
    weights: pd.DataFrame,
    prices: pd.DataFrame,
    *,
    cost_bps: float = 5.0,
    shift_bars: int = 1,
    initial_cash: float = 100_000.0,
    slippage_bps: float = 0.0,
    allow_short: bool = True,
    rebalance_every_bar: bool = True,
    cost_basis: str = "traded",
    analyzers: Optional[list] = None,
) -> BacktestResult:
    """Backtest a target-weights frame with the native event-driven engine.

    Args mirror ``run_weights_backtest`` plus event-driven extras
    (``slippage_bps``, ``rebalance_every_bar``). Returns a native
    ``BacktestResult`` (richer than the vectorized one: trades, positions,
    per-bar turnover).

    ``cost_basis`` selects how transaction costs are charged:

    * ``"traded"`` (default) — realistic: commission/slippage on the *actual*
      shares filled (includes drift-correction trading and decision-to-fill
      price gap). This is the event-driven engine's honest answer.
    * ``"target"`` — *parity* mode: costs charged on the change in **target
      weights** (the vectorized convention), so the NET PnL reproduces
      ``review.engine.run_weights_backtest`` bit-for-bit. Use this to verify the
      two engines agree (see ``backtests.equivalence``). ``slippage_bps`` is
      ignored in parity mode (the vectorized engine has no slippage concept).
    """
    if shift_bars < 1:
        raise ValueError("shift_bars must be >= 1 (0 would be look-ahead)")
    if cost_basis not in ("traded", "target"):
        raise ValueError("cost_basis must be 'traded' or 'target'")

    if cost_basis == "target":
        return _backtest_weights_parity(
            weights,
            prices,
            cost_bps=cost_bps,
            shift_bars=shift_bars,
            initial_cash=initial_cash,
            allow_short=allow_short,
            rebalance_every_bar=rebalance_every_bar,
            analyzers=analyzers,
        )

    cost_model: CostModel = ProportionalCostModel(cost_bps=cost_bps)
    slippage_model: SlippageModel = FixedSlippageModel(slippage_bps=slippage_bps)
    engine = BacktestEngine(
        prices,
        initial_cash=initial_cash,
        cost_model=cost_model,
        slippage_model=slippage_model,
        allow_short=allow_short,
        execution_delay=shift_bars - 1,
        analyzers=analyzers if analyzers is not None else default_analyzers(),
    )
    engine.set_strategy(
        WeightsStrategy(weights, rebalance_every_bar=rebalance_every_bar)
    )
    return engine.run()


def _target_turnover_cost(
    weights: pd.DataFrame,
    prices: pd.DataFrame,
    *,
    cost_bps: float,
    shift_bars: int,
    on_index: pd.DatetimeIndex,
) -> pd.Series:
    """Canonical turnover cost charged on *target*-weight changes.

    Reproduces ``run_weights_backtest``'s cost term exactly: align targets to the
    price calendar (ffill), apply the execution shift, then charge
    ``cost_bps`` on the one-way bar-over-bar change in effective weights (day 1 =
    full entry). Restricted to ``on_index`` (the native engine's earning days).
    """
    common = [c for c in weights.columns if c in prices.columns]
    px = prices[common].sort_index()
    w_eff = weights[common].sort_index().reindex(px.index).ffill().shift(shift_bars)
    w_eff = w_eff.reindex(on_index).fillna(0.0)
    dw = w_eff.diff().abs()
    if len(dw):
        dw.iloc[0] = w_eff.iloc[0].abs()
    return dw.sum(axis=1) * (cost_bps / 10_000.0)


def _backtest_weights_parity(
    weights: pd.DataFrame,
    prices: pd.DataFrame,
    *,
    cost_bps: float,
    shift_bars: int,
    initial_cash: float,
    allow_short: bool,
    rebalance_every_bar: bool,
    analyzers: Optional[list],
) -> BacktestResult:
    """Native engine in vectorized-parity mode (see ``backtest_weights``).

    Runs the event loop *frictionless* to obtain an independently-computed gross
    return stream, then deducts the canonical target-turnover cost. Because the
    gross matches ``run_weights_backtest`` to machine precision and the cost term
    is identical, the NET PnL matches the vectorized engine exactly for any
    ``shift_bars``.

    The vectorized shift is emulated on the *price calendar*: targets are aligned
    (ffill) to daily bars and shifted by ``shift_bars - 1`` rows, then run with
    zero execution delay and daily mark-to-target. A native ``execution_delay``
    would instead carry a stale share count to the next bar (realistic drift),
    which is correct for ``"traded"`` mode but breaks bit-for-bit parity.
    """
    del rebalance_every_bar  # parity always marks to target daily
    common = [c for c in weights.columns if c in prices.columns]
    px = prices[common].sort_index()
    daily_target = (
        weights[common].sort_index().reindex(px.index).ffill().shift(shift_bars - 1)
    )
    engine = BacktestEngine(
        prices,
        initial_cash=initial_cash,
        cost_model=ProportionalCostModel(cost_bps=0.0),
        slippage_model=FixedSlippageModel(slippage_bps=0.0),
        allow_short=allow_short,
        execution_delay=0,
        analyzers=analyzers if analyzers is not None else default_analyzers(),
    )
    engine.set_strategy(WeightsStrategy(daily_target, rebalance_every_bar=True))
    gross_result = engine.run()
    gross = gross_result.daily_returns
    cost = _target_turnover_cost(
        weights, prices, cost_bps=cost_bps, shift_bars=shift_bars, on_index=gross.index
    )
    net = (gross - cost).astype(float)
    return engine.rebuild_with_returns(gross_result, net)


def backtest_strategy(
    strategy: Union[Strategy, Callable[[Context], Optional[Dict[str, float]]]],
    prices: pd.DataFrame,
    *,
    cost_bps: float = 5.0,
    shift_bars: int = 1,
    initial_cash: float = 100_000.0,
    slippage_bps: float = 0.0,
    allow_short: bool = True,
    analyzers: Optional[list] = None,
) -> BacktestResult:
    """Backtest a ``Strategy`` subclass or a ``fn(ctx) -> weights`` closure."""
    if shift_bars < 1:
        raise ValueError("shift_bars must be >= 1 (0 would be look-ahead)")
    strat: Strategy = (
        strategy if isinstance(strategy, Strategy) else CallableStrategy(strategy)
    )
    engine = BacktestEngine(
        prices,
        initial_cash=initial_cash,
        cost_model=ProportionalCostModel(cost_bps=cost_bps),
        slippage_model=FixedSlippageModel(slippage_bps=slippage_bps),
        allow_short=allow_short,
        execution_delay=shift_bars - 1,
        analyzers=analyzers if analyzers is not None else default_analyzers(),
    )
    engine.set_strategy(strat)
    return engine.run()


__all__ = ["backtest_weights", "backtest_strategy"]
