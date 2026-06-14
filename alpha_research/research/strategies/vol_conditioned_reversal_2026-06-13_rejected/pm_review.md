<!-- 2026-06-14: S3 adversarial PM review (PM challenger role) for vol_conditioned_reversal.
SPEC ONLY — no code, no manifest, no runner, no backtest. All Sharpe/return/turnover figures cited
are either reasoned EXPECTATIONS (labelled) or HISTORICAL results for OTHER in-repo strategies
(labelled). No backtest of vol_conditioned_reversal exists. Earlier rounds (none yet) preserved. -->

# PM Review — Vol-Conditioned Sector Reversal (`vol_conditioned_reversal`)

> **Reviewer role:** PM challenger (adversarial) · **Decision owner:** Zelin
> **Artifact under review:** `proposal.md` (S2 canonical, 2026-06-14, Elena)
> **Upstream in hand:** `hypothesis.md` (S0 PASS), `cerebro_briefing.md` (S1 REVISE → 4 pre-commitments)
> **[CEREBRO CONTRADICTION] held:** yes (P1 in hand: 5 supporting / 8 contradicting, rec REVISE).
> A review without it would be invalid; it is the spine of this one.

---

## ROUND 1

### Verdict: CONDITIONAL — proceed to S4/S5 against the numbered checklist below. `revision_needed = false`.

**Why CONDITIONAL and not REJECT.** This is the most honestly-scoped proposal in the folder. It does
not oversell: §0 leads with "cost-bound, not alpha-bound," prices its own modal kills (MinBTL on the
sub-sample, 2× cost gate), pre-commits 13 kill thresholds it pledges not to relax, and wires L1–L7 +
both prior kills into the table. The mechanism is real and cited (Nagel 2012 is a near-exact statement),
the construction is dollar-neutral (no hidden-beta escape hatch), and the diversifier case (§10) is the
genuine reason to spend a slot. None of the 11 kill gates is structurally pre-failed at the *spec* level
— so REJECT is not warranted.

**Why CONDITIONAL and not APPROVED.** The proposal has front-run nearly every obvious challenge, which
is exactly why I have to push on the places where the pre-commitments are *insufficient, internally
inconsistent, or under-specified* rather than absent. There are four spec-level gaps where a word in the
manifest/runner spec changes what the backtest measures (C1, C2, C5, C8 below); leaving them implicit
risks an un-decidable or quietly-rescued result. Everything else is empirical and **can only be resolved
by the S5 battery, not by editing the spec** — so I do not loop. Per the loop rule, `revision_needed`
is **false**: the spec-level gaps are enumerated as binding S4/S5 entry conditions (the researcher
records the decisions; they are not open design questions), and the dominant requirements (R1–R13) are
empirical battery outputs. Looping Round 2 on numbers the spec cannot produce would be theatre.

---

### A. MECHANISM — is the premium real in LIQUID sector ETFs, or is this dressed-up vol-timing?

The proposal's §1 already concedes the two hardest points (Avramov-Chordia-Goyal thin-gross-premium;
Khandani-Lo the-premium-is-the-tail). I do not let the *concession* stand in for the *test*. Three
mechanism attacks, in descending lethality:

- **A1 — Translation risk is the modal kill and the proposal agrees, which means it must be a GATE not
  a footnote.** Every strong supporting result is single-stock (Nagel, Lehmann, Da-Liu-Schaumburg) or
  index-futures-via-overnight (Della Corte, which §14 correctly disowns because daily-close data cannot
  capture the overnight leg). Nagel's own finding is that *industry* reversal "does not yield high
  returns unconditionally." So the located literature supports **mechanism + horizon + gate rationale**
  and explicitly **not** an ETF close-to-close Sharpe. The honest prior on net edge at the ETF layer is
  a coin flip (§5.3, §0: P(net ≤ 0 at 2× cost) ~35–45%). I accept the framing; my requirement (R1) is
  that K1 fires *mechanically* and is computed BEFORE any parameter optimization, alongside K9 — not
  after a sweep has had a chance to dress up the number.

- **A2 — Da-Liu-Schaumburg cuts deeper than the proposal admits, and the v1 baseline runner is on the
  WRONG side of it.** S5 of P1 is decisive: of reversal's components, **only the non-fundamental
  RESIDUAL reverses robustly**, earning ~3× the risk-adjusted return of raw reversal; the
  *across-industry-momentum* term works AGAINST raw sector reversal. The proposal trades **raw 5-day
  reversal with `mom_neutralize = off` in the v1 baseline** (§2). That is, by Da-Liu-Schaumburg's own
  decomposition, the v1 baseline is the version most contaminated by the headwind term and furthest from
  the component that actually pays. The §2 rationale for OFF (L2: noisy to project a momentum factor out
  of 9–11 names; keeps the |ρ| story like-for-like) is *reasonable* but it is a **bet that the
  contamination is smaller than the estimation noise of removing it** — and that bet is untested. This
  is not a reason to reject; it is a reason the `mom_neutralize = on` arm cannot be a buried "declared
  variant." **R7:** the ON arm must be run *in the first battery pass*, not deferred, because if ON
  materially beats OFF, the headline strategy is the wrong one and the whole §10 |ρ|-vs-sector_rotation
  argument inverts (a momentum-neutralized reversal is MORE orthogonal to a momentum stream, not less).

- **A3 — "Is this just dressed-up vol-timing?" — the proposal's own §7 answer is correct but the bar
  is set one notch too soft.** The escape from the `vix_regime` trap is K2 (gate must add ≥ +0.15 net
  Sharpe over unconditional reversal — L5) and K4 (must beat a 21-day trailing-vol filter — L6, the
  exact signal that dominated `vix_regime` on Sharpe 0.341 vs 0.299, MaxDD, AND turnover
  simultaneously). Good. But note the asymmetry the proposal half-buries in §7 baseline 2: the
  unconditional arm is *expected ≈ zero net*. If unconditional ≈ 0 and gated ≈ +0.4 net, then K2's
  "+0.15 over unconditional" is **trivially satisfied by construction** — the gate looks like it adds
  value simply because the unconditional base is dead, not because the *conditioning* is informative.
  The honest test of "vol-conditioning adds value" is **K4 (vs trailing-vol filter), not K2 (vs
  unconditional)** — K4 asks whether *VIX specifically* (vs any cheap realized-vol proxy) is the source.
  **R4 elevates K4 above K2 in the kill hierarchy**: if the trailing-vol filter matches the VIX gate,
  the "VIX-conditioned" branding dies even if K2 passes. The proposal lists K4 as "PM/owner judgment"
  (§9) — I am exercising that judgment now: **K4 is a hard kill of the VIX-specific claim, not a soft
  one.** (You may keep the strategy as "realized-vol-conditioned reversal" if the trailing-vol gate wins
  and clears all other gates, but that is a *different, re-titled* strategy with its own n_trials, not
  this one.)

### B. COSTS at our capital — does net Sharpe survive 2×/3× with the $1 IBKR floor and stressed spreads?

This is where the proposal is strongest *and* where the one quantitative inconsistency lives.

- **B1 — The cost arithmetic in §6 is internally inconsistent with §6's own per-name table, and the
  inconsistency flatters the result.** §6 states "round-trip per name ~12–28 bps stressed" and then
  computes `cost drag ≈ 5.0 × ~0.20% ≈ ~1.0%/yr`. But 5.0 (= 500%/yr two-sided turnover) × 20 bps
  = 100 bps = **1.0%/yr only if "20 bps" is the *per-unit-turnover* round-trip**, whereas the table
  presents 12–28 bps as *per-name in+out*. Worse, §6 separately establishes that the **$1 order floor
  ≈ 9 bps/order at 25k and a full 22-leg rebalance ≈ 9 bps of the book per round trip** — a *fixed*
  cost that does NOT scale with turnover and is **larger than the calm half-spread**. The §6 drag
  figure (~1.0–2.5%/yr) appears to omit or under-weight the commission-floor term at 25k. Re-grossed:
  if a typical weekly active rebalance touches ~4–8 legs (the band's claim) at ~$1 each, that is ~$4–8
  per *active* week; gated active ~half the weeks ≈ ~26 active weeks/yr × ~$6 ≈ ~$156/yr ≈ **~62 bps/yr
  of a 25k book from commissions ALONE**, before a single bp of spread. Add ~500%/yr turnover × the
  stressed half-spread (~3–8 bps one-way → ~6–16 bps round-trip per unit) and the drag at 25k is
  plausibly **~1.5–3.5%/yr, not ~1.0–2.5%**. Against a gross edge of ~2–4%/yr, that pushes the central
  net estimate toward the **lower half of the stated band and materially raises P(net ≤ 0)**. This is a
  spec-level fix: **R2 — the cost model spec must charge `max(per-share, $1/order)` PER LEG PER REBALANCE
  explicitly, and §0/§6's net-edge arithmetic must be re-derived with the floor included at 25k before
  the manifest is written.** This does not change the verdict (it is what the 1×/2×/3× sweep exists to
  surface) but the proposal's *expectation* is currently a touch optimistic and should be corrected so
  the pre-committed kill is honest.

- **B2 — The 500%/yr turnover budget is a TARGET, not a derived quantity, and the band may not hold it.**
  §4 calibrates against `vix_regime` weekly = 916%/yr (HISTORICAL) and asserts weekly + 0.05 band +
  ~50% duty cycle lands "materially below." That is a hope, not a bound. A 5-day reversal signal mean-
  reverts *within* the weekly hold, so at each weekly rebalance the target book can swing substantially
  vs the prior week even with a 0.05 band — the band suppresses *small* drifts but a 5-day signal
  routinely produces *large* week-over-week rank flips (a sector that was worst last week is frequently
  not worst this week). I do not accept "targets below 916%" on assertion. **K12 (turnover > ~800%/yr
  with no band that both controls turnover AND keeps net > 0) is the correct backstop and I keep it
  hard** — but I add **R3: report realized two-sided turnover as a first-class battery output at the
  baseline band AND at every band perturbation (0.03–0.07), and show the turnover×net-Sharpe frontier.**
  If the only band that hits ≤500% kills net Sharpe, the design has failed L7 in a new costume.

- **B3 — Capacity (Gate 10) genuinely passes; do not let it become a distraction.** I agree with §6 /
  P1 §6 that capacity is adequate at 25k–100k and the binding constraints are decay/MinBTL/tail/cost-
  vs-premium, NOT capacity. The 100k column exists to show the floor stops binding. Fine. **The
  decision-grade number is the 25k stressed column** — that is where this lives or dies, and the
  proposal correctly centres there.

### C. PIT / DATA LAGS — look-ahead surface on the VIX gate, the universe, and the splice points

- **C1 — VIXCLS 1-day lag is CORRECT and verified, but the proposal's framing of it is subtly wrong and
  must be pinned in the manifest.** I verified `alpha_research/quant_data/pit.py:71` registers
  `"VIXCLS": 1` calendar-day publication lag, and `get_data(pit=True)` shifts the macro observation to
  its availability date by default. The proposal (§2 step 4, §11.1) says the gate at rebalance date *t*
  uses `VIXCLS` for *t*. **With the PIT shift, the VIXCLS *reference* value for date *t* is not
  available until *t+1*** — so a gate that reads "VIXCLS labelled *t*" at decision-time *t* is reading a
  value the platform will not mark available until *t+1*, i.e. a 1-day look-ahead UNLESS the engine's
  PIT layer is doing the shift for you (it is, by default). The resolution is: **the gate must consume
  the PIT-shifted VIXCLS series, so at decision date *t* it uses the most recent VIXCLS *available* as
  of *t* (which is the reference value for *t−1*).** This is *more* conservative, not less, and is the
  safe choice — but it means the 60-day median and the `V(t) > M(t)` test run on the **availability-
  dated** series, not the reference-dated series. **R5 (spec-level): the manifest's `data_requirements`
  must declare VIXCLS with `pit=True` and the runner must read the gate off the PIT-shifted column; the
  `test_no_lookahead_truncation_invariance` unit test must assert that truncating the VIX panel at *T*
  leaves all gates at ≤ *T* bit-identical AND that the gate at *t* never references a VIXCLS value whose
  availability date > *t*.** If instead the researcher pins same-day refreshed `^VIX` (the risk-lens
  alternative, §13), the gate is same-day-clean but introduces vendor drift and the stale-local-cache
  problem (`vix_daily` ends 2026-02-27) — VIXCLS+PIT is the better-pinned choice and §13 already chose
  it; this requirement just makes the *consumption convention* explicit so it cannot leak.

- **C2 — The 60-day median is backward-looking as written (good), but the WARMUP boundary is a
  look-ahead trap the spec must close.** §2 step 4 requires ≥ 60 consecutive VIX closes before the first
  tradable date. Confirm this is ≥ 60 closes *as of the trading date*, computed on the same PIT-shifted
  series — and that `backtest_start` (§11.4, ~2012-Q2) is the first date with a *real* 60-observation
  trailing window, not a date where the window is partially padded. A partially-warmed median quietly
  biases the gate's duty cycle near the start of the sample. **R6 (spec-level): pin `backtest_start` to
  the first date where the trailing-60 VIX window is fully populated on the PIT-shifted series, and state
  it numerically in the manifest.**

- **C3 — Dynamic 9→10→11 universe is correctly specified (§3) and matches the S0 risk; no backfill is
  the right call.** The eligibility pattern (≥ 5 post-inception days for `r5`, ≥ 60 VIX closes, explicit
  zero weight for ineligible names, `min_eligible = 5`) is clean and mirrors the reference runner. One
  residual: the **2015-10-08 (XLRE) and 2018-06-19 (XLC) splice dates change the cross-section size
  mid-sample**, which changes the z-score denominator and the dollar-neutral renormalization. A 5-day
  reversal is acutely sensitive to a one-day discontinuity (§11.3 flags ex-div). **R8 (spec-level):
  QC preflight must explicitly inspect the ±5 trading days around 2015-10-08 and 2018-06-19 for spurious
  z-score/return spikes from the universe-size change, and the test must confirm no synthetic XLRE/XLC
  history leaks before inception.** This is a one-line addition to the QC spec, hence spec-level.

- **C4 — Total-return vs raw close is declared (§11.3) but not pinned to a column.** A 5-day reversal on
  *raw* (unadjusted) close will read a dividend ex-date as a spurious one-day "loss" and then "buy" that
  sector — a pure artifact. The proposal says "total-return / split-adjusted" but the manifest must name
  the exact field. **Folded into R8.**

### D. BASELINE BEATABILITY — EW (L1), unconditional reversal, AND trailing-vol (L6)

- **D1 — Three baselines pre-registered (§7); the EW comparison needs a sharper definition because the
  strategy is dollar-neutral and EW is long-only.** §7 baseline 1 already flags this: a dollar-neutral
  L/S book cannot be compared to long-only EW on *raw return* (different beta, different sign exposure).
  The proposal's resolution — compare on risk-adjusted standalone return AND diversification benefit
  (|ρ| with EW + blended-Sharpe improvement) — is correct but **K3 as written ("net Sharpe ≤ EW → kill")
  is a category error for a market-neutral stream**: EW carries the equity risk premium and will often
  out-Sharpe a thin market-neutral book in a bull sample without that meaning the L/S book is worthless
  as a *diversifier*. **R9 (spec-level clarification): restate K3 as "the L/S stream must either (a)
  out-Sharpe EW standalone, OR (b) improve the blended portfolio Sharpe when added to the active pool at
  its target weight (|ρ| and marginal-Sharpe contribution), measured by the engine."** L1 is honoured
  (you still benchmark vs EW from R1), but the *kill predicate* must be the portfolio-contribution test,
  not a naive standalone-Sharpe comparison that a market-neutral stream is structurally disadvantaged on.

- **D2 — If the VIX gate adds nothing over unconditional reversal, KILL the gate — and the proposal
  already commits this (K2), but see A3: the binding test is K4 (trailing-vol), not K2.** No new
  requirement; R4 covers it.

### E. L1–L7 + the short-vol / forced-deleveraging tail (this book IS the Aug-2007 quant quake)

- **E1 — The tail is the single most under-quantified risk and the spec's mitigations are passive.**
  §5.1 is admirably blunt: this is a short-liquidity / short-gamma carry trade GATED INTO ITS OWN WORST
  REGIME — the gate concentrates *all* exposure into exactly the Aug-2007 / Mar-2020 states where the
  contrarian book detonates. The proposed mitigations are (i) z-score gross-stabilization, (ii) per-name
  cap 0.20, (iii) no leverage, (iv) a hard tail kill K13. (i)–(iii) are *sizing* controls that do
  nothing about the *autocorrelated cascade* — they cap one name on one day, not a multi-day forced
  unwind across the whole book. K13 is a *post-hoc kill* (it kills the strategy after the backtest shows
  the tail), not a *mitigation*. I accept the §5 argument that vol-targeting is the WRONG fix (L3; the
  cascade is a liquidity gap, not a slow vol grind, so an overlay de-levers too late and locks the loss)
  — agreed, do NOT add a vol overlay. But that leaves the tail genuinely unhedged by design. **R10:
  the battery must report the explicit Mar-2020 window P&L (and Aug-2007 IF the long-history pull lands)
  as a standalone diagnostic — worst-week, worst-3-day, conditional-on-gate-active MaxDD, and return
  autocorrelation during gate-active clusters — and K13's "worst high-VIX week < −15% at gross 1.0"
  must be evaluated on the REALIZED worst cluster, not an average.** This is empirical (battery output),
  so it does not block the spec; it is a binding S5 reporting requirement.

- **E2 — The `vol_scaled_momentum` inversion is handled correctly.** That strategy was fair-weather
  (Sharpe +2.255 low-VIX / −1.305 high-VIX); this one claims profit IN high-VIX, which is the right way
  out of the L3 trap — but it *inverts the burden of proof onto high-VIX costs/turnover/tail*, which §6
  and §5 accept. No relief asked; the burden is correctly placed. The standing red flag applies with
  full force: **if net Sharpe IMPROVES with higher cost multipliers, or is insensitive to 3×, it is a
  bug** (§6 states this; R11 makes it a checked battery assertion).

### F. MinBTL on the HALF-LENGTH high-VIX sub-sample (vix_regime died at 315× over)

- **F1 — This is the modal kill and the proposal correctly leads with it, but the effective-sample
  accounting needs to be even more pessimistic than §5.2 states.** §5.2: flat ~half the days → ~7 yr
  active on ~14 yr local, and high-VIX days are *clustered* (not 7 independent years). Correct. I push
  harder: the trade is dollar-neutral AND gated, so the Sharpe is backed by (a) only the active days,
  (b) of which the *informative* variation is concentrated in a handful of high-VIX clusters (2015-08,
  2018-Q4, 2020-Q1, 2022, 2025-?), so the *number of independent regime episodes* is plausibly **single
  digits**, not "7 years." `vix_regime` — a strategy with MORE data (always-on) — died at MinBTL =
  3,968 yr (315× over). A reversal flat half the days, with clustered active episodes, is structurally
  *worse* on effective sample. **K9 (MinBTL > available history on the high-VIX sub-sample) is the most
  likely kill and the proposal agrees.** **R12: MinBTL on the high-VIX sub-sample must be computed FIRST,
  before any parameter sweep, and reported with the block-bootstrap CI (which §9 expects to span zero).
  If MinBTL > available high-VIX history, the strategy is dead regardless of the point Sharpe — and a
  ~1999 long-history pull is the ONLY lever that helps (it roughly doubles the calendar but does NOT
  change the half-duty-cycle, so it is necessary-not-sufficient).** Empirical; binding S5 entry order.

### G. n_trials = 24 — honest, too low, or too high?

- **G1 — n_trials = 24 is the right FLOOR and I will not let it be shrunk; if anything the SPACE is
  larger and 24 must be defended as a floor, not a ceiling.** §13 enumerates `reversal_lookback`(≈3) ×
  `vix_lookback`/threshold(≈3) × `band`(≈3) × `n_legs`(≈3) × `mom_neutralize`(2) × `rebal_freq`(3) ≈
  a few hundred nominal cells, honestly declared as **24 distinct variations committed to evaluation.**
  That is the correct posture (DSR deflated by 24; never retroactively shrink to pass — §13, K10). My
  challenge is the opposite of "is 24 honest?": **the floor accumulates across versions and this family
  has already consumed trials upstream** — `vix_regime` explored the VIX-gating axis on this same
  universe, and `sector_rotation_v1` explored the sector cross-section. To the extent S3/S5 reasoning
  reuses those results as priors (it does — the whole proposal is calibrated on them), the *honest*
  family trial count is arguably higher than 24. **R13: n_trials = 24 is accepted as the floor for THIS
  strategy's own design space; but if any parameter beyond the declared 24 is touched during S5 (e.g. a
  band value outside 0.03–0.07, a threshold percentile outside the declared grid), n_trials increments
  and DSR re-deflates — pre-commit that the 24 is a FLOOR that only goes up.** The proposal already says
  this (§13); R13 just makes it an auditable battery rule. **24 is not too high** — DSR failing *because*
  n_trials is honestly 24 is the system working, exactly as K10 states.

---

### Cross-cutting: the ONE thing that would change my verdict to APPROVED

If the proposal had (a) corrected the §6/§0 cost arithmetic to include the $1 floor at 25k explicitly
(R2/B1), (b) elevated K4-vs-trailing-vol above K2-vs-unconditional in the kill hierarchy (R4/A3), and
(c) pinned the VIXCLS PIT-consumption convention and warmup boundary in the manifest language (R5/R6),
I would APPROVE to S5 outright. These are the three *spec-editable* gaps. I am issuing CONDITIONAL
rather than looping a Round 2 because: the cost-arithmetic correction is a re-derivation the researcher
records (not a design question), the kill-hierarchy elevation is a one-line pre-commitment, and the PIT
convention is a manifest declaration — none requires a new round of adversarial debate, and **every
other requirement (R1, R3, R7, R8, R10, R11, R12) is an empirical battery output that no amount of spec
editing can produce.** Looping would violate the "do not loop on requirements only the backtest can
resolve" rule.

---

### Requirements for approval (these become the S4/S5 gates)

1. **R1 — Compute K1 (net L/S Sharpe < 0 at 2× stressed cost) and K9/R12 (MinBTL on high-VIX sub-sample)
   FIRST, before any parameter optimization.** These are the two modal kills; a number produced after a
   sweep is contaminated. (Empirical; battery ordering.)
2. **R2 [SPEC] — Re-derive the §6/§0 net-edge arithmetic with the $1 IBKR order floor charged as
   `max(per-share, $1)` PER LEG PER REBALANCE at 25k, and correct the cost-drag estimate (currently
   ~1.0–2.5%/yr; the floor alone is ~50–65 bps/yr).** The cost model in the manifest must charge the
   floor per-leg, not as a percentage approximation.
3. **R3 — Report realized two-sided turnover as a first-class output at the baseline band and at every
   band perturbation (0.03–0.07); show the turnover × net-Sharpe frontier.** K12 (>800%/yr with no
   net-positive band) stays a hard kill. (Empirical.)
4. **R4 [SPEC pre-commitment] — Elevate K4 (must beat the 21-day trailing-vol filter) ABOVE K2 (must
   beat unconditional reversal) in the kill hierarchy. K4 is a HARD kill of the VIX-specific claim, not
   PM-judgment.** If trailing-vol matches/beats the VIX gate, the "VIX-conditioned" thesis is falsified
   (a re-titled "realized-vol-conditioned" strategy would be a separate n_trials entry). This is the
   `vix_regime` kill and the single most important "is it dressed-up vol-timing" test.
5. **R5 [SPEC] — Pin the VIXCLS PIT-consumption convention in the manifest: `data_requirements` declares
   VIXCLS with `pit=True`; the gate reads the PIT-shifted (availability-dated) column so the gate at
   decision date *t* never references a VIXCLS value whose availability date > *t*.** The look-ahead
   unit test must assert truncation-invariance AND this no-future-VIX property.
6. **R6 [SPEC] — Pin `backtest_start` to the first date with a fully-populated trailing-60 VIX window on
   the PIT-shifted series; state it numerically.** No partially-padded warmup window.
7. **R7 — Run `mom_neutralize = on` in the FIRST battery pass alongside OFF, not as a deferred variant.**
   If ON materially beats OFF (Da-Liu-Schaumburg: only the residual reverses), the headline strategy and
   the §10 |ρ|-vs-sector_rotation argument both change. (Empirical; ordering.)
8. **R8 [SPEC] — QC preflight must (a) name the exact total-return/split-adjusted price field used,
   (b) inspect ±5 trading days around the 2015-10-08 (XLRE) and 2018-06-19 (XLC) splice points and all
   dividend ex-dates for spurious 5-day-reversal-triggering return spikes, and (c) confirm no synthetic
   pre-inception XLRE/XLC history leaks into the cross-section.**
9. **R9 [SPEC clarification] — Restate K3 (the EW/L1 gate) as a portfolio-contribution test for a
   market-neutral stream:** the L/S book must EITHER out-Sharpe EW standalone OR improve the blended
   pool Sharpe at its target weight (via |ρ| + marginal-Sharpe). A naive "Sharpe ≤ EW → kill" unfairly
   penalises a market-neutral diversifier; L1 is honoured by still benchmarking vs EW from R1.
10. **R10 — Report standalone Mar-2020 (and Aug-2007 if long history pulled) window P&L: worst-week,
    worst-3-day, gate-active-conditional MaxDD, and return autocorrelation during gate-active clusters.
    Evaluate K13 on the realized worst cluster, not an average.** (Empirical; tail diagnostic.)
11. **R11 — Assert the standing red flags as battery checks: net Sharpe must DEGRADE monotonically from
    1× → 2× → 3× cost; if it improves with cost or is insensitive to 3×, FAIL as a bug.** (Empirical.)
12. **R12 — MinBTL on the high-VIX sub-sample with block-bootstrap CI, computed first (see R1). If MinBTL
    > available high-VIX history, the strategy is dead regardless of point Sharpe.** The ~1999 long-
    history pull is the only lever that helps (necessary, not sufficient — it does not change the
    half-duty-cycle). (Empirical; the modal kill.)
13. **R13 — n_trials = 24 is the accepted FLOOR for this strategy; it only increments (and DSR re-deflates)
    if any parameter outside the declared grid is touched in S5. Never shrink to pass DSR/PSR (K10).**

---

### What I am NOT requiring (to keep the loop honest)
- I am not asking for a vol-targeting overlay (L3 + §5 correctly reject it; it would fail L5's +0.15 bar
  and de-lever too late into the liquidity gap).
- I am not asking to switch the trading clock off weekly (the L7 defense is sound and verified:
  `rebalance_dates(index,"weekly")` snaps to the actual last trading day of each week —
  `alpha_research/review/engine.py:132-143` — not a calendar period-end, so the weekly clock is
  mechanically what §4 claims; daily/biweekly remain declared trials).
- I am not asking to drop `mom_neutralize=off` as the v1 baseline — only to run ON concurrently (R7).
- I am not re-litigating the mechanism's plausibility (§1 satisfies Gate 11; the mechanism is real and
  cited). The bet is on MAGNITUDE-at-the-ETF-layer-net-of-stressed-cost, which only S5 can adjudicate.

**Bottom line:** A genuinely diversifying, honestly-scoped, cost-bound candidate whose viability is an
empirical coin-flip the rigor battery exists to call. The spec is sound; three small spec edits (R2, R4,
R5/R6) and ten binding empirical gates (R1, R3, R7, R8, R9-as-clarified, R10, R11, R12) carry it into
S5. The modal outcome remains death at K1 (2× cost) or K9/K12 (MinBTL on the half-length sub-sample) —
and if it dies there, that is the correct, fast, honest kill this whole system is built to deliver.
**CONDITIONAL → proceed to S4/S5 against R1–R13. revision_needed = false.**
