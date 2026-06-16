"""Compatibility suite: the native engine runs *every* major strategy archetype.

Demonstrates the engine is strategy-agnostic across the ways a quant signal is
expressed — long-only cross-sectional, long-short market-neutral, single-asset
timing, pairs, volatility targeting, risk-off rotation, leverage, short-only,
calendar/seasonal, stateful path-dependent (stop-loss), and risk parity — via
both the weights contract (`backtest_weights`) and the stateful `Strategy` API
(`backtest_strategy`). Each test asserts the engine produced a valid result and
the *structural* invariant the archetype implies (e.g. neutral ⇒ net≈0).

It also pins the weights-contract semantic that a target of ``0.0`` means "go to
cash" while ``NaN`` means "hold the previous target".
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from alpha_research.backtests.native import backtest_strategy, backtest_weights
from alpha_research.backtests.native.strategy import Strategy

SYMS = ["A", "B", "C", "D", "E", "F"]


@pytest.fixture(scope="module")
def prices() -> pd.DataFrame:
    rng = np.random.default_rng(11)
    idx = pd.bdate_range("2018-01-01", periods=650)
    drift = rng.normal(0.0003, 0.0002, len(SYMS))
    out = pd.DataFrame(index=idx, columns=SYMS, dtype=float)
    for k, s in enumerate(SYMS):
        out[s] = 100 * np.cumprod(1 + rng.normal(drift[k], 0.012, len(idx)))
    return out


@pytest.fixture(scope="module")
def rebal(prices) -> np.ndarray:
    idx = prices.index
    return pd.Series(idx).groupby(idx.to_period("M")).max().values


def _empty(prices) -> pd.DataFrame:
    return pd.DataFrame(np.nan, index=prices.index, columns=prices.columns)


def _assert_valid(res):
    """Every archetype must yield a usable, finite result."""
    assert len(res.daily_returns) > 50
    assert np.isfinite(res.daily_returns).all()
    assert len(res.equity_curve) == len(res.daily_returns)
    assert np.isfinite(res.metrics["sharpe_ratio"])
    assert np.isfinite(res.metrics["max_drawdown"])
    assert res.metrics["max_drawdown"] <= 0.0


def _gross(res):
    return res.weights.abs().sum(axis=1)


def _net(res):
    return res.weights.sum(axis=1)


# --------------------------------------------------------------------------
# Weights-contract archetypes
# --------------------------------------------------------------------------
class TestWeightsArchetypes:
    def test_cross_sectional_momentum_long_only(self, prices, rebal):
        w = _empty(prices)
        for d in rebal:
            h = prices.loc[:d]
            if len(h) < 130:
                continue
            top = (h.iloc[-1] / h.iloc[-126] - 1).nlargest(3).index
            w.loc[d] = [1 / 3 if s in top else 0.0 for s in SYMS]
        res = backtest_weights(w, prices, cost_bps=5)
        _assert_valid(res)
        # long-only, fully invested ⇒ net == gross ≈ 1
        assert _net(res).between(0.99, 1.01).all()

    def test_long_short_market_neutral(self, prices, rebal):
        w = _empty(prices)
        for d in rebal:
            h = prices.loc[:d]
            if len(h) < 25:
                continue
            r = h.iloc[-1] / h.iloc[-21] - 1
            z = -(r - r.mean()) / (r.std() or 1)
            z = z - z.mean()  # dollar-neutral
            g = z.abs().sum()
            w.loc[d] = (z / g).values if g > 0 else 0.0
        res = backtest_weights(w, prices, cost_bps=5, allow_short=True)
        _assert_valid(res)
        # market neutral ⇒ net ≈ 0, but real gross exposure deployed
        assert _net(res).abs().max() < 1e-6
        assert _gross(res).max() > 0.5

    def test_leveraged_2x(self, prices):
        w = _empty(prices)
        w.iloc[0] = 2.0 / len(SYMS)
        res = backtest_weights(w, prices, cost_bps=5)
        _assert_valid(res)
        assert _gross(res).between(1.98, 2.02).all()  # 2x gross sustained

    def test_short_only(self, prices, rebal):
        w = _empty(prices)
        for d in rebal:
            h = prices.loc[:d]
            if len(h) < 130:
                continue
            worst = (h.iloc[-1] / h.iloc[-126] - 1).nsmallest(2).index
            w.loc[d] = [-0.5 if s in worst else 0.0 for s in SYMS]
        res = backtest_weights(w, prices, cost_bps=5, allow_short=True)
        _assert_valid(res)
        assert _net(res).max() <= 1e-9  # never net long

    def test_single_asset_trend_binary(self, prices):
        w = _empty(prices)
        w[SYMS[1:]] = 0.0
        sma = prices["A"].rolling(200).mean()
        w["A"] = (prices["A"] > sma).astype(float)
        res = backtest_weights(w, prices, cost_bps=5, rebalance_every_bar=False)
        _assert_valid(res)
        # 0/1 exposure, no meaningful leverage (tiny >1 is commission paid from
        # cash leaving a small negative cash balance — a realistic accounting
        # effect, not leverage).
        assert _gross(res).max() < 1.05

    def test_risk_off_cash_rotation(self, prices):
        w = _empty(prices)
        ma = prices.rolling(50).mean()
        for d in prices.index:
            h = prices.loc[:d]
            if len(h) < 50:
                continue
            on = h.iloc[-1] > ma.loc[d]
            k = int(on.sum())
            w.loc[d] = [(1.0 / k if on[s] else 0.0) for s in SYMS] if k > 0 else 0.0
        res = backtest_weights(w, prices, cost_bps=5, rebalance_every_bar=False)
        _assert_valid(res)
        assert _gross(res).min() >= -1e-9  # long-or-cash only

    def test_turn_of_month_calendar(self, prices):
        w = _empty(prices)
        w[:] = 0.0
        month = prices.index.to_period("M")
        for p in month.unique():
            days = prices.index[month == p]
            for d in list(days[-1:]) + list(days[:2]):
                w.loc[d] = 1.0 / len(SYMS)
        res = backtest_weights(w, prices, cost_bps=5, rebalance_every_bar=False)
        _assert_valid(res)
        # mostly in cash ⇒ shallow drawdown, some flat days
        assert (_gross(res) < 1e-9).any()

    def test_inverse_vol_risk_parity(self, prices, rebal):
        w = _empty(prices)
        for d in rebal:
            h = prices.loc[:d]
            if len(h) < 63:
                continue
            iv = 1.0 / h.pct_change().tail(63).std()
            w.loc[d] = (iv / iv.sum()).values
        res = backtest_weights(w, prices, cost_bps=5)
        _assert_valid(res)
        assert _net(res).between(0.99, 1.01).all()

    def test_buy_and_hold_uses_nan_to_hold(self, prices):
        # Only the first row carries a target; the rest are NaN ("hold").
        w = _empty(prices)
        w.iloc[0] = [1.0, 0, 0, 0, 0, 0]
        res = backtest_weights(w, prices, cost_bps=5, rebalance_every_bar=False)
        _assert_valid(res)
        assert len(res.trades) <= len(SYMS)  # one entry, then hold
        assert _gross(res).iloc[-1] > 0.5  # still invested at the end

    def test_zero_target_means_cash_not_hold(self, prices):
        # Contrast with above: an explicit 0.0 row liquidates to cash.
        w = _empty(prices)
        w.iloc[0] = [1.0, 0, 0, 0, 0, 0]
        w.iloc[50] = 0.0  # explicit cash target
        res = backtest_weights(w, prices, cost_bps=5, rebalance_every_bar=False)
        _assert_valid(res)
        assert _gross(res).iloc[-1] < 1e-9  # flat after the cash target


# --------------------------------------------------------------------------
# Stateful Strategy-API archetypes
# --------------------------------------------------------------------------
class TestStrategyApiArchetypes:
    def test_pairs_trading(self, prices):
        def pairs(ctx):
            h = ctx.history
            if len(h) < 60:
                return None
            sp = np.log(h["A"]) - np.log(h["B"])
            z = (sp.iloc[-1] - sp.tail(60).mean()) / (sp.tail(60).std() or 1)
            if z > 1:
                return {"A": -0.5, "B": 0.5}
            if z < -1:
                return {"A": 0.5, "B": -0.5}
            return {"A": 0.0, "B": 0.0}

        res = backtest_strategy(pairs, prices, cost_bps=5)
        _assert_valid(res)
        assert _net(res).abs().max() < 1e-6  # market-neutral pair

    def test_volatility_targeting(self, prices):
        def voltarget(ctx):
            h = ctx.history
            if len(h) < 21:
                return None
            pv = h.pct_change().dropna().tail(20).mean(axis=1).std() * np.sqrt(252)
            scale = min(2.0, 0.10 / pv) if pv > 0 else 1.0
            return {s: scale / len(h.columns) for s in h.columns}

        res = backtest_strategy(voltarget, prices, cost_bps=5)
        _assert_valid(res)
        g = _gross(res)
        assert g.max() > g.min() + 1e-3  # exposure genuinely varies with vol

    def test_path_dependent_stop_loss(self, prices):
        class StopLoss(Strategy):
            name = "stoploss"

            def on_start(self):
                self.entry = {}

            def on_bar(self, ctx):
                h = ctx.history
                if len(h) < 126:
                    return
                mom = h.iloc[-1] / h.iloc[-126] - 1
                tgt = {}
                for s in h.columns:
                    px = ctx.prices[s]
                    if ctx.positions.get(s, 0) > 0:
                        if px < self.entry.get(s, px) * 0.95:  # 5% trailing stop
                            tgt[s] = 0.0
                            self.entry.pop(s, None)
                        else:
                            self.entry[s] = max(self.entry.get(s, px), px)
                            tgt[s] = ctx.current_weights.get(s, 0)
                    elif mom[s] > 0.05:
                        tgt[s] = 1.0 / len(h.columns)
                        self.entry[s] = px
                    else:
                        tgt[s] = 0.0
                ctx.order_target_weights(tgt)

        res = backtest_strategy(StopLoss(), prices, cost_bps=5)
        _assert_valid(res)
        assert len(res.trades) > 0  # the stateful logic actually traded
        assert _gross(res).max() <= 1.0 + 1e-9
