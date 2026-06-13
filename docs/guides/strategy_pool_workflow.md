# Strategy Pool Workflow — Manifest → Review → Pool

> Created 2026-06-12 (EXECUTION_PLAN.md Phase 1). This is the **mandatory** path from a
> research idea to a registered strategy. There is no supported way into the pool that
> bypasses the review battery. The *why* behind every gate:
> `alpha_research/research/RESEARCH_PHILOSOPHY.md`.

```
proposal.md ──► weights entrypoint ──► manifest.yaml ──► python -m alpha_research.review run
                                                              │
                       data QC preflight ◄────────────────────┤
                       vectorized backtest + EW baseline      │
                       walk-forward segments                  │
                       PSR / DSR / MinBTL / bootstrap CI      │
                       cost 1×/2×/3× + params ±20/40%         │
                       correlation vs active pool             │
                                                              ▼
                              data/backtest_runs/<run_id>/  artifacts
                              strategy_pool table            (candidate)
                                                              │
                  python -m alpha_research.pool promote ... ◄─┘  (human decision)
```

## 1. The strategy contract

A strategy is the pair **(manifest, weights function)**.

**Weights function** — a pure function, importable as `package.module:function`:

```python
def build_weights(prices, macro, params) -> pd.DataFrame:
    """
    prices: wide close-price DataFrame (DatetimeIndex × ticker) for the manifest universe
    macro:  dict[series_id -> pd.Series] PIT-shifted & as-of aligned to prices.index,
            or None when the manifest declares no macro requirements
    params: the manifest `params` dict
    returns: target weights (DatetimeIndex × ticker). NaN = no target set that day
             (the engine forward-fills the last target). DO NOT pre-shift — weights
             at date t may use only data ≤ t; the engine applies the execution shift.
    """
```

Reference implementation: `alpha_research/backtests/runners/sector_rotation.py`.

**Manifest** — git-versioned YAML at `alpha_research/research/pool/<strategy_id>/manifest.yaml`,
validated by `alpha_research/backtests/strategies/manifest.py` (Pydantic). Key fields:

| Field | Notes |
|---|---|
| `strategy_id` | lowercase slug; the pool key |
| `track` | `etf_rotation` \| `cta_futures` \| `factor_etf` (locked decision D3) |
| `universe` | explicit ticker list |
| `entrypoint` | `"package.module:function"` |
| `params` | passed to the entrypoint; numeric params drive ±20/40% sensitivity |
| `rebalance.execution_convention` | `t_close` (1-bar shift) or `t+1_open`/`t+1_close` (2-bar, conservative) |
| `cost_model` | `proportional` + `bps`; review re-runs at 2× and 3× |
| `data_requirements` | macro series (kind: `macro`) are loaded PIT-shifted |
| `n_trials` | **declare honestly** — number of variations tried; feeds DSR & MinBTL |
| `promotion_rules` | pre-committed gates (defaults: DSR ≥ 0.95, PSR ≥ 0.90, survives 2× costs, \|corr\| ≤ 0.4) |
| `proposal_path` | pointer to the narrative/PM-review document |

## 2. Run the review

```bash
export PYTHONPATH=.
python -m alpha_research.review run alpha_research/research/pool/<id>/manifest.yaml
# options: --force (proceed past QC fail), --no-tearsheet, --no-register, --output-dir
```

Artifact bundle under `data/backtest_runs/<run_id>/`:

| File | Content |
|---|---|
| `config.yaml` | frozen run config: params, git commit, seed (RunManager) |
| `manifest_snapshot.yaml` | the manifest exactly as reviewed |
| `qc_report.json` | data QC findings (missing bars, stale prices, extreme returns, coverage) |
| `metrics.json` | net Sharpe/vol/drawdown/turnover + equal-weight-baseline comparison |
| `daily_returns.parquet`, `equity_curve.parquet` | return streams (also feed the pool correlation gate for later candidates) |
| `stats_battery.json` | PSR, DSR, MinBTL, bootstrap CI, walk-forward segment Sharpes, regime-conditional Sharpe |
| `sensitivity.json` | cost grid (1×/2×/3×) + per-param ±20/40% Sharpe grid |
| `correlations.json` | pairwise correlation vs every active pool strategy |
| `gates.json`, `verdict.md` | gate evaluation against the manifest's promotion rules |
| `review.json`, `review.md`, `quantstats_report.html` | standardized review bundle (reporting layer) |

**QC behavior:** end-side coverage gaps **fail** (stale cache / dead feed); start-side gaps
**warn** (usually genuine inception — e.g. XLC listed 2018). The data layer auto-refreshes a
stale local cache (prices > 7 days behind, macro > 75 days) and falls back to the stale copy
if the API is unreachable.

**Verdict semantics:** `PASS` = all pre-committed gates satisfied; `REVISE` = at least one
failed. Either way the run is registered and the pool entry stays `candidate` —
**promotion is always a human decision**.

## 3. Manage the pool

```bash
python -m alpha_research.pool list [--state candidate]
python -m alpha_research.pool show <strategy_id>          # full JSON incl. state history
python -m alpha_research.pool promote <strategy_id> --to paper --reason "gates passed run ee3a7b06"
python -m alpha_research.pool retire <strategy_id> --reason "decayed; see tracker"
```

Lifecycle: `candidate → paper → live → retired`. Demotions (`paper→candidate`, `live→paper`)
are allowed; `retired` is terminal. Every transition is appended to `state_history` with a
timestamp and reason. State lives in the `strategy_pool` table (`core/models.py`); the
manifest in git remains the canonical spec.

## 4. Point-in-time discipline (macro data)

`quant_data.api.get_data` ships macro/FRED series **availability-dated by default**
(`pit=True`): each observation's date is shifted by a conservative publication lag
(`quant_data/pit.py`, e.g. CPI +45d, employment +38d, market-derived series +1d; unknown
series get a spacing-based conservative fallback + warning). The original reference date is
kept in a `reference_date` column. The review pipeline's macro loader additionally as-of
aligns series to the price calendar (`pit.as_of_series`) so a strategy can never see an
unpublished print. `pit=False` is for display/debugging only and logs a warning.

## 5. Current pool

| strategy_id | track | state | note |
|---|---|---|---|
| `sector_rotation_v1` | etf_rotation | candidate | Phase 1 reference strategy. First review (run `ee3a7b06`, 2026-06-12): net Sharpe 0.84 vs EW baseline 0.83, PSR 0.999, DSR 0.912 (< 0.95 gate), MinBTL 4095d > 3485d available → verdict REVISE. Honest marginal result — exactly what the gates are for. |

## 6. Troubleshooting

- `Unknown ticker or alias` — the ticker isn't in `quant_data/ticker_map.py`'s registry.
  ETFs/equities are auto-registered from `config/ticker_universe.py`; add the symbol there.
- `Data QC failed` — read the listed findings. Stale-end failures usually fix themselves on
  re-run (cache refresh); real gaps need a data pull. `--force` records the failure in the
  artifacts and proceeds.
- FRED fetch without `pandas_datareader` — the API falls back to FRED's keyless
  `fredgraph.csv` endpoint automatically.
- Reviews are deterministic (seeded bootstrap): re-running the same manifest on the same
  data and commit reproduces metrics under a new `run_id`.
