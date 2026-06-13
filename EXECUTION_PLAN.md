# Execution Plan — Full-Lifecycle Quant Platform

> **Created:** 2026-06-12 · **Owner:** Zelin (solo decision-maker)
> **Supersedes the roadmap section of** `next_gen_investment_plan.md` (the brief remains the
> source for constraints and success criteria; this file is the actionable build plan).
> **Executing agent:** work packages (WPs) are sized for one focused agent session each.
> Hand a WP to the agent verbatim, together with the *Conventions* section below.

---

## 1. Locked decisions (do not relitigate without owner sign-off)

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| D1 | Strategy pool store | **YAML manifests in git + SQLite state table** (`core/models.py`) | Manifests (spec, promotion rules) are reviewable/diffable in git; mutable lifecycle state is transactional in the existing DB. No MLflow — a tracking server for one user is operational debt. |
| D2 | Futures data vendor | **Vendor-agnostic schema; Databento first.** Final vendor commitment stays open. | Databento is API-native and works on macOS (Norgate's updater is Windows-only). Continuous contracts are built in-house (WP-2.3). Schema must allow swapping/adding vendors without touching research code. |
| D3 | Cross-sectional equity track | **Merged into the ETF track as factor-ETF rotation.** No single-name equity. | IBKR per-order minimums make 100+ name L/S non-viable at $25–100k; merging removes the survivorship-free equity universe requirement (and most of Norgate's value). |
| D4 | Daily ops scheduling | **Standalone idempotent script + macOS launchd** (pattern: `scripts/com.ibkr.pa_automation.plist`) | Trading must not depend on dashboard uptime. Heartbeat alerts on *silence*, not just on error. |
| D5 | Phase 1 scope | **Dash pool dashboard cut from Phase 1** (deferred to Phase 4); **point-in-time FRED layer added** | PIT bugs corrupt every macro-tilted backtest; the UI corrupts nothing by not existing. |
| D6 | Strategy contract | **`weights_fn(data) → DataFrame[date × ticker]` of target weights**, adapted to `builder.py` + `walkforward.py` only; Backtrader layer is validation-only | Collapses the three incompatible strategy shapes (signals.py / runners / Backtrader) into one contract without rewriting all engines. |
| D7 | Backtest engines | Vectorized `builder.py` is primary; `event_driven/` (Backtrader) is validation/execution-sim only; **no further investment in Backtrader** | Backtrader is unmaintained; daily-bar strategies don't need it as primary. |
| D8 | Cerebro pipeline | **Frozen.** No new work; not on the critical path | 7 proposals, 0 implementations — idea supply is not the constraint. |

**Resulting strategy mix (revised from brief):** 1× ETF sector/macro rotation, 1–2× CTA futures
(trend; carry if term-structure data is clean), 1× factor-ETF rotation. Target 3–4 live
strategies, judged by *blended portfolio behavior* (vol on target, designed correlations),
not by count.

**Known risk of D3:** sector rotation and factor-ETF rotation are both long-only US-equity-beta
heavy. WP-2.6 carries an explicit correlation gate — if pairwise correlation of *active returns*
exceeds 0.6, one of them gets redesigned (absolute-momentum cash filter, beta hedge) or dropped.

---

## 2. Conventions for the executing agent (read before every WP)

1. Environment: `conda activate ibkr-analytics && export PYTHONPATH=.` — run from repo root.
2. Every WP ends with `make lint && make test` green. New code gets unit tests under
   `tests/unit/` using the fixtures in `tests/conftest.py` (`test_db` for anything touching SQLite).
3. Respect import layering: `core/` imports nothing internal; `alpha_research/` imports `core/`
   only; `dashboard/` may import both. Never import from `dashboard.backend` in research code.
4. Look-ahead discipline (CLAUDE.md): every `[0]`-bar access in signal code carries a comment
   justifying it; weights at date *t* may use only data with timestamp ≤ *t* (post PIT-shift),
   executed per the manifest's `execution_convention`.
5. Research-tracker logging is **mandatory**: every WP session appends one entry to
   `alpha_research/research/STRATEGY_TRACKER.md` (date, what changed, files, status).
6. One WP per branch/session. Do not start a WP whose listed dependencies aren't merged.
7. Do not modify `alpha_research/cerebro/` (frozen, D8). Do not add MLflow dependencies (D1).
8. Secrets/keys (e.g. `DATABENTO_API_KEY`) go through `core/config.py` Pydantic settings + `.env`,
   never hardcoded.
9. If a WP forces a design decision not covered by D1–D8, **stop and ask the owner** rather
   than improvising infra.

---

## 3. Phase 1 — One-button research loop (ETF track, $0 data)

**Theme:** one canonical strategy contract, one mandatory review pipeline, a real pool registry,
proven end-to-end by the sector-rotation strategy.
**Gate to start:** none. **Data spend:** $0.

### WP-1.1 Strategy contract & manifest schema
*Depends on: —*

- New `alpha_research/backtests/strategies/manifest.py`:
  - Pydantic `StrategyManifest`: `strategy_id`, `name`, `track` (enum: `etf_rotation | cta_futures | factor_etf`),
    `universe` (explicit tickers or named universe ref), `entrypoint` (`"module:function"`),
    `rebalance` (freq + execution_convention, e.g. `t+1_open`), `cost_model` (id + params),
    `data_requirements` (series/tickers + source), `benchmark`, `naive_baseline`,
    `promotion_rules` (structured block — thresholds in §6 are defaults), `proposal_path`,
    `author`, `created`.
  - Weights contract documented in the module docstring: entrypoint returns
    `pd.DataFrame` (DatetimeIndex × ticker columns, values = target weights; NaN = no position).
- Manifests live at `alpha_research/research/pool/<strategy_id>/manifest.yaml`.
- Loader with validation errors that name the offending field; round-trip (load → dump → load) stable.
- Tests: `tests/unit/test_manifest.py` (valid example, missing-field rejection, bad-enum rejection).

**Acceptance:** example manifest for `sector_rotation` validates; invalid manifests fail with
clear messages; lint/test green.

### WP-1.2 Point-in-time FRED layer
*Depends on: —*

- Publication-lag metadata per FRED series (a `publication_lag_days` map — conservative defaults:
  CPI/employment-style monthly releases ≈ 45/7 days, market-derived daily series = 1 day) in
  `alpha_research/quant_data/pit.py`, with series metadata sourced from / aligned with
  `core/market_data_service.py`.
- `quant_data/api.get_data(..., pit=True)` shifts macro series availability dates; **`pit=True`
  is the default** for FRED series; `pit=False` requires explicit opt-out and logs a warning.
- Tests proving: CPI value for month *M* is unavailable until *M+45d*; `T10Y2Y` shifts 1 day.

**Acceptance:** a backtest consuming CPI via `get_data` cannot see it before publication;
tests demonstrate the shift; existing callers still pass.

### WP-1.3 Data QC preflight
*Depends on: —*

- `alpha_research/quant_data/qc.py`: per-ticker checks — missing bars vs trading calendar
  (reuse `alpha_research/backtests/calendar.py`), stale-price runs (N identical closes),
  extreme-return flags (>|25%| daily for ETFs), coverage vs the manifest's requested date range.
  Optional cross-source spot check (yfinance vs Stooq closes, tolerance 50 bps).
- Emits a `QCReport` dataclass → JSON artifact; severity levels `pass | warn | fail`.
- Tests with synthetic corrupted series.

**Acceptance:** QC on the current `data/market_data/prices` ETF set runs clean or surfaces real
issues; `fail` is machine-readable for WP-1.4 to block on.

### WP-1.4 One-call review pipeline
*Depends on: WP-1.1, WP-1.2, WP-1.3*

- `python -m alpha_research.review run <manifest.yaml>` (new package `alpha_research/review/`),
  wiring existing pieces into one library call:
  1. Load + validate manifest → **QC preflight** (block on `fail` unless `--force`).
  2. Primary backtest via `backtests/builder.py` under the weights contract (D6 adapter).
  3. `backtests/walkforward.py` walk-forward.
  4. Full stats battery from `backtests/stats/`: PSR, DSR (with declared trial count), MinBTL,
     block-bootstrap CI, rolling Sharpe, regime-conditional Sharpe.
  5. Cost sensitivity 1×/2×/3×; parameter sensitivity ±20%/±40% on declared params.
  6. `correlation_with_existing()` vs all non-retired pool strategies.
  7. QuantStats tearsheet + review bundle via `backtests/reporting/review.py`, registered under a
     `run_id` via `backtests/run_manager.py`; `scripts/generate_backtest_review.py` becomes a thin wrapper.
- Fixed artifact set per run: `manifest_snapshot.yaml`, `qc_report.json`, `metrics.json`,
  `stats_battery.json`, `sensitivity.json`, `correlations.json`, `tearsheet.html`, `verdict.md`.
- Deterministic: seeded; re-run on same commit+data reproduces metrics.
- Integration test on a synthetic 3-ticker dataset (fast, in CI).

**Acceptance:** one command, full artifact set, reproducible `run_id`; synthetic-data
integration test green.

### WP-1.5 Pool registry (SQLite state + CLI)
*Depends on: WP-1.1*

- `core/models.py`: `StrategyPoolEntry` table — `strategy_id`, `state`
  (`candidate | paper | live | retired`), `manifest_path`, `latest_run_id`, `registered_at`,
  `state_history` (JSON list of `{state, at, reason}`), `health` (JSON, written by Phase 4 reports).
- `alpha_research/pool/registry.py`: `register(manifest)`, `set_state()` (validated transitions:
  `candidate→paper→live`; `→retired` from any), `list_entries()`, `get(strategy_id)`,
  `attach_run(strategy_id, run_id)`.
- CLI: `python -m alpha_research.pool list | show <id> | promote <id> --to paper --reason "..."`.
- WP-1.4 auto-registers/updates the pool entry on review completion.
- Tests on the `test_db` fixture, including illegal-transition rejection.

**Acceptance:** register → review → `pool list` shows the entry with latest `run_id`; transitions
audited in `state_history`.

### WP-1.6 Reference strategy: ETF sector/macro rotation
*Depends on: WP-1.1–WP-1.5*

Implements `alpha_research/research/strategies/sector_rotation_2026-03-13_conditional/proposal.md`,
**closing its PM requirements first**:

- Add XLI to `config/` ticker universe; pull missing data via the data layer.
- Regime rules pre-committed: write the exact macro-tilt rules into the manifest/proposal
  **before** running the first backtest (anti-data-mining requirement from the PM review).
- Signals: `MacroTiltSignal`, `RelativeStrengthSignal` added to
  `backtests/strategies/signals.py`; strategy module
  `alpha_research/backtests/runners/sector_rotation.py` exposes the weights-contract entrypoint
  (compose with existing `MomentumSignal(lookback=126, skip=21)`).
- FRED inputs via PIT layer (WP-1.2). Naive baseline: equal-weight 11 sectors, monthly.
- Run the full WP-1.4 review; register as `candidate`; record the verdict **whatever it is** —
  Phase 1's goal is the loop, not a pass.

**Acceptance:** full battery artifacts exist; pool entry live; tracker updated; proposal's
"Requirements for Approval" checklist all checked or explicitly waived in writing.

### WP-1.7 Phase 1 gate review
*Depends on: all above*

- Reproducibility check: re-run WP-1.6's review from a clean checkout; metrics match.
- Demonstrate zero manual notebook steps end-to-end.
- Write gate sign-off into `STRATEGY_TRACKER.md`.

**Phase 1 exit criteria:** ☐ one command takes manifest → pool entry with full battery
☐ reproducible `run_id`s ☐ sector-rotation registered with verdict ☐ PIT default-on with tests
☐ $0 spent.

**Phase 1 biggest risk:** engine-contract fragmentation (trying to adapt all three engines).
**Mitigation:** D6 — adapt `builder.py`/`walkforward.py` only; Backtrader gets a one-way adapter
later, and only if cheap.

---

## 4. Phase 2 — Futures data + CTA + factor-ETF track

**Gate to start:** Phase 1 exit criteria signed off.
**Data spend begins here** (Databento historical is largely one-off; expect well under the
$78/mo placeholder; hard ceiling $150/mo).

### WP-2.1 Vendor-agnostic futures schema + contract specs
*Depends on: Phase 1 gate*

- `alpha_research/quant_data/futures/contracts.yaml` + Pydantic models in
  `quant_data/futures/spec.py`: per root — exchange, currency, multiplier, tick size/value,
  contract months, micro flag, IBKR commission + exchange fees (all-in per side), initial-margin
  estimate. Seed with: MES, MNQ, MYM, M2K, MCL, MGC (+ ES, NQ, CL, GC full-size for reference).
  Full fidelity from day one — it's ~30 rows of static YAML.
- Bar schema (vendor-agnostic): `(date, contract_id, root, open, high, low, close, volume, open_interest)`
  → Parquet under `data/market_data/futures/`, registered in the existing catalog/DuckDB flow.

**Acceptance:** specs load + validate; a unit test computes notional and per-side cost for MES
from the table alone.

### WP-2.2 Databento connector + ingestion
*Depends on: WP-2.1*

- `quant_data/connectors/databento.py` (historical daily OHLCV, GLBX.MDP3, by parent symbol →
  individual contract series), conforming to `connectors/base.py`; `DATABENTO_API_KEY` via
  `core/config.py`.
- Ingestion pipeline entry in `quant_data/pipelines/` (pattern: `ingest_bars.py`); log the
  actual dollar cost of the historical pull in the tracker.
- **Vendor-agnostic check:** research code reads only the WP-2.1 schema, never Databento types.

**Acceptance:** ≥10 years of daily bars for the 6 micro roots (or their full-size ancestors where
micros are young) land in Parquet; QC (WP-1.3) passes; no vendor types leak past the connector.

### WP-2.3 Continuous-contract builder + reconciliation
*Depends on: WP-2.2*

- `quant_data/futures/continuous.py`: roll rule (volume/OI crossover with calendar-days-before-expiry
  fallback), producing per root: **Panama (difference) back-adjusted series**, **unadjusted chain**,
  and a **roll-calendar table** (dates + from/to contracts). Term-structure snapshots retained for
  future carry signals.
- **Reconciliation tests (the critical deliverable):** contract-level PnL vs adjusted-series PnL
  for 2 roots × 2 years must match to the dollar; roll counts match the calendar.
- External sanity: eyeball-compare one adjusted series against a public reference; document.

**Acceptance:** reconciliation tests green and kept in CI. *A silent back-adjustment error
inflates trend Sharpe — this WP is not done until the reconciliation passes.*

### WP-2.4 Futures cost model + integer vol-target sizing
*Depends on: WP-2.1, WP-2.3*

- `backtests/costs/futures.py`: per-side commission+fees from the spec table; spread = 1 tick ×
  tick value; roll cost = 2 sides per roll per contract held (driven by the roll calendar).
  **No market-impact term** (irrelevant at this AUM).
- `alpha_research/portfolio/sizing.py`: per-instrument vol-targeted sizing with **integer contract
  rounding** + no-trade band.
- **Granularity report** (markdown artifact): at $25k/$50k/$100k, can a 10%-vol book across the
  6 micros express the signal? Min/max positions per instrument, rounding-error vol contribution.

**Acceptance:** cost model unit-tested against hand-computed MES round-trip + roll; granularity
report reviewed by owner before WP-2.5 starts.

### WP-2.5 CTA trend strategy
*Depends on: WP-2.3, WP-2.4*

- Multi-speed trend: EWMAC-style crossovers (≈16/64, 32/128) + breakout confirmation,
  per-instrument vol targeting, 6–10 roots; weights-contract entrypoint under
  `backtests/runners/`; manifest + proposal per R2.
- Full review pipeline; register as `candidate`.
- **Sanity gate:** correlation of strategy returns vs SG Trend Index monthly returns — expect
  ≈0.5–0.7; below ≈0.3 means data or signal is broken → stop and investigate.

**Acceptance:** pool entry with full battery incl. futures costs at 1×/2×/3×; SG Trend check
documented. Carry variant: only if WP-2.3 term-structure data is clean — owner decides after
seeing it.

### WP-2.6 Factor-ETF rotation strategy (replaces single-name equity, D3)
*Depends on: Phase 1 gate (parallel to WP-2.1–2.5)*

- Universe: liquid factor ETFs (MTUM, VLUE, QUAL, USMV, + candidates from the
  quality/safe-haven research in `STRATEGY_TRACKER.md`); free data.
- Relative momentum across factors + **absolute-momentum cash filter** (the decorrelation lever
  vs sector rotation, D3 risk).
- **Correlation gate:** pairwise correlation of *active returns* (vs SPY) against sector rotation
  > 0.6 → redesign or drop one; decision goes to owner.

**Acceptance:** pool entry with full battery; correlation-gate result documented either way.

### WP-2.7 Phase 2 gate
**Exit criteria:** ☐ ≥3 candidates in pool (sector rotation, CTA trend, factor-ETF) with full
battery ☐ pairwise correlation matrix artifact across pool ☐ continuous-futures reconciliation
in CI ☐ data spend logged and ≤ ceiling.

**Phase 2 biggest risk:** silently wrong back-adjusted futures (the error flatters you).
**Mitigation:** WP-2.3's dollar-exact reconciliation + WP-2.5's SG Trend correlation check.

---

## 5. Phase 3 — Strategy-level portfolio + unattended paper trading

**Gate to start:** ≥2 pool candidates with pairwise correlation < ~0.4.

### WP-3.1 Strategy-level allocator
- New `alpha_research/portfolio/strategy_allocator.py`: inputs are pool strategies' **return
  streams** (not assets). Baseline: risk parity / ERC with Ledoit-Wolf shrinkage (reuse
  `portfolio/risk.py`); comparison: constrained mean-variance. **Explicit 10% portfolio-vol
  target** — note the existing `optimizer.py` `sum(w)==1` formulation does *not* apply
  (futures margin ⇒ capital fractions, not fully-invested weights).
- Output: capital fraction per strategy → netted instrument-level **integer** targets via WP-2.4
  sizing.
- Tests: synthetic 3-stream case with known answer; vol-target realized within tolerance in
  simulation.

### WP-3.2 Daily ops runner
- `scripts/run_daily_ops.py` — staged, idempotent, journaled (stage state in DB):
  `data pull → QC gate → signals → allocator targets → diff vs IBKR paper positions →
  pre-trade risk (execution/risk.py) → orders (paper, port 7497) → audit (execution/audit.py) →
  forward-pass snapshot (forward_pass/trade_tracker.py) → notification summary`.
- `--dry-run` prints intended orders; safe to re-run after partial failure (stages skip if
  journaled complete). **Degraded mode:** on QC fail or stale data, hold positions + alert,
  never trade on bad data.

### WP-3.3 Scheduling + heartbeat
- launchd plist (pattern: `scripts/com.ibkr.pa_automation.plist` + `setup_pa_scheduler.sh`).
- **Heartbeat on silence:** a separate check (cron or healthcheck-ping service) alerts if the
  daily job hasn't journaled a completed run by T+X — the dead-cron failure mode is the one that
  silently costs a month of paper record.

### WP-3.4 Reconciliation + forward pass
- Nightly `scripts/run_reconcile.py`: expected vs actual positions/fills/PnL from IBKR paper;
  tolerance config; breaks logged to DB + alert. This log **is** the Phase 4 go-live evidence.

### WP-3.5 Closed-loop rebalancer
- Drive `portfolio/rebalancer.py` from drift vs allocator targets with no-trade bands sized to
  micro-contract granularity (WP-2.4) so integer rounding doesn't cause churn.

### WP-3.6 Phase 3 gate
**Exit criteria:** ☐ **20 consecutive trading days unattended** (zero manual interventions)
☐ reconciliation within tolerance throughout ☐ every position forward-tracked ☐ heartbeat
verified by a deliberate kill test. **The promotion clock starts only when this is true.**

**Phase 3 biggest risk:** unattended reliability (IBKR Gateway session expiry, data flakiness,
scheduler death). **Mitigation:** idempotent staged design, degraded mode, heartbeat-on-silence,
deliberate failure-injection test before the 20-day clock starts.

---

## 6. Phase 4 — Monitoring, gated go-live, refinement loop

**Gate to start:** Phase 3 exit + paper clock running.

### WP-4.1 Pool & live dashboard (the deferred UI, now earns its keep)
- `dashboard/backend/api/` pool routes reading the registry + latest run artifacts; Dash tab:
  per-strategy attribution, realized vs design vol, drawdown vs budget, rolling pairwise
  correlation drift, regime flags, lifecycle states.

### WP-4.2 Promotion gate engine
- Rules engine reading each manifest's pre-committed `promotion_rules`. **Defaults:**
  - `candidate → paper`: DSR > 0 at 95% confidence; PSR(SR★=0) > 0.90; survives 2× costs;
    |corr| < 0.4 vs active pool.
  - `paper → live`: Phase 3 ops record clean **and** paper returns within the backtest's PSR
    confidence band for elapsed N **and** realized vol within ±25% of design **and** zero
    unexplained reconciliation breaks. *(The 3–6-month paper window validates operations and
    consistency — it cannot statistically validate Sharpe; do not pretend otherwise.)*
  - Overrides require a written owner note in `state_history`.

### WP-4.3 Monthly strategy-health report
- Automated job: `sharpe_decay_rate`, `strategy_half_life`, regime-conditional Sharpe,
  live-vs-backtest tracking error (forward-pass comparison) → written to pool `health` JSON +
  appended to `STRATEGY_TRACKER.md`. **Retire/refit rules are pre-committed in the manifest at
  registration** — demotion is mechanical, not a mood.

### WP-4.4 Go-live runbook + capital ramp
- Runbook: switch paper→live config, capital ramp 25% → 50% → 100% across subsequent months,
  rollback procedure, kill-switch (flatten-all via `execution/`).

**Phase 4 exit criteria:** ☐ ≥1 strategy live via the gate ☐ monthly health report fully
automated ☐ one retire-or-refit decision executed by rule ☐ lifecycle loop documented
(Data → Research → Deploy → Monitor → Research).

**Phase 4 biggest risk:** behavioral — overriding your own gates. **Mitigation:** rules in the
manifest before the paper period starts; overrides only as written, audited notes.

---

## 7. Deferred / open items (revisit at the phase that forces them)

- **Final futures vendor commitment** (D2): revisit after WP-2.2 — if Databento ingestion +
  in-house continuous build is clean, commit; if painful, Norgate-in-VM is the fallback.
- **CTA carry strategy:** decision after WP-2.3 term-structure quality is known.
- **Tax-aware allocation:** futures get 60/40 treatment; monthly-turnover ETF strategies generate
  short-term gains in a taxable account — a structural argument to tilt the allocator toward CTA.
  Note in WP-3.1 design; no build until Phase 4+.
- **Fundamentals / single-name equity revival:** only if the factor-ETF track proves too
  correlated AND capital grows past ~$100k.
