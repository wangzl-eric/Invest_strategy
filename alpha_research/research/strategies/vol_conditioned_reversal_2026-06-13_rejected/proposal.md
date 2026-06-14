<!-- 2026-06-14: S2 canonical proposal (Elena, researcher of record) for vol_conditioned_reversal.
Synthesizes three independent S2 drafts (cost-realism, signal-regime, risk-baseline lenses).
SPEC ONLY — no code, no manifest.yaml, no runner, no trial-ledger row. There is NO backtest of this
strategy. Every Sharpe / return / turnover figure is a reasoned EXPECTATION (labelled), or a
HISTORICAL result for a DIFFERENT in-repo strategy (labelled). Nothing here is a measured result. -->

# Proposal — Vol-Conditioned Sector Reversal (`vol_conditioned_reversal`)

> **Strategy id:** `vol_conditioned_reversal` · **Track:** `etf_rotation`
> **Folder:** `vol_conditioned_reversal_2026-06-13_PENDING`
> **Stage:** S2 canonical proposal (the spec the PM will challenge) · **Date:** 2026-06-14
> **Researcher of record:** Elena · **Decision owner:** Zelin
> **Upstream:** `hypothesis.md` (S0, PASS→S1) · `cerebro_briefing.md` (S1, REVISE → 4 pre-commitments)
> **Synthesized from:** `proposal_draft_cost_realism.md`, `proposal_draft_signal_regime.md`,
>   `proposal_draft_risk_baseline.md` (three independent lenses).
> **Scope guard:** SPEC ONLY. No code, no `manifest.yaml`, no runner, no trial-ledger row.
> **Honesty flag:** No `vol_conditioned_reversal` backtest exists. **Every Sharpe / return / turnover
> figure below is a reasoned EXPECTATION or a HISTORICAL result for a DIFFERENT strategy (labelled).
> None is a realized result for this strategy.** Pre-commit everything BEFORE any backtest.

---

## 0. Decision-grade summary (read this first)

This is a **cost-bound, not alpha-bound** strategy whose entire harvestable edge lives in the spread
between a thin high-VIX liquidity-provision premium (Nagel 2012) and the cost of trading a
high-turnover 5-day reversal **precisely when spreads/impact are widest** — the same
constrained-intermediary state drives both. The three independent drafts converge on this and on the
construction (dollar-neutral L/S, weekly clock, no-trade band, VIX-median gate, vol-conditional
costs); they differed only on the trading clock, band width, VIX source, and n_trials, which §13
resolves into ONE pre-committed configuration.

| Quantity | Reasoned EXPECTATION | Basis |
|---|---|---|
| Gross L/S Sharpe, high-VIX days only, pre-cost | **~0.7–1.1** | Nagel: industry-reversal conditional Sharpe rises strongly with VIX; haircut 50–60% (McLean-Pontiff decay) + ETF-vs-stock translation (Avramov-Chordia-Goyal thin gross premium). |
| Gross annualized L/S edge (full period, flat ~half the days) | **~2–4%/yr** | PM L/S prior; gate active ~50% of days, so per-active-day edge ≈ 2× the full-period figure. |
| Annual cost drag at the turnover budget (≤ ~500%/yr two-sided) | **~1.0–2.5%/yr** | §6: turnover × **vol-conditional stressed** round-trip cost incl. the $1 IBKR order floor at 25k. |
| **Net annualized L/S edge** | **~0.5–2.5%/yr, with a real probability of ≤ 0** | gross − drag; the band **straddles zero by construction.** |
| **NET L/S Sharpe (the number that ships)** | **~0.3–0.5, mode ~0.4, live left tail < 0** | LOW end of the 0.4–0.8 platform band; ~35–45% probability of net Sharpe ≤ 0 at 2× stressed costs. |

**Bottom line:** I expect this to land at the **bottom of the 0.4–0.8 per-strategy net band, or fail.**
I propose it anyway because (a) the mechanism is real, well-cited and **falsifiable**; (b) it is a
genuine candidate **diversifier** (predicted |ρ| ∈ [−0.3,+0.2], i.e. inside the 0.4 gate, vs the only
active pool peer); and (c) the binding kill — cost-vs-premium and MinBTL on the high-VIX sub-sample —
is exactly what the rigor battery exists to adjudicate. **If the weekly + no-trade-band design cannot
hold net Sharpe > 0 at 2× stressed costs, or MinBTL exceeds the high-VIX sub-sample, the strategy is
dead — and that is the correct outcome.** Anything the backtest reports **above ~1.0 net Sharpe on
this universe must be treated as a bug or look-ahead** (standing red flag), not skill.

**Cross-references to prior art (explicit):** this design is built to escape the three `vix_regime`
kills (§9 K5 spanning t = −0.18; §9 K4 dominated-by-trailing-vol; §9 K9 MinBTL 3,968yr) and to invert
the `vol_scaled_momentum` fair-weather trap correctly (we claim profit IN high-VIX, so the burden is
**stressed costs + the stress-state tail**, not crash protection — §6, §10, K13). L1–L7 are wired
into the kill table (§9). The `sector_rotation_v1` |ρ| ≤ 0.4 gate (run ee3a7b06, net Sharpe 0.84,
HISTORICAL) is the central portfolio-fit test (K6).

---

## 1. Economic rationale — who loses money, and why (≥ 2 cited papers)

**The trade is selling immediacy in stress.** In high-volatility regimes, volatility-constrained
intermediaries — dealers, market-neutral stat-arb desks, leveraged liquidity providers, ETF
authorized participants — cut risk capital and widen the price they demand to absorb one-sided
*sector-level* flow. Whoever steps in to take the other side of forced, uninformed sector
selling/buying is paid an inventory- and adverse-selection premium. The **5-day cross-sectional
reversal portfolio (long the worst recent sectors, short the best) IS that liquidity-provision
return**, and the premium **scales with the VIX** because that is when intermediary balance-sheet
capacity is scarcest.

**Who is on the other side (who loses money to us):** de-risking and vol-target funds dumping the
recently-weakest sectors and chasing the strongest; margin-driven liquidation; **leveraged/inverse-ETF
daily rebalancing, which mechanically buys winners and sells losers into the close — the exact
opposite of our book**; and retail/panic sector rotation. They demand immediacy; we sell it and
warehouse the inventory across the ~5-day horizon until the transitory price pressure mean-reverts.

**Primary supporting papers (verified upstream, real venues):**

1. **Nagel, S. (2012). "Evaporating Liquidity." *Review of Financial Studies* 25(7):2005–2039.** The
   near-exact statement of our mechanism: short-term reversal return ≈ the return to liquidity
   provision; expected return and conditional Sharpe **rise strongly with the VIX**. Decisively for
   *this* spec, Nagel finds **industry/sector reversal "does not yield high returns unconditionally"**
   but **does** pay **conditional on high VIX**. This simultaneously blesses a *sector-level,
   VIX-gated* trade and pins our central design constraint: **the unconditional leg is ≈ zero, so the
   VIX gate is not an enhancement — it is the entire strategy.**
2. **Hameed, A., Kang, W. & Viswanathan, S. (2010). "Stock Market Declines and Liquidity." *Journal of
   Finance* 65(1):257–293.** Independent confirmation of the **supply-side** channel and, decisively
   for trading *sectors*, documents **inter-industry liquidity spillovers** when market-maker capital
   is constrained — i.e., the premium exists at the level we actually trade, not only single names.

**Horizon support:** Lehmann, B. (1990), *QJE* 105(1):1–28 — validates the ~5-day weekly contrarian
horizon as a real, transitory-price-pressure effect (net-of-cost survival was a 1990-era claim that
has since decayed).

**The rationale is pre-loaded with its own contradictions — stated plainly, not hidden:**

- **The premium is payment for a catastrophic tail (Khandani, A. & Lo, A. (2011), *JFM* 14(1):1–46).**
  The dollar-neutral buy-losers/short-winners book — our *exact* construction — suffered
  unprecedented, **autocorrelated** losses in the Aug 6–9 2007 quant quake as leveraged providers
  de-levered simultaneously. The premium we collect on calm-ish high-VIX days **is** the insurance
  premium for that cascade. We are structurally **short liquidity / short gamma**, and the gate
  concentrates ALL exposure into exactly the regime where the cascade detonates (§5).
- **The premium is smallest exactly where we trade (Avramov, D., Chordia, T. & Goyal, A. (2006),
  *JF* 61(5):2365–2394).** Reversal is concentrated in *illiquid, high-turnover* single names, where
  even there gross profit ≈ transaction costs. Sector ETFs are the *opposite* population — the most
  liquid, most-AP-arbitraged instruments on the tape. The harvestable gross premium is therefore
  structurally damped; the VIX gate must select the ~half of days where compensation exceeds cost, or
  there is nothing to harvest. **This is the single strongest reason the strategy can fail net at the
  ETF layer (translation risk).**

**The cost lens reads this rationale as a warning:** the same constrained-intermediary state that
creates the premium is the state in which spreads, depth, and impact are worst (Hameed et al.'s
liquidity withdrawal is two-sided — it raises both our premium and our cost). Premium and cost are
driven by the **same latent variable**; the strategy is viable only if, on the high-VIX sub-sample,
the premium curve sits **above** the cost curve net — an empirical question the battery must answer
(§6, §9).

---

## 2. Signal construction (exact, pre-committed, look-ahead-clean)

All quantities use **daily total-return (split- & dividend-adjusted) closes**. Weights at date *t*
use only data **≤ t**; the review engine applies the execution-convention shift. **The strategy
function must NOT pre-shift** (weights contract). Steps, in order:

1. **5-day reversal score.** For each eligible sector *i*, trailing 5-trading-day total return
   `r5_i(t) = close_i(t) / close_i(t−5) − 1`.
2. **Cross-sectional demean + standardize.** `z_i(t) = (r5_i − mean_j r5_j) / std_j r5_j` over the
   *eligible* universe (dynamic, §3). Demeaning removes the common (market) component so the score is
   *relative dispersion only*; standardizing keeps the book's gross stable across regimes (high-VIX
   days have larger return magnitudes — z-scoring prevents the position size from exploding exactly
   when the tail is worst; a direct Khandani-Lo defense, §5).
3. **Reversal tilt = negation.** `s_i(t) = −z_i(t)` — long the worst 5-day performers, short the best.
4. **VIX regime gate (binary, the duty cycle).** Let `V(t)` be the VIX close at *t* and
   `M(t) = median(V(t−59 .. t))` the trailing **60-trading-day** median (inclusive, **strictly
   backward** — never centered). **Gate ACTIVE iff `V(t) > M(t)`**; otherwise the book is **flat
   (all weights 0)** — zero gross, zero turnover. Needs ≥ 60 consecutive VIX closes before the first
   tradable date (warmup).
5. **Dollar-neutral weighting.** On an active rebalance date, demean `s_i` again post-gate so
   `Σ_i w_i = 0` exactly (longs fund shorts), clip per-name `|w_i| ≤ max_weight = 0.20`, then
   renormalize to `Σ_i |w_i| = gross = 1.0` (50% long / 50% short, net 0). Continuous **proportional-
   to-z** tilt, not top-k/bottom-k: with only 9–11 names, hard buckets discard the magnitude of
   dispersion (the paid quantity) and are brittle to one name flipping rank; the continuous tilt
   degrades gracefully, is lower-turnover, and has exactly one shape parameter (the cap). Mirrors the
   `sector_rotation` reference runner's z-tilt + cap + renormalize.
6. **No-trade band (THE cost/commission control, §6).** Hold `w_prev_i` unless
   `|w_target_i − w_prev_i| > band` (`band = 0.05` of gross); otherwise move to `w_target_i`. Converts
   a continuously-drifting signal into a discrete, low-churn book — the single most important turnover
   AND $1-commission-floor lever.

**Momentum-neutralization — pre-committed OFF in v1 baseline, declared ON as a counted variant.**
The S1 briefing (Da-Liu-Schaumburg 2014; Blitz et al. 2024) is explicit that raw sector reversal is
partly a bet *against* short-term industry momentum — a known drag that is also mechanically the
`sector_rotation_v1` peer. **Decision: `mom_neutralize = off` in baseline.** Rationale: (a) with 9–11
assets, projecting out a momentum factor estimated on the same cross-section is noisy and burns
degrees of freedom (echoes **L2** — tight constraints add noise); (b) keeping the raw signal makes the
unconditional-reversal baseline an honest like-for-like null and the |ρ| vs `sector_rotation`
*measurable as-is* rather than entangled with a neutralization choice; (c) the across-industry-momentum
drag's size is read **directly off the unconditional baseline** (§7). `mom_neutralize = on` (project
`s_i` orthogonal to a 126-day 6-1 cross-sectional sector-momentum vector before z-scoring) is a
**declared, pre-registered variant counted in `n_trials`** — never silently substituted.

**Look-ahead hygiene (unit-test target `test_no_lookahead_truncation_invariance`):** truncating the
price/VIX panel at any date `T` must leave all weights at dates `≤ T` bit-identical. The VIX gate uses
only `V(≤ t)`; the 60-day median is strictly backward; the 5-day return uses `close(t−5..t)`; the
function returns **unshifted** weights and the engine applies the 1-bar shift.

---

## 3. Universe (dynamic 9 → 10 → 11; never backfill)

Eleven SPDR sector ETFs, **membership by date** (never backfill late inceptions — that is look-ahead
on the universe definition; S0 risk #3):

| Window | Members | n |
|---|---|---|
| start → 2015-10-07 | XLK XLF XLE XLV XLY XLP XLI XLB XLU | 9 |
| 2015-10-08 → 2018-06-18 | + XLRE | 10 |
| 2018-06-19 → end | + XLC | 11 |

A sector is **eligible** on date *t* only once it has ≥ 5 trading days of post-inception history (so
`r5` is real, not partly synthetic) AND ≥ 60 VIX closes exist for the gate. Dollar-neutral and
z-score operations run over the *eligible* set each date; ineligible sectors get an explicit weight of
0 (reference runner's `mom.loc[d].notna()` eligibility pattern), never a phantom slot. **Minimum
eligible cross-section `min_eligible = 5`**; below this, flat.

**Local history starts 2012-01-03** for the 9 core sectors (~14.4 yr; **NOT ~1999** as the original
brief assumed); XLRE 2015-10-08, XLC 2018-06-19; all to 2026-06-11. A yfinance/Stooq pull back to SPDR
~Dec-1998 inception would *relieve* MinBTL and is worth attempting **in implementation** (data task,
not assumed here) — but **does not fix the binding constraint**: the *effective* high-VIX sub-sample
is ~half the calendar regardless (§5, §9).

**Benchmark / control (not universe members):** SPY (beta/spanning control). **VIX** drives the gate
only.

---

## 4. Rebalance frequency & execution convention

**Pre-committed: WEEKLY rebalance clock** (`rebalance.frequency = "weekly"`, review-engine
`rebalance_dates(index, "weekly")` → last trading day of each week), **execution convention
`t+1_open`** (gate + weights decided at the weekly rebalance date *t* from data ≤ *t*, executed at the
next session's open; the engine applies the shift). The 5-day reversal naturally implies a ~weekly
hold, so the weekly clock aligns decision cadence to the signal horizon and **cuts turnover ~5× vs
daily** without materially changing the captured premium (the reversal is largely spent within the
week). `t+1_open` is the realistic retail convention (we cannot trade the close we used to compute the
signal) and is more conservative than `t_close`.

**Gate timing:** read `G(t)` **on the weekly rebalance date only** using `V(≤ t)`; intra-week the book
is held (no daily re-gating). If `G = 0` at a rebalance date, flatten to zero that week. We explicitly
accept that the Della Corte overnight/intraday leg is **out of reach** on daily-close data (S1 §4.5).

**Why weekly and not daily-eval-throttled-by-band (resolving the draft conflict, §13):** the
risk-lens draft proposed daily evaluation throttled only by the band. The weekly clock is the cleaner,
more transparent L7 defense and is **structurally** turnover-bounded rather than relying on the band
alone to suppress daily churn — **L7** is unambiguous: daily rebalancing of a regime signal produced
**2430%/yr turnover in `vix_regime` (HISTORICAL), cut to 916%/yr by a weekly resample**. Daily +
high-VIX bursts + widest spreads (C6, IOSCO/Mar-2020) would almost certainly drive net ≤ 0. Daily and
biweekly are retained as **declared sensitivity trials** (counted in `n_trials`).

**Turnover budget (pre-committed, reported):** two-sided annual turnover **≤ ~500%/yr** as a hard
design target. Calibration: `vix_regime` weekly was 916%/yr (HISTORICAL); our weekly + no-trade band +
~50% duty cycle (flat half the year) targets materially below that. **If realized turnover > ~800%/yr
with no band setting that both controls turnover AND keeps net Sharpe > 0, the design has failed —
widen the band (declared parameter move, bumps `n_trials`) or kill** (K12).

---

## 5. Failure modes — the short-vol tail & the binding statistical risk

**This strategy is a short-liquidity / short-vol carry trade gated into its own worst regime.** Average
Sharpe is the *least* informative statistic about this stream; the spec leads with the failure modes.

**5.1 Short-vol / forced-deleveraging tail (PRIMARY risk).** We provide liquidity *only* in high-VIX
windows — a stream of small gains punctuated by rare, large, **autocorrelated** losses when a crowded
contrarian book is force-unwound. Canonical event: **Aug 6–9 2007** (Khandani-Lo) — the buy-losers/
short-winners book lost a multi-sigma amount over three days, a loss the prior Sharpe gave no warning
of. **Mar-2020** is the modern analog: VIX > median for an extended stretch (gate maximally active),
sector dispersion enormous, ETF creation/redemption arbitrage strained (IOSCO PD682: bond ETFs
dislocated 3–8% from NAV; equity sector ETFs far less, but the channel is the concern). A reversal
book that bought the worst sector into a falling, illiquid tape would take repeated gap losses
precisely when fully sized. **The edge and the tail are the SAME trade, and the gate concentrates ALL
exposure into the regime where the tail detonates.** Reasoned (NOT backtested) crash profile to be
*tested by the battery*: left-skewed, fat-tailed, **worst-week −10% to −20% at gross 1.0** in a
2007/2020-type cluster; losses autocorrelated (breaks i.i.d. Sharpe annualization → block-bootstrap CI
is the honest interval, likely wider).

**5.2 MinBTL on the high-VIX SUB-sample (the MODAL kill — compute EARLY).** The trade is flat ~half
the days, so the **effective sample** backing the Sharpe is ~half the calendar — on ~14 yr local that
is ~7 yr of *active* trading, and high-VIX days are themselves *clustered* (not 7 independent years).
HISTORICAL calibration: `vix_regime` **died at MinBTL = 3,968 yr (315× over budget; bootstrap CI spans
zero)**; the long-only *monthly* `sector_rotation_v1` (Sharpe 0.84, full sample) **already fails MinBTL
(needs 4095d vs 3485 available)**. A 5-day reversal flat half the days has an **even shorter effective
sample → MinBTL on the conditional sub-sample is the single most likely kill (K9), computed before any
optimization.**

**5.3 Translation risk (≈ coin-flip, not a tail).** Nagel's strong results are single-stock and he
notes *industry* reversal pays nothing unconditionally; Avramov-Chordia-Goyal locate the premium in
illiquid names where it ≈ costs. Across 11 tight-spread, AP-arbitraged ETFs the harvestable dispersion
may be **too thin to clear vol-conditional costs even in high-VIX** → **net Sharpe ≤ 0 at 2× costs is
roughly a coin-flip** (K1). The spec is designed to let that result kill the strategy at the 2× cost
gate rather than be rescued by parameter search.

**Sizing philosophy (deliberate):** `gross = 1.0`, **no leverage** (leverage amplifies the exact tail
that kills it); **do NOT vol-target** — L3 (vol targeting does NOT fix crash risk for long-only equity)
and the `vol_scaled_momentum` kill both warn against it, and our tail is a *liquidity cascade* not a
slow vol grind, so a vol overlay would react too late and *de*-lever after the gap, locking in the
loss (and would add a trial likely failing the L5 +0.15 bar). The honest mitigation is fixed
conservative gross + the z-score gross-stabilization (§2 step 2) + per-name cap + a hard tail kill
(K13), not a dynamic overlay.

---

## 6. Cost & turnover model — volatility-conditional, NOT flat bps

Flat average-bps is the cardinal error here because the strategy **trades only in the high-VIX column
where spreads/impact are worst** (Avramov-Chordia-Goyal; IOSCO/Mar-2020). The model is
**regime-dependent**, evaluated by the engine at **1× / 2× / 3× on the stressed (high-VIX) column**.

**Per-leg one-way cost stack, 25k–100k AUM on IBKR:**

| Component | Calm | High-VIX (gate-active) | Source / rationale |
|---|---|---|---|
| Commission | IBKR Pro $0.005/share, **min $1.00/order**; the **$1 floor BINDS at 25k AUM** | same | IBKR schedule. At 25k the per-order floor is the dominant, *fixed*, non-scaling cost. |
| Half-spread | SPDR sectors among tightest on tape: ~1 bp (XLK/XLF) to ~1–3 bps (XLB/XLRE/XLU) | **2×–5× wider: ~3–8 bps**; tail 15–30 bps on Mar-2020-type dislocation | SSGA practitioner data (cred 2); IOSCO PD682 / Mar-2020 ETF-NAV dislocation. |
| Market impact | Negligible at 25k–100k | small but nonzero in thin high-VIX books; ~1–3 bps square-root floor | We are not at HFT scale; impact is the smallest term. |
| Short financing/borrow | sector SPDRs GC, easy-to-borrow | small but **non-zero** on the 50% short book | The L/S book cannot pretend shorts are free. |
| **Round-trip per name (in+out)** | ~4–10 bps | **~12–28 bps** | the cost the battery applies to turnover |

**The 25k commission-floor problem (often missed).** At 25k, an 11-name L/S book at gross 1.0 is
~$1.1k notional/name/side; IBKR's **$1.00 order minimum ≈ 9 bps/order**, and a full 22-leg rebalance
≈ $22 ≈ 9 bps of the 25k book per round trip — **larger than the calm half-spread and fixed.**
Mitigations, pre-committed and floor-aware:
1. The **no-trade band (0.05)** is also a commission-floor defense: a typical weekly rebalance touches
   ~4–8 legs, not 22.
2. **`n_legs_per_side` (declared, baseline 2–3, perturbed 1–4):** optionally trade only the extreme
   tails of the cross-section so each clip is larger relative to the $1 floor — a genuine trade-off
   (fewer names = less diversification) that the battery perturbs.
3. The cost model charges **max(per-share commission, $1 order floor)** explicitly (a percentage-bps
   model understates cost at 25k); **report cost drag at BOTH 25k and 100k** for an honest capacity
   story. At 100k the floor binds far less; **capacity (Gate 10) passes comfortably** — decay, MinBTL
   and the tail are binding, not capacity.

**Net arithmetic (EXPECTATION):** at ≤ ~500%/yr turnover × ~12–28 bps stressed round-trip,
`cost drag ≈ 5.0 × ~0.20% ≈ ~1.0%/yr`, to **~2.5%/yr** at the high end / 2× multiplier. Against a gross
L/S edge of ~2–4%/yr, **net edge ≈ 0.5–2.5%/yr and can be ≤ 0** — this is the entire risk, stated
honestly. **If NET *improves* with higher cost multipliers, it is a bug** (standing red flag).

**Expected GROSS vs NET Sharpe (EXPECTATION):** gross high-VIX-days Sharpe ~0.7–1.1; **NET full-period
L/S Sharpe ~0.3–0.5, mode ~0.4, left tail < 0**; P(net ≤ 0 at 2× stressed cost) ~35–45%.

---

## 7. Baselines to beat (pre-registered — changing these later bumps `n_trials`)

Per **L1/L6** and the S1 four pre-commitments, THREE baselines, all on the same universe/costs/dates:

1. **Equal-weight buy-and-rebalance** (L1, the dumbest credible alternative). Long-only EW of the
   eligible sectors. **Beat it net or do not ship.** (Ours is dollar-neutral, so the binding test is
   risk-adjusted standalone return *and* diversification benefit — |ρ| with EW and blended-Sharpe
   improvement — not raw return.)
2. **Unconditional 5-day reversal** (identical signal, **VIX gate removed / always-on**). The P0
   falsification baseline (L4): **the gated version must add ≥ +0.15 net Sharpe** over this (L5 overlay
   bar). The unconditional arm is expected **≈ zero net** (Chordia et al.; Blitz et al.; Nagel) — so
   the gap *is* the whole thesis. If gated ≤ unconditional, the "vol-conditioned" thesis is
   **falsified** (it's just reversal, and reversal is dead).
3. **Plain 21-day trailing-vol filter** (gate the same reversal on realized 21-day vol > its own
   median instead of VIX). **The exact challenge that killed `vix_regime`** (dominated by a 21-day
   trailing-vol signal; HISTORICAL trailing-vol Sharpe 0.341 vs vix_regime 0.299; spanning t = −0.18).
   If the cheaper, simpler gate matches/beats the VIX gate, the "VIX" framing adds nothing → kill the
   VIX-specific claim.

**Spanning alpha (engine, must measure):** independent spanning-alpha **t ≥ 1.96** vs ALL of
{unconditional reversal, monthly momentum / `sector_rotation_v1`, trailing-vol filter} — mirrors the
`vix_regime` t = −0.18 kill. **L5 overlay rule:** the VIX gate must ADD ≥ +0.15 Sharpe over the
unconditional reversal, not merely reduce drawdown.

---

## 8. Every parameter, with value and rationale (battery perturbs each ±20/40%)

| Parameter | Baseline value | Rationale | Perturbation (±20/40%) |
|---|---|---|---|
| `reversal_lookback` | **5 trading days** | Lehmann weekly / Nagel reversal horizon; long enough to be liquidity-pressure, short enough to dodge 1-day bid-ask bounce; **not tuned** (from literature). | 4 / 6 and 3 / 7 |
| `vix_lookback` (median window) | **60 trading days** | Pre-registered gate window; ~3 trading-months balances responsiveness vs a stable regime estimate; untuned. **Free parameter — battery must perturb.** | 48 / 72 and 36 / 84 |
| `vix_threshold` | **trailing 60-day MEDIAN (50th pct), `V(t) > M(t)`, binary** | Least-parameterized split; ~50% duty cycle **maximizes the effective sample** (the binding stat risk); relative (not absolute VIX) → regime-stationary & look-ahead-clean; median robust to spikes. | percentile ±20/40% → ~40th/60th, ~30th/70th (and `>0.9×`/`>1.1×` median) |
| `construction` | **long_short, dollar-neutral, gross 1.0** (0.5 long / 0.5 short) | §1: mechanism is cross-sectional; isolates the liquidity-provision residual; removes hidden beta (red flag: long-only Sharpe ≫ EW → beta/look-ahead); cleaner |ρ| vs the long-only peer. | gross 0.8 / 1.2 and 0.6 / 1.4 |
| `max_weight` (per-name cap) | **0.20** | Mirrors `sector_rotation` cap; prevents one extreme 5-day mover (e.g. XLE on an oil shock) dominating a 9–11-name book; caps single-sector gap risk. | 0.16 / 0.24 and 0.12 / 0.28 |
| `no_trade_band` | **0.05** (5% per-name of gross) | §6 — core turnover AND $1-commission-floor control; set so weekly rebalances touch ~4–8 legs, target turnover ≤ 500%/yr; **NOT Sharpe-tuned**. | 0.04 / 0.06 and 0.03 / 0.07 |
| `n_legs_per_side` | **2–3** (tails-only option) | §6.2 — defends the $1 commission floor at 25k via larger clips; genuine diversification trade-off. | 1 / 2 and 3 / 4 |
| `min_eligible` | **5 sectors** | Below this the cross-section is too thin for a meaningful dollar-neutral tilt; flat otherwise. | structural (not perturbed) |
| `rebalance.frequency` | **weekly** | §4 — kills the L7 daily-turnover hazard; matches the 5-day hold. | structural; daily & biweekly as **declared trials** |
| `execution_convention` | **`t+1_open`** | Realistic retail; conservative vs `t_close`; engine applies shift. | structural (engine) |
| `mom_neutralize` | **off (baseline); on (declared variant)** | §2 — noisy to project out on 9–11 names (L2); confronts Da-Liu-Schaumburg / Blitz drag; both count toward `n_trials`. | binary variant (both reported) |
| `vix_source` | **`VIXCLS` (FRED, PIT)** | §11 — vendor-stable, PIT-clean; 1-day publication lag is *conservative* (cannot leak); platform PIT-shifts macro by default. Alt refreshed `^VIX` same-day close is defensible but ONE is pinned. | data choice (declared) |
| `cost_model` | **volatility-conditional** spread + impact + short financing; max(per-share, $1 floor); evaluated at 25k AND 100k | §6 — the whole point; flat bps understates stressed costs. | 1× / 2× / 3× on the stressed column |

---

## 9. Pre-committed kill thresholds (mapped to the 11 gates; L1–L7 wired in)

Committed BEFORE any backtest. **I will not relax any of them after seeing the result it blocks** — the
URGE to relax a gate after seeing what it blocks is THE failure mode this system prevents.

| # | Kill predicate | Maps to |
|---|---|---|
| K1 | **NET L/S Sharpe < 0 at 2× stressed costs** (PRIMARY cost kill; P0 falsification predicate 1) | Gate 8 analogue |
| K2 | **VIX-gated net Sharpe ≤ unconditional-reversal net Sharpe**, OR gate adds < +0.15 Sharpe | P0 predicate 2; **L4/L5** |
| K3 | **Net Sharpe ≤ equal-weight** (does not beat the dumbest credible alternative) | **L1**; first-principle (3) |
| K4 | **21-day trailing-vol filter matches/beats the VIX gate** on Sharpe (it's just dressed-up vol timing) | **L6**; the `vix_regime` kill |
| K5 | **Spanning-alpha t < 1.96** vs {unconditional reversal, `sector_rotation`, trailing-vol filter} | Gate 9; `vix_regime` t = −0.18 |
| K6 | **\|ρ\| > 0.4 vs `sector_rotation_v1`** (predicted [−0.3,+0.2], **UNMEASURED**) or any active pool stream | Gate (portfolio-fit) |
| K7 | **IS Sharpe < 0.5** | Gate 1 |
| K8 | **OOS walk-forward Sharpe < 0.3**, or IS/OOS Sharpe ratio < 0.5 | Gates 2 / 6 |
| K9 | **MinBTL > available history on the high-VIX SUB-sample** | Gate 7 — **the MODAL kill** (computed EARLY) |
| K10 | **DSR < 0.95 or PSR < 0.90** with honestly-declared `n_trials = 24` | Gates 4 / 5 (default promotion) |
| K11 | **Sharpe < 0 at 3× stressed costs** | Gate 8 (hard auto-kill) |
| K12 | **Two-sided turnover > ~800%/yr** with no band setting that both controls turnover AND keeps net Sharpe > 0 | **L7**; cost-lens design failure |
| K13 | **Max DD > −30%**, OR worst high-VIX week < −15% at gross 1.0 / conditional high-VIX-cluster MaxDD < −25%, OR active-day skew < −1.5 (or < −1.0 with Sharpe < 0.6) / autocorrelated cascade losses (short-vol carry, not alpha) | Gate 3; Khandani-Lo tail |

**Auto kills (1–8 analogues):** K1, K3, K7, K8, K9, K10, K11, K13(DD). **PM/owner judgment (9–11):**
K2, K4, K5, K6, K12, K13(tail/skew), and Gate 11 (credible mechanism — §1 satisfies). **Must-measure
(engine, not proposal text):** vol-tercile conditional Sharpe (reframed as a *concentration* warning —
report top-tercile worst-week & MaxDD, not just Sharpe); cost 1×/2×/3× slope; block-bootstrap CI
(expected to span zero on the sub-sample); left-tail diagnostics conditional on VIX > median incl.
explicit Aug-2007 (if long history pulled) and Mar-2020 windows.

---

## 10. Expected correlation & spanning vs `sector_rotation_v1`

**Predicted |ρ| ∈ [−0.3, +0.2]** vs `sector_rotation_v1` (S0) — opposite tilt (contrarian vs
momentum), different horizon (5-day vs monthly), different duty cycle (flat ~half the days vs
always-on) — **plausibly inside the |ρ| ≤ 0.4 gate but UNMEASURED.** The honest risk: both are L/S on
the same 11 sectors, so a sector-dispersion regime could co-move them, and the high-VIX gate overlaps
exactly the months `sector_rotation`'s momentum is most stressed. Dollar-neutral construction keeps the
streams structurally distinct (one contrarian, one trend; ours net-zero beta, the peer long-only). The
gate is **K6** (kill if |ρ| > 0.4) and **K5** requires independent spanning alpha t ≥ 1.96 vs
`sector_rotation` — i.e., the stream must be both *uncorrelated* and *additive*, not merely different.

---

## 11. Data prerequisites (decided here)

1. **VIX source — DECISION: FRED `VIXCLS`** (not `^VIX` via yfinance) for the gate. Rationale:
   vendor-stable PIT-friendly daily close; local `^VIX` (`vix_daily`) is **stale (ends 2026-02-27)**.
   `VIXCLS` carries a ~1-business-day publication lag, resolved cleanly by the execution convention:
   with `t+1_open` execution, the gate at rebalance date *t* uses the `VIXCLS` value for *t* published
   before next-session open — **no extra look-ahead, and the lag is conservative (can only remove
   information, never add it).** QC must confirm no centered/forward fill injects future VIX. (This
   resolves the draft conflict: signal-lens recommended VIXCLS, risk-lens preferred same-day `^VIX`;
   VIXCLS is chosen for vendor stability + PIT-cleanliness + the stale local `^VIX`.)
2. **Dynamic universe** per §3 — enforced by eligibility, never backfilled.
3. **Total-return / split-adjusted closes** consistent across all 11 ETFs; QC preflight
   (`quant_data/qc.py`) flags stale prices / extreme returns around dividend ex-dates and the
   2015/2018 universe splice points (a 5-day reversal is acutely sensitive to an unadjusted ex-div
   jump showing up as a spurious one-day "return").
4. **`backtest_start`:** first tradable date after the 60-day VIX warmup on available history
   (≈ 2012-Q2 on the local lake). **`backtest_end`:** latest common date (ETFs to 2026-06-11; refresh
   VIX to match). A ~1999 long-history pull relieves MinBTL but does NOT remove the half-duty-cycle
   effective-sample constraint.

---

## 12. How this proposal discharges the four S1 REVISE pre-commitments

1. **Beat the gate's own null (two head-to-head baselines + EW).** §7: unconditional reversal (K2),
   trailing-vol filter (K4), equal-weight (K3) — all pre-registered with thresholds.
2. **Sector-momentum headwind addressed explicitly.** §2: `mom_neutralize = off` in baseline with
   stated L2 rationale (noisy on 9–11 names); `on` as a declared, trial-counted variant; drag size
   read off the unconditional baseline; doubles as the `sector_rotation` |ρ| story.
3. **Volatility-conditional cost model + no-trade band.** §6 (regime-dependent spread/impact/financing,
   $1 commission-floor accounting at 25k AND 100k, 1×/2×/3× on the stressed column) + §4 (weekly clock
   + 0.05 no-trade band + turnover budget ≤ 500%/yr, reported). Defuses **L7**.
4. **MinBTL on the high-VIX sub-sample, computed early.** §5.2 + K9; flagged as the **modal** kill.

**Also addressed:** ETF translation risk (§1, §5.3, K1); unconditional-reversal decay-to-zero (§7
baseline 2, expected ≈ zero net); the three `vix_regime` kills (K5 spanning, K4 trailing-vol
dominance, K9 MinBTL); the `vol_scaled_momentum` fair-weather inversion (we claim profit IN high-VIX,
so the burden is stressed costs + tail — §5, §6, K13); |ρ| vs `sector_rotation_v1` (K6, §10).

---

## 13. Conflicts resolved across the three drafts (pre-committed; variants feed `n_trials`)

| Dimension | Cost lens | Signal lens | Risk lens | **CANONICAL DECISION** |
|---|---|---|---|---|
| Trading clock | weekly | weekly | daily-eval + band | **Weekly** (cleaner, structurally turnover-bounded L7 defense; daily/biweekly are declared trials) |
| `no_trade_band` | 0.05 | 0.02 | 0.05 | **0.05** — the $1-commission-floor defense at 25k is decisive; 0.02 does not protect the order floor |
| VIX source | VIXCLS | VIXCLS | refreshed `^VIX` | **VIXCLS (FRED, PIT)** — vendor-stable, PIT-clean, conservative lag, stale local `^VIX` |
| `n_legs_per_side` | 2–3 (tails-only) | full z-tilt | full z-tilt | **Full proportional-z tilt baseline; tails-only (2–3) a declared, perturbed commission-floor variant** |
| `n_trials` | 24 | ≥ 6–8 | ≥ 6–8 | **24** — the higher honest FLOOR; never shrink to pass DSR |
| `mom_neutralize` | off (declared on) | off (declared on) | off (v2 only) | **Off in v1 baseline; on as a declared, trial-counted variant** |
| Expected net Sharpe | 0.3–0.6 (~0.4) | 0.3–0.6 (~0.4) | 0.2–0.5 (~0.3) | **~0.3–0.5, mode ~0.4, live left tail < 0** |

**Honest `n_trials = 24` (feeds DSR; a FLOOR that accumulates across versions).** The deliberately
explored design space is `reversal_lookback` (≈3) × `vix_lookback`/threshold (≈3) × `no_trade_band`
(≈3) × `n_legs_per_side` (≈3) × `mom_neutralize` (2) × `rebalance freq` (3) — a few hundred nominal
combinations; the **honestly declared** count of distinct variations I commit to evaluating is **24**,
explicitly NOT 1. **DSR is deflated by this. If DSR < 0.95 only because `n_trials` is high, that is the
system working — I will not retroactively shrink `n_trials` to pass the gate.**

---

## 14. References (verified upstream; real titles/venues — no fabrication)

- **Nagel, S. (2012). "Evaporating Liquidity." *Review of Financial Studies* 25(7):2005–2039.** — core
  mechanism; reversal ≈ liquidity provision; conditional Sharpe rises with VIX; *industry* reversal
  pays only conditional on high VIX.
- **Hameed, A., Kang, W. & Viswanathan, S. (2010). "Stock Market Declines and Liquidity." *Journal of
  Finance* 65(1):257–293.** — supply-side mechanism; inter-industry liquidity spillovers (sector level).
- **Lehmann, B. (1990). "Fads, Martingales, and Market Efficiency." *QJE* 105(1):1–28.** — validates
  the ~5-day weekly contrarian horizon.
- **Avramov, D., Chordia, T. & Goyal, A. (2006). "Liquidity and Autocorrelations in Individual Stock
  Returns." *Journal of Finance* 61(5):2365–2394.** — reversal concentrated in illiquid names; gross
  ≈ costs even there → thin gross premium expected at the liquid ETF layer (central cost contradiction).
- **Khandani, A. & Lo, A. (2011). "What Happened to the Quants in August 2007?" *Journal of Financial
  Markets* 14(1):1–46 (NBER w14465).** — the short-vol / forced-deleveraging tail of this exact book.
- **Da, Z., Liu, Q. & Schaumburg, E. (2014). "A Closer Look at the Short-Term Return Reversal."
  *Management Science* 60(3):658–674.** — only the non-fundamental residual reverses robustly;
  across-industry momentum works against raw sector reversal.
- **Blitz, D., van der Grient, B. & Honarvar, I. (2024). "Reversing the Trend of Short-Term Reversal."
  *Journal of Portfolio Management* 50(6) (SSRN 4575689).** — classic STR "vanished"; naive STR bets
  against short-term industry momentum.
- **Chordia, T., Subrahmanyam, A. & Tong, Q. (2014). *Journal of Accounting & Economics* 58(1):41–58.**
  — post-decimalization anomaly decay (~halved).
- **McLean, R. D. & Pontiff, J. (2016). "Does Academic Research Destroy Stock Return Predictability?"
  *Journal of Finance* 71(1):5–32.** — ~58% post-publication decay → 50–60% haircut prior.
- **IOSCO (2020, PD682) + Mar-2020 ETF-arbitrage/AP-constraint literature.** — tight ETF spreads NOT
  guaranteed in stress → volatility-conditional cost model (§6).

*(NOT relied upon — flagged at S1: Della Corte et al. ≈2023 is a non-peer-reviewed WP whose strongest
leg is overnight/intraday, uncapturable on daily-close data; Dai-Medhat-Novy-Marx-Rizova
vol-conditioned-reversal was single-sourced and must be cite-checked before any reliance; the
"cost-of-immediacy ~1.9%/yr" and ">70% HFT volume" figures are headlines, not independently
re-verified.)*

---

**Disposition:** A cost-bound, mechanism-sound, genuinely-diversifying *candidate* whose viability is
decided entirely by whether a thin high-VIX liquidity-provision premium clears a volatility-conditional
cost stack on a half-length effective sample. The spec is built so the **kill is fast and honest**: if
the weekly + no-trade-band + dollar-neutral design cannot hold net Sharpe > 0 at 2× stressed costs, or
MinBTL exceeds the high-VIX sub-sample, the strategy dies at K1 / K9 — exactly as it should. **Proceed
to S3 with all of §9's thresholds pre-committed.**
