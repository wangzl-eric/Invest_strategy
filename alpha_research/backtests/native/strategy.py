"""Strategy API and the point-in-time context handed to it each bar.

Design lineage:

* **backtrader** — a ``Strategy`` base class with lifecycle hooks
  (``on_start`` / ``on_bar`` / ``on_finish``) and high-level order helpers
  (``order_target_percent``) so users express *intent* (target exposure) rather
  than share arithmetic.
* **qlib** — a hard separation between *signal/decision* and *execution*. The
  strategy only ever receives a ``Context`` exposing history **up to and
  including the current bar** — never the future — which makes look-ahead a
  structural impossibility rather than a convention to remember.

The two built-in strategies cover the common cases:

* ``WeightsStrategy`` — replay a precomputed target-weights frame (the repo's
  "weights contract"), so any existing manifest runner plugs straight in.
* ``CallableStrategy`` — wrap a ``fn(context) -> {symbol: weight}`` closure for
  quick experiments without subclassing.
"""

from __future__ import annotations

from datetime import datetime
from typing import Callable, Dict, List, Optional

import pandas as pd

from .objects import Order


class Context:
    """Read-only-by-convention view of the world at one decision bar.

    The engine constructs a fresh ``Context`` for every bar and guarantees that
    ``history`` contains **no rows after** ``now``. Strategies read state and
    push orders via the ``order_*`` helpers; the engine drains ``pending_orders``
    after ``on_bar`` returns.
    """

    def __init__(
        self,
        *,
        now: datetime,
        history: pd.DataFrame,
        prices: Dict[str, float],
        equity: float,
        weights: Dict[str, float],
        positions: Dict[str, float],
    ) -> None:
        self.now = now
        self.history = history  # close prices up to and including `now`
        self.prices = prices  # latest close per symbol at `now`
        self.equity = equity
        self.current_weights = weights
        self.positions = positions  # symbol -> share quantity
        self.pending_orders: List[Order] = []
        self._target_weights: Optional[Dict[str, float]] = None

    # -- order helpers -----------------------------------------------------
    def order_shares(self, symbol: str, quantity: float) -> None:
        """Queue a market order for a signed share delta."""
        if quantity and abs(quantity) > 1e-12:
            self.pending_orders.append(
                Order(symbol=symbol, quantity=float(quantity), created_dt=self.now)
            )

    def order_target_percent(self, symbol: str, pct: float) -> None:
        """Trade ``symbol`` to ``pct`` of current equity (backtrader semantics)."""
        price = self.prices.get(symbol)
        if price is None or price != price or price <= 0:
            return
        target_value = pct * self.equity
        current_value = self.positions.get(symbol, 0.0) * price
        delta_shares = (target_value - current_value) / price
        self.order_shares(symbol, delta_shares)

    def order_target_weights(self, weights: Dict[str, float]) -> None:
        """Rebalance the whole book to a ``{symbol: weight}`` target map.

        Symbols held but absent from ``weights`` are closed. Recorded as the
        bar's target so the engine can report effective weights.
        """
        self._target_weights = dict(weights)
        symbols = set(weights) | set(self.positions)
        for sym in symbols:
            self.order_target_percent(sym, float(weights.get(sym, 0.0)))


class Strategy:
    """Base class for native-engine strategies.

    Subclass and override ``on_bar``. ``on_start`` / ``on_finish`` are optional
    setup/teardown hooks. The engine injects per-bar state through ``Context``.
    """

    name: str = "strategy"

    def on_start(self) -> None:  # pragma: no cover - optional hook
        pass

    def on_bar(self, ctx: Context) -> None:
        raise NotImplementedError

    def on_finish(self) -> None:  # pragma: no cover - optional hook
        pass


class CallableStrategy(Strategy):
    """Adapt a ``fn(ctx) -> {symbol: weight}`` closure into a ``Strategy``."""

    def __init__(
        self,
        fn: Callable[[Context], Optional[Dict[str, float]]],
        name: str = "callable",
    ) -> None:
        self.fn = fn
        self.name = name

    def on_bar(self, ctx: Context) -> None:
        target = self.fn(ctx)
        if target:
            ctx.order_target_weights(target)


class WeightsStrategy(Strategy):
    """Replay a precomputed target-weights frame (the repo weights contract).

    ``weights`` is a ``DatetimeIndex x ticker`` frame of *unshifted* target
    weights (NaN = no target that day). The strategy forward-fills the most
    recent target and rebalances to it. With ``rebalance_every_bar=True``
    (default) it re-issues a full rebalance every bar (matching the vectorized
    engine's daily mark-to-target); set it False to trade only when the target
    row actually changes (lower turnover, more realistic).
    """

    def __init__(
        self,
        weights: pd.DataFrame,
        *,
        name: str = "weights",
        rebalance_every_bar: bool = True,
    ) -> None:
        if not isinstance(weights.index, pd.DatetimeIndex):
            raise ValueError("weights must have a DatetimeIndex")
        self.weights = weights.sort_index()
        self.name = name
        self.rebalance_every_bar = rebalance_every_bar
        self._last_target: Optional[Dict[str, float]] = None

    def _target_as_of(self, now: datetime) -> Optional[Dict[str, float]]:
        rows = self.weights.loc[:now]
        if rows.empty:
            return None
        # Carry forward the most recent *issued* target: an all-NaN row means
        # "no new target — hold the previous one" (the weights-contract rule).
        issued = rows.dropna(how="all")
        if issued.empty:
            return None
        latest = issued.iloc[-1]
        return {k: float(v) for k, v in latest.items() if v == v}  # drop NaNs

    def on_bar(self, ctx: Context) -> None:
        target = self._target_as_of(ctx.now)
        if target is None:
            return
        if not self.rebalance_every_bar and target == self._last_target:
            return
        self._last_target = target
        ctx.order_target_weights(target)


__all__ = ["Context", "Strategy", "CallableStrategy", "WeightsStrategy"]
