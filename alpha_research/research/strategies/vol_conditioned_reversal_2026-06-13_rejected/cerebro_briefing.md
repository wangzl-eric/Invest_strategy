<!-- 2026-06-13: S1 briefing (Cerebro synthesis) for vol_conditioned_reversal — supporting + contradicting literature, decay, crowding, in-repo prior art, recommendation. Spec only; no code. -->

# S1 Briefing — Vol-Conditioned Sector Reversal

> **Strategy id (proposed):** `vol_conditioned_reversal`
> **Folder:** `vol_conditioned_reversal_2026-06-13_PENDING`
> **Stage:** S1 (Cerebro briefing) · **Date:** 2026-06-13 · **Decision owner:** Zelin
> **Inputs:** S0 framing (`hypothesis.md`, PASS to S1), 4 parallel literature/prior-art finders.
> **Hard requirement check:** ≥ 2 supporting papers AND ≥ 1 contradicting study/failure mode.
> **Result: SATISFIED with wide margin** — 5 verified supporting peer-reviewed papers, 6 verified
> contradicting peer-reviewed papers / documented failure modes (counts below). Briefing is VALID.
> **Recommendation (this stage): REVISE** — proceed to S2, but the proposal must be written to a
> narrowed, pre-committed spec that discharges four named burdens of proof. Rationale in §7.

---

## 0. The idea in one line (carried from S0)

In high-VIX regimes (VIX above its trailing 60-day median), a **dollar-neutral, cross-sectional
5-day reversal** among the 11 liquid SPDR sector ETFs — **long the worst 5-day performers, short
the best** — earns a positive **net-of-cost** return because volatility-constrained intermediaries
withdraw liquidity and demand higher compensation to absorb uninformed sector flow (Nagel 2012).
**Falsified** if net Sharpe at 2× costs ≤ 0, OR it fails to beat equal-weight, OR it is
statistically indistinguishable from an *unconditional* reversal that ignores the VIX gate.

This is **not** a backtest. No `vol_conditioned_reversal` backtest exists yet. **Every Sharpe /
return figure in this briefing is either (a) a HISTORICAL result for a DIFFERENT in-repo strategy,
explicitly labelled, or (b) a reasoned EXPECTATION, explicitly labelled.** No number here is a
prediction of this strategy's realized performance.

---

## 1. Supporting evidence (mechanism + horizon + VIX gate)

The economic mechanism is **exceptionally well-supported** at the single-stock level by top-tier,
peer-reviewed work. The 5-day/weekly horizon and the VIX gate both have a direct literature basis.

| # | Source | Venue / cred | What it establishes for THIS idea |
|---|--------|--------------|-----------------------------------|
| S1 | **Nagel, "Evaporating Liquidity" (2012)** | *Review of Financial Studies* 25(7):2005–2039 · cred 5 · **verified** | **Near-exact statement of P0.** Short-term reversal return ≈ liquidity-provision return; expected return and **conditional Sharpe rise strongly with VIX** (spiked 2007–09) via constrained-intermediary liquidity withdrawal. **Crucially: reversal formed from INDUSTRY portfolios "do not yield high returns unconditionally" but DO produce high returns/Sharpe conditional on high VIX** — this is the literature basis for *gating* sector reversal on VIX rather than trading it always-on. |
| S2 | **Lehmann, "Fads, Martingales, and Market Efficiency" (1990)** | *Quarterly Journal of Economics* 105(1):1–28 · cred 5 · **verified** | Validates the **specific weekly (~5-day) horizon**: weekly winners reverse and losers rebound the following week, with contrarian profits that persisted net of bid-ask spreads and plausible costs *as of 1990*. Establishes short-horizon cross-sectional reversal as real and economically meaningful (transitory price pressure, not fundamentals). |
| S3 | **Hameed, Kang & Viswanathan, "Stock Market Declines and Liquidity" (2010)** | *Journal of Finance* 65(1):257–293 · cred 5 · **verified** | Independent confirmation of the **supply-side** mechanism: negative market returns reduce liquidity (worse when funding is tight); there are economically significant returns to *supplying* liquidity after large drops. **Documents INTER-INDUSTRY liquidity spillovers** from market-maker capital constraints — ties the mechanism to the *sector* level we actually trade. |
| S4 | **Della Corte, Kosowski, Liu & Wang, "Overnight–Intraday Reversal Everywhere" (≈2023, WP)** | Working paper (Imperial) · cred 3 · **verified (unpublished)** | Best **transfer evidence**: reversal-as-liquidity-provision works across international equity markets **and on equity-INDEX futures** (closest public analog to sector ETFs), attributed to asset-class liquidity provision; **cross-sectional return DISPERSION predicts the strategy's conditional Sharpe** — a sibling of our VIX gate. **Caveat: not peer-reviewed; strongest leg is overnight-vs-intraday (close-to-open), which our daily-close-only data CANNOT capture.** |
| S5 | **Da, Liu & Schaumburg, "A Closer Look at the Short-Term Return Reversal" (2014)** | *Management Science* 60(3):658–674 · cred 4 · **verified** | Decomposes reversal into across-industry momentum, within-industry expected-return variation, cash-flow underreaction, and a **residual**. **Only the residual (reaction to recent NON-fundamental moves) is robustly positive** and earns ~3× standard reversal's risk-adjusted return. Reversal long side ≈ liquidity shocks. **Double-edged (see §2/§4): the across-industry-momentum term works AGAINST raw sector reversal.** |

**Supplementary / mechanism-corroborating (not counted toward the supporting bar):**
Avramov, Chordia & Goyal, *JF* 2006 (reversal tied to illiquidity — but net profit ≈ costs, see §4);
Lo & MacKinlay, *RFS* 1990 (a large share of contrarian profit is cross-autocorrelation/lead-lag,
not own-stock overreaction — a *source-of-profit ambiguity* caution, see §4).

**Counted supporting papers (verified, peer-reviewed or established-author WP): 5** — Nagel 2012,
Lehmann 1990, Hameed-Kang-Viswanathan 2010, Da-Liu-Schaumburg 2014, Della Corte et al. ≈2023.
The hard bar (≥ 2) is cleared decisively on the first three alone (all top-3/top-5 journals).

### What the supporting evidence does and does NOT buy us

- **It buys MECHANISM PLAUSIBILITY and the rationale for the horizon + VIX gate.** The chain
  "stress → constrained intermediaries withdraw liquidity → reversal compensation rises with VIX,
  including at the industry level" is as well-evidenced as a published anomaly mechanism gets.
- **It does NOT buy an expected Sharpe at the sector-ETF level.** Every strong result is on
  *single stocks* (Nagel, Lehmann, Da et al.) or on *index futures via overnight-intraday* (Della
  Corte). **The peer-reviewed daily close-to-close sector-ETF version is essentially untested in
  the located literature.** Any Sharpe downstream is a backtest output, deflated for trials.

---

## 2. CONTRADICTING EVIDENCE AND DOCUMENTED FAILURE MODES (prominent — read this section)

The hard requirement is met with margin. The contradictions cluster into four kill vectors, and
each maps to a pre-commitment the S2 proposal must make. **The single strongest reason this fails
net at the ETF level:** the reversal premium is payment for absorbing *idiosyncratic single-name*
immediacy demand and is **smaller than transaction costs even where it is strongest** (illiquid
single stocks; Avramov-Chordia-Goyal). Across 11 internally-diversified, AP-arbitraged, tight-spread
sector ETFs the gross signal is **structurally damped**, while the high-VIX gate forces concentrated
trading into the exact crowded-unwind regimes (Aug-2007, Mar-2020) where this book bleeds — making
**net Sharpe ≤ 0 at 2× costs (the P0 falsification condition) the MODAL outcome, not the tail.**

| # | Source | Venue / cred | Kill vector |
|---|--------|--------------|-------------|
| C1 | **Avramov, Chordia & Goyal (2006)** | *Journal of Finance* 61(5):2365–2394 · cred 5 · **verified** | **Cost erosion + liquidity mismatch.** Reversal is concentrated in HIGH-turnover, LOW-liquidity (small/illiquid) stocks; even there the contrarian gross profit is **smaller than likely transaction costs** (rational equilibrium, no exploitable EMH violation). Sector ETFs are the *opposite* population (most liquid on the tape) → expect a **small gross premium** to begin with. |
| C2 | **de Groot, Huij & Zhou, "Another look at trading costs and short-term reversal profits" (2012)** | *Journal of Banking & Finance* 36(2):371–384 · cred 4 · **verified (precise bps not independently re-extracted — see flags)** | **Double-edged, net contradicting for THIS form.** Net reversal survives only by restricting to **large-cap single stocks** with low-turnover construction (~30–50 bps/week net reported). But (a) the surviving premium is a **single-stock cross-section across hundreds of names**, with no analog in an 11-asset ETF set, and (b) it confirms the premium is about absorbing *single-name* liquidity shocks. The "it survives in large caps" rescue does **not** transfer to sector ETFs. |
| C3 | **Chordia, Subrahmanyam & Tong (2014)** | *Journal of Accounting & Economics* 58(1):41–58 · cred 4 · **verified** | **Post-decimalization decay.** A broad set of cross-sectional anomalies **roughly halved** after decimalization (2001), linked to rising arbitrage capacity (HF AUM, short interest, turnover). Direct evidence that liquidity-provision-type edges decayed in exactly the modern, high-liquidity regime this strategy must trade. *(A worldwide follow-up / Jacobs-Muller dispute global robustness; the defensible claim is US-specific halving.)* |
| C4 | **Blitz, van der Grient & Honarvar, "Reversing the Trend of Short-Term Reversal" (2024)** | *Journal of Portfolio Management* 50(6) · SSRN 4575689 · cred 4 · **verified** | **"Vanished" + the sector-momentum headwind.** Classic STR "has steadily weakened over time, to the point of now having vanished entirely in most regions." **Naive STR loses partly because it bets AGAINST short-term INDUSTRY and factor momentum** — a sector-ETF reversal IS precisely that bet. Revivable only by neutralizing those terms. Recent (2024) practitioner evidence. |
| C5 | **Khandani & Lo, "What Happened to the Quants in August 2007?" (2011)** | *Journal of Financial Markets* 14(1):1–46 (NBER w14465, 2008) · cred 5 · **verified** | **Short-vol / short-liquidity TAIL + crowding.** The dollar-neutral buy-losers/short-winners book — the SAME mechanical construction — suffered unprecedented, sharply negative, highly autocorrelated losses in the Aug-2007 quant quake as leveraged liquidity providers de-levered together. **The edge and the tail are the same trade**, and the strategy is MOST ACTIVE in exactly the high-VIX states where the tail detonates. Returns also declined late-1990s→2000s as the space became crowded. |
| C6 | **IOSCO (2020, PD682) + AP-constraint ETF-arbitrage literature (Mar-2020)** | IOSCO public report + *JBF* (2025) · cred 4 · **verified** | **ETF tradability is not guaranteed in stress.** In Mar-2020, ETF prices dislocated from NAV (IG-bond ETFs ~3–8% discounts) because AP regulatory/leverage constraints broke the creation/redemption arbitrage. Demonstrates that **tight ETF spreads are NOT guaranteed in the high-VIX regimes this strategy trades** → cost models calibrated on calm periods understate execution risk when the gate is active. *(Equity sector ETFs dislocated far less than bond ETFs in Mar-2020 — see flags — but the mechanism is the concern.)* |

**Counted contradicting items (verified): 6 external** (C1–C6) **+ 2 internal** (vix_regime kill,
vol_scaled_momentum kill — see §5). The hard bar (≥ 1) is cleared many times over.

### The decay sub-argument, in one place (load-bearing)

Three independent threads say the *unconditional* premium is largely gone in liquid modern markets:
**Chordia-Subrahmanyam-Tong (anomalies halved post-2001)**, **Blitz et al. ("vanished entirely in
most regions," 2024)**, and the **HFT-dominance channel** (HFT ≈ >70% of US equity volume by ~2010,
performing most intraday market-making — Menkveld and the broader HFT literature; the >70% figure is
a widely-cited TABB/SEC estimate, cred 3). Nagel's own result that **industry reversal earns ≈ nothing
unconditionally** is the same message from the supporting side. **Net: the VIX gate is not an
enhancement — it is the ENTIRE strategy.** There is essentially no edge to harvest outside the gate.

---

## 3. Post-publication decay estimate

**Working haircut: apply a 50–60% reduction to any published-mechanism gross edge**, anchored on
the canonical base rate:

- **McLean & Pontiff (2016), *Journal of Finance* 71(1):5–32 [verified]:** across 82–97 predictors,
  returns are **~26% lower pre-publication-OOS** (an upper bound on data-mining) and **~58% lower
  post-publication**; implied publication-informed-trading decay ≈ 32%. Use **~58% post-publication**
  as the working prior for any *published* component.

**Component split (the key nuance for this idea):**

- **Unconditional 5-day reversal component → treat as effectively decayed to ~zero.** Multiple
  half-lives have elapsed since the 1990s data / 2012 publication; Blitz et al. (2024) corroborate
  empirically ("vanished"); HFT explains the channel. Nagel confirms industry reversal pays ≈ nothing
  unconditionally. **Expectation (reasoned, not backtested): the always-on sector reversal is
  near-zero net.**
- **High-VIX-CONDITIONED component → more durable, but NOT immune.** This is a *stress-state*
  liquidity premium that cannot be fully arbitraged because it requires balance-sheet/risk capacity
  exactly when intermediaries are constrained (Nagel's economic point). It is the part with a real
  reason to survive — **but the realized payoff is path-dependent, concentrated in the worst market
  states, and is ex-ante compensation for bearing the Aug-2007/Mar-2020 left tail, not a free lunch.**

**Net working estimate (EXPECTATION, labelled):** haircut the high-VIX-conditioned gross edge by
~50%. Be prepared for the result to land at the **low end of the platform's 0.4–0.8 per-strategy net
Sharpe band**, and to be at material risk of failing **Gate 1 (IS Sharpe < 0.5)** and/or **Gate 8
(Sharpe < 0 at 3× costs)** once conditioning + stressed costs are honestly applied. The effective
sample is **~half the calendar** (flat when VIX ≤ 60-day median), so the **high-VIX sub-sample MinBTL
is the binding statistical risk** (§5, gate 7).

---

## 4. Magnitude / transfer cautions the proposal MUST carry (not contradictions — burden of proof)

These temper the supporting case without negating the mechanism. They are the reasons a *real*
mechanism can still produce a *non-tradable* sector-ETF strategy.

1. **Magnitude/liquidity mismatch (Avramov-Chordia-Goyal 2006).** Premium concentrated in illiquid
   names; net ≈ costs even there. Sector ETFs are the most liquid instruments → **expect a small
   gross premium**; the whole bet rests on the VIX gate selecting the ~half of days when liquidity
   provision clears costs.
2. **Sector-level headwind (Da-Liu-Schaumburg 2014; Blitz et al. 2024; Moskowitz-Grinblatt 1999).**
   Raw reversal mixes in an **across-industry MOMENTUM** term that works *against* reversal at the
   sector level. We are **not isolating the clean liquidity-provision residual.** This is the single
   most important transfer risk **and** it is mechanically the same term as the monthly sector-
   momentum stream — reinforcing the |ρ| check vs `sector_rotation_v1`. **Proposal must pre-commit
   whether to neutralize/condition on short-term sector momentum, or accept it as a known drag.**
3. **Source-of-profit ambiguity (Lo-MacKinlay 1990).** With only 11 highly-correlated sector
   portfolios, profits may come from **cross-autocorrelation / lead-lag** structure rather than
   robust per-name liquidity provision; lead-lag is the channel most easily arbitraged and most
   likely to vanish net of costs in liquid ETFs. The P0 "must beat unconditional reversal" control
   only *partially* guards this.
4. **Tail risk = the trade (Khandani-Lo 2011).** Short-vol / short-liquidity / potentially crowded
   book; worst losses in the high-VIX states traded most. Discharges the burden that the prior-art
   fair-weather failure (`vol_scaled_momentum`) and the quant-quake explicitly demand.
5. **Data-channel honesty.** Della Corte's strongest leg is **overnight-vs-intraday**, which
   **daily-close-only data cannot capture**; Nagel/Lehmann/Da et al. are **single names**. So the
   located literature supports *mechanism + horizon + gate rationale*, **not** an ETF close-to-close
   Sharpe.

---

## 5. In-repo prior art (graveyard / pool / lessons — all paths verified on disk)

No prior verdict **pre-empts** this idea (S0 correctly adjudicated it a distinct mechanism), but
three in-repo records convert directly into S1/S3 requirements. Cited backtest numbers below are
**HISTORICAL results for OTHER strategies**, verified against the files on disk; they are NOT
predictions for `vol_conditioned_reversal`.

### (A) `vix_regime_2026-03-15_rejected` — nearest neighbor, NOT a duplicate
`.../research/strategies/vix_regime_2026-03-15_rejected/pm_review.md` (verified). Different
mechanism (VIX as *directional exposure scalar* vs VIX as *regime gate on cross-sectional reversal*).
Its three structural kills become **mandatory** here because the universe + VIX overlap guarantees
the PM's "is this just dressed-up vol timing?" challenge:
- **MinBTL = 3,968 yr** vs ~12.6 yr available (315× over); bootstrap CI **[-0.167, 0.824]** spans
  zero → Sharpe indistinguishable from chance. **This idea is MORE exposed: flat ~half the days, so
  the effective high-VIX sub-sample is far shorter than the ~14 yr local calendar. Estimate MinBTL
  on the CONDITIONAL sub-sample early in S2.**
- **Spanning alpha t = −0.18** after SPY+momentum → no independent alpha. Mirror requirement:
  independent spanning alpha **t ≥ 1.96** vs (a) unconditional reversal, (b) monthly momentum /
  `sector_rotation`, (c) a plain trailing-vol filter.
- **Dominated by a 21-day trailing-vol signal** on Sharpe (0.341 vs 0.299), MaxDD and turnover
  simultaneously (L6). Must **win head-to-head vs the simplest baselines in Round 1.**
- Cooling: rejected 2026-03-15; **90-day window ends exactly today (2026-06-13)** — but **moot**,
  because cooling binds resurrection of the *same* hypothesis, and this is a distinct mechanism.

### (B) `vol_scaled_momentum_2026-03-13_rejected` — most pointed verdict (contradicting)
`.../research/strategies/vol_scaled_momentum_2026-03-13_rejected/{pm_review.md,cerebro_briefing.md}`
(verified). Barroso VIX-conditioned decomposition: **Sharpe +2.255 in low-VIX vs −1.305 in high-VIX**
— a *fair-weather* fund that earned everything in calm markets and blew up in stress; alpha vs
equal-weight **−3.32%/yr** (L1); vol targeting did NOT fix crash risk (L3); IS/OOS 0.516→0.180.
**This idea claims the OPPOSITE direction** (profit *in* high-VIX) — the correct way out of the L3
fair-weather trap — **but that INVERTS the burden of proof onto high-VIX costs/turnover/tail.** The
net edge must survive **stressed, regime-dependent** spreads/impact at 25k–100k AUM and the left tail,
not flat average bps.

### (C) `sector_rotation_v1` (from `sector_rotation_2026-03-13_conditional`) — the |ρ| ≤ 0.4 peer
`.../research/strategies/sector_rotation_2026-03-13_conditional/proposal.md` +
`STRATEGY_TRACKER.md` (verified). The **only active pool peer**, SAME 11 SPDR sector ETFs, monthly
6-1 cross-sectional momentum + macro tilt. First review run **ee3a7b06** (2012→2026): **net Sharpe
0.84 vs EW 0.83, PSR 0.999, DSR 0.912 (< 0.95 → FAIL), MinBTL needs 4095d vs 3485 available (FAIL),
survives 3× costs → REVISE, state `candidate`.** Two takeaways:
- The **default promotion gates** are DSR ≥ 0.95, PSR ≥ 0.90, Sharpe > 0 at 2× cost, |ρ| ≤ 0.4,
  MinBTL < available. A Sharpe-0.84 monthly momentum on this universe over ~14 yr **already fails
  MinBTL** — a 5-day reversal flat half the days has an **even shorter effective sample**, so MinBTL
  is the single most likely kill.
- **Correlation gate is central.** Predicted ρ ∈ **[-0.3, +0.2]** (opposite sign, different duty
  cycle) → plausibly inside |ρ| ≤ 0.4, a genuine diversifier *if realized* — but **both are L/S on
  the same 11 sectors, so a sector-dispersion regime could co-move them. UNMEASURED; decided only by
  the engine.** Note the Da et al. / Blitz "across-industry momentum" headwind term in §4 IS this
  momentum stream — the same factor that drags the reversal is the peer we must decorrelate from.

### (D) Lessons L1–L7 + the DSR/MinBTL fix
`STRATEGY_TRACKER.md` (verified, lessons block + ee3a7b06 entry). Binding here: **L1** (benchmark
vs EW from R1); **L4** (VIX/VRP is a crisis signal, not standalone alpha — frames "the VIX gate must
add MEASURED value over unconditional reversal"); **L5** (overlays must ADD ≥ +0.15 Sharpe, not just
cut DD); **L6** (beat the simplest alternative — unconditional reversal + trailing-vol filter);
**L7** (daily rebalancing of regime signals → catastrophic turnover: vix_regime **2430%/yr daily →
916%/yr even weekly**). A 5-day reversal evaluated daily in high-VIX bursts is a direct **L7 hazard**
→ pre-commit a rebalance-frequency / no-trade-band design. Also confirmed: the **DSR/MinBTL math in
`stats/` was buggy and has since been fixed** (Bailey & López de Prado), so DSR/MinBTL are now
trustworthy gates and **n_trials must be declared honestly** (this VIX-gated reversal family — gate
threshold, lookback, horizon, momentum-neutralization on/off — represents multiple trials).

---

## 6. Crowding & capacity assessment

**Verdict: capacity is ADEQUATE at our AUM; crowding/decay of the unconditional edge is the real
problem.**

- **Capacity (Gate 10) likely PASSES comfortably.** At 25k–100k with a ~5-day horizon in the 11 SPDR
  sector ETFs — the **most liquid, tightest-spread** instruments on the tape (SSGA practitioner
  materials, cred 2, issuer source: Select Sector SPDRs carry the tightest/most-consistent spreads
  across vol regimes, ~12× the nearest competitor's volume) — we are **not competing at HFT latency**
  and the cost drag *at this size* is small under normal conditions. We will not move these markets.
- **Crowding at the FAST end is severe but not OUR competition.** HFT ≈ >70% of US equity volume
  (~2010) and performs most intraday market-making; this book was industrialized pre-2007 (Khandani-Lo).
  That crowding **compresses the intraday/sub-daily premium and the spreads that fund it**, and it is
  the source of the **forced-deleveraging tail** (Aug-2007). We trade slower, so we are not crushed by
  latency — **but we inherit the decay and the tail.**
- **The binding constraints are therefore (a) DECAY of the unconditional premium toward zero (§3) and
  (b) whether the high-VIX-conditioned residual survives deflation + 2×/3× stressed-cost gates on a
  half-length effective sample** — NOT capacity.
- **Stressed-cost caveat (C6, IOSCO/Mar-2020).** The gate trades when spreads are widest. Cost
  modeling MUST use a **volatility-conditional spread/impact**, not flat bps. Equity sector ETFs
  dislocated far less than bond ETFs in Mar-2020, but the direction of the bias is unambiguous.

---

## 7. Recommendation: **REVISE** (proceed to S2 against a narrowed, pre-committed spec)

**Why not ACCEPT_TO_S2 unconditionally:** the literature gives a strong *mechanism* but an explicitly
*weak magnitude* case at the ETF level, and three independent decay threads plus our own two kills say
the modal outcome is net Sharpe ≤ 0 at 2× costs (the P0 falsification condition). Letting an unscoped
proposal proceed would replicate the `vix_regime` / `vol_scaled_momentum` failure path.

**Why not REJECT:** the hard requirement is met decisively; the mechanism is genuinely distinct from
the nearest neighbor (cooling moot); Nagel specifically blesses *industry-portfolio* reversal
*conditional on high VIX*; the data exist (with named S2 tasks); capacity is fine at our AUM. There is
a real, falsifiable bet here — it has simply not earned the right to skip the burdens of proof.

**The S2 proposal is APPROVED to proceed ONLY IF it pre-commits ALL of the following (each maps to a
contradiction above; changing any later bumps `n_trials`):**

1. **Beat the gate's own null — pre-register TWO head-to-head baselines:** VIX-gated reversal vs
   **(i) unconditional reversal** (does the gate add Sharpe? — P0 predicate 2, L4) and **(ii) a plain
   trailing-vol filter** (is it just dressed-up vol timing? — the exact challenge that killed
   `vix_regime`, L6). Plus the standard **equal-weight** baseline (L1).
2. **Address the sector-momentum headwind explicitly (Da et al., Blitz et al.):** pre-commit whether
   to neutralize/condition on short-term sector momentum or accept it as a declared drag — and state
   why. This term is *also* the `sector_rotation_v1` peer, so it doubles as the |ρ| story.
3. **Volatility-conditional cost model (C1, C6):** stressed (regime-dependent) spread + impact at
   25k–100k AUM, evaluated at 1×/2×/3×; **not** flat average bps. Pre-commit a **rebalance-frequency /
   no-trade-band** design to defuse the L7 turnover hazard, and report turnover.
4. **MinBTL on the high-VIX SUB-sample, computed early (gate 7, the vix_regime kill):** the trade is
   flat ~half the days, so the effective sample backing the Sharpe is far shorter than ~14 yr — show
   it can clear MinBTL on the conditional sample, or accept this as the most likely kill up front.

**Additional must-measure (engine, not proposal):** independent **spanning alpha t ≥ 1.96** vs
unconditional reversal + monthly momentum + trailing-vol filter; **|ρ| ≤ 0.4 vs `sector_rotation_v1`**
(predicted [-0.3,+0.2], UNMEASURED); **left-tail diagnostics conditional on VIX > median** (skew,
worst-week, MaxDD, the Aug-2007/Mar-2020 days); **DSR ≥ 0.95 / PSR ≥ 0.90** with honestly-declared
`n_trials`. **Data prerequisites (from S0):** refresh `^VIX` or switch to FRED `VIXCLS` (decide the
same-day-close vs 1-day-lag convention); enforce the **dynamic universe** (9 sectors pre-2015, 10 to
2018, 11 after — never backfill XLC/XLRE); confirm consistent total-return/split adjustment.

> **Bottom line for the owner:** A well-motivated, genuinely diversifying *candidate* with a real
> economic mechanism and a clean distinction from prior kills — but whose entire edge lives inside a
> VIX gate, on a heavily-decayed unconditional base, at the most liquid (lowest-premium) layer of the
> asset class, carrying a short-liquidity tail that detonates in the exact regime it trades. **Proceed
> to S2 only against the four pre-commitments above.** The disciplined expectation is a low-end-of-band
> net Sharpe with a non-trivial probability of dying at MinBTL or the 2×/3× cost gate — exactly the
> outcome the rigor battery exists to surface before capital is committed.

---

## 8. Verification & honesty flags (read before citing downstream)

- **Verified peer-reviewed (cred 4–5), safe to cite:** Nagel 2012 (RFS); Lehmann 1990 (QJE);
  Hameed-Kang-Viswanathan 2010 (JF); Da-Liu-Schaumburg 2014 (Mgmt Sci); Avramov-Chordia-Goyal 2006
  (JF); de Groot-Huij-Zhou 2012 (JBF); Chordia-Subrahmanyam-Tong 2014 (JAE); Khandani-Lo 2011 (JFM,
  NBER w14465); McLean-Pontiff 2016 (JF); Lo-MacKinlay 1990 (RFS); Blitz-van der Grient-Honarvar 2024
  (JPM, SSRN 4575689).
- **Verified but NOT peer-reviewed — flag in the proposal:** Della Corte-Kosowski-Liu-Wang
  "Overnight–Intraday Reversal Everywhere" (working paper, established authors; **strongest leg is
  overnight/intraday which our daily-close data cannot use**).
- **Single-source / re-derive before quoting a number:** the **decimalization-decay magnitude**
  (~5.5 bps/mo, t≈11 pre-2000) comes from a **secondary USU graduate report (cred 3)** — directionally
  consistent with the peer-reviewed Chordia et al. attenuation result, but the *figure* must be
  re-derived, not quoted as authoritative. The **de Groot "30–50 bps/week net large-cap" number** is
  the authors' widely-reported headline; one finder could **not** extract it from clean full-text
  (403s / encoded PDFs) — treat as headline, not independently re-verified. The **HFT ">70% of volume"**
  figure is a widely-cited TABB/SEC estimate (cred 3), not a single peer-reviewed primary source.
- **Counter-counter surfaced by ONE finder, only PARTIALLY verified — do NOT rely on it without
  S2 verification:** Dai, Medhat, Novy-Marx & Rizova (attributed *FAJ* 2024 / NBER w30917) arguing
  reversals ARE a robust, persistent liquidity-provision return when **conditioned on volatility**
  (faster/stronger reversals in high-vol) and turnover. This is the **strongest pro-idea evidence and
  would even rationalize the high-VIX gate**, but it was surfaced by a single finder, the exact
  cite/venue was not cross-verified here, and it is again a **single-stock, low-turnover,
  breadth-dependent** result. **Verify the cite and read it before leaning on it in S2.**
- **NOT promoted from S0:** the S0 `hypothesis.md` cited a "Drechsler/Moreira/Savov-or-related, JBF
  2022" cost-of-immediacy paper whose **exact author list was explicitly not re-verified at S0** and
  which **no S1 finder independently surfaced**. It is **excluded** from this briefing's verified set;
  the decay/cost-erosion case stands without it (Avramov-Chordia-Goyal, de Groot et al., Chordia et
  al., Blitz et al.). Re-verify before any S2 citation.
- **Repo housekeeping (verified):** the referenced `memory/LESSONS_LEARNED.md` and
  `memory/knowledge/KNOWLEDGE_*.md` files do **not** exist on disk — the working lessons source is the
  **L1–L7 block in `STRATEGY_TRACKER.md`**. The `graveyard/` directory holds only `README.md` (no
  per-kill files yet); pre-factory kills are tracked in that table. All `pm_review.md` /
  `proposal.md` paths cited in §5 were confirmed present.
- **No backtest numbers for THIS strategy exist.** ee3a7b06 (Sharpe 0.84), the vix_regime gate table
  (MinBTL 3,968 yr, t = −0.18), and the vol_scaled_momentum decomposition (+2.255 / −1.305) are
  **historical results for OTHER strategies**, used only as calibration for the battery on this exact
  universe.

---

### Counts (honest, verified-only)
- **Supporting papers counted:** 5 (Nagel 2012; Lehmann 1990; Hameed-Kang-Viswanathan 2010;
  Da-Liu-Schaumburg 2014; Della Corte et al. ≈2023). Hard bar (≥ 2): **MET.**
- **Contradicting studies / documented failure modes counted:** 6 external (Avramov-Chordia-Goyal;
  de Groot-Huij-Zhou; Chordia-Subrahmanyam-Tong; Blitz et al.; Khandani-Lo; IOSCO/Mar-2020 AP) + 2
  internal (vix_regime kill; vol_scaled_momentum kill) = **8.** Hard bar (≥ 1): **MET with margin.**
- **Briefing validity:** **VALID.** Recommendation: **REVISE → proceed to S2 against the four
  pre-commitments in §7.**
