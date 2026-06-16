"""Unit tests for the native event-driven backtest engine.

Covers objects, broker, strategy/context, the engine loop, analyzers, the
one-call API, results, input validation, and — most importantly — the
no-look-ahead guarantee and reconciliation against the vectorized engine.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from alpha_research.backtests.costs.slippage import FixedSlippageModel
from alpha_research.backtests.costs.transaction_costs import ProportionalCostModel
from alpha_research.backtests.native import (
    Account,
    AnalysisInput,
    BacktestEngine,
    BacktestResult,
    Bar,
    Context,
    Direction,
    DrawdownAnalyzer,
    Order,
    OrderStatus,
    OrderType,
    PerformanceAnalyzer,
    Position,
    ReturnsAnalyzer,
    SharpeAnalyzer,
    SimBroker,
    StatsAnalyzer,
    Strategy,
    Trade,
    TradeAnalyzer,
    WeightsStrategy,
    backtest_strategy,
    backtest_weights,
    default_analyzers,
)
from alpha_research.review.engine import run_weights_backtest


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------
@pytest.fixture
def prices() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    idx = pd.bdate_range("2020-01-01", periods=300)
    syms = ["AAA", "BBB", "CCC"]
    data = 100 * np.cumprod(1 + rng.normal(0.0004, 0.01, (len(idx), 3)), axis=0)
    return pd.DataFrame(data, index=idx, columns=syms)


@pytest.fixture
def const_weights(prices) -> pd.DataFrame:
    w = pd.DataFrame(np.nan, index=prices.index, columns=prices.columns)
    w.iloc[0] = [0.4, 0.35, 0.25]
    return w


@pytest.fixture
def monthly_weights(prices) -> pd.DataFrame:
    # Deterministic rotating weight vectors (avoid np.random.dirichlet, which
    # trips numpy's _NoValue sentinel when conftest reloads numpy under coverage).
    vectors = [
        [0.5, 0.3, 0.2],
        [0.2, 0.5, 0.3],
        [0.34, 0.33, 0.33],
        [0.6, 0.1, 0.3],
    ]
    w = pd.DataFrame(np.nan, index=prices.index, columns=prices.columns)
    rebal = pd.Series(prices.index).groupby(prices.index.to_period("M")).max().values
    for i, d in enumerate(rebal):
        w.loc[d] = vectors[i % len(vectors)]
    return w


# --------------------------------------------------------------------------
# Objects
# --------------------------------------------------------------------------
class TestObjects:
    def test_direction_sign(self):
        assert Direction.LONG.sign == 1
        assert Direction.SHORT.sign == -1

    def test_bar_price_accessor(self):
        from datetime import datetime

        b = Bar(dt=datetime(2020, 1, 1), symbol="X", close=100.0, open=99.0)
        assert b.price() == 100.0
        assert b.price("open") == 99.0

    def test_order_direction(self):
        assert Order("X", 5).direction == Direction.LONG
        assert Order("X", -5).direction == Direction.SHORT
        assert Order("X", 5).order_type == OrderType.MARKET
        assert Order("X", 5).status == OrderStatus.SUBMITTED

    def test_trade_notional_and_direction(self):
        from datetime import datetime

        t = Trade(dt=datetime(2020, 1, 1), symbol="X", quantity=-10, price=50.0)
        assert t.notional == 500.0
        assert t.direction == Direction.SHORT

    def test_position_open_and_add(self):
        p = Position("X")
        p.apply_trade(10, 100)
        p.apply_trade(5, 110)
        assert p.quantity == 15
        assert p.avg_price == pytest.approx(103.3333, rel=1e-4)
        assert p.market_value(120) == pytest.approx(1800)
        assert p.unrealized_pnl(120) == pytest.approx((120 - 103.3333) * 15, rel=1e-3)

    def test_position_reduce_books_realized_pnl(self):
        p = Position("X")
        p.apply_trade(10, 100)
        p.apply_trade(-4, 120)
        assert p.quantity == 6
        assert p.realized_pnl == pytest.approx((120 - 100) * 4)
        assert p.avg_price == pytest.approx(100)  # unchanged on a pure reduction

    def test_position_flip_through_zero(self):
        p = Position("X")
        p.apply_trade(10, 100)
        p.apply_trade(-15, 120)  # close 10, open 5 short
        assert p.quantity == -5
        assert p.avg_price == pytest.approx(120)
        assert p.realized_pnl == pytest.approx((120 - 100) * 10)

    def test_position_full_close_resets(self):
        p = Position("X")
        p.apply_trade(10, 100)
        p.apply_trade(-10, 100)
        assert p.quantity == 0.0
        assert p.avg_price == 0.0

    def test_position_zero_trade_noop(self):
        p = Position("X")
        p.apply_trade(0, 100)
        assert p.quantity == 0.0

    def test_account_equity_and_weights(self):
        acc = Account(cash=1000.0)
        acc.position("X").apply_trade(10, 50)  # 500 of stock
        acc.cash -= 500
        prices = {"X": 50.0}
        assert acc.equity(prices) == pytest.approx(1000.0)
        assert acc.weights(prices)["X"] == pytest.approx(0.5)
        assert acc.gross_exposure(prices) == pytest.approx(500.0)

    def test_account_skips_nan_prices(self):
        acc = Account(cash=1000.0)
        acc.position("X").apply_trade(10, 50)
        assert acc.equity({"X": float("nan")}) == pytest.approx(1000.0)

    def test_account_zero_equity_weights_empty(self):
        acc = Account(cash=0.0)
        assert acc.weights({"X": 50.0}) == {}


# --------------------------------------------------------------------------
# Broker
# --------------------------------------------------------------------------
class TestBroker:
    def _dt(self):
        from datetime import datetime

        return datetime(2020, 1, 1)

    def test_buy_reduces_cash_and_opens_position(self):
        b = SimBroker(initial_cash=10_000, cost_model=ProportionalCostModel(0.0))
        trade = b.execute(Order("X", 10), 100.0, self._dt())
        assert trade is not None
        assert b.account.cash == pytest.approx(9_000)
        assert b.account.position("X").quantity == 10

    def test_commission_charged(self):
        b = SimBroker(initial_cash=10_000, cost_model=ProportionalCostModel(10.0))
        b.execute(Order("X", 10), 100.0, self._dt())
        # 10 bps of 1000 notional = 1.0
        assert b.total_commission == pytest.approx(1.0)
        assert b.account.cash == pytest.approx(10_000 - 1000 - 1.0)

    def test_slippage_worsens_fill_and_is_tracked(self):
        b = SimBroker(
            initial_cash=10_000,
            cost_model=ProportionalCostModel(0.0),
            slippage_model=FixedSlippageModel(slippage_bps=50.0),
        )
        trade = b.execute(Order("X", 10), 100.0, self._dt())
        assert trade.price > 100.0  # buy fills above market
        assert b.total_slippage == pytest.approx(abs(trade.price - 100.0) * 10)

    def test_nan_price_rejected(self):
        b = SimBroker(initial_cash=10_000)
        assert b.execute(Order("X", 10), float("nan"), self._dt()) is None
        assert b.execute(Order("X", 10), None, self._dt()) is None

    def test_zero_quantity_noop(self):
        b = SimBroker(initial_cash=10_000)
        assert b.execute(Order("X", 0.0), 100.0, self._dt()) is None

    def test_long_only_clips_oversell(self):
        b = SimBroker(initial_cash=10_000, allow_short=False)
        b.execute(Order("X", 10), 100.0, self._dt())
        # try to sell 25 — should clip to -10 (flat), never go short
        b.execute(Order("X", -25), 100.0, self._dt())
        assert b.account.position("X").quantity == pytest.approx(0.0)

    def test_short_allowed_when_enabled(self):
        b = SimBroker(initial_cash=10_000, allow_short=True)
        b.execute(Order("X", -10), 100.0, self._dt())
        assert b.account.position("X").quantity == -10

    def test_order_status_set_to_filled(self):
        b = SimBroker(initial_cash=10_000)
        o = Order("X", 10)
        b.execute(o, 100.0, self._dt())
        assert o.status == OrderStatus.FILLED


# --------------------------------------------------------------------------
# Strategy & Context
# --------------------------------------------------------------------------
class TestContext:
    def _ctx(self, equity=10_000, positions=None):
        from datetime import datetime

        hist = pd.DataFrame({"X": [100.0]}, index=[datetime(2020, 1, 1)])
        return Context(
            now=datetime(2020, 1, 1),
            history=hist,
            prices={"X": 100.0, "Y": 50.0},
            equity=equity,
            weights={},
            positions=positions or {},
        )

    def test_order_target_percent_from_flat(self):
        ctx = self._ctx()
        ctx.order_target_percent("X", 0.5)
        assert len(ctx.pending_orders) == 1
        # target 5000 / price 100 = 50 shares
        assert ctx.pending_orders[0].quantity == pytest.approx(50)

    def test_order_target_percent_skips_bad_price(self):
        ctx = self._ctx()
        ctx.order_target_percent("Z", 0.5)  # no price
        assert ctx.pending_orders == []

    def test_order_target_weights_closes_missing(self):
        ctx = self._ctx(positions={"X": 50})
        ctx.order_target_weights({"Y": 1.0})  # X absent -> should be sold
        syms = {o.symbol for o in ctx.pending_orders}
        assert "X" in syms and "Y" in syms

    def test_order_shares_ignores_tiny(self):
        ctx = self._ctx()
        ctx.order_shares("X", 1e-15)
        assert ctx.pending_orders == []

    def test_base_strategy_on_bar_not_implemented(self):
        with pytest.raises(NotImplementedError):
            Strategy().on_bar(self._ctx())


class TestWeightsStrategy:
    def test_requires_datetime_index(self):
        with pytest.raises(ValueError):
            WeightsStrategy(pd.DataFrame({"X": [0.5]}))

    def test_target_as_of_forward_fills(self, const_weights):
        s = WeightsStrategy(const_weights)
        d = const_weights.index[50]
        target = s._target_as_of(d)
        assert target == pytest.approx({"AAA": 0.4, "BBB": 0.35, "CCC": 0.25})

    def test_target_none_before_first(self, monthly_weights):
        s = WeightsStrategy(monthly_weights)
        # before the first issued target row
        before = monthly_weights.dropna(how="all").index[0] - pd.Timedelta(days=1)
        assert s._target_as_of(before) is None

    def test_rebalance_only_on_change(self, monthly_weights, prices):
        r = backtest_weights(
            monthly_weights, prices, cost_bps=5.0, rebalance_every_bar=False
        )
        r2 = backtest_weights(
            monthly_weights, prices, cost_bps=5.0, rebalance_every_bar=True
        )
        # trading every bar to correct drift creates more turnover
        assert r2.metrics["annual_turnover"] >= r.metrics["annual_turnover"]


# --------------------------------------------------------------------------
# Engine + look-ahead
# --------------------------------------------------------------------------
class TestEngine:
    def test_requires_strategy(self, prices):
        with pytest.raises(ValueError):
            BacktestEngine(prices).run()

    def test_rejects_non_datetime_index(self, prices):
        with pytest.raises(ValueError):
            BacktestEngine(prices.reset_index(drop=True))

    def test_rejects_duplicate_timestamps(self, prices):
        dup = pd.concat([prices.iloc[:5], prices.iloc[:5]])
        with pytest.raises(ValueError):
            BacktestEngine(dup)

    def test_rejects_empty(self):
        with pytest.raises(ValueError):
            BacktestEngine(pd.DataFrame(index=pd.DatetimeIndex([])))

    def test_drops_all_nan_columns(self, prices):
        p = prices.copy()
        p["DEAD"] = np.nan
        eng = BacktestEngine(p)
        assert "DEAD" not in eng.prices.columns

    def test_rejects_negative_delay(self, prices):
        with pytest.raises(ValueError):
            BacktestEngine(prices, execution_delay=-1)

    def test_run_returns_result(self, prices, const_weights):
        r = BacktestEngine(prices).set_strategy(WeightsStrategy(const_weights)).run()
        assert isinstance(r, BacktestResult)
        assert len(r.daily_returns) > 0
        assert "sharpe_ratio" in r.metrics

    def test_no_lookahead_history_never_sees_future(self, prices):
        """The decisive test: history handed to the strategy never extends past now."""
        seen = []

        class Spy(Strategy):
            def on_bar(self, ctx):
                seen.append((ctx.now, ctx.history.index.max(), len(ctx.history)))

        eng = BacktestEngine(prices).set_strategy(Spy())
        eng.run()
        for i, (now, hist_max, hist_len) in enumerate(seen):
            assert hist_max == now  # last row is exactly the decision bar
            assert hist_len == i + 1  # exactly the bars up to and including now

    def test_forward_returns_only(self, prices):
        """A one-shot bet on a single bar earns the NEXT bar's return, not the same bar's."""
        target_date = prices.index[10]
        asset = "AAA"

        class OneShot(Strategy):
            def on_bar(self, ctx):
                if ctx.now == target_date:
                    ctx.order_target_weights({asset: 1.0})

        r = backtest_strategy(OneShot(), prices, cost_bps=0.0)
        # the first earned return is the day AFTER the decision bar
        first_earn_date = prices.index[11]
        expected = prices[asset].pct_change().loc[first_earn_date]
        assert r.daily_returns.loc[first_earn_date] == pytest.approx(expected, rel=1e-9)

    def test_costs_reduce_returns(self, prices, monthly_weights):
        free = backtest_weights(monthly_weights, prices, cost_bps=0.0)
        costly = backtest_weights(monthly_weights, prices, cost_bps=30.0)
        assert costly.metrics["total_return"] < free.metrics["total_return"]
        assert costly.metrics["total_commission"] > 0

    def test_exec_prices_used_for_fills(self, prices, const_weights):
        # execution at a separate (higher) price frame still runs and trades
        eng = BacktestEngine(
            prices, exec_prices=prices * 1.01, execution_delay=1
        ).set_strategy(WeightsStrategy(const_weights))
        r = eng.run()
        assert len(r.trades) > 0

    def test_no_position_strategy_flat(self, prices):
        class DoNothing(Strategy):
            def on_bar(self, ctx):
                pass

        r = backtest_strategy(DoNothing(), prices)
        assert len(r.trades) == 0


# --------------------------------------------------------------------------
# Reconciliation against the vectorized engine
# --------------------------------------------------------------------------
class TestReconciliation:
    def _maxdiv(self, nat, vec):
        j = pd.concat(
            [nat.daily_returns.rename("n"), vec.daily_returns.rename("v")], axis=1
        ).dropna()
        return float((j["n"] - j["v"]).abs().max()), len(j)

    def test_const_weights_cost_free_matches_vectorized(self, prices, const_weights):
        nat = backtest_weights(const_weights, prices, cost_bps=0.0, shift_bars=1)
        vec = run_weights_backtest(const_weights, prices, cost_bps=0.0, shift_bars=1)
        maxdiv, n = self._maxdiv(nat, vec)
        assert n > 250
        assert maxdiv < 1e-9

    def test_monthly_weights_cost_free_matches_vectorized(
        self, prices, monthly_weights
    ):
        nat = backtest_weights(monthly_weights, prices, cost_bps=0.0, shift_bars=1)
        vec = run_weights_backtest(monthly_weights, prices, cost_bps=0.0, shift_bars=1)
        maxdiv, n = self._maxdiv(nat, vec)
        assert maxdiv < 1e-9

    def test_shift_bars_below_one_rejected(self, prices, const_weights):
        with pytest.raises(ValueError):
            backtest_weights(const_weights, prices, shift_bars=0)
        with pytest.raises(ValueError):
            backtest_strategy(lambda ctx: None, prices, shift_bars=0)


# --------------------------------------------------------------------------
# Parity (cost_basis="target") — exact vectorized reproduction incl. costs
# --------------------------------------------------------------------------
class TestParityMode:
    def _maxdiv(self, nat, vec):
        j = pd.concat(
            [nat.daily_returns.rename("n"), vec.daily_returns.rename("v")], axis=1
        ).dropna()
        return float((j["n"] - j["v"]).abs().max())

    @pytest.mark.parametrize("cost_bps", [0.0, 5.0, 25.0])
    @pytest.mark.parametrize("shift_bars", [1, 2])
    def test_parity_matches_vectorized_with_costs(
        self, prices, monthly_weights, cost_bps, shift_bars
    ):
        nat = backtest_weights(
            monthly_weights,
            prices,
            cost_bps=cost_bps,
            shift_bars=shift_bars,
            cost_basis="target",
        )
        vec = run_weights_backtest(
            monthly_weights, prices, cost_bps=cost_bps, shift_bars=shift_bars
        )
        assert self._maxdiv(nat, vec) < 1e-9

    def test_invalid_cost_basis_rejected(self, prices, const_weights):
        with pytest.raises(ValueError):
            backtest_weights(const_weights, prices, cost_basis="bogus")

    def test_parity_preserves_trades_and_weights(self, prices, monthly_weights):
        nat = backtest_weights(
            monthly_weights, prices, cost_bps=10.0, cost_basis="target"
        )
        # parity still exposes the event-driven artifacts (frictionless fills)
        assert len(nat.trades) > 0
        assert not nat.weights.empty
        assert "sharpe_ratio" in nat.metrics


# --------------------------------------------------------------------------
# Analyzers
# --------------------------------------------------------------------------
class TestAnalyzers:
    def _input(self, n=260):
        rng = np.random.default_rng(3)
        idx = pd.bdate_range("2020-01-01", periods=n)
        r = pd.Series(rng.normal(0.0005, 0.01, n), index=idx)
        equity = (1 + r).cumprod() * 100_000
        turnover = pd.Series(0.05, index=idx)
        return AnalysisInput(returns=r, equity=equity, turnover=turnover, trades=[])

    def test_returns_analyzer(self):
        out = ReturnsAnalyzer().analyze(self._input())
        assert set(out) >= {
            "total_return",
            "annualized_return",
            "volatility",
            "hit_rate",
        }

    def test_sharpe_analyzer_rf(self):
        out = SharpeAnalyzer(rf_annual=0.03).analyze(self._input())
        assert out["rf_annual"] == 0.03
        assert "sortino_ratio" in out

    def test_drawdown_analyzer(self):
        out = DrawdownAnalyzer().analyze(self._input())
        assert out["max_drawdown"] <= 0
        assert out["max_drawdown_days"] >= 0

    def test_trade_analyzer_counts(self):
        from datetime import datetime

        trades = [
            Trade(datetime(2020, 1, 1), "X", 10, 100, commission=1.0, slippage=0.5)
        ]
        ai = self._input()
        ai.trades = trades
        out = TradeAnalyzer().analyze(ai)
        assert out["n_trades"] == 1
        assert out["total_commission"] == pytest.approx(1.0)
        assert out["total_slippage"] == pytest.approx(0.5)

    def test_performance_analyzer_full_suite(self):
        out = PerformanceAnalyzer().analyze(self._input())
        assert "risk_adjusted" in out and "risk" in out

    def test_stats_analyzer_psr_dsr(self):
        out = StatsAnalyzer(n_trials=5).analyze(self._input())
        assert out["available"] is True
        assert 0.0 <= out["psr"] <= 1.0
        assert 0.0 <= out["dsr"] <= 1.0
        assert len(out["sharpe_ci_95"]) == 2

    def test_stats_analyzer_too_short(self):
        out = StatsAnalyzer().analyze(self._input(n=10))
        assert out["available"] is False

    def test_base_analyzer_not_implemented(self):
        from alpha_research.backtests.native.analyzers import Analyzer

        with pytest.raises(NotImplementedError):
            Analyzer().analyze(self._input())

    def test_default_analyzers_names(self):
        names = {a.name for a in default_analyzers()}
        assert names == {"returns", "sharpe", "drawdown", "trades"}


# --------------------------------------------------------------------------
# API + Result
# --------------------------------------------------------------------------
class TestApiAndResult:
    def test_callable_strategy_runs(self, prices):
        def ew(ctx):
            syms = ctx.history.columns
            return {s: 1.0 / len(syms) for s in syms}

        r = backtest_strategy(ew, prices, cost_bps=5.0)
        assert r.metrics["n_days"] > 0

    def test_callable_strategy_none_target(self, prices):
        r = backtest_strategy(lambda ctx: None, prices)
        assert len(r.trades) == 0

    def test_passing_strategy_instance(self, prices, const_weights):
        r = backtest_strategy(WeightsStrategy(const_weights), prices)
        assert r.metrics["n_days"] > 0

    def test_result_summary_and_to_dict(self, prices, const_weights):
        r = backtest_weights(const_weights, prices)
        assert "Native backtest summary" in r.summary()
        d = r.to_dict()
        assert d["n_days"] == int(len(r.daily_returns))

    def test_result_trades_frame(self, prices, monthly_weights):
        r = backtest_weights(monthly_weights, prices, cost_bps=5.0)
        tf = r.trades_frame
        assert set(["dt", "symbol", "quantity", "price"]).issubset(tf.columns)
        assert len(tf) == len(r.trades)

    def test_empty_trades_frame_columns(self, prices):
        r = backtest_strategy(lambda ctx: None, prices)
        assert list(r.trades_frame.columns) == [
            "dt",
            "symbol",
            "quantity",
            "price",
            "commission",
            "slippage",
        ]

    def test_slippage_increases_cost(self, prices, monthly_weights):
        no_slip = backtest_weights(
            monthly_weights, prices, cost_bps=0.0, slippage_bps=0.0
        )
        slip = backtest_weights(
            monthly_weights, prices, cost_bps=0.0, slippage_bps=20.0
        )
        assert slip.metrics["total_slippage"] > no_slip.metrics["total_slippage"]
