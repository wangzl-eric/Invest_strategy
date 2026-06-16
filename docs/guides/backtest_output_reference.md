# Shared Backtester — Node Pattern & Output Reference

> Created 2026-06-14. How a strategy plugs into the **one shared backtester**, and the
> full set of results every run produces. Grounding: `RESEARCH_PHILOSOPHY.md` §4 (rigor
> battery), `docs/guides/alpha_factory_workflow.md` (stages), `strategy_pool_workflow.md`
> (commands). The engine is `alpha_research/review/` (vectorized, primary; D7).

## The shared backtester is a node graph

There is **one** backtester (`alpha_research.review.run_review`). A strategy is a **node**
plugged into it — you never write backtest plumbing. A node is two files:

1. **A weights function** (the node's logic) under `alpha_research/backtests/runners/<id>.py`:

   ```python
   def build_weights(prices: pd.DataFrame,
                     macro: dict[str, pd.Series] | None,
                     params: dict) -> pd.DataFrame:   # DatetimeIndex × ticker target weights
       ...
   ```
   Pure function. Weights at date *t* use only data ≤ *t*; return them **unshifted** — the
   engine applies the execution shift. Long-only (Σw=1) or dollar-neutral L/S (Σw=0, gross
   normalized) both work; the engine is sign-correct. (Reference nodes:
   `runners/sector_rotation.py` long-only, `runners/vol_conditioned_reversal.py` L/S.)

2. **A manifest** (the node's registration) at `alpha_research/research/pool/<id>/manifest.yaml`
   declaring `entrypoint`, `universe`, `params`, `rebalance`, `cost_model`,
   `data_requirements` (price + macro, e.g. FRED `VIXCLS`), `benchmark`, `n_trials`,
   `promotion_rules`. Schema: `alpha_research/backtests/strategies/manifest.py`.

Then run the shared logic with the node as input — **one command, no other code**:

```bash
python -m alpha_research.review run alpha_research/research/pool/<id>/manifest.yaml
```

That's the entire contribution required to backtest an idea: write `build_weights`, declare
the manifest, run. The pipeline loads data (local Parquet first, PIT-shifted macro), runs
QC, backtests, runs the full battery, writes the bundle, and registers the pool entry.

## Canonical strategy deliverable (exactly 4 docs)

Each strategy folder `research/strategies/<id>_<date>_<verdict>/` holds four templated
markdown docs (numeric-prefixed; templates in `docs/templates/strategy/`):
`00_BRIEFING.md` (what/expression/why/gates), `01_RESEARCH_LOG.md` (dated per-stage audit
trail), `02_BACKTEST_REPORT.md` (**auto-generated**, charts embedded), `03_PM_REVIEW.md`
(challenges + verdict). The runner, manifest, and machine bundle live in their own homes
(below) and are linked from `00`. Full convention: `docs/templates/strategy/README.md`.

## The output bundle (`data/backtest_runs/<run_id>/`)

Every run emits the same comprehensive set:

| Artifact | Contents |
|---|---|
| `metrics.json` | headline: Sharpe, ann. return/vol, max DD, turnover, **+ CAGR, Sortino, Calmar, tail ratio, win rate, profit factor, max-DD duration** |
| `performance.json` | **comprehensive return/risk suite** (see groups below) |
| `engine_reconciliation.json` | vectorized engine vs an **independent event-driven replay** — `reconciled: true` corroborates the result; a divergence flags a shift/cost/look-ahead bug |
| `stats_battery.json` | PSR, DSR (deflated by ledger n_trials), MinBTL, Sharpe CI, walk-forward segments, regime-conditional Sharpe |
| `sensitivity.json` | cost 1×/2×/3× and every numeric parameter ±20/40% |
| `correlations.json` | pairwise \|ρ\| vs every active pool strategy |
| `gates.json` | pre-committed promotion-gate pass/fail |
| `daily_returns.parquet`, `equity_curve.parquet` | the return stream |
| `qc_report.json` | data QC preflight |
| `verdict.md` | human-readable summary (now includes the rich headline metrics) |
| `review.json` / `review.md` | standardized review payload |
| `report.md` + `charts/` | **auto-generated, chart-embedded report** (deliverable artifact `02`): equity+drawdown, rolling Sharpe, monthly heatmap, cost sensitivity, return distribution + all metric/gate/significance/sensitivity tables + engine reconciliation. Re-render into a strategy folder with `python -m alpha_research.review report <run_id> --out <folder>`. |
| `03_PROFESSIONAL_REPORT.md` + `charts_pro/` | **auto-generated, presentation-grade report** (additive deliverable artifact `03`, alongside — not replacing — the human `03_PM_REVIEW.md`): return-vs-buy&hold with buy/sell markers, drawdown, parameter stability, signal seasonality decomposition, skew/kurtosis distribution, multi-index beta, rolling & vol-adjusted Sharpe + the signal's mathematical rationale, a methodology/rigor section (horizon, win-probability, data source, engine, qualitative process), and a generated PM review. Re-render with `python -m alpha_research.review report-pro <run_id> --out <folder>`. |
| `weights.parquet`, `prices.parquet`, `benchmarks.parquet` | support frames for the professional report (effective post-shift weights, universe prices, benchmark price level) — additive; absent → that report degrades gracefully |
| `quantstats_report.html` | **rich visual tear sheet** (when `quantstats` is installed; degrades gracefully otherwise) |

### `performance.json` groups (computed in-house, always present)

- **returns** — total, CAGR, annualized, best/worst day, win rate, avg win/loss, win/loss
  ratio, profit factor, gain-to-pain.
- **risk** — annual vol, downside deviation, skew, (excess) kurtosis, 95% VaR/CVaR, tail
  ratio, max drawdown (depth + duration days + current + avg + episode count +
  time-in-drawdown), Ulcer index.
- **risk_adjusted** — Sharpe, Sortino, Calmar, common-sense ratio.
- **periodic** — monthly & yearly return tables, positive-period %, best/worst month/year.
- **vs_benchmark** (when a `benchmark` is set) — beta, annualized alpha, correlation, R²,
  tracking error, information ratio, up/down capture, benchmark Sharpe.

## Third-party packages

- **QuantStats** (`quantstats`, in `requirements.txt`) — the HTML tear sheet
  (`reporting/review.py::generate_quantstats_tearsheet`). Our in-house `performance.json`
  covers the metrics dependency-free so reviews are complete even without it.
- **Backtrader** (`backtrader`, in `requirements.txt`) — the heavyweight event-driven
  execution-sim adapter (`backtests/event_driven/`) for fill/slippage realism (D7,
  validation-only). The always-on `engine_reconciliation.json` is the lightweight
  engine-agreement check that runs every review without the dependency.

## Adding a node — checklist

1. `runners/<id>.py:build_weights` (+ a `test_<id>_strategy.py` with the
   `test_no_lookahead_truncation_invariance` pattern).
2. `research/pool/<id>/manifest.yaml` (honest `n_trials`; pre-committed `params`/gates).
3. `python -m alpha_research.review run <manifest>` → inspect the bundle (`verdict.md`,
   `performance.json`, `engine_reconciliation.json` first; promotion stays human).
4. `python -m alpha_research.review report <run_id> --out <strategy folder>` → drops the
   chart-embedded `02_BACKTEST_REPORT.md` (+ `charts/`) into the strategy folder.
5. `python -m alpha_research.review report-pro <run_id> --out <strategy folder>` → drops the
   presentation-grade `03_PROFESSIONAL_REPORT.md` (+ `charts_pro/`) into the strategy folder
   (both reports also land in the run bundle automatically during `run`).
