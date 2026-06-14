<!-- 2026-06-14: S2 independent proposal draft — lens: RISK, TAIL BEHAVIOR & BASELINE BEATABILITY. Spec only; no code, no manifest, no runner, no trial-ledger row. All Sharpe/return figures are reasoned EXPECTATIONS, explicitly labelled; no backtest for this strategy exists. -->

# S2 Proposal Draft (Risk / Tail / Baseline lens) — Vol-Conditioned Sector Reversal

> **Strategy id (proposed):** `vol_conditioned_reversal`
> **Folder:** `vol_conditioned_reversal_2026-06-13_PENDING`
> **Stage:** S2 independent draft · **Lens:** risk, tail behavior & baseline beatability · **Date:** 2026-06-14 · **Decision owner:** Zelin
> **Inputs:** S0 `hypothesis.md` (PASS to S1), S1 `cerebro_briefing.md` (REVISE, 4 pre-commitments).
> **Scope guard:** SPEC ONLY. No code, no `manifest.yaml`, no runner, no trial-ledger row.
> **Honesty:** No `vol_conditioned_reversal` backtest exists. Every Sharpe / return / turnover figure here is a reasoned **EXPECTATION** (labelled) or a **HISTORICAL** result for a *different* in-repo strategy (labelled). Nothing here is a measured result for this strategy.

---

## 0. Lens thesis (read this first)

This strategy is a **short-liquidity / short-volatility carry trade in disguise**. It earns a small premium on most high-VIX days for absorbing one-sided sector flow, and it pays that premium back — violently — in the rare forced-deleveraging cascade (Aug-2007, Mar-2020). Crucially, **the gate concentrates ALL of our exposure into exactly the regime where the tail detonates.** So the central question of this draft is not "is there an edge?" (the briefing's mechanism case is strong) but **"does the edge survive its own tail and beat the three dumbest credible alternatives net of stressed costs?"** My prior, before any data: **net L/S Sharpe lands at or below the LOW end of the 0.4–0.8 band, with a left tail far heavier than its Sharpe implies, and a real (≈40%) chance it fails to clear the unconditional-reversal baseline or Gate 8 (Sharpe < 0 at 3× cost).** I write the spec so that those outcomes are *surfaced early and kill the strategy cleanly*, not buried under an attractive average Sharpe.

Three load-bearing claims from the briefing drive every design choice below:
1. **The unconditional 5-day sector reversal is decayed to ~zero** (Chordia-Subrahmanyam-Tong 2014; Blitz et al. 2024; Nagel's own "industry reversal pays ≈ nothing unconditionally"). → The VIX gate is not an enhancement; it is the entire strategy. → The single most important baseline is the **unconditional reversal** itself (does the gate add measured Sharpe?).
2. **The edge and the tail are the same trade** (Khandani-Lo 2011). → Tail diagnostics are gating, not decorative. → I pre-commit kill thresholds on worst-week, conditional MaxDD, and skew, not just on average Sharpe.
3. **Sector ETFs are the lowest-premium layer of the asset class** (Avramov-Chordia-Goyal 2006; AP arbitrage keeps prices tight). → The gross signal is structurally thin, so **stressed (vol-conditional) costs, not flat bps, decide the outcome.** This is a *translation-risk* bet that may simply not clear ETF costs.

---

## 1. Economic rationale — who loses money, and why the premium survives where it does

The reversal long/short **is** a liquidity-provision return (Nagel 2012, *RFS* 25(7):2005–2039). When a sector ETF sells off hard over a week, some of that move is transitory price pressure from forced/uninformed flow — de-risking funds cutting beta, panic rebalancers, leveraged-ETF daily hedging, index/sector reallocations. Whoever stands in to absorb that flow earns compensation for bearing inventory and adverse-selection risk until the pressure dissipates. **The counterparties who lose money to us are the sellers of immediacy:** participants who must transact *now* and pay to do so. Nagel's key empirical fact is that **this compensation scales with the VIX** — because in high-vol states, volatility-constrained intermediaries (dealers, stat-arb desks, APs) shrink risk capital, fewer agents will warehouse the flow, and the surviving providers demand a higher premium. Hameed, Kang & Viswanathan (2010, *JF* 65(1):257–293) independently confirm the supply-side channel and, importantly for us, document **inter-industry liquidity spillovers** from market-maker capital constraints — tying the mechanism to the *sector* level we actually trade rather than only single stocks.

**But the rationale comes pre-loaded with its own contradiction, and the risk lens insists we state it plainly:**

- **The same premium is payment for a catastrophic tail (Khandani-Lo 2011, *JFM* 14(1):1–46).** The dollar-neutral buy-losers/short-winners book — our *exact* mechanical construction — suffered unprecedented, autocorrelated losses in the Aug-2007 quant quake as leveraged liquidity providers de-levered simultaneously. The premium we collect on calm-ish high-VIX days **is** the insurance premium for that cascade. We are structurally **short liquidity and short gamma.** And the gate makes this worse: we are most exposed precisely when a crowded contrarian book is most likely to unwind.
- **The premium is smallest exactly where we trade (Avramov-Chordia-Goyal 2006, *JF* 61(5):2365–2394).** Reversal is concentrated in *illiquid, high-turnover* single names, where even there gross profit ≈ transaction costs. Sector ETFs are the *opposite* population — the most liquid, most-arbitraged instruments on the tape. So the gross premium available to us is structurally damped; the VIX gate must select the ~half of days when liquidity-provision compensation actually exceeds cost, or there is nothing to harvest.

**Who loses money, in one sentence:** forced/uninformed sector sellers (and short-coverers) pay us to provide immediacy in high-vol states; we collect a thin, structurally-decayed premium most of the time and **wire a large check back to the market in the next deleveraging cascade.** The edge is real *as compensation for a known risk* — it is not a free lunch, and the risk lens treats the average Sharpe as the *least* informative statistic about this stream.

---

## 2. Signal construction

**Tradeable signal (per tradeable date *t*, daily evaluation):**

1. **5-day reversal score.** For each eligible sector *i*, compute the trailing 5-trading-day total return `r_i = P_i(t) / P_i(t−5) − 1` using split/dividend-adjusted closes. Cross-sectionally z-score across the eligible universe: `z_i = (r_i − mean_j r_j) / std_j r_j`.
2. **Reversal tilt = negative of the score.** Target a dollar-neutral tilt proportional to `−z_i`: long the worst 5-day performers (most negative `r_i` → most positive weight), short the best. Demean so `sum_i w_i = 0`; this is enforced *within the eligible cross-section only* (dynamic universe, §3).
3. **VIX regime gate.** Compute the trailing-60-trading-day median of the VIX **close** through date *t*: `m_t = median(VIX_{t−59..t})`. The gate is **active** iff `VIX_t > m_t`, else **flat** (all weights 0). Gate uses only data ≤ *t* (trailing, never centered) — confirmed look-ahead-clean.
4. **Sizing / scaling.** Scale the dollar-neutral tilt so gross exposure (`sum_i |w_i|`) equals a fixed `gross_target` on active days; per-name cap `|w_i| ≤ max_weight`. No leverage beyond `gross_target`. (Sizing rationale and the deliberate choice *not* to vol-target are in §6 — vol-targeting a short-vol book is a known trap, L3.)
5. **No-trade band (turnover control, L7).** Only rebalance a name when its target weight has moved by more than `band` from the currently-held weight; otherwise hold. This is *not* a free parameter to tune for Sharpe — it exists solely to defuse the L7 turnover hazard and is perturbed by the battery (§7).

**Weights-contract compliance:** the entrypoint will return *unshifted* target weights — weights at *t* use only data ≤ *t* (the 5-day window ends at *t*, the VIX gate uses VIX ≤ *t*). The review engine applies the execution-convention shift (trade next open / next close per the manifest). The function must **NOT** pre-shift. Look-ahead unit test to mirror: `test_no_lookahead_truncation_invariance` (truncating the price/VIX history at any date must not change weights on or before that date).

**Why this construction and not the alternatives:**
- **Z-score tilt, not top-k/bottom-k buckets.** With only 9–11 names, hard buckets (e.g., long bottom-3 / short top-3) throw away cross-sectional information and make the strategy brittle to one name flipping rank. A continuous `−z` tilt around dollar-neutral degrades gracefully and matches the reference runner's design philosophy (z-score tilt + cap + renormalize).
- **Dollar-neutral, not long-only.** The mechanism is cross-sectional liquidity provision; net market exposure is noise here and would smuggle in equity beta (a standing red flag: "long-only Sharpe >> EW → hidden beta"). Dollar-neutral also makes the |ρ| story vs `sector_rotation` cleaner (that stream is long-only).

---

## 3. Universe

**11 SPDR sector ETFs:** XLK, XLF, XLE, XLV, XLC, XLY, XLP, XLI, XLB, XLRE, XLU.

**Dynamic universe (MANDATORY — never backfill):**

| Window | Eligible sectors | N |
|---|---|---|
| start → 2015-10-07 | XLK XLF XLE XLV XLY XLP XLI XLB XLU | 9 |
| 2015-10-08 → 2018-06-18 | + XLRE | 10 |
| 2018-06-19 → end | + XLC | 11 |

A sector is eligible on date *t* only once it has ≥ 5 trading days of post-inception history (so the 5-day return is real, not partly synthetic). XLC and XLRE are **never** backfilled with synthetic or pre-inception data — doing so is look-ahead on the universe definition (S0 risk #3). The dollar-neutral and z-score operations run over the *eligible* cross-section on each date, so weights always sum to zero within the names actually tradeable that day.

**Data convention (resolve before backtest, S0/S1 tasks):**
- **VIX:** refresh `^VIX` (Cboe via yfinance, same-day close) **or** switch to FRED `VIXCLS`. Pre-commit: **use the VIX close at *t* for the gate at *t*** (same-day-close convention), consistent with the daily-close trade-next-open execution shift the engine applies. If `VIXCLS` is used, confirm its 1-day publication lag does not inject a second shift; the gate must reflect information available at the *t* close. The 60-day rolling median needs ≥ 60 consecutive VIX closes before the first tradeable signal (warmup).
- **Total-return / split adjustment** must be consistent across all 11 ETFs; QC preflight (`quant_data/qc.py`) flags stale prices / extreme returns around ex-div dates and the 2015/2018 splice points (a 5-day reversal is acutely sensitive to an unadjusted dividend showing up as a spurious one-day "return").
- **Local history** starts 2012-01-03 for the 9 core sectors (NOT ~1999 the original brief assumed). MinBTL on the high-VIX sub-sample is the binding statistical risk (§5, §7); a long-history pull (yfinance/Stooq to ~1999) would *help* MinBTL and is worth attempting in implementation, but the spec is written to survive on the ~14-yr local window or die honestly.

---

## 4. Rebalance frequency & every parameter (with rationale)

Daily *evaluation* of the gate and signal; **trading is throttled by the no-trade band**, so realized rebalances are far fewer than daily. This is the explicit L7 defense (vix_regime: daily rebalancing → 2430%/yr turnover; even weekly → 916%/yr). The risk lens treats turnover as a primary kill input, not an afterthought.

| Parameter | Pre-committed value | Rationale | Battery perturbs? |
|---|---|---|---|
| `reversal_lookback` | **5 trading days** | Lehmann (1990) weekly horizon; Nagel's reversal horizon. Not tuned — taken from literature. | ±20/40% → {3,4,6,7} days |
| `vix_gate_lookback` | **60 trading days** | Carried from the hypothesis; ~3 months balances "current regime" vs noise. Free parameter → battery-perturbed. | ±20/40% → {36,48,72,84} days |
| `vix_gate_threshold` | **median (50th pct)** of the trailing window | Splits the sample ~50/50 (max effective sample subject to "high-vol"); raising it shrinks the sub-sample and worsens MinBTL. **Free parameter — the most dangerous one.** | ±20/40% on the *percentile* → {30th,40th,60th,70th} |
| `gross_target` | **1.0** (100% gross, ~50% long / 50% short) | No leverage; keeps capacity comfortable at 25k–100k and avoids amplifying the short-vol tail. Sizing is deliberately conservative for a short-liquidity book. | ±20/40% → {0.6,0.8,1.2,1.4} |
| `max_weight` (per name) | **0.20** (|w_i| ≤ 20% of gross) | Matches reference runner cap; with 9–11 names prevents one sector dominating; caps single-name gap risk on a high-VIX day. | ±20/40% → {0.12,0.16,0.24,0.28} |
| `no_trade_band` | **0.05** (5% of gross per name) | The L7 defense. Set by turnover-control reasoning, NOT Sharpe-tuned. Wider band = less turnover but more signal slippage; perturbation tests robustness. | ±20/40% → {0.03,0.04,0.06,0.07} |
| `min_eligible` | **5 sectors** | Below this the cross-section is too thin for a meaningful dollar-neutral tilt; flat otherwise. | not perturbed (structural) |
| `execution_convention` | **trade next open** (engine-applied) | Conservative vs trade-at-signal-close; avoids the look-ahead of trading at the same close that generated the signal. | n/a (engine) |

**Honest `n_trials` accounting (feeds DSR — declare a FLOOR, not a wish):** the design space already explored across S0–S2 spans at minimum: reversal horizon (the 5-day choice vs neighbors), VIX-gate lookback, VIX-gate threshold/percentile, gross/sizing, no-trade-band, and the **momentum-neutralization on/off** decision (§5). Counting honestly, this is a **family of ≥ 6–8 declared variations**; the manifest `n_trials` must reflect that floor and accumulate across versions. The risk lens flags that under-declaring `n_trials` to flatter DSR is the exact failure mode the platform exists to prevent — and DSR is the gate this strategy is most likely to fail.

**The sector-momentum headwind decision (S1 pre-commitment #2, Da et al. 2014 / Blitz et al. 2024).** Raw 5-day reversal mixes in an *across-industry momentum* term that works *against* reversal at the sector level — and that term is mechanically the **same factor** as the `sector_rotation_v1` peer. **Pre-committed decision for v1: do NOT add a separate momentum-neutralization overlay.** Rationale: (a) it adds a free parameter and a trial; (b) keeping the raw reversal makes the unconditional-reversal baseline an honest like-for-like null; (c) the headwind is a *declared known drag* whose size we will read directly from the unconditional-reversal baseline's performance. If, and only if, the unconditional baseline shows the across-industry-momentum drag is the dominant loss source, a v2 may add neutralization (new trial, re-deflate). This keeps v1 clean and falsifiable rather than pre-optimized.

---

## 5. Failure modes FIRST (the lens) — quantified crash exposure & the binding statistical risk

### 5.1 Short-vol / forced-deleveraging tail — the primary risk

We are providing liquidity *only* in high-VIX windows. Structurally this is short-vol and short-liquidity: a stream of small gains punctuated by rare, large, **autocorrelated** losses when a crowded contrarian book is force-unwound. The canonical event is **Aug 6–9, 2007** (Khandani-Lo 2011): the buy-losers/short-winners book lost a multi-sigma amount over three days as leveraged providers de-levered together — a loss that the *prior* Sharpe gave no warning of. **Mar-2020** is the modern analog: VIX > median for an extended stretch (gate maximally active), sector dispersion enormous, and — per IOSCO PD682 (2020) — ETF creation/redemption arbitrage strained (bond ETFs dislocated 3–8% from NAV; equity sector ETFs far less but the channel is the concern). A reversal book that bought the worst-performing sector into a falling, illiquid tape in March 2020 would have taken repeated gap losses precisely when it was fully sized.

**Expected (reasoned, NOT backtested) crash profile** — the numbers below are *priors to be tested by the battery*, stated so the kill thresholds in §6 are calibrated honestly:
- **Daily/weekly return distribution: left-skewed, fat-tailed.** I expect negative skew (worst single weeks several times the magnitude of best weeks) and a conditional MaxDD in high-VIX clusters that is a large multiple of the average drawdown. A Sharpe that looks fine on averages can hide a worst-week of −10% to −20% at `gross_target = 1.0` in a 2007/2020-type cluster. **The Sharpe is the wrong sufficient statistic for this stream; the worst-week and conditional MaxDD are.**
- **Autocorrelated losses.** Unlike a well-diversified factor, deleveraging losses cluster across consecutive days (Khandani-Lo's defining feature). This breaks the i.i.d. assumption behind naive Sharpe annualization and makes block-bootstrap CI (battery) more honest than parametric intervals — and likely *wider*.

### 5.2 The binding statistical risk: MinBTL on the high-VIX sub-sample

The trade is **flat ~half the days** (VIX ≤ median by construction). So the *effective* sample backing the Sharpe is roughly **half the calendar** — on the ~14-yr local window that is ~7 yr of *active* trading, and the high-VIX days are themselves *clustered* (not 7 independent years). The nearest neighbor `vix_regime` **died on MinBTL = 3,968 yr vs ~12.6 yr available (315× over budget; bootstrap CI [−0.167, 0.824] spans zero)** [HISTORICAL, other strategy]. Even the *long-only monthly* `sector_rotation_v1` already **fails MinBTL (needs 4095d vs 3485 available)** at Sharpe 0.84 [HISTORICAL, other strategy]. A 5-day reversal that is flat half the days has an **even shorter effective sample** → **MinBTL on the conditional sub-sample is the single most likely kill, and it must be computed early in S2/implementation, not at the end.**

### 5.3 Translation risk — the edge may simply not exist at the ETF layer

Nagel's strong results are *single-stock*; he explicitly notes *industry* reversal "does not yield high returns unconditionally." Avramov-Chordia-Goyal locate the premium in *illiquid* names where it ≈ costs. Across 11 tight-spread, AP-arbitraged ETFs the harvestable dispersion may be **too thin to clear costs even in high-VIX**. The briefing's modal outcome is **net Sharpe ≤ 0 at 2× costs** — the P0 falsification condition. This is not a tail scenario in my prior; it is roughly a coin-flip. The spec is designed to let that result kill the strategy cleanly at the 2× cost gate rather than be rescued by parameter search.

### 5.4 "Is it just dressed-up vol timing?" — the spanning requirement

The `vix_regime` PM challenge ("is this just vol timing?") recurs here by construction (same universe, VIX overlap). We must show **independent spanning alpha (t ≥ 1.96)** vs (a) unconditional reversal, (b) monthly momentum / `sector_rotation`, and (c) a plain trailing-vol filter. `vix_regime` failed this at **t = −0.18** [HISTORICAL]. If the VIX gate adds no measured value over always-on reversal, predicate #2 of the hypothesis falsifies the thesis outright.

---

## 6. Expected NET Sharpe & sizing philosophy (risk lens)

**PM prior for the family:** long-only tilt 1–2% alpha; L/S 2–4% gross alpha. After the briefing's ~50% post-publication haircut on the *conditioned* component and treating the *unconditional* component as ~zero, and after **stressed (vol-conditional) costs** on a high-turnover book that trades when spreads are widest:

| Quantity | Expectation (REASONED, not backtested) | Basis |
|---|---|---|
| Gross L/S alpha (conditioned component) | ~2–4%/yr **before** stressed costs | PM prior, halved from published mechanism (McLean-Pontiff ~58% decay) |
| Stressed cost drag (active high-VIX days) | **Large and uncertain** — the swing factor | Vol-conditional spread+impact; cost-of-immediacy ~1.9%/yr unconditional baseline (cited, not re-verified) |
| **Net L/S Sharpe (my point estimate)** | **~0.2–0.5**, i.e. **at or below the LOW end of the 0.4–0.8 band** | After stressed costs + decay on a half-length effective sample |
| P(net Sharpe ≤ 0 at 2× cost) | **~35–45%** (modal-adjacent, not tail) | Briefing: net ≤ 0 at 2× is the MODAL outcome at ETF level |
| Left tail (worst week, gross_target=1.0) | **−10% to −20%** in a 2007/2020-type cluster | Khandani-Lo cascade analog; to be measured, sized for survivability |

**Sizing philosophy (deliberate, risk-lens):**
- **`gross_target` fixed at 1.0, no leverage.** Leverage on a short-liquidity book amplifies the exact tail that kills it. We accept a modest Sharpe for survivability.
- **Do NOT vol-target.** L3 (vol targeting does NOT fix crash risk for long-only equity) and the `vol_scaled_momentum` kill (vol targeting did not fix crash risk; fair-weather fund) both warn against bolting a vol overlay onto an equity book to "tame" the tail. Worse, our tail is a *liquidity* cascade, not a slow vol grind — vol-targeting reacts too late and would *de*-lever after the gap, locking in the loss. The honest mitigation is a *fixed, conservative* gross and a hard kill threshold, not a dynamic overlay (which would also add a trial and likely fail the L5 "+0.15 Sharpe" bar).
- **Capacity (Gate 10) passes comfortably** at 25k–100k in the most-liquid ETFs on the tape; capacity is *not* the binding constraint (the briefing is explicit). Decay, MinBTL, and the tail are.

---

## 7. Baselines this MUST beat (pre-committed) & the gates

### 7.1 The three baselines (L1 / L6 / the gate's own null)

1. **Equal-weight sector buy-and-rebalance (L1).** Same 11-ETF universe, same costs, monthly rebalance. The dumbest credible alternative. **Beat it or do not ship.** (Note: this is long-only and ours is dollar-neutral, so the comparison is on risk-adjusted standalone return *and* on diversification benefit, not raw return.)
2. **Plain 21-day trailing-vol filter (L6) — the baseline that KILLED `vix_regime`.** A naive "scale exposure / gate by 21-day realized vol" filter dominated the VRP overlay on Sharpe, MaxDD, and turnover simultaneously [HISTORICAL]. We pre-commit to run the *same* reversal signal gated by a 21-day trailing-vol threshold (instead of the VIX-median gate). **If the cheap trailing-vol gate matches or beats the VIX-median gate, the VIX gate adds nothing distinctive — kill the VIX-specific claim** (it's just vol timing, the exact `vix_regime` failure).
3. **UNCONDITIONAL 5-day reversal (no VIX gate) — the gate's own null (L4, predicate #2).** Same signal, always-on. The briefing's load-bearing claim is that the unconditional version is decayed to ~zero. **The conditioned version must beat the unconditional version on NET Sharpe by a meaningful margin** (the L5 overlay bar is +0.15 Sharpe; I adopt that as the minimum "the gate earns its keep" threshold). If conditioned ≤ unconditional, the "vol-conditioned" thesis is falsified — it's just reversal, and reversal is dead.

### 7.2 Pre-committed kill thresholds (these are hard; the urge to relax them after seeing a blocked result IS the failure mode)

**Auto gates (battery, 1–8 of the kill checklist):**
| # | Threshold | Kill if |
|---|---|---|
| K1 | IS Sharpe < 0.5 | violated |
| K2 | OOS walk-forward Sharpe < 0.3 | violated |
| K3 | Max DD worse than −30% | violated |
| K4 | PSR < 0.90 | violated |
| K5 | DSR < 0.95 (deflated by honest `n_trials` ≥ 6–8) | violated — **most likely failure** |
| K6 | IS/OOS Sharpe ratio < 0.5 | violated |
| K7 | **MinBTL on the high-VIX SUB-sample > available active history** | violated — **co-most-likely failure** |
| K8 | **Net Sharpe < 0 at 3× stressed cost** (and the falsification condition: ≤ 0 at **2×** cost) | violated |

**Lens-specific tail & baseline gates (pre-committed, PM/owner-adjudicated 9–11 + risk additions):**
| # | Threshold | Kill if |
|---|---|---|
| K9 | Spanning-alpha t-stat < 1.96 vs (unconditional reversal **AND** `sector_rotation` **AND** 21-day trailing-vol filter) | any < 1.96 |
| K10 | **|ρ| > 0.4 vs `sector_rotation_v1`** (predicted [−0.3,+0.2], UNMEASURED) | violated |
| K11 | No credible economic mechanism survives review | PM judgment |
| **KT1** | **Conditioned NET Sharpe ≤ Unconditional NET Sharpe + 0.15** (the VIX gate fails to earn its keep, L4/L5) | violated → kill the *thesis* |
| **KT2** | **Trailing-vol-gated reversal ≥ VIX-median-gated reversal** on Sharpe (it's just vol timing — the `vix_regime` failure) | violated → kill the VIX-specific claim |
| **KT3** | **Worst high-VIX week worse than −15%** at `gross_target=1.0`, OR **conditional MaxDD in high-VIX clusters worse than −25%** | violated → un-survivable tail |
| **KT4** | **Return skew (active days) < −1.5** OR losses materially autocorrelated (cascade signature) without a Sharpe high enough to compensate (Sharpe < 0.6 with skew < −1.0) | violated → short-vol carry masquerading as alpha |
| **KT5** | **Does NOT beat equal-weight** on risk-adjusted standalone return AND adds no diversification (|ρ| with EW not < 0.4 OR blended Sharpe with EW not improved) | violated (L1) |

### 7.3 Must-measure (engine, not proposal text)
- **Vol-tercile conditional Sharpe** (regime honesty): expectation is that *essentially all* return is in the top vol tercile (the gate guarantees it). The risk lens reframes this as a *concentration* warning, not a feature: a stream whose entire P&L lives in the top vol tercile is maximally exposed to that tercile's tail. Report the top-tercile **worst-week and MaxDD**, not just its Sharpe.
- **Cost sensitivity 1×/2×/3× with vol-conditional spreads** — the curve's slope is diagnostic: if NET *improves* with higher cost multipliers, it's a bug (standing red flag).
- **Block-bootstrap CI on Sharpe** — expect it to span zero on the conditional sub-sample (vix_regime's did). If it does, MinBTL/DSR will agree.
- **Left-tail diagnostics conditional on VIX > median** — skew, worst-week, conditional MaxDD, and an explicit look at the Aug-2007 (if long history pulled) and Mar-2020 windows.

---

## 8. How this draft discharges the four S1 pre-commitments + the REVISE concerns

| S1 burden | Discharged by |
|---|---|
| **(1) Beat the gate's own null — two head-to-head baselines + EW** | §7.1: unconditional reversal (KT1), 21-day trailing-vol gate (KT2), equal-weight (KT5). All pre-registered with thresholds. |
| **(2) Sector-momentum headwind (Da et al., Blitz et al.)** | §4: pre-committed **NOT** to neutralize in v1 (keeps the unconditional baseline an honest null and avoids an extra trial); the drag is read directly off the unconditional baseline; v2-only neutralization with re-deflation. |
| **(3) Vol-conditional cost model + no-trade-band** | §4 `no_trade_band=0.05` (L7 defense, not Sharpe-tuned), §6/§7.3 stressed 1×/2×/3× costs, turnover reported. K8 uses **2× falsification / 3× kill**. |
| **(4) MinBTL on the high-VIX sub-sample, computed early** | §5.2 + K7: declared the co-most-likely kill; computed on the *conditional* (active-day) sample, not the calendar. |

**Other REVISE concerns:** ETF translation risk → §5.3 + K8 (let it die at the cost gate). Unconditional-reversal decay-to-zero → §0, §1, KT1 (the gate is the whole strategy; prove it). Three `vix_regime` kills → mirrored as K7 (MinBTL), K9 (spanning t≥1.96), KT2 (beat trailing-vol). |ρ| vs `sector_rotation` → K10, plus dollar-neutral construction to keep the streams structurally distinct. Look-ahead hygiene → §2/§3 (trailing-only VIX median, same-day-close convention, dynamic universe never backfilled, weights-contract unshifted, `test_no_lookahead_truncation_invariance`).

---

## 9. References (verified in S0/S1 — real titles/venues; not re-fabricated here)

- **Nagel, S. (2012).** "Evaporating Liquidity." *Review of Financial Studies* 25(7):2005–2039. (Core mechanism; reversal = liquidity provision; conditional Sharpe rises with VIX; industry reversal pays *conditional on high VIX*.)
- **Khandani, A. & Lo, A. (2011).** "What happened to the quants in August 2007? Evidence from factors and transactions data." *Journal of Financial Markets* 14(1):1–46 (NBER w14465). (The short-vol / forced-deleveraging tail = our exact construction.)
- **Avramov, Chordia & Goyal (2006).** "Liquidity and Autocorrelations in Individual Stock Returns." *Journal of Finance* 61(5):2365–2394. (Premium concentrated in illiquid names; net ≈ costs even there → ETF layer is structurally thin.)
- **Hameed, Kang & Viswanathan (2010).** "Stock Market Declines and Liquidity." *Journal of Finance* 65(1):257–293. (Supply-side mechanism + inter-industry liquidity spillovers → sector-level relevance.)
- **Da, Liu & Schaumburg (2014).** "A Closer Look at the Short-Term Return Reversal." *Management Science* 60(3):658–674. (Across-industry-momentum term works *against* raw sector reversal.)
- **Blitz, van der Grient & Honarvar (2024).** "Reversing the Trend of Short-Term Reversal." *Journal of Portfolio Management* 50(6) (SSRN 4575689). (Classic STR "vanished" in most regions; bets against short-term industry momentum.)
- **Chordia, Subrahmanyam & Tong (2014).** *Journal of Accounting & Economics* 58(1):41–58. (Anomaly returns ~halved post-decimalization.)
- **Lehmann (1990).** "Fads, Martingales, and Market Efficiency." *Quarterly Journal of Economics* 105(1):1–28. (Validates the ~5-day/weekly horizon.)
- **McLean & Pontiff (2016).** *Journal of Finance* 71(1):5–32. (~58% post-publication decay base rate.)
- **IOSCO (2020), PD682** + Mar-2020 ETF-arbitrage/AP-constraint literature. (Tight ETF spreads NOT guaranteed in the high-VIX regimes we trade → vol-conditional costs.)

> **Flags carried from S1 (do not over-rely):** Della Corte et al. (≈2023 WP) is unpublished and its strongest leg is overnight/intraday (uncapturable on daily closes). The de Groot "30–50 bps/week net large-cap" figure and the HFT ">70% of volume" figure are headlines, not independently re-verified here. The Dai-Medhat-Novy-Marx-Rizova counter-counter (vol-conditioned reversal robust) is the strongest pro-idea evidence but was single-sourced and uncross-verified — do not lean on it without S2 verification.

---

## 10. Bottom line (risk lens)

A genuinely diversifying *candidate* with a real, well-cited economic mechanism — but it is a **short-liquidity carry trade gated into its own worst regime**, on a heavily-decayed unconditional base, at the lowest-premium layer of the asset class. My disciplined expectation: **net Sharpe ~0.2–0.5 (low end of band or below), a left tail far heavier than that Sharpe implies, and a ~40% chance of dying cleanly at MinBTL (K7), the 2× cost gate (K8), or the unconditional-reversal null (KT1).** I have written the spec so those deaths happen *early and honestly* rather than being parameter-searched away. **Proceed to S3 with all of §7's thresholds pre-committed.** If the strategy clears them, it is a real diversifier; if it doesn't, the battery has done its job.
