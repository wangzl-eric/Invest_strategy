# Backtesting Engine: Comparison & What We Adapted

*Created 2026-06-16. Covers the new native event-driven engine in
`alpha_research/backtests/native/` and the third-party engines it learns from.*

## Why a new engine

The repo already has a **vectorized** weights-contract engine
(`alpha_research/review/engine.py::run_weights_backtest`). It is fast, reproducible,
and the right tool for the review battery. But "fast" was never the goal of a
*research* backtest — **rigour and clarity are**. A vectorized engine hides the
execution model inside a `.shift()` and a `.diff()`, treats the portfolio as a
weight vector (no cash, no shares, no fills), and silently assumes you rebalance
perfectly to target every bar with no decision-to-fill gap.

The native engine (`alpha_research.backtests.native`) is the opposite trade-off:
**prioritise rigour and user-friendliness over speed.** It is a real
event-driven, share-based portfolio simulator with cash, positions, fills,
commission, slippage, and — above all — **no look-ahead bias by construction.**
It does not replace the vectorized engine; it complements it and cross-checks it
(the two reconcile to ~1e-16, see below).

## The headline guarantee: no look-ahead bias

This was the explicit design priority. Look-ahead bias is the single most common
way a backtest lies to you, so the native engine removes the *opportunity* for it
rather than relying on the strategy author's discipline:

1. **Structural history slicing.** Every bar, the strategy receives a
   `Context` whose `history` is sliced to `prices.iloc[:i+1]` — it is *impossible*
   to read a row dated after the decision bar. The engine enforces
   `history.index[-1] == now` with an always-on runtime check (not an `assert`,
   which `python -O` would strip).
2. **Forward returns only.** A target set at bar *t* is filled at *t*'s close (or
   later, with `execution_delay`) and earns the return from *t* to *t+1*. The
   contemporaneous return — the one you'd need future knowledge to trade on — is
   never credited to a position decided on that same bar.
3. **Explicit execution convention.** The decision-to-fill delay is a visible
   parameter (`execution_delay` / `shift_bars`), not an implicit `.shift(1)`
   buried in vector code. `shift_bars=1` = decide and fill at close *t*;
   `shift_bars=2` = fill one bar later (conservative).
4. **PIT macro data unchanged.** Macro/FRED inputs remain point-in-time shifted
   upstream (`quant_data/pit.py`); the engine never undoes that.
5. **Cross-engine reconciliation.** Because the native and vectorized engines
   share the same execution economics, any look-ahead bug in one shows up as a
   divergence against the other — an always-available regression test.

> **Rule of thumb encoded in the engine:** weights at date *t* may use only data
> with timestamp ≤ *t*, and they only ever earn *future* returns. If you can
> compute it inside `on_bar(ctx)` from `ctx.history`, it is safe by construction.

## The three engines and what we took from each

### 1. vnpy — explicit event objects & a gateway-style broker
*<https://github.com/vnpy/vnpy>*

**Edge:** vnpy is built around small, immutable event/data objects
(`BarData`, `OrderData`, `TradeData`, `PositionData`, `AccountData`) that flow
through an event loop. Execution frictions (slippage, commission) are applied at
the *gateway* boundary, so the strategy never sees an idealised fill.

**What we adapted:**
- `objects.py` mirrors this with `Bar`, `Order`, `Trade`, `Position`, `Account`
  — plain dataclasses, cheap to create in the hot loop, trivial to unit-test.
- `broker.py::SimBroker` is the gateway: it is the *only* component allowed to
  mutate cash/positions, and it applies slippage to the fill price and commission
  to cash — frictions live at the boundary, exactly as in vnpy.

**What we did *not* copy:** vnpy's live-trading gateways, the GUI, and the
multi-asset contract registry — out of scope for a research backtester.

### 2. backtrader — Strategy / Broker / Sizer / Analyzer lifecycle
*<https://github.com/mementum/backtrader>*

**Edge:** backtrader's developer experience. A `Strategy` with lifecycle hooks
(`next()`, `notify_order`), high-level order helpers (`order_target_percent`),
a `Broker` that owns cash and a commission scheme, and a pluggable `Analyzer`
ecosystem you attach to a run.

**What we adapted:**
- `strategy.py::Strategy` has `on_start` / `on_bar` / `on_finish` hooks and the
  `Context` exposes `order_target_percent`, `order_target_weights`,
  `order_shares` — users express *intent* (target exposure) instead of doing
  share arithmetic.
- `analyzers.py` is the backtrader Analyzer pattern: small, pure functions of the
  finished return stream (`ReturnsAnalyzer`, `SharpeAnalyzer`, `DrawdownAnalyzer`,
  `TradeAnalyzer`, `PerformanceAnalyzer`). Add your own without touching the loop.
- `engine.py::BacktestEngine` is the `Cerebro` analogue: assemble data + strategy
  + broker + analyzers, call `run()`.

**What we improved on:** backtrader's line/indexing model (`self.data.close[0]`
vs `[-1]`) is a notorious look-ahead foot-gun. We replaced it with a sliced
`ctx.history` frame that *cannot* reference the future.

### 3. qlib — point-in-time discipline & account/execution separation
*<https://github.com/microsoft/qlib>*

**Edge:** qlib is built by an ML-finance team obsessed with leakage. Its data
layer is point-in-time; it cleanly separates *signal/decision* from *execution*
(the nested decision-executor framework); and its `Account`/`Position` objects
value the book consistently so reports derive from state, not side calculations.

**What we adapted:**
- The **no-look-ahead-by-construction** philosophy above is the qlib lesson,
  applied to a per-bar loop: the strategy sees only `[:current_bar]`.
- `objects.py::Account` follows qlib's discipline — equity is *always*
  `cash + Σ position value`, never a tracked scalar that can drift out of sync.
  Exposure, weights, and PnL are all derived from that single source of truth.
- Decision/execution separation: the strategy emits orders; the broker executes
  them on an explicit delay. Signal generation and fill simulation never mix.

**What we did *not* copy:** qlib's expression-engine alpha language and its
Qlib-format binary data store — the repo already has its own data lake and
weights-contract runners.

## Side-by-side

| Dimension | vectorized (`review.engine`) | **native (new)** | vnpy | backtrader | qlib |
|---|---|---|---|---|---|
| Paradigm | vectorized weights | **event-driven, share-based** | event-driven | event-driven | vectorized + nested executor |
| Accounting | weight vector | **cash + shares + positions** | full | full | full |
| Costs | turnover × bps | **commission + slippage at fill** | gateway | commission scheme | executor |
| Look-ahead defence | `shift_bars` convention | **structural history slice + forward-only returns** | author discipline | line indexing (foot-gun) | PIT data layer |
| Fills | none (idealised) | **slippage-adjusted, decision-to-fill gap** | realistic | realistic | configurable |
| Extensible metrics | fixed suite | **pluggable Analyzers** | — | Analyzers | reports |
| Speed | fastest | slower (a loop) | medium | slow | medium |
| Primary use here | review battery | **rigorous research & validation** | live trading | retail backtests | ML research |

## Reconciliation (the rigour proof)

Run the native engine cost-free with daily rebalancing and it reproduces
`run_weights_backtest` (the canonical `shift_bars=1` / T_CLOSE convention) to
**~1e-16** on every daily return — verified in
`tests/unit/test_native_engine.py::TestReconciliation`. The economics are
identical; only the *implementation* differs (an explicit per-bar loop vs vector
algebra), so agreement is strong evidence neither has a shift/cost/look-ahead bug.

With frictions or a decision-to-fill delay (`shift_bars=2`), the native engine
intentionally *diverges slightly* from the idealised vector model — it charges
drift-correction turnover and lets prices move between decision and fill. That
gap is **realism, not error**, and is exactly why this engine exists.

## What "the edge" cost us

The native engine is a Python bar loop, so a multi-year, multi-asset run is
seconds, not milliseconds. That is the deliberate trade-off: use the vectorized
engine for the review battery's many runs, and the native engine when you need to
*trust* a single result — realistic fills, full accounting, and a look-ahead bias
that is structurally impossible rather than merely discouraged.

## Consolidation: one kernel, proven equivalent

"Several engines" must never mean "several answers." The engines are consolidated
around a single proven economics, cross-checked on every run:

- **One canonical economics.** `run_weights_backtest` (vectorized) defines the
  weights-contract PnL. The native engine reproduces it **bit-for-bit** in
  *parity mode* (`backtest_weights(..., cost_basis="target")`) — ~4e-16 on every
  daily return, for any `shift_bars`, with or without costs. It does this by
  running its event loop frictionless for an independent gross stream, then
  applying the canonical turnover cost — so the agreement tests the *engine*, not
  a shared formula.
- **One correctness gate.** `alpha_research/backtests/equivalence.py` —
  `compare_engines()` / `assert_engines_agree()` run the same target weights
  through the vectorized engine, native-parity, and an independent `reference`
  bar loop, and assert all three agree to machine precision. The native
  *realistic* mode (`cost_basis="traded"`) is reported alongside; its divergence
  (drift-correction turnover + decision-to-fill gap) is surfaced explicitly.
- **One reference loop.** The review pipeline's `reconcile_event_driven` gate now
  delegates to `equivalence.reference_returns`, so the review and the equivalence
  tests exercise the *same* independent implementation (3 hand-written
  return-engines collapsed to vectorized + native, with reconcile a thin wrapper).

Equivalence is regression-tested in `tests/unit/test_engine_equivalence.py` across
constant / monthly / long-short schedules and the real `sector_rotation` runner
(identical Sharpe across engines).

```python
from alpha_research.backtests.equivalence import compare_engines
report = compare_engines(weights, prices, cost_bps=5.0, shift_bars=1)
assert report["exact_match"]                    # vectorized == native_parity == reference
report["native_traded_vs_vectorized"]           # realistic friction gap (expected > 0 with costs)
```

See **`docs/guides/native_engine_user_guide.md`** for usage.
