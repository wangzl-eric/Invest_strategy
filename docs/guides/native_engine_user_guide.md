# Native Backtest Engine — User Guide

*The rigorous, event-driven backtester in `alpha_research/backtests/native/`.
Companion to `docs/guides/backtesting_engine_comparison.md`.*

The native engine is a **share-based, event-driven portfolio simulator** with
real cash, positions, fills, commission, slippage, and **no look-ahead bias by
construction**. Use it when you need to *trust* a single backtest result. For the
many-runs review battery, keep using the fast vectorized engine
(`python -m alpha_research.review run ...`).

## Install / import

Nothing to install — it is part of the repo. Set `PYTHONPATH=.` and import:

```python
from alpha_research.backtests.native import (
    backtest_weights, backtest_strategy, BacktestEngine,
    Strategy, WeightsStrategy, CallableStrategy,
    SharpeAnalyzer, StatsAnalyzer, PerformanceAnalyzer,
)
```

## 1. Backtest a target-weights frame (the common case)

If you already produce a `DatetimeIndex × ticker` frame of **target weights**
(the repo "weights contract" — what every manifest runner returns), one call
backtests it:

```python
import pandas as pd
from alpha_research.backtests.native import backtest_weights

# weights: rows are dates, columns tickers, values target weights.
# NaN row = "no new target, hold previous". Weights at date t use only data <= t.
result = backtest_weights(
    weights, prices,        # prices: wide close-price frame, same tickers
    cost_bps=5.0,           # one-way commission in bps on turnover
    shift_bars=1,           # 1 = decide & fill at close t (T_CLOSE); 2 = fill next bar
    slippage_bps=2.0,       # optional fill-price impact
    initial_cash=100_000,
    allow_short=True,
)

print(result.summary())
print(result.metrics["sharpe_ratio"], result.metrics["max_drawdown"])
```

`backtest_weights` mirrors `review.engine.run_weights_backtest`'s signature, so
it is a drop-in with **realistic share-based accounting** instead of idealised
weight algebra.

## 2. Write a strategy (full control)

Subclass `Strategy` and override `on_bar`. You receive a `Context` exposing only
the past — there is no way to read the future:

```python
from alpha_research.backtests.native import Strategy, BacktestEngine

class MomentumTopN(Strategy):
    name = "mom_top2"

    def __init__(self, lookback=126, n=2):
        self.lookback, self.n = lookback, n

    def on_bar(self, ctx):
        h = ctx.history                       # closes UP TO AND INCLUDING ctx.now
        if len(h) <= self.lookback:
            return                            # warm-up
        mom = h.iloc[-1] / h.iloc[-self.lookback] - 1
        winners = mom.nlargest(self.n).index
        ctx.order_target_weights({s: 1.0 / self.n for s in winners})

engine = BacktestEngine(prices, initial_cash=100_000)
engine.set_strategy(MomentumTopN(lookback=126, n=2))
result = engine.run()
```

### The `Context` API (inside `on_bar`)

| Member | Meaning |
|---|---|
| `ctx.now` | Current decision timestamp. |
| `ctx.history` | Close prices sliced to `[:now]` — **never** any future row. |
| `ctx.prices` | `{symbol: latest close}` at `now`. |
| `ctx.equity` | Current portfolio equity (cash + positions). |
| `ctx.positions` | `{symbol: share quantity}` currently held. |
| `ctx.current_weights` | `{symbol: weight}` currently held. |
| `ctx.order_target_weights({sym: w})` | Rebalance whole book to these weights. |
| `ctx.order_target_percent(sym, pct)` | Trade one symbol to `pct` of equity. |
| `ctx.order_shares(sym, qty)` | Signed share delta (raw order). |

### Quick experiments without subclassing

```python
from alpha_research.backtests.native import backtest_strategy

def equal_weight(ctx):
    syms = ctx.history.columns
    return {s: 1.0 / len(syms) for s in syms}

result = backtest_strategy(equal_weight, prices, cost_bps=5.0)
```

## 3. Read the results

`result` is a `BacktestResult`:

| Field | Type | Contents |
|---|---|---|
| `daily_returns` | `Series` | Net daily returns (after costs). |
| `equity_curve` | `DataFrame` | `date`, `portfolio_value`. |
| `weights` | `DataFrame` | Effective per-bar portfolio weights. |
| `positions` | `DataFrame` | Per-bar share quantities. |
| `turnover` | `Series` | Per-bar turnover (fraction of equity). |
| `trades` | `list[Trade]` | Fill blotter (`.trades_frame` for a DataFrame). |
| `metrics` | `dict` | Headline: return, vol, Sharpe, max DD, turnover, costs. |
| `analyzers` | `dict` | One entry per attached analyzer (see below). |

```python
result.metrics            # {'sharpe_ratio': ..., 'max_drawdown': ..., ...}
result.trades_frame       # blotter as DataFrame
result.equity_curve       # plot-ready
print(result.summary())   # human-readable one-liner per metric
```

## 4. Analyzers — pluggable, professional metrics

Attach any analyzers; each writes a block into `result.analyzers[name]`.

```python
from alpha_research.backtests.native import (
    BacktestEngine, WeightsStrategy,
    SharpeAnalyzer, StatsAnalyzer, PerformanceAnalyzer,
)

engine = BacktestEngine(
    prices,
    analyzers=[
        SharpeAnalyzer(rf_annual=0.02),     # excess-of-rf Sharpe & Sortino
        StatsAnalyzer(n_trials=10),         # PSR, DSR, bootstrap Sharpe CI
        PerformanceAnalyzer(benchmark=spy_returns),  # full QuantStats-grade suite
    ],
)
engine.set_strategy(WeightsStrategy(weights))
result = engine.run()

result.analyzers["stats"]        # {'psr': .., 'dsr': .., 'sharpe_ci_95': [..], ..}
result.analyzers["performance"]  # returns/risk/risk_adjusted/periodic/vs_benchmark
```

- `StatsAnalyzer` reuses the repo's `backtests.stats.sharpe_tests`, so PSR/DSR
  here match the review battery. **Declare `n_trials` honestly** — it is the
  multiple-testing deflation.
- `PerformanceAnalyzer` reuses `reporting.performance.compute_performance_metrics`,
  producing the same `performance.json` payload as a review run.
- Write your own: subclass `Analyzer`, set `name`, implement
  `analyze(ctx) -> dict` over `ctx.returns / ctx.equity / ctx.turnover / ctx.trades`.

## 5. Avoiding look-ahead bias (read this)

The engine makes look-ahead **structurally impossible**, but you can still defeat
it if you feed it bad data. The contract:

1. **Only use `ctx.history` inside `on_bar`.** It is sliced to `[:now]`; the
   engine raises if that ever fails. Do not close over the full price frame and
   index into the future.
2. **Weights at date *t* must use only data ≤ *t*.** A target set at *t* is filled
   at *t*'s close (or later) and earns the *forward* return — it can never profit
   from the same-bar move it was computed from.
3. **Pick the execution convention deliberately.** `shift_bars=1` (default) =
   end-of-day: decide on the close and trade it. `shift_bars=2` = conservative:
   decide on the close, trade the next bar (use it when your signal needs the
   close but you cannot realistically trade at it).
4. **Keep macro data point-in-time.** Pull FRED/macro via `quant_data.api.get_data`
   (PIT-shifted by default); never pass `pit=False` series into a backtest.
5. **Pre-clean inputs.** The engine rejects duplicate timestamps and all-NaN
   columns; align your price frame to the trading calendar
   (`backtests.calendar.align_to_trading_days`) before backtesting.

## 6. Validating a result — reconcile against the vectorized engine

Because both engines share the same execution economics, agreement is strong
evidence of correctness:

```python
from alpha_research.review.engine import run_weights_backtest
from alpha_research.backtests.native import backtest_weights

vec = run_weights_backtest(weights, prices, cost_bps=0.0, shift_bars=1)
nat = backtest_weights(weights, prices, cost_bps=0.0, shift_bars=1)

j = (nat.daily_returns.rename("n")
     .to_frame().join(vec.daily_returns.rename("v"), how="inner"))
assert (j.n - j.v).abs().max() < 1e-9     # they match to machine precision
```

With costs or `shift_bars=2`, the native engine intentionally differs (it charges
drift-correction turnover and lets prices move between decision and fill) — that
is realism, not error.

## 7. When to use which engine

| Situation | Engine |
|---|---|
| Review battery, parameter sweeps, many runs | vectorized (`alpha_research.review`) |
| Trusting one result with realistic fills | **native** |
| Custom intra-bar logic, stops, sizing | **native** (`Strategy` subclass) |
| Cross-checking a suspicious vectorized result | **native** (reconcile) |

## API quick reference

```python
backtest_weights(weights, prices, *, cost_bps=5.0, shift_bars=1,
                 initial_cash=100_000, slippage_bps=0.0, allow_short=True,
                 rebalance_every_bar=True, analyzers=None) -> BacktestResult

backtest_strategy(strategy_or_fn, prices, *, cost_bps=5.0, shift_bars=1,
                  initial_cash=100_000, slippage_bps=0.0, allow_short=True,
                  analyzers=None) -> BacktestResult

BacktestEngine(prices, *, initial_cash=100_000, cost_model=None,
               slippage_model=None, allow_short=True, execution_delay=0,
               exec_prices=None, analyzers=None)
    .set_strategy(strategy) -> self
    .run() -> BacktestResult
```
