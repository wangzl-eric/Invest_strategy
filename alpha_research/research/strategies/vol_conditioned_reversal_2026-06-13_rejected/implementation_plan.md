<!-- 2026-06-14: S4 implementation plan (Dev role) for vol_conditioned_reversal.
PLAN ONLY — no code, no manifest.yaml, no runner, no notebook, no trial-ledger row is written by this
artifact. Every Sharpe / return / turnover figure quoted is a labelled EXPECTATION carried from the
proposal, or a HISTORICAL result for a DIFFERENT in-repo strategy (labelled). No vol_conditioned_reversal
backtest exists. This document describes EXACTLY how Fire 2 (coding) will implement the vetted proposal. -->

# Implementation Plan — Vol-Conditioned Sector Reversal (`vol_conditioned_reversal`)

> **Role:** Dev (implementation planner) · **Stage:** S4 (between vetted proposal and Fire-2 coding)
> **Decision owner:** Zelin · **Researcher of record:** Elena · **Date:** 2026-06-14
> **Inputs read:** `proposal.md` (S2 canonical), `pm_review.md` (S3, verdict CONDITIONAL, R1–R13),
> reference runner `alpha_research/backtests/runners/sector_rotation.py`, review engine
> `alpha_research/review/engine.py`, manifest schema
> `alpha_research/backtests/strategies/manifest.py`, pipeline `alpha_research/review/pipeline.py`,
> trial ledger `alpha_research/review/ledger.py`, PIT table `alpha_research/quant_data/pit.py`.
> **Scope guard:** SPEC of the implementation only. NO code, NO `manifest.yaml`, NO runner, NO test
> file, NO ledger row is produced here. The yaml block in §2 is *text in this plan*, not a written file.
> **Honesty flag:** all performance figures are EXPECTATIONS or HISTORICAL (other strategies), never
> realized results for this strategy.

---

## 0. What I verified in the engine before planning (load-bearing constraints)

Three facts in the current review stack drive every decision below. They are not assumptions — I read
them out of the code:

1. **The entrypoint receives `macro` as a `dict[series_id -> pd.Series]`, PIT-shifted, NOT as a price
   column.** `pipeline.run_review` builds `macro` via `default_macro_loader`, which calls
   `get_data(series_ids, source="fred", pit=True)` and `as_of_series(...)` aligned to the price index
   (`pipeline.py:87-99`, `:470-471`). Therefore **VIX must be declared as a `macro` `data_requirement`
   with `id: VIXCLS, source: fred`**, and the runner reads the gate off `macro["VIXCLS"]` — *never* off
   the price frame. `pit.py:71` already registers `"VIXCLS": 1` calendar-day publication lag, so the
   series the runner sees is availability-dated by default. This is the mechanical satisfaction of PM
   **R5** (no future VIX) and resolves the proposal's §11.1 framing into the only correct plumbing.

2. **The vectorized engine charges ONLY a flat proportional cost on turnover.**
   `run_weights_backtest` computes `costs = turnover * (cost_bps / 10_000)` with a single scalar
   `cost_bps` (`engine.py:89-97`); `_cost_sensitivity` re-runs at `bps × {1,2,3}` (`pipeline.py:179-194`).
   **There is NO volatility-conditional spread and NO `max(per-share, $1)` order floor in the engine
   today.** The proposal's §6 (vol-conditional stressed spreads, $1 IBKR floor at 25k) and PM **R2**
   (charge the floor per-leg-per-rebalance) **cannot be expressed by the current `CostModelSpec`**
   (`manifest.py:80-85`: only `id` + `bps`). This is the single biggest implementation gap and is an
   **OWNER decision** (§5, D-COST). The plan below specifies both the honest-but-coarse path (pick a
   stressed `bps` that the 1×/2×/3× sweep brackets the real cost with) and the correct-but-larger path
   (extend the engine with a regime/floor-aware cost model).

3. **Shorts and gross-1.0 normalization already work; the EW baseline does not.** The engine computes
   `gross = (w_eff * rets).sum(axis=1)` (`engine.py:89`), which is sign-correct for negative weights;
   turnover is `|Δw|` summed (`:91-94`), correct for a long/short book; `_validate_weights` keys off
   `weights.abs().sum(axis=1)` and permits gross ≤ 3.0 (`pipeline.py:657-662`), so a dollar-neutral book
   at `Σ|w| = 1.0` passes. **No engine change is needed for shorts.** BUT `equal_weight_baseline`
   (`engine.py:146-165`) is **long-only** `1/n`, so it carries the equity risk premium our market-neutral
   book does not — the K3-vs-EW comparison is a category error on raw Sharpe (PM **R9**). The runner
   cannot fix this; it is a reporting/gate-interpretation decision recorded in the manifest description
   and §4 below.

---

## 1. Target runner file & entrypoint

**File:** `alpha_research/backtests/runners/vol_conditioned_reversal.py`
**Entrypoint (manifest `entrypoint`):**
`alpha_research.backtests.runners.vol_conditioned_reversal:build_weights`

**Signature (weights contract — identical to `sector_rotation.build_weights`):**

```
build_weights(prices: pd.DataFrame,
              macro: Optional[Dict[str, pd.Series]],
              params: dict) -> pd.DataFrame   # DatetimeIndex × ticker target weights
```

**How it mirrors `sector_rotation.build_weights`, and where it deliberately differs:**

| Aspect | `sector_rotation` (long-only ref) | `vol_conditioned_reversal` (this strategy) |
|---|---|---|
| Rebalance dates | `rebalance_dates(px.index, "monthly")` | `rebalance_dates(px.index, "weekly")` — same engine helper, snaps to last trading day of each week (`engine.py:132-143`; PM confirms in `pm_review.md` "What I am NOT requiring") |
| Eligibility | `mom.notna() & rs.notna()`, `n_elig ≥ 3`, ineligible → explicit 0 | `r5.notna()` AND `≥5` post-inception days AND `macro["VIXCLS"]` warm; `n_elig ≥ min_eligible (5)`; ineligible → explicit 0 (same `mom.loc[d].notna()` pattern) |
| Signal | composite `0.5·z(mom)+0.3·macro+0.2·z(rs)` | `r5_i = close_i(t)/close_i(t-5) − 1`; cross-sectional `z_i`; reversal tilt `s_i = −z_i` |
| Regime gate | none (always invested) | **binary VIX gate**: active iff `V(t) > median(V(t−59..t))` on the PIT-shifted `macro["VIXCLS"]`; else **all weights 0** that week |
| Normalization | tilt around `1/n`, clip `≤ max_weight`, renormalize so `Σw = 1` (LONG-ONLY) | **dollar-neutral**: demean `s_i` so `Σw_i = 0`, clip `|w_i| ≤ max_weight (0.20)`, renormalize so `Σ|w_i| = gross (1.0)` → 50% long / 50% short, net 0 |
| Sign | weights ≥ 0 | weights signed (longs `>0`, shorts `<0`) |
| No-trade band | none | `band = 0.05`: hold `w_prev_i` unless `|w_target_i − w_prev_i| > band` (stateful across rebalance dates) |
| Pre-shift | NEVER (engine shifts) | NEVER (engine shifts) — returns **unshifted** weights |

**Construction sequence inside `build_weights` (pre-committed, proposal §2):**
1. `universe = [t for t in prices.columns if t in SECTOR_ETFS]`; `px = prices[universe].sort_index()`.
2. `r5 = px / px.shift(5) − 1` (entirely backward-looking).
3. Pull VIX from `macro["VIXCLS"]` (already PIT-shifted, as-of-ffilled to the price index by the loader).
   Compute the **trailing-60 strictly-backward median** `M(t) = r5_index_rolling(window=60, min_periods=60).median()`
   shifted to use only `V(≤t)`. **`min_periods=60` is mandatory** — a partially-padded window biases the
   duty cycle (PM **R6**); the first tradable date is the first index date where the 60-obs window is full
   AND ≥5 post-inception days exist for ≥`min_eligible` sectors.
4. `rebal = rebalance_dates(px.index, "weekly")`, filtered to dates ≥ the warmup boundary.
5. For each `d in rebal`: if `macro["VIXCLS"][d] ≤ M(d)` → gate OFF → set `weights.loc[d] = 0.0` for all
   eligible cols (explicit flat, zero gross). Else: compute `z` over eligible cols, `s = −z`, demean `s`,
   clip to `±max_weight`, renormalize to `Σ|w| = gross`, then apply the **no-trade band vs the previously
   set book** (`w_prev` = the last non-NaN weight row, carried as engine ffills between rebalances).
6. Return the full `weights` frame (NaN before warmup; 0.0 on gated-off weeks; signed on active weeks).
   **Do not pre-shift.** The engine applies `shift_bars=2` for `t+1_open`.

**Helper functions to expose (mirroring `sector_rotation`'s `__all__`):** `build_weights`,
`vix_gate(macro, index, vix_lookback)` (returns the boolean active-series for testability), `SECTOR_ETFS`
(the dynamic-membership list), `DEFAULT_PARAMS`. Exposing `vix_gate` separately lets the look-ahead test
(§4) assert the gate's truncation-invariance in isolation.

**Engine/cost interaction the implementer must respect (from §0):**
- Gross-1.0 dollar-neutral weights pass `_validate_weights` unchanged; **no engine patch for shorts.**
- The cost model the engine applies is the manifest's flat `cost_model.bps` on `Σ|Δw|` turnover. The
  vol-conditional / $1-floor cost story (proposal §6, PM R2) is **NOT representable** without an engine
  extension — see §5 D-COST. The runner itself does not implement costs; it only emits weights.
- Because the book is flat ~half the weeks, turnover on gated-off→on transitions is a full `gross`
  entry and on→off is a full exit; the no-trade band only suppresses churn *between two active weeks*.
  The implementer must confirm `dw.iloc[0]` seeding (`engine.py:92-93`) does not double-count the first
  active entry.

---

## 2. Manifest skeleton (TEXT in this plan — NOT a written file)

This is the pre-committed manifest the researcher will create at
`alpha_research/research/pool/vol_conditioned_reversal_v1/manifest.yaml` in Fire 2. **`strategy_id` ends
in `_v1` on purpose**: `ledger.derive_hypothesis_id` strips the `_vN` suffix (`ledger.py:44-56`), so
trials accumulate under the `vol_conditioned_reversal` hypothesis across future spec versions — the
floor-that-only-goes-up behaviour PM **R13** requires.

```yaml
schema_version: 1
strategy_id: vol_conditioned_reversal_v1
name: Vol-Conditioned Sector Reversal
track: etf_rotation
# Dynamic 9->10->11 membership is enforced in the runner by eligibility (>=5
# post-inception days), NOT by the manifest universe. The universe lists the
# full 11; XLRE/XLC get explicit 0 weight before their inception (no backfill).
universe:
  - XLK
  - XLF
  - XLE
  - XLV
  - XLY
  - XLP
  - XLI
  - XLB
  - XLU
  - XLRE
  - XLC
entrypoint: alpha_research.backtests.runners.vol_conditioned_reversal:build_weights
params:
  reversal_lookback: 5        # Lehmann/Nagel weekly horizon; from literature, not tuned
  vix_lookback: 60            # trailing strictly-backward median window (free param; battery perturbs)
  vix_threshold_pct: 50       # gate active iff V(t) > 50th-pct (median) of trailing window
  construction: long_short    # dollar-neutral; sum(w)=0, gross=1.0
  gross: 1.0                  # 0.5 long / 0.5 short
  max_weight: 0.20            # per-name cap (mirrors sector_rotation)
  no_trade_band: 0.05         # turnover AND $1-commission-floor control
  n_legs_per_side: 0          # 0 = full proportional-z tilt (baseline); >0 = tails-only variant
  min_eligible: 5             # below this cross-section -> flat
  mom_neutralize: false       # OFF in v1 baseline; ON is a declared, trial-counted variant (PM R7)
rebalance:
  frequency: weekly
  execution_convention: t+1_open   # engine applies shift_bars=2 (conservative next-bar)
cost_model:
  # ENGINE LIMITATION (see implementation_plan §0.2, §5 D-COST): the current
  # proportional model charges a single flat bps on turnover; it has NO
  # vol-conditional spread and NO $1 order floor. The bps below is a placeholder
  # STRESSED round-trip-equivalent pending the OWNER decision on whether to
  # extend the engine. DO NOT treat this as the proposal's full §6 model.
  id: proportional
  bps: 8.0                    # placeholder: high-VIX stressed half-spread proxy; 1x/2x/3x sweep brackets it
data_requirements:
  - id: VIXCLS               # FRED VIX close; PIT-shifted (1-day pub lag, pit.py:71) -> gate reads availability-dated
    kind: macro
    source: fred
benchmark: SPY
naive_baseline: equal_weight_11_sectors_weekly
backtest_start: "2012-04-01"   # PLACEHOLDER: first date with a fully-populated trailing-60 VIX window
                               # on the PIT-shifted series; pin the EXACT date in Fire 2 (PM R6) before
                               # freezing — do not ship a partially-warmed window.
backtest_end: null             # latest common date (ETFs ~2026-06-11; refresh VIXCLS to match)
n_trials: 24                   # HONEST FLOOR (proposal §13); feeds DSR; ledger accumulates and only grows
promotion_rules:
  min_dsr: 0.95
  min_psr: 0.90
  cost_multiplier_survival: 2.0   # Sharpe must stay > 0 at 2x stressed cost (K1)
  max_abs_correlation: 0.4        # vs sector_rotation_v1 and any active stream (K6)
  min_paper_trading_days: 60
  realized_vol_tolerance: 0.25
proposal_path: alpha_research/research/strategies/vol_conditioned_reversal_2026-06-13_PENDING/proposal.md
author: Zelin (spec), Elena (proposal)
created: 2026-06-14
description: >
  Dollar-neutral cross-sectional 5-day reversal across the 11 SPDR sector ETFs,
  ACTIVE ONLY when VIX > its trailing-60-day median (else flat ~half the weeks).
  Long the worst recent sectors, short the best; weekly clock, t+1_open, no-trade
  band 0.05. Mechanism: liquidity provision to vol-constrained intermediaries in
  stress (Nagel 2012). COST-BOUND, not alpha-bound: expected NET Sharpe ~0.3-0.5,
  ~35-45% chance net<=0 at 2x stressed cost. Modal kills: MinBTL on the half-length
  high-VIX sub-sample (K9) and the 2x cost gate (K1). EW baseline is long-only and
  carries the equity premium this market-neutral book does not -> K3 is a
  portfolio-contribution test (|rho| + marginal Sharpe), NOT a raw Sharpe-vs-EW
  comparison (PM R9). The cost_model bps is a placeholder pending the engine's
  vol-conditional/$1-floor extension (implementation_plan §5 D-COST).
```

**Fields that intentionally differ from the schema defaults / `sector_rotation_v1`:**
- `universe` lists 11 but membership is dynamic via runner eligibility (XLRE/XLC explicit-0 pre-inception).
- `rebalance.frequency: weekly` (vs monthly ref) and `execution_convention: t+1_open` (→ `shift_bars=2`,
  conservative; `manifest.py:68-70`).
- `cost_model.bps` is flagged as a **placeholder** because the schema cannot express the real §6 model.
- `n_trials: 24` is the honest floor (§3), far above the ref's 10.
- `data_requirements` is a **single macro entry (VIXCLS)** — no price `data_requirement` rows are needed
  (the universe drives the price pull; `pipeline.py:463-466`).

---

## 3. Honest `n_trials` FLOOR — validate the declared 24

The proposal declares `n_trials = 24` (§13) and the PM accepts it as a floor and explicitly warns it may
be *too low* (R13). I **validate 24 as the floor** by counting the distinct configurations the researcher
commits to evaluating. Counting the design axes the proposal/PM enumerate:

| Axis | Distinct values committed | Source |
|---|---|---|
| `reversal_lookback` | 3 (4 / 5 / 6; with 3,7 at ±40% the grid is wider but 3 are the committed centres) | §8, §13 |
| `vix_lookback` / threshold | 3 (window 48/60/72 and/or percentile 40/50/60) | §8, §13 |
| `no_trade_band` | 3 (0.04 / 0.05 / 0.06) | §8, §13 |
| `n_legs_per_side` | 3 (full-tilt / 2 / 3) | §6.2, §13 |
| `mom_neutralize` | 2 (off baseline / on variant — PM R7 runs ON in pass 1) | §2, §13 |
| `rebalance.frequency` | 3 (weekly baseline / daily / biweekly as declared trials) | §4, §13 |

A full grid is a few hundred cells; the proposal's **honest committed count is 24 distinct variations**,
explicitly not 1 and explicitly not the full product. **I keep 24 as the manifest floor.** Justification
and the two adjustments the implementer must respect:

1. **24 is a FLOOR, not a ceiling (PM R13).** The ledger (`ledger.py`) computes the *effective* n_trials
   from accumulated distinct `manifest_hash`es under the `vol_conditioned_reversal` hypothesis and feeds
   *that* to DSR (`pipeline.py:117`, `_stats_battery` uses `n_trials_effective`). The manifest 24 is the
   minimum. If S5 touches any parameter outside the declared grid (e.g. a band of 0.10, a threshold
   percentile of 25), the ledger increments and DSR re-deflates — **the runner/manifest must never shrink
   24 to pass DSR** (K10).
2. **Family-history caveat (PM R13, advisory).** `vix_regime` consumed the VIX-gating axis and
   `sector_rotation_v1` consumed the sector cross-section on the *same universe*; the proposal is
   calibrated on their results. The ledger only accumulates within the *same hypothesis_id*, so it will
   NOT auto-fold those priors in (different hypothesis keys). I therefore note 24 as a defensible floor
   **for this strategy's own design space** and flag to the owner that the honest *family* count is
   arguably higher — but I do not inflate the manifest number speculatively; the ledger is the system of
   record and the owner can set a higher floor if they judge the cross-family reuse material (§5 D-TRIALS).

**Net recommendation:** keep `n_trials: 24`. Do not adjust down. The owner may choose to set it higher
(e.g. 30) if they want the cross-family priors counted; that is D-TRIALS in §5.

---

## 4. Look-ahead unit test (truncation-invariance) — what it must assert

**File:** `tests/unit/test_vol_conditioned_reversal_strategy.py`
**Canonical test name (matches the repo pattern):** `test_no_lookahead_truncation_invariance`, mirroring
`tests/unit/test_sector_rotation_strategy.py:65-84`.

**Fixtures (synthetic, offline — mirror the sector_rotation test):**
- `_sector_prices(n, seed)`: wide close frame over the 11 `SECTOR_ETFS`, but with **dynamic inception**:
  XLRE all-NaN before a synthetic 2015-style date, XLC all-NaN before a 2018-style date — so the test
  exercises the eligibility/explicit-0 path AND the cross-section-size change (PM R8).
- `_vix(index)`: a synthetic `macro = {"VIXCLS": pd.Series(...)}` that **crosses its own trailing-60
  median both up and down** within the sample, so both gate-ON and gate-OFF weeks occur (a constant VIX
  would make the gate test vacuous). The series must already be ffilled to the price index (the real
  loader does this via `as_of_series`).

**The test must assert ALL of the following:**

1. **Truncation-invariance of weights (the core property, PM R5).** Build full weights; truncate BOTH
   the price panel AND the VIX series at an interior date `T`; rebuild. On the rebalance rows present in
   both frames (intersection, excluding the truncated frame's final partial-week), the two weight frames
   are **bit-identical** (`pd.testing.assert_frame_equal(..., atol=1e-12, rtol=0)`). This is the
   `sector_rotation` pattern extended to carry the VIX panel through the truncation.
2. **Truncation-invariance of the GATE specifically.** Calling `vix_gate(macro, index, vix_lookback)` on
   the full vs truncated VIX series yields identical boolean values on the common dates. This isolates
   the gate so a regression in the rolling-median window (e.g. accidental `center=True`) is caught
   directly, not masked by the weighting layer.
3. **No-future-VIX property (PM R5, explicit).** For every rebalance date `t`, the gate decision uses no
   VIX observation whose *availability date* > `t`. Concretely: the median at `t` is computed from
   `V(≤t)` only; assert that replacing all `V(>t)` with NaN (or arbitrary values) does not change the
   gate at `t`. Because the loader PIT-shifts VIXCLS by its 1-day lag, the test should also assert the
   runner reads `macro["VIXCLS"]` and never a price column named like VIX (guard against mis-wiring).
4. **Warmup boundary is fully populated (PM R6).** The first non-NaN weight row occurs no earlier than
   the first date with a **full** trailing-60 VIX window (`min_periods=60`) AND ≥5 post-inception days
   for ≥`min_eligible` sectors. Assert there is NO weight row inside the warmup region.
5. **Dollar-neutral / gross invariants on active weeks.** On every gate-ON rebalance row:
   `Σ_i w_i ≈ 0` (atol 1e-9), `Σ_i |w_i| ≈ gross` (atol 1e-9), `max |w_i| ≤ max_weight + 1e-9`, and at
   least one positive and one negative weight exist. On gate-OFF rows: all weights exactly 0.
6. **Dynamic-universe / no-backfill (PM R8).** XLRE/XLC weights are exactly 0 (or NaN) on every date
   before their synthetic inception; no synthetic pre-inception value leaks into the z-score
   cross-section (assert the ineligible names are excluded from the `z` computation, not assigned a
   phantom value).
7. **Unshifted-output contract.** The runner returns weights whose timestamp `t` uses only data `≤ t`
   (covered by 1–4); the test does NOT pre-shift and relies on the engine's `shift_bars`. (No assertion
   on the shift itself — that is the engine's `test_backtest_engine.py` territory.)

**Companion (non-look-ahead) tests to include, mirroring the ref test class:**
`test_weights_contract_shape`, `test_dollar_neutral_and_gross_one`, `test_gate_off_is_flat`,
`test_no_trade_band_reduces_turnover` (build with band 0.0 vs 0.05, assert Σ|Δw| is lower with the band),
`test_runs_with_constant_vix_is_mostly_flat`, `test_default_params_used_when_missing`.

---

## 5. Open decisions needing the OWNER before coding

These are genuine design forks the Dev cannot resolve unilaterally; each blocks or shapes Fire 2.

- **D-COST — the cost model is the whole strategy and the engine can't express it (BLOCKING).** The
  proposal §6 + PM R2 require a **volatility-conditional** spread (calm 1–3 bps vs stressed 3–8 bps,
  tail 15–30 bps) AND a **`max(per-share, $1/order)` floor charged per-leg-per-rebalance at 25k**. The
  current engine charges only flat `cost_bps × turnover` (`engine.py:89-97`). Two paths — **owner picks**:
  (a) *Extend the engine/`CostModelSpec`* with a regime-conditional + per-order-floor cost model
  (cleanest, satisfies R2 literally, but is a non-trivial engine change touching `manifest.py`,
  `engine.py`, `pipeline.py:_cost_sensitivity`, and the gate logic; needs its own tests). (b) *Approximate
  now*: pick a single **stressed** `bps` (placeholder 8.0 in §2) chosen so the 1×/2×/3× sweep brackets the
  realistic stressed round-trip, and compute the $1-floor drag at 25k as an **out-of-engine annotation**
  in the verdict (≈50–65 bps/yr per PM B1) rather than inside the backtest. Path (b) ships faster but
  leaves the floor uncharged *inside* the Sharpe, which the PM's R2 says flatters the result. **My
  recommendation: do (b) for the first battery pass to get K1/K9 numbers fast (PM R1 ordering), then
  (a) before any promotion past candidate.** Owner must confirm.
- **D-VIX-SOURCE — confirm VIXCLS (FRED) over refreshed `^VIX`.** The proposal §11.1 and PM R5 pin
  `VIXCLS` (PIT-clean, vendor-stable, stale local `^VIX` ends 2026-02-27). The plan assumes VIXCLS as a
  `macro` requirement. Owner confirms VIXCLS, OR elects same-day `^VIX` (which would require refreshing
  the `vix_daily` cache AND a different, non-default consumption convention — not recommended).
- **D-HISTORY-START — backfill to ~1999 SPDR inception vs local 2012 start (affects the modal kill).**
  MinBTL on the half-length high-VIX sub-sample (K9/R12) is the most likely kill. A yfinance/Stooq pull
  back to ~Dec-1998 roughly doubles the calendar and is the ONLY lever that relieves K9 (necessary, not
  sufficient — it does not change the half-duty-cycle; PM R12). The local lake starts 2012 for the 9 core
  sectors. **Owner decides:** attempt the long-history pull (extra data-engineering, dividend-adjustment
  QC across 25 years, splice risk) before the first run, OR run on 2012 local first and accept that K9
  may kill it on the short sample. The Aug-2007 Khandani-Lo tail diagnostic (PM R10) is ONLY available
  if the long pull lands.
- **D-EMBARGO — is an 18-month OOS embargo required, and on which window?** The platform's walk-forward
  is 4 contiguous folds (`pipeline.py:64,128-143`) with no explicit held-out embargo. The mission
  cares about OOS Sharpe (Gate 2) and IS/OOS ratio (Gate 6). Owner decides whether to reserve a final
  ~18-month embargo (e.g. 2025-01 → 2026-06) untouched until the spec is frozen, and whether the
  ledger/`backtest_end` should exclude it during development. This is not expressible in the current
  manifest and would be a process commitment.
- **D-CAPITAL — which AUM is the decision-grade column: 25k, 100k, or both reported?** The proposal
  centres the 25k stressed column (where the $1 floor binds, PM B3) and reports 100k for capacity. The
  engine runs at a single `initial_cash` (`engine.py:40`, default 100k). With a percentage-bps cost model
  the AUM is irrelevant to Sharpe; it matters ONLY once the $1 floor is modelled (D-COST path a).
  **Owner confirms 25k is the decision-grade column** so the cost extension (if chosen) is calibrated
  there, and 100k is reported as the capacity check.
- **D-TRIALS — accept `n_trials = 24` floor, or raise it for cross-family reuse?** §3: 24 is defensible
  for this strategy's own design space; the PM (R13) notes the honest *family* count (reusing `vix_regime`
  / `sector_rotation_v1` priors) is arguably higher and the ledger won't auto-fold those in. Owner decides
  whether to set the manifest floor at 24 (my recommendation) or higher (e.g. 30) to pre-pay for the
  cross-family priors. Never lower.
- **D-KILL-HIERARCHY — confirm K4 ≻ K2 as a HARD kill (PM R4).** The PM elevates K4 (must beat the 21-day
  trailing-vol filter) above K2 (must beat unconditional reversal) and makes it a *hard* kill of the
  VIX-specific claim, not PM-judgment. This is a pre-commitment the owner records before any run (it
  changes what "the strategy survived" means). Not a code decision, but it gates interpretation of the
  S5 battery and must be acknowledged before Fire 2.

---

## 6. Fire-2 build order (so the modal kills surface first — PM R1)

For the implementer, the order that respects PM R1/R12 (compute the two modal kills before any sweep):
1. Implement `build_weights` + `vix_gate` + the look-ahead test (§4); get the test green on synthetic data.
2. Write the manifest (§2) at `alpha_research/research/pool/vol_conditioned_reversal_v1/manifest.yaml`;
   pin the exact warmed `backtest_start` (PM R6).
3. Resolve D-COST path (b) for the first pass and D-VIX-SOURCE / D-HISTORY-START with the owner.
4. Run `python -m alpha_research.review run <manifest>` ONCE at baseline — read **K1 (net Sharpe at 2×
   stressed cost)** and **K9/MinBTL on the high-VIX sub-sample** FIRST, before touching any parameter.
   If either fails, stop: the strategy is dead and that is the correct outcome.
5. Only if both survive: run the `mom_neutralize=on` arm (PM R7) and the declared sensitivity trials,
   letting the ledger accumulate n_trials honestly.

---

**Disposition:** The implementation is mechanically straightforward for the runner (shorts and gross-1.0
already work in the engine) and the look-ahead test (the sector_rotation pattern extends cleanly to carry
the VIX panel). The **one hard blocker is D-COST**: the engine cannot today express the vol-conditional +
$1-floor cost model that the proposal's entire cost-bound thesis and PM R2 demand — that is an owner
decision (extend the engine vs approximate-and-annotate). Everything else is a confirm-and-go. With
D-COST and D-VIX-SOURCE / D-HISTORY-START resolved, Fire 2 can build to this spec.
