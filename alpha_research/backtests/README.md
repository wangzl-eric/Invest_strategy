# Backtests

Backtesting infrastructure for the quant research platform. Two engines share one
economics — a fast **vectorized** engine for the review battery and a rigorous
**native** event-driven engine for trustworthy single runs — proven to produce
identical PnL on the same strategy.

- **Engine comparison & design:** `docs/guides/backtesting_engine_comparison.md`
- **Native engine how-to:** `docs/guides/native_engine_user_guide.md`
- **Review output reference:** `docs/guides/backtest_output_reference.md`

---

## The two engines

| | Vectorized | Native (event-driven) |
|---|---|---|
| Entry point | `alpha_research.review.engine.run_weights_backtest` | `alpha_research.backtests.native.backtest_weights` / `backtest_strategy` |
| Model | weight vector × returns | share-based: cash, positions, fills, commission, slippage |
| Speed | fastest (the review battery's workhorse) | slower (a real bar loop) |
| Use for | parameter sweeps, the rigor battery, many runs | trusting one result, custom/path-dependent logic, cross-checks |
| Look-ahead | explicit `shift_bars` | structural — strategy sees only `history[:now]` |

They are **proven PnL-identical** (to ~1e-16) by
`alpha_research.backtests.equivalence.compare_engines`. The native engine can run
in two cost modes: `cost_basis="traded"` (realistic — costs on actual fills) or
`cost_basis="target"` (parity — reproduces the vectorized NET PnL bit-for-bit).

---

## Quick start

**1. Backtest a target-weights frame (the weights contract — most common):**

```python
from alpha_research.backtests.native import backtest_weights

# weights: DatetimeIndex × ticker target weights. prices: wide close frame.
result = backtest_weights(weights, prices, cost_bps=5.0, shift_bars=1)
print(result.summary())
result.metrics          # sharpe_ratio, max_drawdown, annual_turnover, ...
result.trades_frame     # fill blotter
```

**2. Write a strategy (stateful / path-dependent):**

```python
from alpha_research.backtests.native import Strategy, backtest_strategy

class TopN(Strategy):
    def on_bar(self, ctx):                     # ctx.history is sliced to [:now]
        h = ctx.history
        if len(h) <= 126:
            return
        winners = (h.iloc[-1] / h.iloc[-126] - 1).nlargest(2).index
        ctx.order_target_weights({s: 0.5 for s in winners})

result = backtest_strategy(TopN(), prices, cost_bps=5.0)
```

`ctx` exposes `now`, `history`, `prices`, `equity`, `positions`,
`current_weights`, and order helpers `order_target_weights` /
`order_target_percent` / `order_shares`.

**3. Run a registered strategy through the review pipeline (canonical path):**

```bash
# manifest → QC → backtest → rigor battery (PSR/DSR/MinBTL/CPCV) → artifacts → pool
python -m alpha_research.review run alpha_research/research/pool/sector_rotation_v1/manifest.yaml
```

---

## The weights contract

A strategy produces a `DatetimeIndex × ticker` frame of **unshifted target
weights**. The engine applies the execution shift; never pre-shift inside a
strategy. Two semantics matter:

- **`NaN` row** = "no new target — hold the previous one."
- **`0.0`** = "target cash (liquidate this name)." These are different.
- **`shift_bars`**: `1` = decide & fill at close *t* (T_CLOSE); `2` = fill next
  bar (conservative). Maps to the manifest `ExecutionConvention`.

Gross exposure may exceed 1 (leverage allowed); the review pipeline separately
caps gross at 3× as a sanity gate.

---

## No-look-ahead guarantee

The native engine makes look-ahead **structurally impossible**: each bar the
strategy receives only `history[:now]` (enforced by a runtime guard), and a
target set at *t* earns only *forward* returns. Macro/FRED inputs stay
point-in-time (`quant_data.api.get_data`, `pit=True`). See the comparison guide.

---

## Costs

Commission and slippage reuse `backtests/costs/` (`ProportionalCostModel`,
`FixedSlippageModel`, market-impact, composite). Pass `cost_bps=` / `slippage_bps=`
to the one-call API, or a `cost_model` / `slippage_model` to `BacktestEngine`.

---

## Cross-engine equivalence (correctness gate)

```python
from alpha_research.backtests.equivalence import compare_engines
report = compare_engines(weights, prices, cost_bps=5.0, shift_bars=1)
assert report["exact_match"]                 # vectorized == native_parity == reference
report["native_traded_vs_vectorized"]        # realistic friction gap (expected > 0 with costs)
```

The review pipeline's `engine_reconciliation.json` runs this check every review.

---

## Supported strategy archetypes

The engine is strategy-agnostic across long-only, long-short market-neutral,
single-asset timing, pairs, volatility-targeting, risk-off rotation, leverage,
short-only, calendar/seasonal, stateful stop-loss, and risk parity. Each is
exercised in `tests/unit/test_strategy_archetypes.py`. Out of scope: intraday /
tick / limit-order-book microstructure and native option payoffs.

---

## Directory structure

```
backtests/
├── native/             # Native event-driven engine
│   ├── objects.py      #   Bar / Order / Trade / Position / Account
│   ├── broker.py       #   SimBroker: fills, commission, slippage, accounting
│   ├── strategy.py     #   Strategy + Context + WeightsStrategy/CallableStrategy
│   ├── engine.py       #   BacktestEngine: point-in-time bar loop
│   ├── analyzers.py    #   Returns/Sharpe/Drawdown/Trade/Performance/Stats
│   ├── results.py      #   BacktestResult
│   └── api.py          #   backtest_weights / backtest_strategy
├── equivalence.py      # compare_engines / assert_engines_agree / reference_returns
├── runners/            # Weights-contract entrypoints (fn(prices, macro, params))
│   ├── sector_rotation.py
│   └── vol_conditioned_reversal.py
├── stats/              # PSR, deflated Sharpe, MinBTL, CPCV, bootstrap
├── costs/              # Transaction-cost & slippage models
├── strategies/         # Signal library, metadata, triple-barrier labeling
├── forward_pass/       # Prediction-vs-actual dual tracking & attribution
├── reporting/          # performance metrics + chart/markdown reports
├── builder.py          # Higher-level signals → alpha → weights pipeline
├── walkforward.py      # Walk-forward / grid-search analysis
└── event_driven/       # Optional Backtrader execution-sim adapter
```

Related (outside this package): `alpha_research/review/` (the one-call review
pipeline) and `alpha_research/backtests/strategies/manifest.py` (the manifest
schema and weights contract).

---

## Adding a strategy

1. Implement a weights-contract entrypoint under `runners/`:
   `build_weights(prices, macro, params) -> DataFrame[date × ticker]`.
2. Create a manifest under `alpha_research/research/pool/<id>/manifest.yaml`.
3. `python -m alpha_research.review run <manifest>` — runs QC, backtest, the
   rigor battery, engine reconciliation, and registers the pool entry.

Full guide: `docs/guides/strategy_pool_workflow.md`.

---

## Contributing to the engine

Engine changes must stay **minimal, backward-compatible, and non-redundant**:
preserve the weights contract and public signatures, reuse the existing
cost/stats/calendar utilities, never add a parallel engine, keep no-look-ahead
intact, and reconcile any behavior change via `equivalence.compare_engines`. A
project `PreToolUse` hook (`scripts/backtest_engine_guardrail.sh`) surfaces this
reminder automatically when engine files are edited.
