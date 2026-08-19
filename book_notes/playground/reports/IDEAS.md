# IDEAS — the accumulating pool

> **This file is the `mechanism` layer of the [research second brain](../brain/README.md)** — it
> stays here rather than under `brain/` because 105 digest back-links point at it and the IDs are
> permanent. Its companions: [`brain/concepts/`](../brain/concepts/) holds the machinery these
> mechanisms are built from, [`brain/VERDICTS.md`](../brain/VERDICTS.md) holds what we actually tried,
> and [`brain/INBOX.md`](../brain/INBOX.md) is where an unclassified thought goes. Historical naming:
> `IDEA-NNN` means *mechanism*.

> **Stage 1 of 3. Nothing here is validated.** This file accumulates ideas and methodologies that
> make *initial* sense, harvested from the report digests in this library. Selection on economic
> merit is **stage 2**; validation, backtesting and rigor gates are **stage 3**
> (`alpha_research/research/`). See the purpose statement in [`INDEX.md`](INDEX.md).

> **Testability is a score, never a gate.** Ideas that cannot be tested on this platform today are
> kept, with the gap recorded. **Every entry is a transferable mechanism, not a house call** — if it
> could not be applied to a different market next year, it does not belong here.

*46 ideas from 10 reports, pooled from 57 raw candidates after 10 merges. Generated 2026-08-04; last pass 2026-08-15 (re-digest of `flows_gs_cta-bond-futures_2026-06-09` — one candidate merged into [IDEA-028](#idea-028) as a third source, one refinement recorded on [IDEA-010](#idea-010); **no new IDs, no renumbering, no score changes**, so the summary table below is unchanged). Interconnection pass 2026-08-17 — the citation network was made navigable (idea-to-idea, entry-to-digest, digest-to-pool, plus outward links to papers, studies and platform code) and nine mis-pointed cross-references were repaired; again **no score, wording or ranking changes**. See [How the pool interconnects](#how-the-pool-interconnects) to navigate it and the Calibration record for the repair list.*

---

## How to read a score

| | 5 | 3 | 1 |
|---|---|---|---|
| **Economic rationale** | names a counterparty who *must* trade, or a clearly compensated risk | plausible story, no identified payer | pattern with no mechanism |
| **Durability** | structural — mandates, regulation, plumbing on decade clocks; or an arithmetic identity | holds within a policy regime | likely arbitraged, or regime-bound with no way to detect the regime ending |
| **Testability** | data already in the lake | reachable public source | needs proprietary data (swaption vols, dealer inventory, OIS strips) |

`Total` is the unweighted sum (3–15) and is a **sorting convenience, not a verdict** — at stage 2 you
will weight these deliberately. An idea scoring 5/5/1 is not worse than one scoring 4/4/3.

**`IDEA-0NN` is a permanent handle, not a rank.** Digests cite these IDs, so an idea keeps its number
for life; re-scoring changes where it *sorts*, never what it is called. New ideas take the next unused
number wherever they land. Run `python3 scripts/check_ideas_integrity.py` after any pass that edits
this file — it verifies IDs are unique and anchored, the table matches and is sorted, scores sum to
their stated totals, and every cross-reference in the library resolves. Since 2026-08-17 it also
verifies that a cited ID **matches the slug the sentence describes** (a resolving ID pointing at the
wrong entry is the failure that survived two earlier passes), that anchor links point at their own id,
that `*related:*` edges are reciprocal, and that every relative link in the library is live.

---

## The pool at a glance

| # | Type | Idea | Econ | Dur | Test | Total |
|---|---|---|:--:|:--:|:--:|:--:|
| [001](#idea-001) | `regime` | **stock-bond-correlation-is-the-position-and-the-regime** | 5 | 5 | 5 | **15** |
| [002](#idea-002) | `structure` | **structure-geometry-vs-stated-view** | 5 | 5 | 4 | **14** |
| [003](#idea-003) | `method` | **moments-must-match-the-premium** | 4 | 5 | 5 | **14** |
| [004](#idea-004) | `method` | **risk-contribution-vs-capital-weights** | 4 | 5 | 5 | **14** |
| [005](#idea-005) | `signal` | **issuance-mix-taper-sector-loser** | 5 | 5 | 3 | **13** |
| [006](#idea-006) | `signal` | **mandate-rebalancing-is-contrarian-flow** | 5 | 5 | 3 | **13** |
| [007](#idea-007) | `regime` | **term-premium-not-risk-neutral-transmission** | 5 | 5 | 3 | **13** |
| [008](#idea-008) | `structure` | **leverage-aversion-premium** | 5 | 4 | 4 | **13** |
| [009](#idea-009) | `regime` | **hedge-efficacy-scales-with-crash-duration** | 4 | 5 | 4 | **13** |
| [010](#idea-010) | `risk` | **publication-date-ends-the-in-sample** | 4 | 5 | 4 | **13** |
| [011](#idea-011) | `risk` | **official-fx-reaction-function-overlay** | 4 | 4 | 5 | **13** |
| [012](#idea-012) | `risk` | **trailing-window-buffer-undersizing** | 4 | 4 | 5 | **13** |
| [013](#idea-013) | `method` | **mechanical-replicant-as-fee-and-skill-audit** | 5 | 4 | 3 | **12** |
| [014](#idea-014) | `signal` | **reserve-satiation-crossing** | 5 | 4 | 3 | **12** |
| [015](#idea-015) | `signal` | **effective-vs-marginal-rate-refi-runway** | 4 | 5 | 3 | **12** |
| [016](#idea-016) | `regime` | **flat-balance-sheet-is-tightening** | 4 | 5 | 3 | **12** |
| [017](#idea-017) | `signal` | **capital-structure-valuation-wedge** | 4 | 4 | 4 | **12** |
| [018](#idea-018) | `method` | **effective-breadth-discount-for-self-correlated-strategies** | 3 | 5 | 4 | **12** |
| [019](#idea-019) | `method` | **selector-must-span-total-expected-return** | 2 | 5 | 5 | **12** |
| [020](#idea-020) | `structure` | **buy-convexity-back-inside-the-risk-factor** | 5 | 4 | 2 | **11** |
| [021](#idea-021) | `signal` | **administered-price-cpi-wedge** | 4 | 4 | 3 | **11** |
| [022](#idea-022) | `method` | **forced-flow-response-function** | 4 | 4 | 3 | **11** |
| [023](#idea-023) | `structure` | **funding-leg-as-first-order-choice** | 4 | 4 | 3 | **11** |
| [024](#idea-024) | `method` | **horizon-match-regressors-to-instrument** | 3 | 5 | 3 | **11** |
| [025](#idea-025) | `method` | **sharpe-gain-is-diversification-not-leverage** | 3 | 5 | 3 | **11** |
| [026](#idea-026) | `risk` | **annualise-the-level-claim-against-the-competing-rate** | 3 | 4 | 4 | **11** |
| [027](#idea-027) | `method` | **risk-attribution-selects-hedge-instrument** | 3 | 4 | 4 | **11** |
| [028](#idea-028) | `method` | **decompose-the-headline-aggregate** | 2 | 5 | 4 | **11** |
| [029](#idea-029) | `regime` | **real-rate-buffer-supply-shock-reaction** | 4 | 4 | 2 | **10** |
| [030](#idea-030) | `signal` | **wam-drift-reveals-tenor-demand** | 4 | 4 | 2 | **10** |
| [031](#idea-031) | `regime` | **direction-of-travel-conditioning** | 4 | 3 | 3 | **10** |
| [032](#idea-032) | `method` | **base-rate-override-tell** | 3 | 4 | 3 | **10** |
| [033](#idea-033) | `method` | **fair-value-residual-not-level-zscore** | 3 | 4 | 3 | **10** |
| [034](#idea-034) | `structure` | **positive-carry-hedges-survive-the-committee** | 3 | 4 | 3 | **10** |
| [035](#idea-035) | `method` | **retail-access-revealed-preference-test** | 3 | 4 | 3 | **10** |
| [036](#idea-036) | `signal` | **threshold-proximity-dispersion** | 3 | 3 | 4 | **10** |
| [037](#idea-037) | `signal` | **tsmom-12m-sign-vol-scaled-cross-asset** | 3 | 3 | 4 | **10** |
| [038](#idea-038) | `method` | **ois-strip-level-vs-pace** | 2 | 5 | 3 | **10** |
| [039](#idea-039) | `method` | **backstop-censors-the-tail** | 3 | 4 | 2 | **9** |
| [040](#idea-040) | `regime` | **positioning-saturation-one-sided-flow** | 3 | 3 | 3 | **9** |
| [041](#idea-041) | `risk` | **count-independent-estimates-not-outputs** | 2 | 5 | 2 | **9** |
| [042](#idea-042) | `method` | **free-float-denominator-and-market-specific-beta** | 3 | 3 | 2 | **8** |
| [043](#idea-043) | `method` | **publisher-credibility-ledger** | 2 | 3 | 3 | **8** |
| [044](#idea-044) | `regime` | **sentiment-extreme-needs-driver-check** | 2 | 3 | 3 | **8** |
| [045](#idea-045) | `regime` | **premium-scales-with-priced-dispersion** | 2 | 1 | 3 | **6** |
| [046](#idea-046) | `structure` | **calendar-clustered-trigger-resolution** | 1 | 2 | 2 | **5** |

**Composition:** 9 signal · 17 method · 9 regime · 5 risk · 6 structure

---

<a id="how-the-pool-interconnects"></a>
## How the pool interconnects

*Every entry carries an edge block under its `*applies to:*` line — `*related:*` to other ideas,
and where they exist `*literature:*` (paper notes), `*study:*` (book studies) and `*platform:*`
(the code or strategy the idea bears on). The relations are read off the merge record, the
deliberate non-merges and the entries' own reasoning; they are not topic similarity.*

**Shape.** 83 reciprocal relations across the 46 ideas — every edge navigable from both ends, every
idea connected (degree 2–6), and the pool is **one single component**, not clusters of unrelated
readings. Six hubs carry degree 6: [IDEA-003](#idea-003) (moment matching),
[IDEA-018](#idea-018) (effective breadth), [IDEA-020](#idea-020) (convexity inside the factor),
[IDEA-026](#idea-026) (annualise the level claim), [IDEA-031](#idea-031) (direction of travel),
[IDEA-042](#idea-042) (free float). That these six are all *methods* rather than signals is the same
finding the calibration record reaches from the score distribution — this pool is long durable
method and short durable signal.

**Edge kinds.** `contrast` / `not merged` marks ideas deliberately kept apart, and those are the
load-bearing ones — they record a distinction someone already had to think through
([IDEA-005](#idea-005) vs [IDEA-006](#idea-006) carry opposite flow signs and must never be
aggregated; [IDEA-018](#idea-018) vs [IDEA-041](#idea-041) differ by having a code path).
`tension` marks pairs that discipline each other ([IDEA-042](#idea-042) shrinks
[IDEA-005](#idea-005)'s own 3–6bp claim to ~1.2bp). Everything else names the direction of
dependence in plain words.

**The six families.** A reading order for anyone entering the pool cold:

| Family | Ideas | What holds it together |
|---|---|---|
| Balanced-portfolio construction | [001](#idea-001) [004](#idea-004) [008](#idea-008) [025](#idea-025) [022](#idea-022) [009](#idea-009) [034](#idea-034) | Every diversification claim is an unpriced correlation position, and the financing leg is where the claimed edge is not |
| Evaluation statistics & research epistemics | [003](#idea-003) [018](#idea-018) [010](#idea-010) [013](#idea-013) [041](#idea-041) [019](#idea-019) [043](#idea-043) [032](#idea-032) [037](#idea-037) [028](#idea-028) | What a statistic can and cannot see, and how many independent estimates sit behind a number |
| Central-bank plumbing & free float | [014](#idea-014) [016](#idea-016) [042](#idea-042) [005](#idea-005) [030](#idea-030) [007](#idea-007) [039](#idea-039) [012](#idea-012) | Reserves, issuance calendars and price-insensitive holders — measured in the unit that binds |
| Carry, convexity & direction of travel | [020](#idea-020) [031](#idea-031) [033](#idea-033) [045](#idea-045) [024](#idea-024) [023](#idea-023) [026](#idea-026) [011](#idea-011) [002](#idea-002) | The same level is two states depending on how you got there, and the tail is bought back inside the factor |
| Positioning & forced flow | [006](#idea-006) [022](#idea-022) [036](#idea-036) [040](#idea-040) [046](#idea-046) [035](#idea-035) | Who must trade, in which direction, and whether they have room left |
| Macro measurement wedges | [015](#idea-015) [021](#idea-021) [028](#idea-028) [038](#idea-038) [029](#idea-029) [017](#idea-017) [027](#idea-027) [044](#idea-044) | Split the arithmetic part from the behavioural part before treating a print as information |

*Families are a reading aid, not a partition. [022](#idea-022) (forced flow) and
[028](#idea-028) (decompose the aggregate) each sit in two, and the `*related:*` edges cross family
lines freely — which is why the graph is one component rather than six.*

---

## Essence of each report

*What the report fundamentally says once the house view is stripped out, and the lesson that outlives the call.*

### 2012 · factor_bridgewater_risk-parity_2012

- **In one line:** A 60/40 portfolio is not a diversified portfolio but a levered equity bet in disguise — roughly 90% of its risk is equities — so balance must be defined on risk contribution across macro environments and reached with leverage, not on capital weights.
- **Core mechanism:** Because equity volatility is about 3x bond volatility, capital weights systematically misdescribe risk weights; equalizing risk contribution across the growth x inflation quadrants and levering the low-vol sleeves removes the single-regime concentration that makes 60/40 fragile. The entire construction is collateralized by one unstated assumption — that the stock-bond correlation stays near its historically negative value.
- **Market:** Cross-asset / multi-asset allocation: US equities, nominal government bonds, inflation-linked bonds, commodities
- **Load-bearing number:** Equity volatility is approximately 3x bond volatility, which implies approximately 90% of a 60/40 portfolio's risk sits in equities
- **What it teaches:** Measure the exposure you actually hold, not the one your weights are labelled with — and recognize that every diversification claim is an implicit correlation position. Name that position, name the macro state that flips its sign, and you have converted a framework argument into a testable, stress-able construction. Also: a note that presents only descriptive statistics (vol ratios, taxonomies, quadrant maps) and no inferential ones is telling you where its author declined to look.

### 2013 · factor_aqr_managed-futures_2013

- **In one line:** Nearly all managed-futures returns are one mechanical rule — long/short each market on the sign of its trailing 12-month return, sized to constant volatility, aggregated across four asset classes — and that rule paid across 67 markets and 135 years while doing best in the deepest equity drawdowns.
- **Core mechanism:** A deliberately slow signal only flips after a move has already persisted for months, so the same latency that bleeds money in choppy markets converts protracted repricings into profit; volatility scaling makes ~67 weakly-related versions of that same bet combinable into one portfolio, and the resulting ensemble — not manager skill — is what the CTA industry sells at hedge-fund fees.
- **Market:** Cross-asset futures (equity index, government bond, FX, commodity) and the managed-futures / CTA industry as an asset class
- **Load-bearing number:** R^2 > 0.9 from regressing CTA index monthly returns on the synthetic vol-scaled 12-month TSMOM strategy (dimensionless); the supporting numbers are Sharpe ~0.7 over 1880-2012 and ~0.9 post-1985, net of estimated transaction costs.
- **What it teaches:** When a strategy has no identifiable counterparty paying for it, its credibility has to be bought two ways: with sample breadth (independent markets and regimes) and with a mechanism deducible from the rule's own construction. The deeper lesson is that both are double-edged here — the slow signal that gives trend its crisis hedge value also makes that hedge conditional on crash *duration*, and the correlated cross-market positioning that produces crisis alpha is exactly what shrinks 67 markets x 135 years to far fewer effective independent observations. Separately: always price an active industry against the cheapest mechanical replicant of it, and read a vendor's publication date as the end of the in-sample period.

### 2025/11 · rates_gs_vol-strategies_2025-11-13

- **In one line:** Selling rates volatility harvests a real 10-20% implied-over-realized premium, but it cannot be timed off how cheap or rich implied vol looks against its own history — only against a fundamentals-implied fair value, and only when vol is both rich and already falling; and the resulting short-convexity payoff must be paired with long convexity and judged on its tail rather than its Sharpe.
- **Core mechanism:** End users structurally overpay for crash protection, so implied vol exceeds subsequently-realized vol by 10-20%; but the *level* of implied vol is itself 70-85% explained by observable macro fundamentals (consensus forecast dispersion for growth/inflation/policy, plus distance from the neutral policy rate), so a level-based valuation signal is mostly measuring fundamentals and only faintly measuring the premium. The harvestable edge is the residual from that fair value, and its size is state-dependent on how much path uncertainty the forward curve is currently pricing.
- **Market:** Rates volatility — USD/EUR/GBP/JPY swaptions (delta-hedged ATM straddles, 1m-10y expiries x 2y-30y tails), 2003-2025 sample; plus vol-carry as a multi-asset overlay benchmarked against equities, Treasuries and 60/40.
- **Load-bearing number:** Return-to-vol ratio ~1.9 in the richest-and-falling quintile vs ~0.2 in the cheapest quintile (Exhibit 13; delta-hedged straddle selling, subsequent 3-month returns, 2003-2025). Everything the report recommends over a naive always-on vol-selling program rests on this ~9x spread. Runner-up: adj. R^2 of 0.7-0.85 for the macro fair-value regression at short expiries.
- **What it teaches:** A valuation signal is only as good as the fair-value model sitting behind it. Z-scoring a level against its own history silently assumes fair value is constant — false whenever the level is driven by observable, slow-moving fundamentals, in which case the z-score measures the fundamentals and not the premium. Second lesson: derive the strategy's P&L identity before choosing its evaluation statistic; a payoff quadratic in a state variable is mechanically asymmetric, and mean-variance statistics are structurally blind to exactly the risk that differentiates it.

### 2026/01 · economics_gs_japan-outlook_2026-01-06

- **In one line:** Stripped of the house call, this is a note about mechanically-driven numbers masquerading as fundamentals: a fiscal ratio improving on legacy coupon arithmetic, a growth rate 'decelerating' on base effects, and an inflation path bent below target by legislated price cuts — none of which say what they appear to say.
- **Core mechanism:** The debt-dynamics identity D_t/Y_t − D_{t-1}/Y_{t-1} ≈ (r−g)·D/Y − PB/Y, where r is the *effective* rate on outstanding debt (interest paid ÷ debt stock), not the marginal market rate. A large stock of long-dated ultra-low-coupon JGBs keeps r far below both nominal growth and current market yields, so debt/GDP falls automatically and independently of the primary balance — until that stock refinances at today's rates over the next 10–15 years, at which point the 'natural decline' disappears with no policy change at all.
- **Market:** Japan macro — JGBs, USD/JPY, BOJ policy path. The transferable machinery applies to any post-ZIRP sovereign and to any corporate issuer that termed out debt at 2020–21 coupons.
- **Load-bearing number:** r − g = 3.1pp (FY2025 effective government interest rate 0.8% vs nominal GDP growth 3.9%, the widest gap since 1980), which mechanically delivers ≈ −7pp/year of debt/GDP decline and is the sole support for the 'fiscal soundness holds' headline.
- **What it teaches:** Before treating any macro or fiscal ratio as information, split it into the arithmetic part (stock/coupon effects, statistical carryover, legislated one-offs, survey methodology changes) and the behavioural part. The arithmetic part is forecastable from public calendars and carries zero information about the future — yet it is what headlines and reaction functions respond to. Second lesson: count the *estimated* nodes in a forecast tree, not the conclusions. A note with three pillars resting on one regression has one pillar, and positions expressing those three pillars are one position.

### 2026/04 · macro_gs_jpy-macro-trading_2026-04-07

- **In one line:** When a central bank tapers its bond purchases while the sovereign changes its issuance mix, the publicly announced calendar tells you which specific curve sector loses its price-insensitive buyer — and that sector-level supply/absorption arithmetic out-forecast a demand-side macro model by 67bp of 10y yield over seven months.
- **Core mechanism:** Sector-specific supply/absorption imbalance rather than a level view: cutting ultra-long issuance by more than mandated life-insurer buying capacity structurally over-bids the 40y, while rinban tapering and liquidity-tap reallocation push net supply into the 10y, which unlike the 2y has no already-priced hike cushion — so the 10y must cheapen against both neighbours regardless of where the policy rate ends up. Everything else in the note (swap spreads, meeting-OIS steepeners, payer structures, short JPY) is the same short-belly position re-expressed, levered to an asserted equilibrium real rate.
- **Market:** JGBs and JPY rates/FX — 10y cash and swap sector, 10s40s and 2s10s40s curve, 5y/10y asset swap spreads, BoJ meeting-dated OIS, USD/JPY spot and JPY swaptions
- **Load-bearing number:** 43bp — the gap between the desks' 1.75% BoJ terminal rate (an asserted r* of -0.25%) and the ~1.32% implied by the Jan-2027 meeting-dated OIS, i.e. ~1.7 unpriced hikes. Seven of the twelve trades are levered to this one unestimated parameter. The auditable counterpart is the supply arithmetic: a 0.75trn JPY/month ultra-long issuance cut against a 0.6trn JPY/month maximum lifer absorption pace.
- **What it teaches:** Score a sell-side note's direction and its packaging separately — the direction call is free for the dealer to publish and was right twice, while the structures (zero-cost payer ladder capped at 10bp, delta-exchanged receivers with a breakeven above two of the three realized-vol regimes the desk itself measured, a range-accrual citing 'competitive GS funding level') are inventory and at least one caps the very view it claims to express. Second: public plumbing quantities — issuance calendars, taper schedules, mandated-buyer capacity — can beat a demand-side macro forecast on RELATIVE sector performance even when nobody can forecast the level. Third: a clean mechanism that has not moved the price for ten months is evidence the mechanism is not the marginal driver, and restating it is not analysis.

### 2026/05 · rates_gs_fed-balance-sheet_2026-05-21

- **In one line:** A central bank's monetary stance is set by reserves relative to *bank* balance sheets, not by the size of its own — and because currency, the Treasury's cash account and the banking system all grow with nominal GDP, the balance sheet must expand ~\$25bn/month just to hold reserves constant, so 'flat' is a tightening and the shrink debate is really a one-time level question dressed up as a flow question.
- **Core mechanism:** Reserves are the residual claim on the central bank's asset side after autonomous, nominal-GDP-linked liabilities (currency in circulation, the government's cash account) are satisfied, while regulated banks' demand for reserves scales with their own assets and turns inelastic near satiation. The price of overnight secured funding relative to the policy floor (tri-party GC repo minus IORB) is the observable that reveals where that satiation point sits — which is why the whole analytical edifice rests on one regression of that spread on reserve supply.
- **Market:** US rates — front-end funding (tri-party GC repo vs IORB), T-bills, Treasury duration and 2s10s; generalizes to any central-bank reserve system (ECB, BoJ, EM central banks with fast currency growth).
- **Load-bearing number:** \$25bn/month (\$300bn/yr) of steady-state Fed asset growth required merely to hold reserves at 11% of bank assets — independently reconciled at \$24.2bn/mo on live FRED inputs (\$9.06bn currency + \$10.59bn bank-asset matching + \$4.55bn TGA).
- **What it teaches:** Measure policy in the units of the constraint that actually binds (reserves ÷ bank assets), not the units of the press release (total assets) — the two are near-uncorrelated week to week. And when a stress spread normalizes in the same window that a backstop facility was widened, the parameter is unidentified: 'how much room is there' silently becomes 'how far can we lean on a facility never tested at scale.' The corollary is that any estimate of resilience, or any tail hedge priced off history, must be dated against the backstop regime that generated the sample.

### 2026/06 · flows_gs_cta-bond-futures_2026-06-09

- **In one line:** Stripped of the call, this note says the useful object in a positioning read is not the estimated position level but the shape of the conditional flow response — how much a rule-bound cohort must buy or sell under each price path — and that shape just collapsed from one-sided to two-sided.
- **Core mechanism:** Trend-following funds trade by pre-committed rules on price versus momentum thresholds under a volatility target, so given an estimate of their current position their future flow is a near-deterministic function of the price path; when the position sits at its risk-budget bound and a market sits close to its threshold, the forward flow distribution becomes one-sided and the resolution of that state is clustered on the public macro calendar.
- **Market:** Global government bond futures — UST (TU/FV/TY/US), Bund/Bobl/Schatz (RX/OE/DU), long Gilt, JGB; systematic positioning and flow, not fundamental rates valuation
- **Load-bearing number:** 1-month base-case projected CTA flow: +\$36.7m DV01 → −\$3.8m DV01 week-over-week (a ~\$40.5m DV01 swing, and a sign flip). Every conclusion in the note is that sign flip; the −\$128.9m DV01 net position level is only the stock it is measured against. ⚠️ **This number does not reconcile to its own components — flagged 2026-08-11, resolved 2026-08-15.** The nine per-contract figures the note publishes for that same 1-month base case (TU −1.0, FV +0.0, TY +3.0, US +2.7, RX −2.2, OE −2.2, DU −1.9, Gilt −2.1, JGB +3.5) sum to **−\$0.2m**, not −\$3.8m. Extending the check to all four published scenario cells settles what kind of gap it is: residuals of +\$0.4m (1wk base, 9% of headline), +\$10.3m (1wk Up, 50%), −\$3.6m (1mo base, 95%) and +\$24.5m (1mo Up, 18%) — **every one sign-matched to its headline and scaling with the scenario**, which is the signature of an omitted market set rather than an arithmetic error (Figure 1 is captioned "by Country/Region" while the prose names only nine contracts). So the note is internally consistent and *less* usable than that sounds: in the only cell where the full named set is published it sums to flat, and **≈95% of the load-bearing −\$3.8m is supplied by markets never identified.** The 1-week figure (+\$11.9m → +\$4.5m, 91% attributed) is the better-supported half.
- **What it teaches:** Three things outlive the call. First: for any cohort whose trading rule you can approximate and whose capacity is bounded, model the flow response function (∂position/∂price across scenarios and horizons), not the position — the level is a stock that tells you nothing about what happens next, the derivative is the tradable object. Second: this note reports six scenario numbers descending from one undisclosed model, so it contains one piece of evidence, not six. Count independent models, never numbers. Third *(added 2026-08-11)*: **conditional flow is convex in distance-to-trigger.** The note's own grid shows the US leg contributing ~nothing in the base case yet supplying the single largest Up-scenario flow (US +29.6m, above every European contract) — because the distance a laggard must traverse to reach its trigger is also the size of the position that must be covered when it does. The modal path and the tail rank the same markets in opposite order, so "quiet" and "low risk" are not the same statement. The desk never draws this out; it is the most reusable thing in the note. Standing corollary, sharpened 2026-08-15: **always sum a published breakdown against its own headline, then test the residual.** Summing is the free integrity check; the residual's *sign coherence across cells* is what tells you whether you are looking at an error (discard) or an omitted component set (keep the claim, discount it by the unattributed fraction). Here it is the latter, and the unattributed fraction of the note's conclusion is ~95%.

### 2026/07 · crossasset_gs_goal-kickstart_2026-07-27

- **In one line:** When the identified source of drawdown risk is valuation rather than deteriorating growth, and when compensation for corporate risk is unevenly distributed across the capital structure, the right response is to change the *instrument* of risk-taking (convexity, uncapped claims, non-bond diversifiers) rather than the *level* of it.
- **Core mechanism:** Risk-taking capacity is high and fundamentally supported (growth factor elevated, policy/dollar factors neutral), while the price of bearing corporate risk is asymmetric across the capital structure: credit spreads sit in their richest decile because mandate-constrained buyers must own them, while equity multiples sit near their median. Because the flagged drawdown risk attributes to valuation — a persistent level with no timing content and an exogenous trigger — a linear short bleeds and time-limited convexity is the efficient expression, whereas growth-attributed risk would trend and justify simply cutting exposure.
- **Market:** Cross-asset tactical allocation — global equities, US/EUR IG and HY credit, government bonds, USD/JPY, oil; expressed via index options and FX options.
- **Load-bearing number:** The capital-structure valuation wedge: IG/HY spreads at the 91st-98th historical percentile (US HY 279bp, EUR HY 256bp) against S&P 500 12m forward P/E at the 58th percentile (19.8x) — roughly a 35-40 percentile-point gap, on which the entire underweight-credit / equity-via-convexity stance rests. Second load-bearing item: the ~20-25% probability of a >20% 12m S&P drawdown attributed almost wholly to the valuations bucket.
- **What it teaches:** Two things outlive the call. First: the *attribution* of a risk estimate, not its level, determines the correct hedging instrument — a 20% drawdown probability sourced from valuation and one sourced from a growth downturn call for opposite trades (convexity vs beta reduction). Second: when two claims on the same underlying cash flows are priced at very different percentiles of their own histories, the gap is usually manufactured by buyers who are mandated into one of them and cannot substitute — so take the risk in the instrument where you are actually paid for it.

### 2026/07 · flows_gs_japan-savings-jgb-demand_2026-07-20

- **In one line:** Japan's two savings-repatriation measures cannot reprice the JGB curve, because the mechanical rebalancing flow GPIF already runs (~JPY17tn/yr) exceeds the entire discretionary room the policy would unlock, and whatever price effect exists is delivered over 2-4 years at a rate hundreds of times smaller than the market's weekly noise.
- **Core mechanism:** A benchmark-band-constrained asset owner's flow is a mechanical function of relative sleeve returns, not of policy intent, so an announced 'reallocation' supplies signalling rather than new quantity; the price effect is then just (incremental purchase / free float) x an estimated supply-sensitivity beta, spread over the horizon implied by the observed 1-2ppt/yr adjustment speed — which collapses it to 0.014-0.058bp/week against 8bp/week of realised movement.
- **Market:** JGBs / JPY rates — 30y JGB swap spreads (asset swaps), 20y/30y cash JGBs, USD/JPY; generalises to any sovereign bond market with a large statutorily benchmarked domestic asset owner (NBIM, NPS, Dutch pensions, SOMA-adjacent free-float questions).
- **Load-bearing number:** USD 75bn of incremental GPIF JGB purchases (4ppt of a USD 2.8tn portfolio) mapped to 3-6bp on 30y JGB swap spreads, against an 8bp round trip in that same spread inside one week. The USD 75bn is the weakest link: the note's own AUM x band x 80-90% JGB share gives USD 90-101bn (USD 112bn gross), so 75bn implies a 67% JGB share and an AUM of USD 1.88tn; run honestly (Q=112bn, beta=1, free float ~USD 6.4tn) the answer is ~1.75bp.
- **What it teaches:** How to convert a flow narrative into a price effect and then into a per-unit-time signal-to-noise ratio before trading it — and that 'flow' without a sign convention is not a signal at all: mandate-driven rebalancing is contrarian and stabilising (cannot trend), momentum-driven CTA flow is destabilising (can trend), and the two must never be aggregated. Secondarily: a headline quantity that is a product of two independently estimated inputs must have each input verified separately, because errors in opposite directions (understated quantity, overstated sensitivity) produce a plausible-looking product that is not a base case.

### 2026/07 · macro_gs_em-trader_2026-07-30

- **In one line:** A common macro shock prices the EM cross-section almost entirely through a handful of global factors, so the tradable content sits in construction — which statistic you rank on and which leg you fund in — and in the residual, not in the direction of the shock itself.
- **Core mechanism:** EM FX returns are dominated by a small common factor set (equities, oil, copper, US 10y real yields) with the USD as the single largest common volatility factor, so the risk-adjusted return of a carry book is set more by the funding leg and the ranking statistic than by which long you pick (switching funder USD to EUR raises MXN carry-to-vol by 2.07x on the note's own numbers, more than the spread between any two longs in the same carry cohort). The selection statistic itself, carry divided by 3m realised vol, is a first-two-moment ratio built on only the carry half of expected return, applied to the canonical negatively-skewed premium — so it discards the spot forecast printed twenty pages later in the same document and is blind to the crash risk that is the premium's entire economic justification.
- **Market:** EM FX spot and 12m carry (COP, BRL, MXN, INR, ZAR, IDR, THB, PLN, ILS, CLP vs USD and EUR), with secondary reads on EM local 10y rates, EM sovereign USD credit supply, and MSCI EM equities
- **Load-bearing number:** +0.90% per 3 months (+3.6% annualised) — the entire recommended long/funder book marked to the firm's own 3-month forecast table, before transaction cost, against constituent implied 3m vols of 5-14% (i.e. an ex-ante Sharpe well under 0.5 on the author's own inputs). Secondary: the 2.07x MXN carry-to-vol uplift from funding in EUR rather than USD (= 1.49x carry x 1.39x less vol, implied by a 12m USD-EUR differential of 1.46pp).
- **What it teaches:** A ranking statistic must span both the components and the moments of the payoff it is meant to proxy. If a selector uses one component of expected return (carry) while a forecast of the other (spot) exists, rank-correlate them before trusting it — here that correlation is Spearman +0.19 across 21 currencies. If the premium exists to compensate crash risk, a mean-variance ratio is the statistic least able to separate a well-paid tail from an unpaid one. Both failures are invisible to the author because the selector is chosen for observability, not for fidelity to the payoff — and they recur across desks and years, so treat them as a standing audit rather than a one-off critique.

---

## The ideas

<a id="idea-001"></a>
### IDEA-001 · stock-bond-correlation-is-the-position-and-the-regime

`regime` · **status: unvalidated** · **15/15**
*source:* [2012 · factor_bridgewater_risk-parity_2012](2012/factor_bridgewater_risk-parity_2012.md) , [2026/07 · crossasset_gs_goal-kickstart_2026-07-27](2026/07/crossasset_gs_goal-kickstart_2026-07-27.md) **← independent arrival in 2+ reports**
*applies to:* Any multi-asset portfolio; SPY vs TLT/DGS10 directly, and the same growth-vs-inflation shock test on Bunds/Euro Stoxx, JGBs/TOPIX, Gilts/FTSE. Actionable decision is the CTA/real-asset allocation size.
<!-- edges -->
*related:* [IDEA-004](#idea-004) measures it · [IDEA-008](#idea-008) supplies the premium · [IDEA-025](#idea-025) prices the financing leg · [IDEA-009](#idea-009) picks the diversifier when the sign flips · [IDEA-022](#idea-022) who is forced to rebalance
*literature:* [bridgewater2012](../papers/paper_notes_bridgewater2012.md) · [campbell_shiller_1988](../papers/paper_notes_campbell_shiller_1988.md)
*study:* [2026-03-29_expected_returns_ilmanen](../studies/2026-03-29_expected_returns_ilmanen/er_book_briefing.md)

**Statement.** The stock-bond correlation sign is both a position you implicitly hold and the regime variable that selects your diversifier. Growth shocks make bonds hedge equities; inflation/discount-rate shocks make them fall together. Any risk-balanced or levered balanced portfolio is economically short that correlation, so size on the prevailing shock mix rather than the historical average, and when the sign turns positive buy diversification elsewhere (trend, real assets, options) instead of rebalancing into bonds.

**Mechanism — who pays, why it persists.** This is the compensated risk itself, not an anomaly — someone must hold the state where everything falls at once, and you are paid a diversification premium for being that holder. The sign is set by a discount-rate identity: under growth shocks cash-flow and discount-rate news oppose; under inflation shocks the discount-rate channel dominates both. Constrained counterparty: benchmark-mandated 60/40 allocators, target-date glidepaths and LDI schemes mechanically rebalance into bonds regardless of whether the correlation still makes them a hedge, and have no permission to change diversifier.

| | | |
|---|:--:|---|
| Economic rationale | **5/5** | Cleanly identified compensated risk with an economic account of the sign flip, plus a named mandated counterparty who eats the diversification shortfall. Independent arrival from a 2012 risk-parity note and a 2026 cross-asset note. |
| Durability | **5/5** | Rooted in monetary-policy regime and inflation anchoring — the 1970s-80s positive era and 1998-2020 negative era each ran ~two decades. Supplies the mechanism for the switch, so it survives the switch. |
| Testability | **5/5** | Verified: SPY, TLT, DGS10, T10YIE, CPIAUCSL all resolve through get_data. T5YIE and DFII10 sit in treasury_yields.parquet but raise ValueError — one registry line each, not a data gap. |

**Evidence so far.** Descriptive and partly self-contradictory. GOAL Exhibit 49 documents the +0.4 to +0.7 correlation shift since 2024; the risk-parity note cites 2022 as a single ex-post counterexample. No systematic regime classification, no count of prior positive-correlation episodes, no ex-ante test. GOAL Exhibits 21-22 show vol-target and momentum overlays recently underperforming static 60/40, cutting against the naive prescription — worth keeping.

**To test later.** SPY and TLT/IEF daily returns (in lake); FRED CPIAUCSL, T10YIE, T5YIE, DGS10, DFII10, INDPRO/PAYEMS for the growth leg; rolling 60d/126d correlation plus a shock decomposition labelling each month growth- or inflation-dominated; a self-built TSMOM composite for the trend-diversifier leg.

<a id="idea-002"></a>
### IDEA-002 · structure-geometry-vs-stated-view

`structure` · **status: unvalidated** · **14/15**
*source:* [2026/04 · macro_gs_jpy-macro-trading_2026-04-07](2026/04/macro_gs_jpy-macro-trading_2026-04-07.md)
*applies to:* Any packaged derivative sold alongside a directional view: swaption ladders and 1x2s in rates, structured notes and autocallables in equities, range accruals and dual-currency deposits in FX, accumulators in commodities.
<!-- edges -->
*related:* [IDEA-020](#idea-020) same convexity geometry, sell side · [IDEA-043](#idea-043) score direction and packaging apart · [IDEA-026](#idea-026) a target with no horizon

**Statement.** Compute a packaged trade's payoff geometry independently of its label before accepting it: maximum profit, the point at which being right stops paying, and the breakeven expressed in the same units as the seller's own volatility statistics. A direction call and the structure sold alongside it are two different products deserving two different credibility scores — the direction is free to publish, the structure is inventory.

**Mechanism — who pays, why it persists.** The dealer is the named counterparty and is explicitly compensated: the structurer sets the strikes, monetises skew, and in one case cites its own funding level as the product's selling point. The asymmetry persists because the client evaluates the narrative header while the dealer prices the geometry. It is not a mispricing to be arbitraged — it is a distribution-of-payoff choice most readers never compute.

| | | |
|---|:--:|---|
| Economic rationale | **5/5** | Named counterparty with a disclosed incentive; the conflict is visible in strike placement and reproducible with arithmetic alone, not inferred from tone. |
| Durability | **5/5** | Permanent — follows from the dealer business model, not a market regime. Regulation may change disclosure but not the fact that the seller chooses the strikes. |
| Testability | **4/5** | The geometry audit needs no data at all. The breakeven-vs-realized-vol half needs the underlying's daily level — available for anything in the lake, absent for JPY swaption forwards. |

**Evidence so far.** Analytic plus one live mark. Zero-cost 3m10y payer ladder at strikes {2.361, 2.461, 2.561} maxes at 10bp, decays to zero at +40bp, unbounded loss beyond — sold under a bearish header. Delta-exchanged receivers quote 4.32bp/day breakeven against the desk's own realized vol of 2.75/3.65/4.81, clearing one of three regimes by 11%. Live: cash 10y +32bp Apr-Jun landed inside the capped zone; an outright short paid ~3x the 'leveraged' structure. n=1.

**To test later.** Nothing beyond the term sheet's strikes and premium for the audit. For the breakeven test: the underlying's daily level to compute regime-conditioned realized vol (in-lake for FX/equities/UST). For a systematic study: historical structured-product term sheets plus subsequent underlying paths.

<a id="idea-003"></a>
### IDEA-003 · moments-must-match-the-premium

`method` · **status: unvalidated** · **14/15**
*source:* [2025/11 · rates_gs_vol-strategies_2025-11-13](2025/11/rates_gs_vol-strategies_2025-11-13.md) , [2026/07 · macro_gs_em-trader_2026-07-30](2026/07/macro_gs_em-trader_2026-07-30.md) **← independent arrival in 2+ reports**
*applies to:* Universal to option-like, convexity and carry structures: rates and equity vol selling, FX and credit carry, EM local receivers, commodity roll. Immediately applicable to this repo's vol_conditioned_reversal_v1 and fx_carry proposals.
<!-- edges -->
*related:* [IDEA-014](#idea-014) contrast: stops overpaying vs literal transfer · [IDEA-018](#idea-018) compounds: both inflate the same t-stat · [IDEA-027](#idea-027) when to pay for convexity · [IDEA-020](#idea-020) the payoff it mis-scores · [IDEA-019](#idea-019) the moments a selector must span · [IDEA-034](#idea-034) score the hedge on its tail, not Sharpe
*literature:* [carr_wu_vrp_2009](../papers/paper_notes_carr_wu_vrp_2009.md) · [cremers_halling_weinbaum_2015](../papers/paper_notes_cremers_halling_weinbaum_2015.md) · [rates_vrp](../papers/paper_notes_rates_vrp.md)
*study:* [2026-03-29_expected_returns_ilmanen](../studies/2026-03-29_expected_returns_ilmanen/er_book_briefing.md) · [2026-06-24_volatility_workstation](../studies/2026-06-24_volatility_workstation/README.md)
*platform:* [vol_conditioned_reversal_v1 manifest](../../../alpha_research/research/pool/vol_conditioned_reversal_v1/manifest.yaml) · [fx_carry proposal](../../../alpha_research/research/strategies/fx_carry_2026-03-13_conditional/proposal.md)

**Statement.** A selection or evaluation statistic must span the moments the premium actually lives in. Where the P&L identity is quadratic in a state variable (P&L ~ 0.5*Gamma*S^2*(sigma_IV^2 - sigma_RV^2)*dt) or the premium exists to compensate crash risk, a Sharpe- or carry-to-vol ranking is a category error: it loads onto the very risk being paid for and reports it as skill. Skew, kurtosis and max drawdown become mandatory columns, and the selector itself should be penalised by the higher moments rather than reported next to them.

**Mechanism — who pays, why it persists.** If an excess return compensates crash risk, the names with the best mean-variance ratio are best precisely because their third moment is worst. The carry/vol seller is the insurer; the buyer is the leveraged or hedging agent who must unwind in funding stress and pays to avoid doing so at a random time. It persists because a negatively-skewed payoff looks like alpha over every sample without an unwind, and because performance is evaluated on Sharpe — the metric itself creates the incentive to sell the tail.

| | | |
|---|:--:|---|
| Economic rationale | **4/5** | Both the compensated risk and the counterparty are named, and the persistence has an incentive account. Held at 4 not 5 because it prevents mis-selection rather than capturing a transfer — contrast [IDEA-014](#idea-014), where the fee is literal money you can stop paying. |
| Durability | **5/5** | A property of the premium plus an algebraic identity. Cannot be arbitraged; the reporting incentive it guards against is equally permanent. |
| Testability | **5/5** | Verified present: performance.py computes skew and excess kurtosis; report.py and professional_report.py render them; stats/ ships bootstrap, cross_validation, minimum_backtest, multiple_testing, sharpe_tests. Implementation is a gate, not a data problem. |

**Evidence so far.** No quantitative test; the claim is algebraic plus literature (Brunnermeier-Nagel-Pedersen 2008, already cited in this repo's fx_carry proposal). Supporting observation is anecdotal, n=2: two GS notes nine months apart and one desk over characterise every return series by return, vol and return-to-vol only — Exhibits 5, 12, 13, 16, 17 in the rates-vol note, Exhibits 7-8 in the EM note — with no third or fourth moment anywhere. Independent arrival argues house methodology, not oversight.

**To test later.** Nothing beyond a return series. To operationalise: add a short_convexity / carry_like flag to alpha_research/backtests/strategies/manifest.py and extend the review rigor battery to block Sharpe-only benchmark comparisons for flagged strategies.

<a id="idea-004"></a>
### IDEA-004 · risk-contribution-vs-capital-weights

`method` · **status: unvalidated** · **14/15**
*source:* [2012 · factor_bridgewater_risk-parity_2012](2012/factor_bridgewater_risk-parity_2012.md)
*applies to:* Any multi-asset portfolio; equally within-sleeve to sector, country or factor weight sets in any market.
<!-- edges -->
*related:* [IDEA-001](#idea-001) the correlation it is short · [IDEA-008](#idea-008) the premium for levering it · [IDEA-025](#idea-025) where the Sharpe gain is not
*literature:* [bridgewater2012](../papers/paper_notes_bridgewater2012.md)
*platform:* [advanced_analytics.py](../../../alpha_research/portfolio/advanced_analytics.py)

**Statement.** Restate any allocation in risk-contribution space before calling it diversified. When two sleeves differ in volatility by a factor k, capital weights understate the high-vol sleeve's variance share by roughly k-squared; at k=3 a 60/40 split is ~90% equity risk. Applies within sleeves too — sector, country and factor weights lie the same way.

**Mechanism — who pays, why it persists.** Nobody is on the other side of an accounting identity; what persists is the mis-labelling. Institutional policy portfolios, IPS documents and peer-group benchmarks are written in capital terms, so the benchmark-relative allocator is mandated to a number that does not describe the risk held and is not permitted to restate it. The constraint is documentary and slow-moving, which is why an arithmetic point public for decades still describes how most money is allocated.

| | | |
|---|:--:|---|
| Economic rationale | **4/5** | The arithmetic is an identity and the persistence has a named institutional cause. Not 5 because the identity is a measurement correction, not an edge — the premium for exploiting it is a separate claim ([IDEA-008](#idea-008)). |
| Durability | **5/5** | Variance arithmetic does not decay. IPS and policy-portfolio conventions move on decade timescales; the 60/40 label survived both 2008 and 2022 intact. |
| Testability | **5/5** | Verified: risk_parity_optimize and risk_contribution exist in alpha_research/portfolio/advanced_analytics.py; SPY, TLT, IEF, GLD all resolve through get_data. TIP and DBC do not resolve — substitute or add one registry line. |

**Evidence so far.** In-sample and descriptive only. The 3x vol ratio and ~90% risk share are asserted by the originator of the product with no out-of-sample check, no other market and no other period. The note presents only descriptive statistics — vol ratios, taxonomies, quadrant maps — and no inferential ones.

**To test later.** Daily total returns for SPY, TLT/IEF, TIP, DBC/PDBC/DJP from the Parquet price lake; rolling 60d and 252d covariance matrices; marginal-risk-contribution decomposition per sleeve.

<a id="idea-005"></a>
### IDEA-005 · issuance-mix-taper-sector-loser

`signal` · **status: unvalidated** · **13/15**
*source:* [2026/04 · macro_gs_jpy-macro-trading_2026-04-07](2026/04/macro_gs_jpy-macro-trading_2026-04-07.md)
*applies to:* Any sovereign curve with a tapering central bank and tenor-clustered domestic ALM buyers: JGBs, USTs vs QT redemption caps plus quarterly refunding, Gilts vs LDI at the long end, Bunds vs PEPP/APP reinvestment.
<!-- edges -->
*related:* [IDEA-006](#idea-006) contrast: OPPOSITE sign, never aggregate · [IDEA-042](#idea-042) tension: sizes the effect down · [IDEA-030](#idea-030) reads the same tenor demand · [IDEA-007](#idea-007) supplies the global duration channel
*literature:* [litterman1991](../papers/paper_notes_litterman1991.md) · [bernanke2020](../papers/paper_notes_bernanke2020.md)
*study:* [2026-03-26_fixed_income_relative_value_analysis_2e](../studies/2026-03-26_fixed_income_relative_value_analysis_2e/firv_book_briefing.md)

**Statement.** The published sovereign issuance calendar combined with the central bank's purchase-taper schedule identifies WHICH curve sector underperforms, independent of the level view: the loser is the tenor that simultaneously loses the central bank's price-insensitive bid and lacks a natural mandated buyer, while the tenor whose supply is cut below mandated-buyer absorption capacity gets structurally over-bid. Express as a curve fly shorting the squeezed body, not as an outright duration short.

**Mechanism — who pays, why it persists.** Two named constrained counterparties. Life insurers and pensions must buy ultra-long duration to match liabilities whose duration is fixed by solvency regulation — price-insensitive, with a slow-moving and roughly knowable maximum absorption pace (0.6trn JPY/month here). The central bank was the belly's price-insensitive buyer and is withdrawing on an announced schedule. Persists despite public calendars because the relative-sector claim requires balance sheet, negative carry and a multi-quarter horizon, and because demand-side macro models have no channel for issuance mix at all — the information is genuinely unpriced, not merely slow.

| | | |
|---|:--:|---|
| Economic rationale | **5/5** | Two price-insensitive counterparties plus a public, falsifiable quantity comparison (0.75trn/month issuance cut vs 0.6trn/month absorption). The only pillar in the note built on auditable quantities rather than a decoded press-conference adjective. |
| Durability | **5/5** | Solvency regulation, liability structure and announced QT/rinban paths change on multi-year timescales. The squeezed sector rotates as calendars change; the method of locating it does not. |
| Testability | **3/5** | Untestable as stated — no JGB curve points anywhere; only IRLTLT01JPM156N (monthly, 45-day PIT lag) resolves. US transposition is reachable: DGS2/DGS5/DGS10/DGS30 resolve; WSHOMCB/TREAST are in fed_liquidity.parquet but raise ValueError (registry gap); Treasury QRA tables need scraping. |

**Evidence so far.** Ex-ante and directionally confirmed out-of-sample, n=1: published 26-Dec-2025 with 10y JGB at 2.060%; actual 2.670% by Jun-2026 (+61bp) while the same firm's demand-side base case had it flat near 2.0%. Caveat — only the outright level is observable; the actual claim is relative (10s40s 148bp to a 100bp target, 2s10s40s body short) and remains unverified. No controls, one episode.

**To test later.** MoF JGB issuance calendar by tenor bucket; BoJ rinban plan and actuals by maturity bucket; JGB par yields at 2y/5y/10y/20y/40y; life-insurer net purchases by maturity (JSDA/BoJ flow-of-funds). US analogue: Treasury QRA issuance tables, SOMA redemption caps, FRED DGS series.

<a id="idea-006"></a>
### IDEA-006 · mandate-rebalancing-is-contrarian-flow

`signal` · **status: unvalidated** · **13/15**
*source:* [2026/07 · flows_gs_japan-savings-jgb-demand_2026-07-20](2026/07/flows_gs_japan-savings-jgb-demand_2026-07-20.md)
*applies to:* JGBs and JPY rates in the source instance; generalises to NBIM, Korean NPS, Dutch/Danish pensions in the EUR long end, and month/quarter-end rebalancing of US 60/40 and target-date mandates.
<!-- edges -->
*related:* [IDEA-005](#idea-005) contrast: OPPOSITE sign, never aggregate · [IDEA-022](#idea-022) contrast: forced but trend-following · [IDEA-030](#idea-030) the same holder's tenor drift · [IDEA-035](#idea-035) the demand-side falsification

**Statement.** A large asset owner held to a benchmark band rebalances into whatever fell, so its flow is a decreasing function of the asset's own return — stabilising by construction and mechanically incapable of generating a trend. Sign and rough size are computable ex ante from public target weights, band limits, AUM and observable sleeve returns. Treat it as forecastable liquidity supply, and never aggregate it with momentum-driven flow, which carries the opposite sign convention.

**Mechanism — who pays, why it persists.** GPIF and any statutorily benchmarked pool must trade to hold weights inside a legislated band — buying the sleeve that fell, selling the one that rose, regardless of view, and unable to decline. Named, price-insensitive, threshold-driven; you are the liquidity provider. Persists because the policy asset mix is governance-set on a ~5-year cycle (next review 2030), the band is regulatory, and holdings disclose with a lag. It runs in reverse too: a currency rally lifts the domestic-bond share toward the ceiling and turns the same buyer into a seller.

| | | |
|---|:--:|---|
| Economic rationale | **5/5** | THE ANCHOR FOR 5. A single named entity with a legally defined +/-6ppt band around a 25% target, a statutory mandate, and no discretion to abstain. Nothing else in the pool has a counterparty this literally forced. |
| Durability | **5/5** | Market plumbing on a multi-year legislated cycle; the band has only narrowed over time. Mandated rebalancing is universal to benchmarked pools, not a Japan artefact. |
| Testability | **3/5** | Verified: USDJPY=X resolves; ^N225 is physically in equities.parquet from 2005 but raises ValueError through get_data (registry gap), and ^TOPIX is absent entirely. GPIF quarterly composition needs a scraper. Flow is computable; whether it moves JGB prices is not testable here (no JGB curve). |

**Evidence so far.** Descriptive. Exhibit 6 (GPIF annual 2016-2026) shows a clearly negative slope of JGB rebalancing flow against combined FX-and-bond returns; the digest fits b = -0.65 to -0.72 JPYtn per 1% off the chart axes (+/-1.5 JPYtn endpoint resolution, so the sign is the finding, not the magnitude). Exhibit 5: 2026 mechanical domestic-bond flow ~+17 JPYtn vs discretionary capacity ~+11.5 JPYtn = 1.48x. Partially ex-ante: USD/JPY -3.15% in the 13 days post-publication lifts the domestic-bond share ~27.00% to ~27.41%, consuming ~10% of the 4ppt room with no policy — price consequence unobserved.

**To test later.** GPIF quarterly composition and annual ISIN-level holdings (gpif.go.jp, no connector); TOPIX total return; MSCI ACWI ex-Japan in JPY; a JGB total-return index (Nomura BPI); USDJPY=X (in lake). For generalisation: NBIM quarterly holdings, NPS monthly asset mix.

<a id="idea-007"></a>
### IDEA-007 · term-premium-not-risk-neutral-transmission

`regime` · **status: unvalidated** · **13/15**
*source:* [2026/07 · macro_gs_em-trader_2026-07-30](2026/07/macro_gs_em-trader_2026-07-30.md)
*applies to:* EM local 10y, JGBs, Bunds, Gilts, long-dated credit; by extension long-duration equity and infrastructure.
<!-- edges -->
*related:* [IDEA-042](#idea-042) free float sets the local beta · [IDEA-005](#idea-005) who withdraws from which sector · [IDEA-024](#idea-024) horizon of the explaining variables
*literature:* [cochrane_piazzesi_2005](../papers/paper_notes_cochrane_piazzesi_2005.md) · [kimwright2005](../papers/paper_notes_kimwright2005.md) · [duffee2002](../papers/paper_notes_duffee2002.md) · [litterman1991](../papers/paper_notes_litterman1991.md)
*study:* [2026-03-26_fixed_income_relative_value_analysis_2e](../studies/2026-03-26_fixed_income_relative_value_analysis_2e/firv_book_briefing.md)
*platform:* [yield_curve proposal](../../../alpha_research/research/strategies/yield_curve_2026-03-13_rejected/proposal.md)

**Statement.** When transmitting a global rate move to any long-dated risky duration, decompose the driver before sizing the response: foreign and EM 10y local yields load on the US term-premium component roughly 3x more strongly than on the risk-neutral expected-policy-path component (median t of 6-8 vs about 2 across 16 EMs). A 25bp UST selloff driven by term premium is a materially different event for foreign long ends than the same 25bp driven by repricing the Fed path.

**Mechanism — who pays, why it persists.** Term premium is the price of duration risk, set globally by supply and demand for long-dated bonds — net issuance, defence and AI-capex fiscal expansion, QT, and mandated buyers stepping back or forward. Every long-dated claim competes in one global pool of duration-bearing capacity, so this component transmits mechanically across borders. The risk-neutral component is one country's expected policy path, which each local reaction function partially offsets. Constrained parties: benchmark-following local-rate investors and liability-driven buyers who must hold duration regardless of price and cannot reprice global duration risk.

| | | |
|---|:--:|---|
| Economic rationale | **5/5** | Global duration supply/demand is a genuine compensated risk with identifiable mandated participants on both sides, and the asymmetry follows directly from what each component prices. Strongest mechanism in the EM note. |
| Durability | **5/5** | Plumbing-level, with the supply driver visible on a public fiscal and QT calendar. Weakens only if capital controls or a domestic mandated-buyer backstop segments a local market from the global pool — itself observable. |
| Testability | **3/5** | US side near-reachable: NY Fed ACM (public daily) or FRED THREEFYTP10, unregistered; DGS10 resolves. Dependent variable is the gap — no EM local 10y anywhere. DM version viable via the existing stooq connector; DFII10 is in treasury_yields.parquet but raises ValueError. |

**Evidence so far.** In-sample and thinly reported: 3-year rolling weekly OLS across 16 EMs, median t of 6-8 on the term-premium beta vs about 2 on the risk-neutral beta, with no R2, no standard errors and no residual distribution published — so sign and rough ratio only. Rolling 3-year windows on weekly data make the t-statistics heavily overlapping and overstated. Corroborated anecdotally by the JGB 2.06%-to-2.67% move and CTA net-short JGB positioning recorded in two other digests in this library.

**To test later.** ACM term premium or FRED THREEFYTP10; DGS10 (registered); local 10y government yields — hard gap for EM, reachable for DM (JGB/Bund/Gilt via stooq). Add DFII10 to _FRED_ENTRIES to replace the DGS10-minus-T10YIE real-yield proxy.

<a id="idea-008"></a>
### IDEA-008 · leverage-aversion-premium

`structure` · **status: unvalidated** · **13/15**
*source:* [2012 · factor_bridgewater_risk-parity_2012](2012/factor_bridgewater_risk-parity_2012.md)
*applies to:* Cross-asset (levered bonds vs equities) and the within-equity low-beta version; generalizes to any market with a structurally leverage-constrained investor base.
<!-- edges -->
*related:* [IDEA-004](#idea-004) the risk-weight identity · [IDEA-025](#idea-025) not merged: return source vs diagnostic · [IDEA-001](#idea-001) the correlation the leverage rides on
*literature:* [frazzini_pedersen_bab_2014](../papers/paper_notes_frazzini_pedersen_bab_2014.md)
*study:* [2026-03-29_expected_returns_ilmanen](../studies/2026-03-29_expected_returns_ilmanen/er_book_briefing.md)

**Statement.** Prefer levering a high-Sharpe low-volatility asset up to your target volatility over holding a lower-Sharpe high-volatility asset at 1x. The compensation is not for bearing volatility, it is for being willing and able to borrow — so how you reach target vol is a return source, not plumbing.

**Mechanism — who pays, why it persists.** Named constrained counterparty: investors barred from leverage by mandate or regulation — mutual funds under borrowing limits, retail, pensions without derivative authority, insurers facing capital charges — must hit a return target through asset selection rather than gearing. That bids up high-beta assets and depresses their forward Sharpe relative to low-vol assets. The levered holder is paid for bearing funding and margin-call risk. Persists because the constraints are legal and mandate-based, and they bind hardest in a downturn, precisely when the premium is widest.

| | | |
|---|:--:|---|
| Economic rationale | **5/5** | Explicitly names a price-insensitive constrained party and a genuinely compensated risk (funding, margin). This is the real mechanism underneath the note's loose 'leverage improves Sharpe' claim, which the note never articulates. |
| Durability | **4/5** | Structural and regulatory, but among the most heavily traded published anomalies since ~2011: crowding and higher policy rates compress it, and the levered expression is path-fragile even where the average edge survives. |
| Testability | **4/5** | Verified: SPY, TLT, IEF, GLD and DFF all resolve. The honest version needs an achievable financing cost — futures-implied rate or PB spread; SOFR sits in treasury_yields.parquet but raises ValueError, and CME calendar spreads are absent. That gap is the difference between 4 and 5. |

**Evidence so far.** None. The digest asserts 'leverage improves Sharpe, not merely return' with no derivation, no cost accounting, and no citation to the betting-against-beta literature that supplies the mechanism.

**To test later.** SPY, TLT/IEF, TIP and a commodity ETF daily returns; FRED SOFR/EFFR/DTB3 for the cash leg; ideally CME ZN and ES roll/basis for true implied financing (not ingested).

<a id="idea-009"></a>
### IDEA-009 · hedge-efficacy-scales-with-crash-duration

`regime` · **status: unvalidated** · **13/15**
*source:* [2013 · factor_aqr_managed-futures_2013](2013/factor_aqr_managed-futures_2013.md)
*applies to:* Any trend or MA overlay used as a portfolio hedge; equally applicable to vol-targeting and risk-parity de-risking rules, which share the latency property.
<!-- edges -->
*related:* [IDEA-034](#idea-034) why a bleeding hedge gets cut · [IDEA-037](#idea-037) the rule whose latency this bounds · [IDEA-018](#idea-018) hedge value and independence in tension · [IDEA-001](#idea-001) the correlation regime that makes a diversifier necessary
*literature:* [hurst2013](../papers/paper_notes_hurst2013.md) · [daniel_moskowitz_crashes_2016](../papers/paper_notes_daniel_moskowitz_crashes_2016.md)
*study:* [2026-03-29_expected_returns_ilmanen](../studies/2026-03-29_expected_returns_ilmanen/er_book_briefing.md)
*platform:* [vol_scaled_momentum proposal](../../../alpha_research/research/strategies/vol_scaled_momentum_2026-03-13_rejected/proposal.md)

**Statement.** A trend or moving-average rule hedges only those drawdowns lasting longer than its signal latency. All three canonical crisis wins (1929-32, 2000-02, 2008) are multi-month-to-multi-year declines; a 12-month lookback cannot flip short inside a one-month crash. The right question about any trend allocation is not 'does it have crisis alpha' but 'does its lookback match the duration of the crisis I am hedging' — a design parameter, not an empirical discovery.

**Mechanism — who pays, why it persists.** Mechanical rather than counterparty-driven, which is why it is durable: the signal is a moving function of the past N months, so the position cannot be adverse-to-the-crash until the crash occupies a material fraction of the window. The corollary is a genuine risk transfer — trend sellers of crash protection are selling protection only against slow repricings, and buyers who believe they own generic tail protection are mispricing what they hold. Not arbitraged because it is not an anomaly; it is the arithmetic of the estimator.

| | | |
|---|:--:|---|
| Economic rationale | **4/5** | Not a payer story, but the mechanism is fully deducible from the rule's construction and predicts a specific failure mode ex ante — stronger than most plausible-story cases. Below 5 because it describes a hedge property, not an alpha source. |
| Durability | **5/5** | Follows from the definition of the signal, so it survives crowding, regime change and fee compression alike. Only the market's mix of fast versus slow crashes varies. |
| Testability | **4/5** | Verified: SPY resolves and equities.parquet holds ^GSPC and SPY from 2005; VIXCLS resolves. Classify drawdowns by peak-to-trough duration, then measure the trend sleeve conditional on duration bucket. ^GSPC back to 1927 needs yfinance plus a registry line. |

**Evidence so far.** Anecdotal and in-sample. Three cited crisis wins, all long-duration, no counter-example offered; no test conditioning payoff on drawdown length appears anywhere, and 1987 / Feb-2018 / Mar-2020 style fast crashes are absent from the discussion entirely.

**To test later.** Daily ^GSPC back to 1927 and SPY since 1993 to build a drawdown catalogue with peak-to-trough durations; the trend sleeve's monthly returns; optionally VIXCLS to separate vol-spike crashes from grinding declines.

<a id="idea-010"></a>
### IDEA-010 · publication-date-ends-the-in-sample

`risk` · **status: unvalidated** · **13/15**
*source:* [2013 · factor_aqr_managed-futures_2013](2013/factor_aqr_managed-futures_2013.md)
*applies to:* Every externally sourced strategy — sell-side, academic, asset-manager — and by extension every internal backtest with full-sample parameter choice.
<!-- edges -->
*related:* [IDEA-013](#idea-013) same note, fee side · [IDEA-043](#idea-043) publisher-level version · [IDEA-037](#idea-037) the strategy it dates · [IDEA-018](#idea-018) the other inflator of the same statistic
*literature:* [baltussen2021](../papers/paper_notes_baltussen2021.md) · [geczy2017](../papers/paper_notes_geczy2017.md)
*study:* [2026-06-17_advances_financial_ml](../studies/2026-06-17_advances_financial_ml/study_hypotheses.md)
*platform:* [manifest.py — no publication_date field](../../../alpha_research/backtests/strategies/manifest.py) · [pit.py — the series-level analogue](../../../alpha_research/quant_data/pit.py)

**Statement.** Treat the publication date of any vendor-authored strategy note as the exact end of its in-sample period, and size on post-publication evidence only — or, absent enough post-publication history, haircut the reported Sharpe by roughly a third to a half before it enters any allocation. Extend the same rule to internal backtests whose parameters were chosen while looking at the full sample.

**Mechanism — who pays, why it persists.** Publication is asymmetrically selected: a firm that sells the strategy publishes when the backtest looks good and never publishes the version that failed, so the reported statistic is the maximum of an unobserved set of trials. Post-publication decay is then reinforced by real capital arriving on the trade. The constrained party is the allocator who cannot see the unpublished trials; the selection happens before anything reaches the reader, so no amount of rigour applied to the published sample can undo it.

**Practical note added 2026-08-15 — the artifact's date is not the claim's date, and the error runs one way.** This idea is only as good as the date you write down, and the file will lie to you. Re-digesting `flows_gs_cta-bond-futures_2026-06-09` surfaced a PDF carrying **two** dates: the note's dateline (9 June 2026) and a portal sidebar stamped **Jul 30, 2026** — rendered when the page was exported, ~7 weeks later. Filesystem mtimes are worse still. The bias is **always in the same direction** (artifacts are created at or after the claim), so dating from the file systematically ends the in-sample period *late* and quietly counts genuinely out-of-sample months as in-sample — the precise error this idea exists to prevent, injected by the archivist rather than the vendor. Rule: date from the dateline in the document body; treat every other timestamp as rendering furniture. No source line and no score change — this came from handling the artifact, not from any report's argument. It is the document-level analogue of what `alpha_research/quant_data/pit.py` already enforces for series (information date vs availability date), which is exactly the field `manifest.py` is missing below.

| | | |
|---|:--:|---|
| Economic rationale | **4/5** | Named mechanism (publication selection plus capital arrival), a documented effect size in the McLean-Pontiff literature, and a live instance in this very note. Held at 4 rather than 5 because it is a haircut discipline: you avoid overpaying rather than capture a transfer. |
| Durability | **5/5** | Structural feature of how research is produced and marketed. Holds as long as firms publish research about products they sell. |
| Testability | **4/5** | Verified: alpha_research/backtests/strategies/manifest.py has n_trials but NO publication_date field — this is a schema addition plus a pre/post split in the review performance output, a process gap not a data gap. Extending a TSMOM proxy from 2013 to today needs only a yfinance backfill of sleeves that already resolve. |

**Evidence so far.** Ex-ante and adverse: the digest notes post-2013 trend underperformance the 2012-vintage note could not address — one true out-of-sample observation pointing the wrong way against a reported ~0.9 modern-era Sharpe. No formal decay test anywhere.

**To test later.** A publication_date field in alpha_research/research/pool/<id>/manifest.yaml plus pre/post reporting in the review output; for the specific case, monthly returns for a four-sleeve TSMOM proxy 2013-2026 and a listed trend proxy (DBMF, KMLM — neither currently resolves) as a live-capital cross-check.

<a id="idea-011"></a>
### IDEA-011 · official-fx-reaction-function-overlay

`risk` · **status: unvalidated** · **13/15**
*source:* [2026/04 · macro_gs_jpy-macro-trading_2026-04-07](2026/04/macro_gs_jpy-macro-trading_2026-04-07.md)
*applies to:* Any managed or defended currency with a published or inferable official reaction function — USD/JPY (MoF), CHF (SNB), CNH (PBoC fixing band), EM carry pairs with reserve-financed defence; transposable to commodity price bands and circuit-breaker markets.
<!-- edges -->
*related:* [IDEA-031](#idea-031) trigger is direction of travel, not level · [IDEA-023](#idea-023) the funder whose vol it manages
*literature:* [fama1984](../papers/paper_notes_fama1984.md) · [obstfeld2005](../papers/paper_notes_obstfeld2005.md) · [gopinath2021](../papers/paper_notes_gopinath2021.md)
*study:* [2026-03-27_global_macro_trading_gliner](../studies/2026-03-27_global_macro_trading_gliner/gmt_book_briefing.md)

**Statement.** Where an official body defends a currency, the tradable edge is not direction but the authority's reaction function, which is triggered by realized volatility and momentum extremes rather than by a price level. Convert it into a position-management overlay on the carry trade: cut or flatten at a momentum extreme (14-day RSI > 80), exit on the shock day (a daily range several times normal), and re-enter roughly one month after the intervention once the pair has bottomed and rebounded.

**Mechanism — who pays, why it persists.** The counterparty is the finance ministry or central bank — price-insensitive, mandate-driven, not maximising P&L, and therefore unable to arbitrage away its own reaction function. The G7 formulation ('when volatility increases') publicly commits the authority to target disorder rather than level, so the trigger set is observable. The post-intervention rebound persists because intervention removes vol but not the rate differential: the structural sellers (outward FDI, retail overseas allocation, a services deficit) are unchanged, so carry re-asserts once the deterrence premium decays.

| | | |
|---|:--:|---|
| Economic rationale | **4/5** | A named, constrained, non-profit-maximising counterparty with a publicly stated trigger. Not 5 because the ~1-month rebound timing is folklore in the source — 'past intervention cases' with no episode list, no n, no dispersion — so the entry half is weaker than the exit half. |
| Durability | **4/5** | Structural while the policy regime holds, and regime-conditional in a knowable way: a change of finance minister, a shift from smoothing to level-defence, or deliberate unpredictability would break it — all observable events rather than silent decay. |
| Testability | **5/5** | Verified: USDJPY=X resolves through get_data and has a dedicated USDJPY_X.parquet plus coverage in fx.parquet. Daily range and RSI(14) derive from it. Only extra input is MoF's public monthly intervention disclosure. Multiple episodes: Sep/Oct-2022, Apr-May and Jul-2024, 30-Jul-2026. The single most implementable idea in the pool. |

**Evidence so far.** Ex-ante against the Dec-2025 rule set, one live event 2026-07-30, mixed on precision: the 161.96 prior high was breached (peak close 163.86); first-day range 5.74 yen vs the stated ~4 yen estimate; day-2 range 2.17, consistent with the 'about three days' claim; spot closed 160.18 on 31-Jul, parked on the stated 160 line. RSI>80 fired 2026-07-01, a full month early — correct as a stand-aside signal, not sharp as timing. The rebound rule is entirely untested; its window is late Aug/early Sep 2026.

**To test later.** USDJPY=X daily OHLC (in lake); MoF monthly intervention disclosure for episode dates; ideally JPY 1m implied vol and risk reversal to separate the vol trigger from the momentum trigger (no FX options data on the platform). Cross-market: SNB sight deposits, PBoC fixing deviations.

<a id="idea-012"></a>
### IDEA-012 · trailing-window-buffer-undersizing

`risk` · **status: unvalidated** · **13/15**
*source:* [2026/05 · rates_gs_fed-balance-sheet_2026-05-21](2026/05/rates_gs_fed-balance-sheet_2026-05-21.md)
*applies to:* Universal — any buffer, margin, VaR limit, stop-loss or 'excess capacity' claim; any sell-side or regulatory estimate of how much a system can absorb.
<!-- edges -->
*related:* [IDEA-039](#idea-039) the backstop that censored the window · [IDEA-014](#idea-014) the crossing the buffer must survive
*study:* [2026-06-17_advances_financial_ml](../studies/2026-06-17_advances_financial_ml/study_hypotheses.md)

**Statement.** A tail buffer calibrated on a trailing window that excludes the regime it must survive is systematically undersized — here a buffer matched the trailing-12-month 95th percentile (\$211bn) rather than the full post-2019 p95 (\$290bn, +45%), with p99 at \$414bn and observed max \$568bn. Second and less obvious: the sign of the correction flips with an unstated framing choice — a buffer read as releasable capacity adds headroom, read as a floor that must survive a shock it subtracts. Force the framing to be stated before accepting any capacity number.

**Mechanism — who pays, why it persists.** Trailing-window risk calibration is structurally procyclical, and that procyclicality is embedded in regulation and plumbing — VaR limits, initial-margin models and liquidity buffers all loosen after calm and tighten after stress, forcing leveraged holders to delever exactly when spreads widen. Genuine constrained-counterparty mechanism with a compensated risk opposite (being the buyer when margin models force sales). Layered on top: the party arguing for capacity release chooses the calm window, and here the evidence came from the firm's own trading franchise, a direct beneficiary.

| | | |
|---|:--:|---|
| Economic rationale | **4/5** | Procyclical trailing-window calibration is documented, regulated and repeatedly observed with identifiable forced sellers. Not 5 because as written it protects you from a bad number; the tradeable version (own convexity when trailing models say it is unnecessary) needs its own instrument. |
| Durability | **4/5** | The procyclicality survives each cycle, but the magnitude of the undersizing oscillates — largest right after a calm stretch, mechanically shrinking once stress observations enter the window. |
| Testability | **5/5** | Testable today with no new data: trailing-window vs full-sample percentiles are computable on any series in the lake, and the general claim (trailing-p95 buffers breach more often than nominal across regimes) can be run cross-sectionally over every price and macro series held. Only the specific TGA instance needs WTREGEN promoted into the research registry — it is in fed_liquidity.parquet but raises ValueError. |

**Evidence so far.** In-sample distributional arithmetic on live data, no ex-ante test: 4-week increases in the Treasury cash account, 2019-present, give p95 = +\$290.1bn, p99 = +\$413.7bn, max = +\$568.2bn against a trailing-12m p95 of \$211.1bn and a stated \$200bn buffer. The framing ambiguity is demonstrated rather than tested — reading the buffer as a credit lifts aggregate capacity to \$1,140bn, as a floor cuts it to \$960bn, from the identical correction.

**To test later.** General test: any long price/macro history in the lake — rolling-12m p95 vs expanding-window p95, breach rates by regime. Specific: FRED WTREGEN 4-week changes and WRESBAL. Margin extension: CME/ICE initial-margin history (vendor).

<a id="idea-013"></a>
### IDEA-013 · mechanical-replicant-as-fee-and-skill-audit

`method` · **status: unvalidated** · **12/15**
*source:* [2013 · factor_aqr_managed-futures_2013](2013/factor_aqr_managed-futures_2013.md)
*applies to:* Any active manager, hedge-fund index, smart-beta product or internal strategy: CTA/managed futures, equity long-short vs market/value/momentum, risk premia products, multi-strategy vehicles.
<!-- edges -->
*related:* [IDEA-037](#idea-037) the replicant itself · [IDEA-010](#idea-010) date the R-squared · [IDEA-018](#idea-018) discount its breadth
*literature:* [funghsieh2004](../papers/paper_notes_funghsieh2004.md) · [hurst2013](../papers/paper_notes_hurst2013.md)

**Statement.** Before paying for any active manager or manager index, regress its returns on the cheapest mechanical rule that could plausibly generate them. The R^2 is the share of the product you can buy for near-zero cost; only the residual justifies a fee. Here a single vol-scaled 12-month sign rule explained a CTA index with R^2 > 0.9 — roughly 90% of the managed-futures industry is a replicable factor wearing a 2-and-20 wrapper.

**Mechanism — who pays, why it persists.** The payer is identified and constrained: allocators buying through consultants and mandate buckets, who receive monthly, aggregated, opaque return streams and are institutionally rewarded for hiring 'skill' rather than for cheap beta. It persists because the agency structure is stable — nobody's career is advanced by concluding that a whole industry is one regression — and because managers control the disclosure granularity needed to run the test. A genuine, nameable transfer of money.

| | | |
|---|:--:|---|
| Economic rationale | **5/5** | Named constrained counterparty under agency and disclosure constraints, and a documented persistent transfer. The most economically grounded idea in that note, and the one its author has least incentive to overstate. |
| Durability | **4/5** | Agency and disclosure structure change very slowly, so the method keeps working. Marked down because the specific CTA-fee arbitrage has partly closed since 2013 via cheap trend ETFs and managed-futures mutual funds — this idea has been acted on. |
| Testability | **3/5** | Upgraded from the extractor's 2: the replicant side is fully buildable (SPY, QQQ, TLT, IEF, GLD, USO and all seven G10 crosses resolve). Listed proxies DBMF and KMLM raise ValueError but are free via yfinance behind one registry line. SG Trend / BarclayHedge / HFRI remain licensed — that is the residual gap, not the whole test. |

**Evidence so far.** In-sample: a single reported R^2 > 0.9 over the modern sample, with no out-of-sample or rolling-window version, no sub-period stability, and no reporting of how many candidate replicants were tried before this one.

**To test later.** Monthly returns for SG Trend and/or BarclayHedge CTA index, or listed proxies DBMF/KMLM/WTMF post-2019 via yfinance, regressed on the in-house TSMOM sleeve; rolling 36-month R^2 and residual alpha net of stated fees.

<a id="idea-014"></a>
### IDEA-014 · reserve-satiation-crossing

`signal` · **status: unvalidated** · **12/15**
*source:* [2026/05 · rates_gs_fed-balance-sheet_2026-05-21](2026/05/rates_gs_fed-balance-sheet_2026-05-21.md)
*applies to:* Repo-IORB / SOFR-IORB spreads and their tails; front-end bills; by extension 2s10s and any levered position whose funding leg reprices. Same convex-demand-near-satiation structure applies to collateral specials.
<!-- edges -->
*related:* [IDEA-016](#idea-016) the drain that brings the crossing · [IDEA-039](#idea-039) confounds the same tail · [IDEA-012](#idea-012) trailing buffers undersize it · [IDEA-003](#idea-003) contrast: this one is literal money
*literature:* [bernanke2020](../papers/paper_notes_bernanke2020.md)

**Statement.** The tradeable variable is not the level of reserves but the crossing point: the reserve share at which secured overnight funding crosses from below to above the policy floor. Because reserve demand is convex — flat when abundant, steep near satiation — a slope fitted across the abundant regime understates the near-satiation slope by several multiples, so a planned linear drain overshoots its funding-cost target and funding-stress hedges are systematically underpriced as the crossing approaches.

**Mechanism — who pays, why it persists.** Near satiation reserves stop being substitutable: they are the only asset that settles intraday and the only same-day-certain LCR liquidity, so below the satiation point banks bid for cash rather than lend it and the marginal reserve is worth far more than its interest rate. Constrained parties are named and regulated — LCR-bound and intraday-overdraft-capped banks, plus money funds whose alternative parking has been drained — and the compensated risk is real: providing funding when the system is short is precisely when you cannot exit.

| | | |
|---|:--:|---|
| Economic rationale | **5/5** | A named regulatory constraint creating inelastic demand, a genuinely compensated risk, a breaking point observed twice, and a publicly scheduled supply path. You can name who must pay and why they cannot opt out. |
| Durability | **4/5** | Convexity is rooted in liquidity regulation and settlement plumbing, but the LOCATION of the crossing is policy-adjustable — a standing repo redesign, eSLR change or GSIB recalibration moves it, so the threshold must be re-estimated after each regulatory change. |
| Testability | **3/5** | Verified: IORB resolves; SOFR is in treasury_yields.parquet but raises ValueError; TGCRRATE and TGCR99THPERCENTILE are in neither registry nor lake (public FRED, direct REST only); WRESBAL confirmed unresolvable. Binding gap is instruments, not series — no repo/OIS data, so the spread is testable as a conditioning variable but not as a P&L. |

**Evidence so far.** Weakly in-sample plus one quasi-ex-ante window. Base rate: 2 aggregate funding events in 28 quarters (Sep-2019 at rho = 7.99%; late-2025 at 11.65%). Realized slope estimates from 2026 span -11.6 to -21.5bp per pp of reserve share (OLS on four monthly means: -13.6, R2 = 0.50, n = 4) against the report's implied -3.0bp/pp — every internally consistent pairing is steeper, none identified at that sample size. Post-publication: rho fell 12.276% to 11.625% while the spread moved -7.9bp to -2.0bp — right direction, magnitude ~5x the assumed slope.

**To test later.** FRED TGCRRATE, TGCR99THPERCENTILE, SOFR, SOFR99, IORB, EFFR, WRESBAL, RRPONTSYD, TLAACBW027SBOG (in no registry). Tradeable leg: DGS2/DGS10 plus SHY/IEF/TLT (all resolve). Missing: any repo or OIS instrument series, and money-fund balances (OFR/ICI).

<a id="idea-015"></a>
### IDEA-015 · effective-vs-marginal-rate-refi-runway

`signal` · **status: unvalidated** · **12/15**
*source:* [2026/01 · economics_gs_japan-outlook_2026-01-06](2026/01/economics_gs_japan-outlook_2026-01-06.md)
*applies to:* Sovereign bonds/CDS of post-ZIRP issuers (JGBs, Bunds, Gilts, USTs); corporate credit of 2020-21 termed-out issuers; equity of levered names carrying legacy low-coupon debt.
<!-- edges -->
*related:* [IDEA-028](#idea-028) recompute the ratio first · [IDEA-032](#idea-032) the override that explains it away · [IDEA-021](#idea-021) the other arithmetic-not-behaviour wedge

**Statement.** An issuer's effective interest cost (interest paid divided by debt outstanding) can sit far below the marginal market rate for a decade after rates rise, because the legacy low-coupon stock only reprices as it matures. The spread between marginal and effective rate, combined with the maturity schedule, is a public dated calendar of when reported leverage and coverage must deteriorate regardless of any policy or management decision. Rank issuers by (marginal - effective) x (share of debt maturing within N years).

**Mechanism — who pays, why it persists.** The other side is everyone pricing off trailing debt-service metrics: ratings methodologies, fiscal rules, passive credit indices weighted by face value, screens reading current interest expense. It persists not because the information is hidden — issuance calendars are published — but because of a horizon mismatch: the deterioration is arithmetically certain and precisely dated, yet arrives quarter by quarter over 10-15 years, outside the window over which any participant is compensated. The compensated risk is duration of conviction, not information.

| | | |
|---|:--:|---|
| Economic rationale | **4/5** | Grounded in an accounting identity, stated explicitly in the digest. But the payer is diffuse — short-horizon metric-readers in aggregate — rather than a mandated price-insensitive buyer. Real mechanism, no named forced counterparty. |
| Durability | **5/5** | Rooted in debt maturity structure and sovereign issuance calendars, which change over decades. The runway is literally a published schedule; nothing here can be arbitraged away faster than the bonds mature. |
| Testability | **3/5** | Verified: IRLTLT01JPM156N resolves (monthly). FYOINT, GFDEBTN and the nominal GDP series needed for r_effective are public FRED but unregistered — GDP resolves, GDPC1 does not. Binding gap is the debt maturity profile: public via national DMOs, requires a scraper. Corporate version needs proprietary schedules. |

**Evidence so far.** In-sample, one country, one date: FY2025 effective rate 0.8% vs nominal growth 3.9%, the widest gap since 1980, producing ~-7pp/year of debt/GDP decline, with an asserted 10-15 year refinancing runway. One genuinely out-of-sample observation cuts against the benign reading: the note was written at a 10Y JGB of 2.0% in Jan 2026, and the platform's live pull shows 2.65% by the April 2026 reference month — the marginal rate is rising faster than assumed, shortening the runway. One observation, not a test.

**To test later.** FRED FYOINT, GFDEBTN, nominal GDP to build r_effective; the IRLTLT01*M156N long-yield family for the marginal rate; national DMO issuance/maturity calendars for the redemption profile (public, not in lake). Corporate: issuer interest expense plus maturity schedules from Compustat/CapIQ.

<a id="idea-016"></a>
### IDEA-016 · flat-balance-sheet-is-tightening

`regime` · **status: unvalidated** · **12/15**
*source:* [2026/05 · rates_gs_fed-balance-sheet_2026-05-21](2026/05/rates_gs_fed-balance-sheet_2026-05-21.md)
*applies to:* Front-end rates and funding spreads in any reserve system; sharpest where currency growth is fast — an EM central bank with 8-12%/yr currency growth has a far larger neutral expansion rate and a much faster passive drain.
<!-- edges -->
*related:* [IDEA-014](#idea-014) where the drain is heading · [IDEA-028](#idea-028) measure in the binding unit · [IDEA-042](#idea-042) free float as the denominator
*literature:* [bernanke2020](../papers/paper_notes_bernanke2020.md)

**Statement.** A central bank's neutral asset growth rate is strictly positive and computable from an identity: dA = g_C*C + g_T*TGA + rho*g_B*B. Holding the balance sheet flat therefore drains reserves at (g_C*C + g_T*TGA)/B + rho*g_B per year — 1.16pp of bank assets per year in the US today. 'No change to the balance sheet' is a tightening announcement, and the true policy axis is grow-at-neutral vs grow-below-neutral vs flat, only the first of which is neutral.

**Mechanism — who pays, why it persists.** Currency in circulation is a non-interest-bearing liability growing with nominal GDP, and the government's cash balance is set by fiscal cash management — both are senior claims on the asset side, leaving reserves as the residual. On the other side the constrained party is the regulated banking system: LCR and intraday-settlement requirements make reserve demand scale mechanically with bank assets, so banks cannot choose to need proportionally fewer reserves as they grow. The mispricing persists because policy is communicated, headlined and traded in balance-sheet-size units, in which a flat print reads as neutral.

| | | |
|---|:--:|---|
| Economic rationale | **4/5** | An identity plus a named constrained counterparty (banks whose regulatory liquidity requirement scales with their own assets). Not 5 because rho* — the level banks actually need — is a demand parameter, not an accounting one, and it is exactly the parameter the note cannot identify. |
| Durability | **5/5** | Pure balance-sheet plumbing. Currency demand and government cash management change over years; the identity never does. Only a structural collapse in cash demand (CBDC) would lower the neutral rate — which would not break the framework. |
| Testability | **3/5** | Downgraded from the extractor's 4. Verified: WALCL resolves, but WRESBAL and WTREGEN are in fed_liquidity.parquet yet raise ValueError, CURRCIR is in neither registry nor lake (and is ~10 months stale on FRED), and TLAACBW027SBOG is in neither. Three of four inputs are unreachable through get_data. |

**Evidence so far.** Arithmetic reconciliation against live FRED, not a return test: the identity gives \$24.2bn/mo vs the printed \$25bn (3.2% gap), component-by-component \$9.06/\$10.59/\$4.55bn vs \$9/\$11/\$5; the drift identity gives -1.16pp/yr vs the note's 1.2pp/yr; and 'about 4pp, back to the 2019 lows, by end of the decade' reconciles exactly to the 18-Sep-2019 trough of 7.99% arriving in 3.37 years. In-sample verification of the accounting; no evidence on what it earns.

**To test later.** FRED CURRCIR (prefer the H.4.1 currency line given staleness), WTREGEN, TLAACBW027SBOG, WALCL, WRESBAL, WLRRAL. Cross-country: ECB weekly financial statement banknote and government-deposit lines; BoJ current-account balances.

<a id="idea-017"></a>
### IDEA-017 · capital-structure-valuation-wedge

`signal` · **status: unvalidated** · **12/15**
*source:* [2026/07 · crossasset_gs_goal-kickstart_2026-07-27](2026/07/crossasset_gs_goal-kickstart_2026-07-27.md)
*applies to:* US/EUR IG and HY credit vs equity of the same issuer universe. Generalizes wherever a capped and an uncapped claim on the same cash flows are separately benchmarked (preferreds vs common, mezzanine vs equity tranche, sub debt vs equity).
<!-- edges -->
*related:* [IDEA-027](#idea-027) attribution picks the instrument · [IDEA-044](#idea-044) is the extreme growth-carried?
*literature:* [fama_french_1993](../papers/paper_notes_fama_french_1993.md) · [ivashina2015](../papers/paper_notes_ivashina2015.md)
*study:* [2026-03-29_expected_returns_ilmanen](../studies/2026-03-29_expected_returns_ilmanen/er_book_briefing.md)

**Statement.** When credit spreads sit in their richest decile while equity multiples sit near their historical median, allocate corporate risk to equity rather than credit: both are claims on the same firms' cash flows, but the capped instrument offers historically thin compensation while the uncapped one does not. The percentile SPREAD between the two, not either level in isolation, is the signal.

**Mechanism — who pays, why it persists.** Credit's marginal buyer is mandate-constrained: insurers and pensions matching liabilities, ratings-bucketed portfolios, and IG/HY index funds must own the asset class regardless of spread and are structurally forbidden from substituting equity. Equity buyers face no such constraint. A reach-for-yield bid compresses spreads without compressing equity multiples, and persists because the constraint is regulatory and mandate-based. Not free — you accept more idiosyncratic and drawdown risk; the claim is only that you are paid more per unit of it.

| | | |
|---|:--:|---|
| Economic rationale | **4/5** | Named genuinely constrained counterparty. Docked from 5 because forward-P/E percentiles and OAS percentiles are not on a common risk-premium scale — the comparison is percentile-to-percentile, a convenience; a cleaner version compares equity risk premium to spread-implied default compensation net of expected loss. |
| Durability | **4/5** | Mandates, ratings buckets and LDI reach-for-yield change on a decade timescale. Docked because the percentile mapping is contaminated by index composition drift — post-2009 HY quality improved and duration shortened, so a given spread percentile no longer represents the same risk. |
| Testability | **4/5** | Verified directly: BAMLH0A0HYM2 returns data through get_data (154 rows on test) and BAMLC0A0CM is registered — the credit leg is NOT a gap, contrary to the source digest. HYG and LQD resolve. Genuine gap is the equity leg: 12m forward P/E needs consensus EPS. Substitutes: Shiller CAPE, trailing earnings, earnings yield minus real yield. |

**Evidence so far.** Anecdotal, single cross-sectional snapshot: US HY 279bp at the 95th percentile, EUR HY 256bp at the 98th, IG at the 91st, S&P 12m forward P/E 19.8x at the 58th. No ex-ante test of the wedge as a predictor of subsequent credit-vs-equity relative returns appears anywhere — the wedge justifies a current stance, it is not a validated signal.

**To test later.** FRED BAMLH0A0HYM2, BAMLC0A0CM, BAMLHE00EHYIOAS (EUR HY, unregistered); DFII10; Shiller CAPE monthly; ^GSPC, HYG, LQD total returns for the forward-return leg. Gap: consensus 12m forward EPS; issuer-matched credit/equity pairs for the clean same-cash-flow version.

<a id="idea-018"></a>
### IDEA-018 · effective-breadth-discount-for-self-correlated-strategies

`method` · **status: unvalidated** · **12/15**
*source:* [2013 · factor_aqr_managed-futures_2013](2013/factor_aqr_managed-futures_2013.md)
*applies to:* Any multi-market strategy whose credibility rests on breadth: cross-asset trend, cross-asset carry, global value, multi-country macro signals.
<!-- edges -->
*related:* [IDEA-041](#idea-041) not merged: this one has a code path · [IDEA-037](#idea-037) the breadth claim it discounts · [IDEA-013](#idea-013) same note · [IDEA-010](#idea-010) same inflated statistic · [IDEA-003](#idea-003) compounds: both inflate the same t-stat · [IDEA-009](#idea-009) hedge value and independence in tension
*literature:* [baltussen2021](../papers/paper_notes_baltussen2021.md)
*study:* [2026-06-17_advances_financial_ml](../studies/2026-06-17_advances_financial_ml/study_hypotheses.md)
*platform:* [cross_validation.py](../../../alpha_research/backtests/stats/cross_validation.py)

**Statement.** When breadth is offered in place of a mechanism, discount it by the strategy's own cross-market position correlation. 67 markets x 135 years is not 9,000 independent observations if the strategy systematically holds the same directional bet in every market at once. And the property that most compresses effective breadth is precisely the property being sold: crisis alpha exists because all sleeves go short together.

**Mechanism — who pays, why it persists.** Not a market edge but a research-epistemics correction with a real cost of being wrong: over-stated effective sample size inflates t-stats, deflated-Sharpe and MinBTL calculations, and therefore capital allocation. It persists as an error because breadth is rhetorically persuasive and computing effective breadth requires the strategy's position matrix, which readers of a published note never receive. The sharp version: a strategy's hedge value and its statistical independence are in direct tension — you cannot claim both at full strength.

| | | |
|---|:--:|---|
| Economic rationale | **3/5** | No counterparty — an evaluation technique, scored on soundness rather than on who pays. The logic is exact (effective N falls with average pairwise position correlation) and it makes a falsifiable prediction about the note's own numbers, but it corrects a claim rather than generating one. |
| Durability | **5/5** | A statistical identity. Applies unchanged to any future strategy, market or dataset. |
| Testability | **4/5** | Upgraded from 3: verified that alpha_research/backtests/stats ships cross_validation.py, minimum_backtest.py and multiple_testing.py, and runners/ contains working position-producing entrypoints. Fully computable on any strategy we build; not verifiable against the source note's 67-market result, whose position data is unpublished. |

**Evidence so far.** None. The digest asserts 67 markets x 135 years as the anti-data-mining defence and reports no effective-sample or cross-market position-correlation adjustment. This is a critique of the note's inference, not a finding taken from it.

**To test later.** The strategy's own signed-position matrix over time from any runner in alpha_research/backtests/runners/; average pairwise position correlation by period; a modification to the deflated-Sharpe / MinBTL inputs in alpha_research/backtests/stats/cross_validation.py to consume effective rather than nominal sample size.

<a id="idea-019"></a>
### IDEA-019 · selector-must-span-total-expected-return

`method` · **status: unvalidated** · **12/15**
*source:* [2026/07 · macro_gs_em-trader_2026-07-30](2026/07/macro_gs_em-trader_2026-07-30.md)
*applies to:* Any cross-sectional ranking — FX carry, equity factor scores, credit relative value, commodity roll yield, and in-house signal construction generally.
<!-- edges -->
*related:* [IDEA-003](#idea-003) the moments a selector must span · [IDEA-023](#idea-023) the funder leg it misses · [IDEA-026](#idea-026) the horizon it misses
*literature:* [koijen_carry_2018](../papers/paper_notes_koijen_carry_2018.md)
*platform:* [fx_carry proposal — ranks on raw rate diffs](../../../alpha_research/research/strategies/fx_carry_2026-03-13_conditional/proposal.md) · [sector_rotation_v1 manifest](../../../alpha_research/research/pool/sector_rotation_v1/manifest.yaml)

**Statement.** Before trusting any cross-sectional ranking statistic, rank-correlate it against the total expected return it is meant to proxy, computed on the same author's own inputs. A selector built from one component of expected return while a forecast of the other exists will systematically misselect: here carry vs the firm's own 12m forecast total return has Spearman +0.19 across 21 currencies (+0.47 dropping two capital-controlled names), and the resulting book picks a leg forecast to lose 2.33% over one forecast to make 6.11%.

**Mechanism — who pays, why it persists.** A research-process control, not a market edge, and scored as such. Its value comes from a structural asymmetry in how selectors are chosen: carry, roll, book yield and spread are observable today at zero cost, while the drift/spot/default component requires a forecast — so selection metrics gravitate to the observable half and the omission is systematic rather than random. Nobody is on the other side; the payer is the analyst's own future P&L. The check is a two-line rank correlation that detects the failure before any backtest.

| | | |
|---|:--:|---|
| Economic rationale | **2/5** | Mechanically true and useful, but no compensated risk and no constrained counterparty — it prevents a loss rather than earning a premium. Scoring it higher would misrepresent what kind of claim it is. |
| Durability | **5/5** | A consistency check on a selector; cannot be arbitraged and does not decay with regime. The specific failure recurs — this repo's own fx_carry_2026-03-13_conditional proposal ranks on raw rate differentials with no drift term (verified present). |
| Testability | **5/5** | Requires only two vectors: selector score and any expected-return proxy. Verified runnable today against every runner in alpha_research/backtests/runners/ (sector_rotation.py, vol_conditioned_reversal.py) with no new data at all. |

**Evidence so far.** In-sample, single vintage, and against a forecast rather than realised returns. The +0.19/+0.47 Spearman is computed on one forecast table dated 29 Jul 2026, so it demonstrates that two rankings disagree — it does not establish that the carry-only ranking loses money. No historical version exists.

**To test later.** Nothing new for the audit. For a historical version: cross-sectional signal scores per date from any existing runner, plus realised forward returns at the matching horizon from data/market_data/prices/. Reporting the time series of that rank correlation is a natural addition to the review pipeline.

<a id="idea-020"></a>
### IDEA-020 · buy-convexity-back-inside-the-risk-factor

`structure` · **status: unvalidated** · **11/15**
*source:* [2025/11 · rates_gs_vol-strategies_2025-11-13](2025/11/rates_gs_vol-strategies_2025-11-13.md) , [2026/07 · crossasset_gs_goal-kickstart_2026-07-27](2026/07/crossasset_gs_goal-kickstart_2026-07-27.md) **← independent arrival in 2+ reports**
*applies to:* Rates vol (short gamma vs long vega), equity vol (front-month vs back-month), FX (short JPY/CHF carry vs long its convexity), credit (near-dated tranche risk vs far-dated protection); any premium-harvesting sleeve with a term structure of convexity.
<!-- edges -->
*related:* [IDEA-003](#idea-003) why Sharpe cannot score it · [IDEA-034](#idea-034) carry-positive alternative · [IDEA-046](#idea-046) the event-dated version · [IDEA-031](#idea-031) when convexity is cheap · [IDEA-002](#idea-002) the same geometry from the buy side · [IDEA-023](#idea-023) the funding leg's convexity
*literature:* [carr_wu_vrp_2009](../papers/paper_notes_carr_wu_vrp_2009.md) · [rates_vrp](../papers/paper_notes_rates_vrp.md)
*study:* [2026-06-24_volatility_workstation](../studies/2026-06-24_volatility_workstation/README.md)

**Statement.** Manufacture a carry sleeve's diversification inside the sleeve by pairing the short-convexity leg with long convexity bought at the point of the same risk factor where mandated protection demand is NOT concentrated — short front gamma against long back-dated vega, or short a funding currency for carry while long its calls. Paying away part of the carry to buy the tail back from the same market converts a procyclical strategy into a near-zero-correlation one, and that convexity is cheapest exactly when carry is widest and short positioning most crowded.

**Mechanism — who pays, why it persists.** Two funders at two horizons. Near-dated gamma and near-term protection are rich because end users concentrate crash-protection buying where their accounting and mandate windows sit; far convexity is comparatively cheap because far fewer natural buyers extend out the curve. In FX the same shape appears as the carry-crash asymmetry: carry earns the differential because it is short a negatively skewed payoff, and the crash IS the price of the carry — yet implied vol is lowest in calm wide-carry regimes when leveraged short positioning is most crowded and the unwind most self-reinforcing. Both are segmentation effects driven by where hedging mandates live, and mandates move on regulatory timescales.

| | | |
|---|:--:|---|
| Economic rationale | **5/5** | The FX half names both sides explicitly — carry sellers paid to bear a negatively skewed crash payoff, vol sellers underpricing the tail in quiet regimes — and the rates half names where protection demand concentrates. Independent arrival from a rates-vol note and a cross-asset note, neither of which states the reconciliation itself. |
| Durability | **4/5** | UIP failure and carry-crash dynamics are documented across decades and pairs; the identity of the funding currency rotates but the structure does not. Docked because the vol term-structure slope that funds the long-vega leg is compressible by crowding — the payoff shape survives, the return may not. |
| Testability | **2/5** | Verified: there is NO options pricing or P&L module anywhere in alpha_research/backtests — only the exploratory alpha_research/notebooks/vix_futures_options_research.ipynb. FX implied vol and 25-delta risk reversals are absent. Spot-side proxies (USDJPY=X, CFTC positioning) test whether drawdown scales with carry width, but 'is the convexity cheap?' cannot be answered here. The polygon connector exists but implements equity aggregates only. |

**Evidence so far.** Rates half, in-sample portfolio statistics (Exhibits 16-17, 2003+): short gamma ~6.7% return / ~11.2% vol; long vega ~2% / ~4%; vol-weighted blend ~6.4% / ~6.7%, with blend correlation near zero across stocks, bonds and 60/40 — but no skew, kurtosis or max drawdown reported for any of the three, and the vol weights appear chosen with full-sample knowledge. FX half: no evidence at all — it is an inference from the cross-asset note's internal inconsistency (a 165 weaker-yen 12m base case alongside a long-JPY-call tail hedge, never reconciled), with strong prior-literature support.

**To test later.** A swaption vol surface by expiry x tenor (proprietary), or a listed proxy: CBOE VIX futures curve (free settlements) plus SPX option chains; JPY/CHF 1m-3m ATM implied vol and 25-delta risk reversals (dealer data). Plus an options pricing / delta-hedging P&L engine built inside alpha_research/backtests — a larger undertaking than any registry addition in this pool.

<a id="idea-021"></a>
### IDEA-021 · administered-price-cpi-wedge

`signal` · **status: unvalidated** · **11/15**
*source:* [2026/01 · economics_gs_japan-outlook_2026-01-06](2026/01/economics_gs_japan-outlook_2026-01-06.md)
*applies to:* Inflation swaps, linkers and front-end rates in any jurisdiction with active fiscal price intervention: Japan now, Euro-area energy caps 2022-23, UK energy price guarantee, US ACA/health-CPI methodology shifts.
<!-- edges -->
*related:* [IDEA-028](#idea-028) decompose the print · [IDEA-015](#idea-015) the other arithmetic-not-behaviour wedge

**Statement.** A measurable share of any CPI print is set by legislation rather than markets — fuel-tax changes, tuition waivers, capped utilities, administered health prices. These enter the index with a magnitude and a date that are public in advance and exit exactly 12 months later. Forecast the legislated wedge separately from the market-priced core, and trade the divergence between the mechanical path of the published fixing and the smoothed path priced by inflation markets and embedded in backward-looking policy reaction functions.

**Mechanism — who pays, why it persists.** Inflation swaps and linkers settle on the published fixing, so a mechanically known distortion in the fixing is a cash-settled near-certainty. The constrained parties are LDI and pension hedgers who must hold index-linked exposure regardless of what drives the index, and dealers who hedge fixings on smoothed seasonal assumptions. A second layer sits at the central bank: a reaction function anchored on realised core eases into a legislated disinflation and then meets the base-effect reversal on the anniversary. Persists because capturing it requires reading budget legislation against basket weights — unglamorous, jurisdiction-specific work.

| | | |
|---|:--:|---|
| Economic rationale | **4/5** | Names a genuinely price-insensitive counterparty — mandated linker holders settling on a fixing they do not choose — and a mechanically knowable input. Short of 5 only because the wedge is often partially priced by specialist inflation desks who do exactly this work. |
| Durability | **4/5** | The plumbing (legislated prices entering and exiting on a public calendar with published weights) is structural. What varies is whether governments are actively intervening: high in a cost-of-living-politics regime, near zero otherwise. Episodic rather than always-on. |
| Testability | **3/5** | Verified: CPIAUCSL and T10YIE resolve; T5YIE is in treasury_yields.parquet but raises ValueError. US/EA component indices plus BLS relative-importance weights or Eurostat HICP components are free and directly pullable — that version is a 5. Japan specifically is a 1: every FRED-mirrored OECD Japan CPI series died in June 2021, leaving only the annual World Bank proxy. |

**Evidence so far.** Anecdotal, single instance: ~-0.5pp of 2026 Japan core CPI attributed to two legislated measures (gasoline tax rate elimination, free high-school tuition), and this wedge is what pulls core below 2% by mid-2026, which in turn licenses the semiannual rather than accelerated BOJ hiking path. No backtest, no historical wedge series.

**To test later.** CPI component indices with basket weights (FRED subindices + BLS relative importance; Eurostat HICP; Japan via e-Stat — gap); a hand-built calendar of legislated price measures with effective dates and estimated pp contributions from budget documents; inflation breakevens (T5YIE, T10YIE) as free proxies for dealer fixings.

<a id="idea-022"></a>
### IDEA-022 · forced-flow-response-function

`method` · **status: unvalidated** · **11/15**
*source:* [2012 · factor_bridgewater_risk-parity_2012](2012/factor_bridgewater_risk-parity_2012.md) , [2026/06 · flows_gs_cta-bond-futures_2026-06-09](2026/06/flows_gs_cta-bond-futures_2026-06-09.md) **← independent arrival in 2+ reports**
*applies to:* Levered risk-parity, vol-target and managed-volatility portfolios cross-asset; the flow lands in equity index and government bond futures. Applies wherever CTA/vol-target AUM is material relative to depth.
<!-- edges -->
*related:* [IDEA-006](#idea-006) not merged: OPPOSITE sign · [IDEA-040](#idea-040) when the cohort has no room left · [IDEA-036](#idea-036) how synchronised the triggers are · [IDEA-001](#idea-001) the portfolio that forces it
*literature:* [bridgewater2012](../papers/paper_notes_bridgewater2012.md)

**Statement.** For any cohort that trades by a replicable rule under a capacity or volatility constraint, the research deliverable is the conditional flow response function — projected net flow under up/base/down price paths at multiple horizons — not the estimated position level. The level is a stock; the derivative with respect to price is the tradable object. Any inverse-volatility sizing rule carrying leverage converts a volatility spike into a mechanical, calendar-predictable sale, so build the deleveraging schedule explicitly and choose to pre-empt it or supply liquidity into it.

**Mechanism — who pays, why it persists.** The constrained party is the fund itself: its trades are pre-committed by a published rule, a volatility target and a margin agreement, so at execution it is price-insensitive — it must trade whether or not the price is attractive, and cannot wait for a better one. The other side is dealers and liquidity providers warehousing that flow and charging for immediacy. It persists because the rules are written into risk mandates and margin documents that cannot be suspended mid-shock — the same reason it is exploitable is the reason it cannot be fixed — and because threshold-crossing timing is uncertain, so front-running means holding an unhedged position through what may be a false breakout.

| | | |
|---|:--:|---|
| Economic rationale | **4/5** | A genuinely forced, price-insensitive seller with a documented trigger, arrived at independently from a 2012 risk-parity note and a 2026 CTA flow note. Not 5 because the flow only moves price if dealer capacity is finite at that moment — that intermediate link is asserted in both sources, never measured — and the counter-trade is widely watched. |
| Durability | **4/5** | Margin rules and vol-target mandates are structural and have grown. But crowding decays the timing edge specifically as more participants model the same trigger. |
| Testability | **3/5** | Corrected downward. The trigger is computable from prices (SPY/TLT realized vol, VIXCLS, a rebalance calendar — all resolve). But ZB/ZN/ZF/ZT exist ONLY as IBKR live-feed definitions in core/market_data_service.py; ZN raises ValueError and no bond-futures series is in the lake, so even the US panel must be ETF-proxied (TLT/IEF/SHY resolve). European contracts absent entirely. Aggregate flow sizing needs CFTC COT (public, no connector anywhere in the repo) and fund AUM (proprietary). |

**Evidence so far.** Near-zero. The CTA note reports one week of model output vs the prior week — 1-month projected flow +\$36.7m DV01 to -\$3.8m DV01, a sign flip — with no hit rate, no out-of-sample record, and a source disclaimer stating the simulated backtest carries 'no assurance'. The risk-parity note offers only that risk parity 'drew down hard' in 2022 and prescribes 2-3x bond leverage with monthly rebalancing, which is the trigger machinery, not evidence. No flow, positioning or AUM data in either.

**To test later.** Continuous front-month settles for ZN/ZB/ZF/ZT (gap — IBKR live only), Bund RX, Bobl OE, Schatz DU, long Gilt (vendor gap); rolling realized vol per contract; DV01 per contract; SPY/TLT realized vol and ^VIX for the ETF-proxy version; CFTC COT for the positioning leg.

<a id="idea-023"></a>
### IDEA-023 · funding-leg-as-first-order-choice

`structure` · **status: unvalidated** · **11/15**
*source:* [2026/07 · macro_gs_em-trader_2026-07-30](2026/07/macro_gs_em-trader_2026-07-30.md)
*applies to:* Any carry book: EM FX, G10 FX, and by extension cross-currency-funded credit, rates or commodity carry.
<!-- edges -->
*related:* [IDEA-019](#idea-019) selector must span the funder · [IDEA-020](#idea-020) the convexity of the funding leg · [IDEA-026](#idea-026) annualise the carry pickup · [IDEA-011](#idea-011) the official reaction on the funding leg
*literature:* [asness2013_fx](../papers/paper_notes_asness2013_fx.md) · [koijen_carry_2018](../papers/paper_notes_koijen_carry_2018.md) · [du_tepper_verdelhan2018](../papers/paper_notes_du_tepper_verdelhan2018.md)
*study:* [2026-03-27_global_macro_trading_gliner](../studies/2026-03-27_global_macro_trading_gliner/gmt_book_briefing.md)
*platform:* [fx_carry proposal](../../../alpha_research/research/strategies/fx_carry_2026-03-13_conditional/proposal.md)

**Statement.** In any carry book the short (funding) leg is a first-order decision, not a residual: switching funder changes the carry numerator and the volatility denominator simultaneously, and because the USD is the dominant common factor in EM FX volatility, funding in a non-USD currency can raise carry and lower cross volatility at once. For an identical MXN long, carry-to-vol is 2.07x higher funded in EUR than USD (1.49x more carry x 1.39x less vol), and EUR-funded vol is lower for 8 of 9 legible crosses.

**Mechanism — who pays, why it persists.** The dollar is the global invoicing, funding and reserve numeraire, so a large share of every EM cross's variance is common dollar-factor variance rather than idiosyncratic; expressing the same long against a different funder nets part of that factor out. Not an arbitrage — a construction choice most books never make because the constraint is institutional: mandates and total-return benchmarks are USD-denominated, prime-broker margining and NDF liquidity are USD-centric, and internal risk systems report vs USD. The constrained party is the USD-benchmarked investor who cannot express a non-USD funder even when it dominates ex ante, and knowing this does not let a benchmarked account act on it.

| | | |
|---|:--:|---|
| Economic rationale | **4/5** | Names a genuinely constrained counterparty (USD-benchmarked mandates and USD-centric margining plumbing) and the vol effect follows from a documented common dollar factor. Not 5 because it is a construction improvement, not a compensated risk — nobody pays you for it; you remove an uncompensated common exposure. |
| Durability | **4/5** | Downgraded from the extractor's 5 on its own counterexample: TWD's EUR-funded vol was 36% HIGHER, so this is a strong prior, not a law — it fails where the local currency is itself managed against the dollar. Dollar dominance in invoicing and benchmark convention is decade-scale, so the sign is anchored; the magnitude is not. |
| Testability | **3/5** | Verified: all seven G10 crosses plus DX-Y.NYB resolve or sit in fx.parquet, so the G10 version runs today (though fx.parquet starts 2024-02 — dedicated EURUSD_X/USDJPY_X/USDCAD_X/USDCHF_X/NZDUSD_X parquets and yfinance fallback extend it). EM version blocked twice: USDBRL=X confirmed raising ValueError despite being defined in core/market_data_service.py FX_TICKERS (~15-line registry fix), and 12m forward points or NDF quotes are nowhere on the platform. COP, CLP, PEN, CZK, ILS, RON absent from both registries. |

**Evidence so far.** In-sample, single snapshot. The 2.07x decomposition is an arithmetic identity from one date's carry column and ratio table; the 8-of-9 count is a one-date cross-section with no time series and no return test. The internal cross-check is real but limited: five currencies quoted against both funders imply the same USD-EUR differential (CZK 1.5, HUF 1.4, PLN 1.4, RON 1.4, RUB 1.6pp; mean 1.46, dispersion 0.2), validating the arithmetic, not the trade.

**To test later.** Spot for 13 EM crosses plus EURUSD=X to construct EUR-funded crosses; 12m outright forwards or NDF points per currency (or 12m money-market rates) — vendor or central-bank published, currently absent. Registry additions to alpha_research/quant_data/ticker_map.py for the crosses already defined in core/market_data_service.py. Minimum viable test: G10 only, rebuilding each long against USD, EUR, JPY and CHF funders and comparing realised Sharpe.

<a id="idea-024"></a>
### IDEA-024 · horizon-match-regressors-to-instrument

`method` · **status: unvalidated** · **11/15**
*source:* [2025/11 · rates_gs_vol-strategies_2025-11-13](2025/11/rates_gs_vol-strategies_2025-11-13.md)
*applies to:* Any term structure explained by a factor model: implied vol surfaces, the yield curve, credit spread curves by maturity bucket, commodity forward curves.
<!-- edges -->
*related:* [IDEA-033](#idea-033) residual is model error at the long end · [IDEA-045](#idea-045) the state variable it scopes · [IDEA-007](#idea-007) the term-premium component it scopes
*literature:* [diebold2006](../papers/paper_notes_diebold2006.md) · [nelson1987](../papers/paper_notes_nelson1987.md) · [svensson1994](../papers/paper_notes_svensson1994.md)
*study:* [2026-03-26_fixed_income_relative_value_analysis_2e](../studies/2026-03-26_fixed_income_relative_value_analysis_2e/firv_book_briefing.md)

**Statement.** A factor model's explanatory power is not uniform across a term structure — it holds only where the horizon of the explanatory variables spans the horizon of the instrument. Cyclical macro variables explain short-dated implied vol well (adj. R^2 ~0.7-0.85) and long-dated poorly (~0.3-0.4), because long-dated instruments price regime-change risk beyond any forecast panel's reach. Report fit across the whole grid, and refuse to let a short-horizon result be generalised in prose to 'the surface'.

**Mechanism — who pays, why it persists.** Structural rather than behavioural: consensus forecast panels extend only one to two years, so by construction they contain zero information about states ten to thirty years out. What remains in the long-dated instrument is the price of regime uncertainty — a different risk, plausibly bearing a different premium and facing different buyers, since pension and insurance ALM hedging is the natural long-dated bid and is price-insensitive in a way no cyclical macro variable can proxy. Consequence: the residual from a cyclical fair-value model is a meaningful premium estimate at the short end and mostly model error at the long end.

| | | |
|---|:--:|---|
| Economic rationale | **3/5** | The information-horizon argument is structural and near-tautological, and it names a plausible long-dated counterparty (ALM hedgers). But it is a specification rule that scopes other people's signals rather than an edge with a payer — and the source note does not make this argument; it is the reader's inference from the R^2 grid against the prose. |
| Durability | **5/5** | A property of what forecast data exists, not of any market regime. Forecast panels will keep ending at one to two years, and long-dated instruments will keep pricing beyond that. |
| Testability | **3/5** | Verified: DGS2, DGS5, DGS10, DGS30 resolve, but DGS1 and DGS20 sit in treasury_yields.parquet and raise ValueError. The yield-curve replication (adj. R^2 decaying with maturity) needs SPF dispersion and NY Fed HLW r* — both public, both unregistered. The vol-surface version needs swaption grids and is out of reach. |

**Evidence so far.** In-sample, full-sample adj. R^2 across the expiry x tenor grid (Exhibit 11): roughly 0.7-0.85 for 1m-1y expiries across most tenors, degrading to 0.3-0.4 at 30y tenor and 10y+ expiry. The decay is in the exhibit; the scope-limitation reading is inference, since the prose generalises the strong fit to 'the surface' more broadly than the exhibit supports.

**To test later.** Yield-curve replication: DGS1/2/5/10/30, Philly Fed SPF forecast dispersion (public, unregistered), NY Fed HLW r* (public, unregistered). Vol-surface version: swaption ATM vol grid by expiry x tenor (proprietary).

<a id="idea-025"></a>
### IDEA-025 · sharpe-gain-is-diversification-not-leverage

`method` · **status: unvalidated** · **11/15**
*source:* [2012 · factor_bridgewater_risk-parity_2012](2012/factor_bridgewater_risk-parity_2012.md)
*applies to:* Any levered vol-targeted or risk-budgeted portfolio, in any market or currency where the financing leg is priced separately from the asset leg.
<!-- edges -->
*related:* [IDEA-008](#idea-008) not merged: diagnostic vs return source · [IDEA-001](#idea-001) the correlation that fails with financing · [IDEA-004](#idea-004) the identity it corrects
*literature:* [frazzini_pedersen_bab_2014](../papers/paper_notes_frazzini_pedersen_bab_2014.md)

**Statement.** Leverage is Sharpe-neutral before financing costs and Sharpe-negative after, so none of a levered balanced portfolio's claimed improvement comes from leverage itself — all of it comes from the correlation matrix. The right diagnostic is the break-even financing spread at which the levered balanced portfolio stops beating the unlevered concentrated one; that spread is the actual margin of safety.

**Mechanism — who pays, why it persists.** The financing counterparty — prime broker, repo desk, or the futures basis — extracts a spread that is the mirror of the leverage-aversion premium; the levered holder keeps the difference. The trap is correlated failure: financing spreads widen and stock-bond correlation turns positive in the SAME inflation or liquidity shock, so the cost leg and the diversification leg break together. Unlevered summary statistics hide this convexity, which is why framework notes that never price the financing leg systematically overstate the edge.

| | | |
|---|:--:|---|
| Economic rationale | **3/5** | Downgraded from the extractor's 4. A named cost-payer and a real correlated-failure channel, but it identifies where the edge is NOT — derivative of [IDEA-008](#idea-008) and [IDEA-001](#idea-001) rather than a source of return in its own right. |
| Durability | **5/5** | Scale-invariance of the Sharpe ratio is algebra. The joint blow-out of financing spreads and cross-asset correlation in stress is a structural feature of funding markets, repeatedly observed. |
| Testability | **3/5** | DFF resolves; SOFR is in treasury_yields.parquet but raises ValueError. The achievable financing cost — futures-implied rate, PB spread, ETF borrow — is not in the lake at all. A public proxy exists via ES and ZN calendar spreads but is not ingested, so the honest break-even is one data source away. |

**Evidence so far.** None. The digest reports the 'leverage improves Sharpe' claim without derivation or cost accounting; this idea is a correction to it, not a finding from it.

**To test later.** Asset returns as in [IDEA-004](#idea-004); FRED SOFR, EFFR, DTB3; ES and ZN front/back calendar spreads to back out implied financing (gap); FRED NFCI (present in macro_indicators.parquet but unregistered) or a TED-style spread as a funding-stress conditioner.

<a id="idea-026"></a>
### IDEA-026 · annualise-the-level-claim-against-the-competing-rate

`risk` · **status: unvalidated** · **11/15**
*source:* [2026/04 · macro_gs_jpy-macro-trading_2026-04-07](2026/04/macro_gs_jpy-macro-trading_2026-04-07.md) , [2026/07 · flows_gs_japan-savings-jgb-demand_2026-07-20](2026/07/flows_gs_japan-savings-jgb-demand_2026-07-20.md) , [2026/07 · macro_gs_em-trader_2026-07-30](2026/07/macro_gs_em-trader_2026-07-30.md) **← independent arrival in 2+ reports**
*applies to:* Any negative-carry RV position (curve trades, cash-futures basis, credit curves, commodity calendars); any carry-vs-value ranking (FX, credit spread vs expected default drift, commodity roll vs inventory normalisation); any government bond, FX or equity market on official-flow, SWF-reallocation or QT/issuance-remit headlines.
<!-- edges -->
*related:* [IDEA-019](#idea-019) same class of selector error · [IDEA-023](#idea-023) carry net of the funder · [IDEA-038](#idea-038) level vs pace is the same split · [IDEA-042](#idea-042) size the flow per unit time · [IDEA-002](#idea-002) a target published with no horizon · [IDEA-029](#idea-029) annualise before trading it
*literature:* [koijen_carry_2018](../papers/paper_notes_koijen_carry_2018.md) · [asness_value_momentum_2013](../papers/paper_notes_asness_value_momentum_2013.md)
*study:* [2026-03-26_fixed_income_relative_value_analysis_2e](../studies/2026-03-26_fixed_income_relative_value_analysis_2e/firv_book_briefing.md)
*platform:* [fx_carry proposal](../../../alpha_research/research/strategies/fx_carry_2026-03-13_conditional/proposal.md)

**Statement.** Every level claim must be converted to a per-unit-time rate through its delivery or reversion horizon and compared against the competing rate over the same period, before it becomes a position. Three forms: target divided by carry defines an implicit maximum holding period and therefore an implicit stop; a valuation gap becomes an annual drag of gap x (1 - 2^(-1/h)) that must be netted against carry pickup before ranking; and an announced flow effect delivered over years must be divided by that horizon and set against the instrument's realised weekly volatility. A published target with no horizon has not specified a trade.

**Mechanism — who pays, why it persists.** Different counterparty in each form, same arithmetic. The carry receiver is paid to be patient and is compensated precisely for the convergence not happening on schedule — a negative-carry convergence trade is economically a long option on FAST convergence with the carry as premium, so expected return depends on the SPEED of the move, not just its size. In the valuation form the payer is the horizon mismatch itself: the trade is evaluated over 3-12 months while reversion has a 3-5 year half-life, so the drag never appears inside the evaluation window. In the flow form the payer is discretionary, event-driven money pricing a stock effect within hours while the quantity arrives as a rate over years — you are compensated for supplying liquidity to headline demand.

| | | |
|---|:--:|---|
| Economic rationale | **3/5** | Three independent arrivals of one operation, which is itself evidence the omission is systematic. But in all three forms nobody is forced onto the other side — headline chasers can decline to chase, and the carry receiver is fairly compensated rather than mispricing. It corrects your own expected return; it does not extract one. |
| Durability | **4/5** | The arithmetic is timeless and the horizon-mismatch cause is structural, but the fade version is competable — nothing stops more macro funds running the same three lines — and the half-life parameter h is unstable enough (the PPP puzzle) that the specific drag number never transfers. |
| Testability | **4/5** | General rule testable on any spread in the lake with a computable roll/carry: DGS2/DGS5/DGS10/DGS30 all resolve for a UST curve-trade test bed. BIS REER is public for the valuation-gap version, with half-life estimable per currency from an AR(1) on the REER itself. Specific instances blocked: 10s40s JGB carry needs a JGB curve and repo; 30y JGB asset-swap spreads have no public feed at all. |

**Evidence so far.** Arithmetic on single instances, no tested version. Carry form: 0.83bp/month against a 148bp-to-100bp target burns ~10bp/year, 21% of total target P&L per year — net of carry the flattener returns 38bp at 12 months and 28bp at 24; neither the December nor the April note states a horizon anywhere. Valuation form: long-COP/short-CLP earns 9.6pp carry against a 37.1pp valuation spread running the wrong way, netting ~-5%/yr at h=4 (7.65/5.90/4.80pp at h=3/4/5 — the parameter is doing the work), while the same book's other legs were valuation-neutral at -0.21pp, so the effect is pair-specific. Flow form: 3-6bp over 2-4 years = 0.014-0.058bp/week against an 8bp one-week realised round trip, a 0.2-0.7% signal-to-noise ratio, with the spread at its richest print in the Jan-25 to Jul-26 window; the fade was never tracked to resolution.

**To test later.** UST curve via FRED DGS2/5/10/30 with roll-down carry for the general test; BIS broad REER monthly (public) plus AR(1) half-lives for the valuation form; announcement date/time series (hand-collected) plus trailing realised weekly vol for the flow form. Blocked specifics: JGB par curve, GC repo, 30y JGB ASW, EM forward points.

<a id="idea-027"></a>
### IDEA-027 · risk-attribution-selects-hedge-instrument

`method` · **status: unvalidated** · **11/15**
*source:* [2026/07 · crossasset_gs_goal-kickstart_2026-07-27](2026/07/crossasset_gs_goal-kickstart_2026-07-27.md)
*applies to:* Any asset with a listed options market and a decomposable risk model — S&P puts vs cutting equity beta, CDX payers vs spread-duration cuts, FX equivalents.
<!-- edges -->
*related:* [IDEA-003](#idea-003) moments the hedge choice depends on · [IDEA-044](#idea-044) same decompose-before-acting move · [IDEA-017](#idea-017) the wedge it instruments · [IDEA-034](#idea-034) whether the hedge survives
*literature:* [ang_hodrick_xing_zhang_2006](../papers/paper_notes_ang_hodrick_xing_zhang_2006.md)

**Statement.** The level of a drawdown-probability estimate tells you nothing about how to hedge; its attribution does. Risk attributed to valuation carries no timing content — the level is highly persistent and the trigger exogenous — so the efficient response is time-limited convexity. Risk attributed to deteriorating growth is trending and serially correlated, so the efficient response is simply reducing exposure. Decompose the model output before choosing the instrument.

**Mechanism — who pays, why it persists.** A statistical property of the signals rather than a market inefficiency, and labelled as such. Valuation is near-unit-root and weakly informative at short horizons — rich markets stay rich for years — so a linear short bleeds carry waiting for an exogenous trigger; an option caps that bleed and pays only if the trigger arrives. Growth deterioration is serially correlated in changes, giving persistence a linear position captures without paying the variance risk premium. On the other side of the convexity leg: option sellers harvesting the VRP. The claim is only about WHEN paying that premium is efficient.

| | | |
|---|:--:|---|
| Economic rationale | **3/5** | An honest 3. A real statistical argument about the differing autocorrelation of valuation vs growth signals, but no constrained counterparty is named and the convexity leg pays a well-documented risk premium — a plausible story with no identified payer. |
| Durability | **4/5** | A property of the signals themselves, so not competed away like a price anomaly. Docked because VRP level and the implied-vol term structure vary enough across regimes to move the crossover point at which convexity beats beta reduction. |
| Testability | **4/5** | Verified: BAMLH0A0HYM2, VIXCLS, DGS10, T10YIE, UNRATE all resolve, and vix3m_daily.parquet plus equities.parquet from 2005 support the drawdown-label side; shap is pip-installable. Gap: SPX option chains for realistic put-hedge P&L. Also worth replicating the note's weakest link — Shapley over correlated macro features is attribution-order-sensitive. |

**Evidence so far.** None ex-ante. A single dated snapshot (~20-25% probability of a >20% 12m drawdown, attributed almost entirely to the valuations bucket) with no out-of-sample validation, and the digest itself names this Shapley attribution as the note's weakest link — the most load-bearing inferential claim and the least interrogated.

**To test later.** FRED ISM/USSLIND, BAMLH0A0HYM2, DGS10, T10YIE, UMCSENT; Shiller CAPE; ^GSPC daily for drawdown labels; VIX and VIX3M as a crude convexity-cost proxy; Python shap. Gap: SPX option-chain history.

<a id="idea-028"></a>
### IDEA-028 · decompose-the-headline-aggregate

`method` · **status: unvalidated** · **11/15**
*source:* [2026/01 · economics_gs_japan-outlook_2026-01-06](2026/01/economics_gs_japan-outlook_2026-01-06.md) , [2026/05 · rates_gs_fed-balance-sheet_2026-05-21](2026/05/rates_gs_fed-balance-sheet_2026-05-21.md) , [2026/06 · flows_gs_cta-bond-futures_2026-06-09](2026/06/flows_gs_cta-bond-futures_2026-06-09.md) **← independent arrival in 3 reports**
*applies to:* Any macro series where an annual average is the headline (GDP, IP, retail sales, credit growth), and any central-bank reserve system used as a conditioning variable for duration, credit or risk-asset exposure — US, ECB (banknotes + government deposits), BoJ (current-account balances). Extended 2026-08-15 to **any published figure accompanied by a breakdown** — scenario grids, sector attributions, flow decompositions, P&L attributions, index contributions.
<!-- edges -->
*related:* [IDEA-041](#idea-041) not merged: arithmetic vs dependency · [IDEA-016](#idea-016) the reserves half · [IDEA-015](#idea-015) the growth-arithmetic half · [IDEA-042](#idea-042) the denominator version · [IDEA-021](#idea-021) recompute the print first
*platform:* [professional_report.py — no contribution table](../../../alpha_research/backtests/reporting/professional_report.py) · [report.py](../../../alpha_research/backtests/reporting/report.py)

**Statement.** Recompute every headline aggregate from its components before treating it as information, and measure in the units of the constraint that actually binds. Annual-average growth mechanically embeds the prior year's within-year path, so a series can print decelerating annual growth while quarter-on-quarter momentum accelerates — report carryover, Q4/Q4 and annual-average together. Central-bank liquidity is reserves divided by commercial-bank assets, never headline balance-sheet size, whose week-to-week momentum is near-uncorrelated with the liquidity that prices the front end.

**Extension added 2026-08-15 (third source) — when the recomputation leaves a residual, the residual is itself the measurement.** The original statement says *recompute*; it does not say what to do when the sum misses. Test the residual across every cell of the breakdown you are given:

- **Sign-coherent with the headline across independent cells, scaling with the scenario** → an *omitted component set*, not an error. The claim is internally consistent, but you have lost **attribution** — and the unattributed fraction is the honest discount to apply to it.
- **Small and sign-random** → transcription or rounding. Ignore.
- **Large and sign-incoherent** → aggregate and breakdown come from different runs or vintages. Discard the headline.

Two cells suffice to run the test, and it costs nothing. The live instance: the GS CTA note publishes four scenario cells; every one leaves a residual, and every residual matches its headline's sign (+/+, +/+, −/−, +/+) while scaling with the scenario — so the model's universe is wider than its prose (Figure 1 is captioned "by Country/Region"; the commentary names nine contracts). The consequence is the point: in the one cell where all nine named contracts are given, they sum to **−\$0.2m** against a **−\$3.8m** headline, so **≈95% of the number the note's conclusion rests on comes from markets the reader is never shown.** Attribution failure, not arithmetic failure — and the distinction is only visible because the residual was tested rather than just noticed. *(Prior passes had flagged the single-cell mismatch as "unresolvable from the text"; the four-cell sign test is what resolved it.)*

**Mechanism — who pays, why it persists.** No compensated risk and no constrained counterparty — a measurement fix, and it should be scored as one. What gives it structure is that the informative component is systematically diluted by mechanical ones the publisher does not control: statistical carryover and base-year one-offs in the growth case; currency demand and fiscal cash management in the reserves case. The correct series sit in lower-profile releases than the headline that wire services quote and vendor dashboards carry. The distortion is not concealed, merely unrecomputed — which also means it decays if the better series become standard.

| | | |
|---|:--:|---|
| Economic rationale | **2/5** | **Held at 2 despite a third independent arrival.** Three arrivals of the same correction, still no payer in any of them. Professional macro desks run the growth decomposition routinely, so its value is defensive rather than positive-expectancy; the reserves version is better because the wedge has an exogenous cause, but it is still measurement quality, not risk premium. The 2026-08-15 residual extension is a sharper diagnostic, not a mechanism — a method that tells you how much of a claim is unattributable does not create a transfer. |
| Durability | **5/5** | Arithmetic properties of how statistics are published plus a balance-sheet identity. Cannot decay while agencies publish annual averages and autonomous factors absorb the difference between assets and reserves. The residual test inherits this: it is addition. |
| Testability | **4/5** | Growth half is a 5: quarterly real GDP levels give carryover, Q4/Q4 and annual-average from one series, with PIT shifting default-on for revisions — though GDP resolves while GDPC1 raises ValueError despite sitting in macro_indicators.parquet. Reserves half is a 3: WRESBAL and WTREGEN confirmed unresolvable, TLAACBW027SBOG in no registry, and fed_liquidity.parquet only covers 2024-02 onward. Residual half is a 5 and needs no market data at all — it runs on any document with a breakdown, and was executed in full on the CTA note. |

**Evidence so far.** Residual half: fully worked, four cells, on the GS CTA note (see the extension above) — the only part of this idea that has been run end-to-end rather than proposed. Growth: one instance — Japan 2026E annual-average real GDP 0.8% vs 1.2% in 2025 (reads as deceleration) while Q4/Q4 accelerates from 0.7% to 1.1%, with base-year one-offs named (auto-production stoppage, a services-survey methodology change in 2025Q1). Reserves: weekly since Jan-2024, n=134, corr(dWALCL, dWRESBAL) = 0.189, sd \$17.3bn vs \$73.5bn, while net liquidity reaches corr 0.72-0.73 — ~3.8x better; plus one ex-post episode where WALCL rose \$24.5bn (a momentum filter says LONG DURATION) while reserves fell \$145bn and DGS10 sold off +11bp. No ex-ante test either side, no return series attached.

**To test later.** Quarterly real GDP levels (FRED GDPC1 and the OECD quarterly family) plus optional SPF individual responses to size the wedge markets trade against; FRED WRESBAL, TLAACBW027SBOG, WTREGEN, RRPONTSYD, WALCL, TREAST, WSHOMCB with DGS2/DGS10 and IEF/TLT as the validation dependent. For the residual half there is nothing to test — it is a standing audit to run on every future digest, and the natural place to institutionalise it is our own output: `alpha_research/backtests/reporting/professional_report.py` and `report.py` currently emit **no per-ticker or per-sleeve contribution at all** (verified 2026-08-15), so our own reports cannot be residual-tested. A contribution table that sums to the headline, with the residual flagged when it does not, would close that.

<a id="idea-029"></a>
### IDEA-029 · real-rate-buffer-supply-shock-reaction

`regime` · **status: unvalidated** · **10/15**
*source:* [2026/07 · macro_gs_em-trader_2026-07-30](2026/07/macro_gs_em-trader_2026-07-30.md)
*applies to:* EM local front-ends and EM FX under a commodity/supply shock; generalises to any inflation-targeting complex facing a common shock, with the DM vs EM split of 2021-22 as the natural out-of-sample analogue.
<!-- edges -->
*related:* [IDEA-038](#idea-038) reaction function vs priced path · [IDEA-026](#idea-026) annualise before trading it
*literature:* [obstfeld2005](../papers/paper_notes_obstfeld2005.md)
*study:* [2026-03-27_global_macro_trading_gliner](../studies/2026-03-27_global_macro_trading_gliner/gmt_book_briefing.md)

**Statement.** Under a supply-driven inflation shock, the cross-section of central-bank reaction — and therefore local front-end direction — sorts on the ex-ante real policy rate buffer (policy rate minus forward-looking CPI), not on the country's exposure to the shock. Large restrictive buffers look through the shock or even cut; negative buffers must hike to rebuild regardless of oil exposure. Critically, the buffer is convention-sensitive: India swings 2.7pp purely on which fiscal-year CPI forecast is used, so the sort key must be convention-standardised before it is a signal.

**Mechanism — who pays, why it persists.** An inflation-targeting central bank with an already-restrictive real stance has bought insurance against second-round effects and can treat a relative-price shock as transitory without risking expectations; one running an accommodative real stance would ratify the shock into expectations, so it must act. The behaviour is largely mandated by the framework rather than discretionary, which is why it is forecastable ahead of the meeting. The other side is flow positioned off headline commodity beta — payers and receivers set by the size of the shock rather than the reaction function.

| | | |
|---|:--:|---|
| Economic rationale | **4/5** | The reaction function is mandate-driven and the constrained party identifiable — inflation targeters with credibility at stake. Not 5 because the buffer is not a compensated risk: you are forecasting a policy decision, and payment arrives only if the market has priced the shock rather than the reaction. |
| Durability | **4/5** | Holds while independent inflation targeting is the dominant framework. Breaks under fiscal dominance, an FX anchor, or overt political pressure — and it would break SILENTLY, since the buffer would still compute. Turkey is the standing counterexample in the same table. |
| Testability | **2/5** | EM policy rates have no source on this platform, and forward-looking CPI forecast vintages are harder still — using realised CPI introduces look-ahead. Public routes exist (BIS policy rate database free CSV; IMF WEO / OECD forecasts) but are semi-annual, too coarse for a 13-day event window. The PIT problem, not the data, is the binding constraint. |

**Evidence so far.** Descriptive and anecdotal, one episode. Six to eight country-decisions in July 2026 (SARB held against full hike pricing, Bank Indonesia held, Hungary/Brazil/Mexico cut, NBP signalled September) are consistent with the buffer ordering, but this is a single shock with no formal test, no base rate, and no count of countries where the ordering failed. The buffer numbers are the digest author's recomputation, and they disagree with the note's own Exhibit 14 placement of India — which is how the convention sensitivity was found.

**To test later.** BIS policy rate database or per-country CB rate series; forward-looking CPI forecasts WITH vintage dates (IMF WEO semi-annual; Consensus Economics paid/monthly is the only one fine enough for event studies); market-implied policy paths from OIS/FRA per country (hard gap). Minimum viable: US, EA, UK, JP, CA, AU, SE, NO across the 2021-22 energy shock using FRED policy rates and SPF/ECB SPF vintages.

<a id="idea-030"></a>
### IDEA-030 · wam-drift-reveals-tenor-demand

`signal` · **status: unvalidated** · **10/15**
*source:* [2026/07 · flows_gs_japan-savings-jgb-demand_2026-07-20](2026/07/flows_gs_japan-savings-jgb-demand_2026-07-20.md)
*applies to:* Long-end government curves wherever a large mandated holder's maturity profile is disclosed — JGB 20s/30s, USTs via SOMA's maturity ladder, gilts via the APF, EUR long end via insurer regulatory filings.
<!-- edges -->
*related:* [IDEA-042](#idea-042) free float the WAM drift implies · [IDEA-005](#idea-005) which sector loses its buyer · [IDEA-006](#idea-006) the same mandated holder
*literature:* [litterman1991](../papers/paper_notes_litterman1991.md)
*study:* [2026-03-26_fixed_income_relative_value_analysis_2e](../studies/2026-03-26_fixed_income_relative_value_analysis_2e/firv_book_briefing.md)

**Statement.** Read a large mandated holder's duration demand from the drift in its portfolio weighted-average maturity, not from its stated policy or notional purchases: a holder whose WAM is falling replaces less than 100% of annual maturity decay and is therefore a net supplier of duration to the market even while it is a net buyer of bonds. It is the cleanest available falsification of any 'constrained buyer supports the long end' story.

**Mechanism — who pays, why it persists.** Roll-down mechanically shortens a static portfolio by one year per year, so holding WAM flat requires continuously buying longer maturities; observed WAM drift is a direct read on the replacement rate of the holder's long-end bid. GPIF's JGB WAM fell 10.7y (2020) to 9.7y (2026) — a ~83% replacement rate — so the long-end tilt used to justify 'most bang for the buck at the long end' is real but incomplete and decaying, and the market must absorb the duration the holder declines to replace. Persists because holdings files are published while WAM drift is never headlined, and because tenor demand is set by liability structure and internal risk limits moving on multi-year timescales.

| | | |
|---|:--:|---|
| Economic rationale | **4/5** | Roll-down arithmetic is an identity and the holders are named and liability-constrained, so the duration-supply channel is mechanical rather than statistical. Docked because the link from a slowly drifting replacement rate to realised curve shape is established nowhere — many other duration suppliers and demanders sit in between. |
| Durability | **4/5** | Liability structures, internal risk limits and disclosure regimes all move slowly, so both the signal and its observability persist. Not 5 because a mandate review or ALM regime change can reset a holder's tenor demand discontinuously. |
| Testability | **2/5** | Computable in principle from public files but every one needs a new connector and non-trivial parsing. NY Fed SOMA holdings by maturity (weekly, public) is the cleanest test bed; GPIF annual ISIN-level holdings exist since 2019. Nothing relevant is in the lake — no JGB 20y/30y cash points, no maturity-bucket holdings feed anywhere — and the dependent variable, long-end curve shape, is also missing on the JPY side. |

**Evidence so far.** In-sample descriptive, one holder, no link tested. Exhibit 4 shows GPIF JGB WAM 10.7y to ~9.7y while the exhibit's own title calls it 'relatively steady'; gilts 21y to ~12.3y, EGBs 10.5 to ~9.3, USTs flat at ~7.5-8y. The supporting curve-flow evidence is asymmetric: the sub-2y selling used to argue a long-end tilt is clear in USTs (~-15 to -22bn/yr) but near zero in JGBs, while the text claims it shows 'this for both'.

**To test later.** GPIF annual ISIN-level holdings files (public since 2019, no connector); NY Fed SOMA holdings by maturity bucket (weekly, public); BoE APF maturity ladder; matched long-end curve points (JGB 20y/30y, UST 10s30s, gilt 10s30s) to test the link.

<a id="idea-031"></a>
### IDEA-031 · direction-of-travel-conditioning

`regime` · **status: unvalidated** · **10/15**
*source:* [2025/11 · rates_gs_vol-strategies_2025-11-13](2025/11/rates_gs_vol-strategies_2025-11-13.md) , [2026/04 · macro_gs_jpy-macro-trading_2026-04-07](2026/04/macro_gs_jpy-macro-trading_2026-04-07.md) **← independent arrival in 2+ reports**
*applies to:* Any carry or mean-reversion sleeve: equity and rates vol selling, credit spread carry, FX carry, commodity calendar carry, cross-sectional value overlays. For the vol half, any market with an options skew and a measurable positioning imbalance — the direction of the asymmetry flips with positioning and must be re-measured per market and regime.
<!-- edges -->
*related:* [IDEA-033](#idea-033) residual, then direction · [IDEA-011](#idea-011) the official-flow instance · [IDEA-045](#idea-045) the competing read of flat regimes · [IDEA-036](#idea-036) distance as the state variable · [IDEA-020](#idea-020) when the convexity is cheapest · [IDEA-044](#idea-044) confirmed or unconfirmed extreme
*literature:* [asness_value_momentum_2013](../papers/paper_notes_asness_value_momentum_2013.md) · [moskowitz_tsmom_2012](../papers/paper_notes_moskowitz_tsmom_2012.md)
*study:* [2026-06-24_volatility_workstation](../studies/2026-06-24_volatility_workstation/README.md)

**Statement.** The same level is two different states depending on how you got there, so condition on the direction of travel rather than the level. Take a valuation or mean-reversion entry only when the variable is both stretched AND already moving back toward fair value — 'rich and falling' and 'rich and rising' are different states at identical levels, and only the first is paid. The same discipline applies to the vol estimate: realized volatility is directionally asymmetric (here 4.81bp/day in a rally regime vs 3.65 in a sell-off vs 2.75 unconditional) and frequently points opposite to option skew, so measure it conditionally and treat the cheap side that realizes faster as systematically under-priced gamma.

**Mechanism — who pays, why it persists.** In the adverse phase the constrained flow has not finished executing: hedgers under margin or mandate and dealers covering short gamma are still buying regardless of price, so supplying liquidity into it is standing in front of an unfinished order. Once the variable turns, that flow has exhausted and the liquidity provider collects both the premium and the reversion. The persistence is real because the counterparty's constraint is an obligation, not a view. The vol-asymmetry half rests on a weaker footing — positioning, not structure: when the consensus POSITION is already short, rallies are stop-out driven and fast while sell-offs grind along the crowd. Real payer (the crowded short covering), but no mandate holds it in place.

| | | |
|---|:--:|---|
| Economic rationale | **4/5** | Scored on the stronger half. Named constrained counterparty in the flow-exhaustion mechanism (forced hedgers, short-gamma dealers during the widening phase), and the value-plus-momentum interaction is documented across asset classes independently. The positioning half would be a 3 alone — a measured statistical asymmetry with no positioning data to support its cause. |
| Durability | **3/5** | The merge exposes a split: the flow-exhaustion half is plumbing-rooted (4-5), but the vol-asymmetry half lasts only as long as the positioning imbalance, which is unobservable without CFTC/CTA proxies, and a crowd that has already been squeezed leaves no trace in the price series. The blend cannot honestly clear 3. |
| Testability | **3/5** | Realized half fully testable: regime-conditioned realized vol on any daily series that resolves (USDJPY=X, SPY, DGS10, HYG), and a double-sort on level-richness x 20/60d change using VIXCLS minus 21d realized SPX vol or HYG-LQD carry. Skew half is not: no swaption vols, no FX risk reversals, no options surface anywhere on the platform. You can measure the asymmetry but not the mispricing it implies. |

**Evidence so far.** In-sample quintile sort (Exhibit 13): return-to-vol rising from ~0.2 in the cheapest quintile to ~1.9 in the richest-and-falling quintile — but buckets are double-sorted on a proprietary fair-value model, so the ~9x spread is a fitted, full-sample, model-dependent number with no count of independent episodes per bucket. Vol half: desk-computed with no disclosed sample period, no n, no dispersion, and the desk's own trade built on it fails its breakeven in two of the three states it measured. Crowding premise corroborated only anecdotally, from a separate CTA positioning note.

**To test later.** Proxy double-sort: VIXCLS + SPY realized vol, or HYG-LQD spread carry, or FX rate differentials, all with 20/60d change buckets and forward return-to-vol by bucket. Skew half (gap): swaption vol and skew by expiry/tenor, FX 25-delta risk reversals, or equity index skew. Positioning input to make the mechanism testable rather than assumed: CFTC COT (public, free, no connector).

<a id="idea-032"></a>
### IDEA-032 · base-rate-override-tell

`method` · **status: unvalidated** · **10/15**
*source:* [2026/01 · economics_gs_japan-outlook_2026-01-06](2026/01/economics_gs_japan-outlook_2026-01-06.md)
*applies to:* Capex-sensitive equities (industrials, capital goods, semis) across countries; extends to credit and housing cycles wherever a datable cycle-length distribution exists.
<!-- edges -->
*related:* [IDEA-041](#idea-041) count the nodes behind the override · [IDEA-043](#idea-043) the publisher who writes it · [IDEA-015](#idea-015) the runway an override explains away

**Statement.** When a forecast explicitly cites a base rate and then overrides it with qualitative differentiators — 'this cycle is different because X, Y, Z' — treat the override itself as a marker of elevated reversion risk rather than as evidence against it. Quantitative form: cycle age relative to the empirical distribution of historical cycle lengths gives a hazard rate; use that hazard as a conditioning variable on cyclical exposure, and treat the narrative case for extension as a contrarian input.

**Mechanism — who pays, why it persists.** Forecasters are constrained by house-view continuity and by the fact that clients are already positioned in the prevailing cycle. Calling a turn is asymmetrically costly — early is indistinguishable from wrong, and the entire client book is on the other side — so extension arguments are manufactured at precisely the point in the cycle where the base rate has turned against them. That is a named constrained party. The base rate itself persists because capital-stock adjustment and financing-cycle physics are indifferent to the narrative.

| | | |
|---|:--:|---|
| Economic rationale | **3/5** | The incentive mechanism for why extension narratives cluster at cycle-ends is coherent and names who produces them, but nobody is mandated to hold the losing side, and the hazard-rate claim (older cycles are riskier) is only weakly supported — some cycles genuinely are structurally longer. |
| Durability | **4/5** | Both legs move slowly: sell-side incentive structure and the physics of investment cycles. Erodes only if forecasting incentives change or a structural break genuinely lengthens investment cycles — which is exactly what the override claims, and that is the uncomfortable part. |
| Testability | **3/5** | Hazard-rate version testable with real private non-residential fixed investment (FRED PNFIC1 plus OECD equivalents, public, unregistered): date peaks/troughs, fit a duration model, test whether downturn hazard rises with cycle age, then overlay on cyclical equity via the XL* sector ETFs (which resolve). The narrative-override half needs a hand-labelled report corpus — no dataset exists. |

**Evidence so far.** Anecdotal, one instance: Japan's capex cycle placed in year 5 against a post-1990s average length of 4.5 years, then exactly three qualitative differentiators supplied (software rather than machinery, growing order backlogs, record-high free cash flow). The digest flags this as 'the textbook shape of an argument built to explain away mean reversion rather than test for it'. No hazard model was fit by anyone.

**To test later.** Real private non-residential fixed investment, quarterly, multi-country (FRED PNFIC1 plus OECD) for cycle dating and duration modelling; machinery-orders and capital-goods-shipment series for a higher-frequency version (Japan via e-Stat — gap); a labelled corpus of research notes for the narrative half (does not exist).

<a id="idea-033"></a>
### IDEA-033 · fair-value-residual-not-level-zscore

`method` · **status: unvalidated** · **10/15**
*source:* [2025/11 · rates_gs_vol-strategies_2025-11-13](2025/11/rates_gs_vol-strategies_2025-11-13.md)
*applies to:* Any market where an insurance-like premium is embedded in a price with identifiable fundamental drivers: equity vol vs macro dispersion, rates vol, credit spreads vs default fundamentals, FX carry vs rate differentials and terms of trade.
<!-- edges -->
*related:* [IDEA-024](#idea-024) where the residual stops meaning anything · [IDEA-031](#idea-031) rich AND falling · [IDEA-045](#idea-045) what the residual scales with
*literature:* [campbell_shiller_1988](../papers/paper_notes_campbell_shiller_1988.md)
*study:* [2026-06-24_volatility_workstation](../studies/2026-06-24_volatility_workstation/README.md)

**Statement.** For any premium-harvesting trade whose price level is itself driven by observable fundamentals, build the timing signal on the residual from a fundamentals fair-value model, not on a z-score of the level against its own history. Where fundamentals explain 70-85% of the level, a level z-score is predominantly a fundamentals reading with the premium buried inside its noise.

**Mechanism — who pays, why it persists.** No new counterparty — the payer is the same structural buyer of crash protection who funds the volatility risk premium. What changes is measurement: a level signal conflates 'implied vol is high because macro uncertainty is genuinely high' (no edge, the vol will realize) with 'implied vol is high relative to what fundamentals justify' (edge). It persists not because the inputs are secret — forecast dispersion and distance from neutral are public and slow-moving — but because the intuitive level signal is what practitioners reach for. Honest weakness: the residual borrows all its credibility from the specification, so a mis-specified model manufactures a spurious premium out of omitted fundamentals.

| | | |
|---|:--:|---|
| Economic rationale | **3/5** | Downgraded from the extractor's 4. The underlying premium has a named payer, but the residual construction does not create the edge — it isolates it, and nobody is forced to mis-price the residual. Scored as the specification technique it is, not as the premium it measures. |
| Durability | **4/5** | Demand for downside protection is mandate- and risk-limit-driven and changes slowly, and the specification insight (fair value is not constant) is permanent. Marked down because the specific fair-value drivers are regime-dependent — the neutral-rate anchor is itself an unstable estimate. |
| Testability | **3/5** | Rates version out of reach: no MOVE-equivalent anywhere in the platform, swaption grids proprietary. Equity analogue reachable — VIXCLS resolves and SPY/equities.parquet gives realized vol from 2005; SPF forecast dispersion and NY Fed HLW r* are free but unregistered. |

**Evidence so far.** In-sample and descriptive. Exhibits 6-7 show near-flat scatters for the raw IV/realized ratio and the 1y IV z-score against subsequent realized-vs-implied; Exhibit 12 shows a noisy but upward-sloping scatter for richness-vs-fair-value (subsequent 3m return-to-vol roughly -6 to +12). No ex-ante or out-of-sample split, and the fair-value model is proprietary and not reproducible.

**To test later.** Dependent: rates implied vol (MOVE or a swaption ATM grid) — absent. Regressors: SPF/Consensus dispersion for GDP, CPI and the policy rate; a neutral-rate estimate (HLW, public); forward curve from DGS1/DGS2/DGS10. Equity substitute testable now: VIXCLS + SPX realized vol + SPF dispersion + EPU.

<a id="idea-034"></a>
### IDEA-034 · positive-carry-hedges-survive-the-committee

`structure` · **status: unvalidated** · **10/15**
*source:* [2013 · factor_aqr_managed-futures_2013](2013/factor_aqr_managed-futures_2013.md)
*applies to:* Portfolio hedge construction generally: trend overlays vs long puts vs long vol vs gold vs long duration, in any book with an equity or credit core.
<!-- edges -->
*related:* [IDEA-009](#idea-009) the duration its payoff depends on · [IDEA-020](#idea-020) buy the tail inside the factor instead · [IDEA-003](#idea-003) score it on the tail, not Sharpe · [IDEA-027](#idea-027) whether the hedge survives the committee
*literature:* [hurst2013](../papers/paper_notes_hurst2013.md)

**Statement.** Prefer crisis hedges whose expected carry is positive or zero over hedges that bleed, even at the cost of a weaker or slower payoff. A negative-carry hedge (option premium, or a fee-laden fund) must be timed, and timing failures are governance failures rather than market failures: the position gets cut after a few quiet quarters, precisely before it would have paid. A positive-expected-return hedge can be held permanently, so its realized hedge value is far closer to its theoretical hedge value.

**Mechanism — who pays, why it persists.** The constrained party is the allocator's own governance process — quarterly review cycles, drag attribution, career risk on visible bleed. That constraint is real, price-insensitive and does not arbitrage away, which is exactly the point: the market prices the hedge's payoff, not the holder's ability to keep holding it. The trade-off must be stated honestly — the positive-carry hedge is paid for in a different currency, reversal risk and duration-dependence (see [IDEA-009](#idea-009)) instead of premium outlay.

| | | |
|---|:--:|---|
| Economic rationale | **3/5** | Downgraded from the extractor's 4. The constrained party is your own investment committee — a self-inflicted constraint — and the cost differential it exploits (option buyers pay the VRP) is well known and priced. The source's own 'cheap' comparison is against CTA fees, not option premium; the carry framing is an extension, defensible but unevidenced here. |
| Durability | **4/5** | Governance and behavioural constraints change slowly, so the asymmetry between holdable and un-holdable hedges persists. Marked down because the underlying cost gap (VRP size, option liquidity, fee levels) varies materially across regimes and can compress. |
| Testability | **3/5** | Partially buildable: VIXCLS resolves and vix3m_daily.parquet is in the lake, giving a crude rolling put-cost proxy, with SPY/equities.parquet supporting the crisis-payoff side. The clean version needs CBOE PPUT/PUTW/CLL index history (public, unregistered) or an SPX chain. Realized 'hedge fatigue' — when allocators actually cut hedges — is not observable in any dataset we can reach. |

**Evidence so far.** None from the digest, which argues only that trend is cheap relative to CTA fees. The comparison against explicit option convexity is a proposed extension, not a reported result.

**To test later.** CBOE PPUT / PUTW / CLL index history as the explicit-convexity leg; the TSMOM sleeve returns as the implicit-convexity leg; VIXCLS and vix3m_daily for carry-cost context; cost per unit of crisis payoff computed over the drawdown catalogue from [IDEA-009](#idea-009).

<a id="idea-035"></a>
### IDEA-035 · retail-access-revealed-preference-test

`method` · **status: unvalidated** · **10/15**
*source:* [2026/07 · flows_gs_japan-savings-jgb-demand_2026-07-20](2026/07/flows_gs_japan-savings-jgb-demand_2026-07-20.md)
*applies to:* Government bonds and retail savings instruments under any retail-access policy — Japan NISA, UK ISA and retail gilts, Italy BTP Italia, US TreasuryDirect / I-bonds, India retail G-sec.
<!-- edges -->
*related:* [IDEA-006](#idea-006) the flow it falsifies · [IDEA-043](#idea-043) the house that published it

**Statement.** A policy that widens retail access to an asset — a tax wrapper, a retail bond programme, app distribution — moves nothing if a near-substitute is already accessible and unbought; that is a revealed-preference falsification available before any post-policy flow data arrives. Household participation is set by a reservation yield, not by tax status, so causality runs yield to retail ownership, not ownership to yield: rising retail ownership is a symptom of cheapening, not a cause of richening.

**Mechanism — who pays, why it persists.** The tax wrapper shifts after-tax yield by a small fraction of the gap between the asset's yield and the household's reservation yield, so it cannot bind when the yield gap is the binding constraint. The falsification is clean and cheap: JGB funds were already eligible inside NISA's growth quota and evidently unbought, while households put 93% of growth-quota equity money into domestic equities — access was never the constraint. Honest weakness: no constrained counterparty is created by the policy; the edge is fading unconstrained narrative demand, so there is no forced payer, only a mis-sized story.

| | | |
|---|:--:|---|
| Economic rationale | **3/5** | The reservation-yield mechanism and the already-eligible-and-unbought test are strong as evidence, but the trade is fading a narrative whose counterparty is unconstrained discretionary money. Plausible story, no forced payer — a 3 even though the underlying claim is well supported. |
| Durability | **4/5** | The behavioural constraint is structural and slow-moving. What would break it is a policy that removes optionality rather than widening access — mandated default enrolment, auto-allocation, or a tax differential large enough to close the yield gap itself. |
| Testability | **3/5** | Reachable from public sources, none in the lake. JSDA NISA traded-value statistics and BoJ Flow of Funds need connectors; the Italy analogue needs Banca d'Italia / MEF retail BTP placements; a US test bed exists in TreasuryDirect I-bond sales against CPI and Treasury yields. Yield side partially covered — IRLTLT01JPM156N resolves but is monthly with a 45-day PIT lag. |

**Evidence so far.** In-sample descriptive plus one uncited cross-country anecdote. Exhibit 10 fully reconciles on independent re-derivation — growth quota 75% of JPY71tn, equities 59% of that, domestic 93% of those gives 41.2% vs a printed 41%, every cell tying to <=0.2pp, which is a real credibility mark on the one auditable table in the note. Sized properly the incremental demand is JPY2.13tn (~USD 13bn), 18% of the GPIF lever, 0.21ppt of free float, 0.21-0.83bp. The Italy result is cited as 'as we have shown' with no coefficient, sample or period.

**To test later.** JSDA NISA statistics (quarterly); BoJ Flow of Funds household financial assets; Banca d'Italia / MEF retail BTP placements and BTP yields; TreasuryDirect savings-bond sales; matched sovereign yield series per market.

<a id="idea-036"></a>
### IDEA-036 · threshold-proximity-dispersion

`signal` · **status: unvalidated** · **10/15**
*source:* [2026/06 · flows_gs_cta-bond-futures_2026-06-09](2026/06/flows_gs_cta-bond-futures_2026-06-09.md)
*applies to:* Panels of correlated futures: global bond futures, global equity index futures, the G10 FX complex, the energy strip.
<!-- edges -->
*related:* [IDEA-040](#idea-040) saturation is the other half · [IDEA-046](#idea-046) when the trigger resolves · [IDEA-022](#idea-022) the flow the trigger produces · [IDEA-031](#idea-031) distance as the state variable
*literature:* [moskowitz_tsmom_2012](../papers/paper_notes_moskowitz_tsmom_2012.md)
*platform:* [sector_rotation_v1 manifest](../../../alpha_research/research/pool/sector_rotation_v1/manifest.yaml)

**Statement.** Across a panel of correlated markets, measure each one's distance to its trend trigger in volatility units and take the cross-sectional dispersion. Low dispersion — everything sitting near its threshold at once — means a common shock triggers synchronized same-direction flow and amplifies; high dispersion means the shock is absorbed by whichever market is closest and the panel diverges rather than moves together.

**Refinement added 2026-08-11 (re-read of the source note) — the measurement splits in two, and only the first half was originally captured.** Distance-to-trigger carries two separable pieces of information and they answer different questions:
- **Proximity → synchronization.** How *near* the panel sits to its triggers, measured by cross-sectional dispersion of the normalized distance. This is the original statement: low dispersion means one shock fires everything at once.
- **Distance → conditional magnitude.** How *far below* a given market sits, taken as a level rather than a dispersion. This proxies accumulated latent position: a market far from its trigger contributes nothing on the modal path but the most in the tail, because the traverse to the trigger is exactly the position that must be unwound when it arrives.

The source note evidences the second half without stating it: in its 1-month grid the US complex is inert in the base case (net +\$4.7m) yet supplies the single largest Up-scenario contributor (US +29.6m, above every European contract, with TY +11.5m behind). **The practical consequence is that the modal path and the tail rank the same panel in opposite order** — so a screen ranking on proximity alone will systematically flag the wrong markets when the question is "where is the tail risk", and vice versa. Build both statistics; they are the same measurement read two ways and cost nothing extra.

**Mechanism — who pays, why it persists.** Dealer inventory capacity is finite and shared across correlated markets on one balance sheet. When triggers align, the same direction is demanded simultaneously across the panel, so price impact per unit of flow rises. When distances are dispersed — Europe at its threshold, US and JGB far below theirs — the near market absorbs the shock and the far ones are pushed further offside, producing divergence instead of amplification. Persists because intermediary capacity is regulated by capital and leverage rules and moves on a slow structural clock.

| | | |
|---|:--:|---|
| Economic rationale | **3/5** | Mechanically coherent, but the dealer-capacity link is asserted, not observed — no named payer and no visible inventory data to confirm the channel. Good story, unidentified counterparty. |
| Durability | **3/5** | Intermediation capacity is durable, but the threshold conventions defining 'distance' are guesses, and the relationship is regime-conditional on how concentrated trend AUM is in the panel at the time. |
| Testability | **4/5** | Pure price mathematics — rolling N-day high/low or MA distance normalized by ATR, then cross-sectional dispersion, tested against subsequent realized vol and release-day gaps. Verified runnable today on registered panels: SPY/QQQ/IWM/DIA, all eleven XL* sector ETFs (XLB and XLI confirmed resolving via the US_ETFS expansion), and the seven G10 crosses. The specific bond-futures panel is blocked — ZN raises ValueError and no European contracts exist. |

**Evidence so far.** In-sample and anecdotal only — one week's regional split described qualitatively. No numbers on distance-to-threshold are disclosed anywhere in the note; Figure 7 is referenced but its construction is never stated. The 2026-08-11 re-read adds *indirect* support for the distance→magnitude half — the scenario grid's US +29.6m vs inert-base-case pattern is what the mechanism predicts — but this is the note's model output, not an observation, so it corroborates the logic without evidencing the effect. **Scores unchanged: a mechanism sharpened is not a mechanism evidenced.**

**To test later.** Daily settles for the futures panel; rolling 20/50/100-day high/low and moving averages; ATR or 20d realized vol for normalization; **two state variables, not one** — (a) cross-sectional std-dev of normalized distance (proximity/synchronization), (b) per-market signed normalized distance level (latent-magnitude); outcomes = forward realized vol and absolute daily range for (a), forward conditional move size given a trigger crossing for (b). Re-verified 2026-08-11 that `DGS2`/`DGS10`/`DGS30` resolve daily through `get_data` (145 obs YTD) alongside the previously confirmed SPY/QQQ/IWM/DIA, `XL*` and G10 panels — so a rates-proxy version is buildable on cash yields even though the futures panel is not.

<a id="idea-037"></a>
### IDEA-037 · tsmom-12m-sign-vol-scaled-cross-asset

`signal` · **status: unvalidated** · **10/15**
*source:* [2013 · factor_aqr_managed-futures_2013](2013/factor_aqr_managed-futures_2013.md)
*applies to:* Any liquid market with a continuous price history; applied to 67 equity index / bond / FX / commodity markets, and transfers to single names, crypto and rates without modification.
<!-- edges -->
*related:* [IDEA-013](#idea-013) the fee audit built on it · [IDEA-009](#idea-009) its hedge value is duration-bounded · [IDEA-010](#idea-010) its sample ends at publication · [IDEA-018](#idea-018) its breadth is self-correlated
*literature:* [moskowitz_tsmom_2012](../papers/paper_notes_moskowitz_tsmom_2012.md) · [hurst2013](../papers/paper_notes_hurst2013.md) · [geczy2017](../papers/paper_notes_geczy2017.md) · [asness_momentum_fact_fiction_2014](../papers/paper_notes_asness_momentum_fact_fiction_2014.md) · [daniel_moskowitz_crashes_2016](../papers/paper_notes_daniel_moskowitz_crashes_2016.md)
*study:* [2026-03-27_global_macro_trading_gliner](../studies/2026-03-27_global_macro_trading_gliner/gmt_book_briefing.md) · [2026-03-29_expected_returns_ilmanen](../studies/2026-03-29_expected_returns_ilmanen/er_book_briefing.md)
*platform:* [equity_momentum proposal](../../../alpha_research/research/strategies/equity_momentum_2026-03-13_conditional/proposal.md) · [vol_scaled_momentum proposal](../../../alpha_research/research/strategies/vol_scaled_momentum_2026-03-13_rejected/proposal.md)

**Statement.** Take the sign of each market's trailing 12-month excess return as a directional signal, size every position to a constant ex-ante volatility target, rebalance monthly, and aggregate across equity index, bond, FX and commodity markets. Refinements to the signal add little; breadth and risk-equalized sizing do the work.

**Mechanism — who pays, why it persists.** The source does NOT name a payer — its entire defence is sample breadth plus crisis behaviour, so on its own terms this is a well-travelled pattern rather than an identified transfer of money. Candidate payers imported from the surrounding literature are real but unverified here: commodity producers and FX-intervening central banks transacting on mandate rather than price, and investors who under-react to slow news then herd late. The honest compensated-risk story is that trend is short reversals — it pays an insurance-like premium in whipsaw markets and is compensated in persistent ones, which is why the payoff is convex rather than smooth.

| | | |
|---|:--:|---|
| Economic rationale | **3/5** | Plausible story, no payer identified in the source itself. Breadth and crisis timing are offered in place of a mechanism — 135 years rules out narrow data mining but does not establish who loses the money. |
| Durability | **3/5** | Structural in principle across many policy regimes, but the sample ends in 2012 and the following decade of weaker trend returns is uncovered. The rule is public, cheap and heavily traded, and the note's own transaction-cost and capacity assumptions are flagged as the vulnerable point. Cannot honestly clear 3 until post-2013 is checked. |
| Testability | **4/5** | Better than the source digest implies. Verified: SPY, QQQ, TLT, IEF, SHY, GLD, USO and all seven G10 crosses resolve through get_data with yfinance fallback for full history, so a four-sleeve proxy is buildable today. DBC, UUP, EFA, EEM, TIP do not resolve (registry lines). fx/commodities/rates_yf bundles start 2024-02 — confirmed — so history must come from the fallback. The 67-market / 135-year claim itself is a 1-2 (needs GFD or Bloomberg continuous futures). |

**Evidence so far.** In-sample only. Sharpe ~0.7 (1880-2012) and ~0.9 (post-1985) net of estimated costs, plus three crisis episodes selected after the fact, and R^2 > 0.9 regressing a CTA index on the synthetic rule. Everything predates the 2013 publication; the digest explicitly flags that the one genuinely out-of-sample decade is missing.

**To test later.** Continuous front-month futures excess returns for ~40-70 markets across four asset classes (Norgate/CSI/Bloomberg) for the real test; as a proxy, monthly total returns for SPY, EFA, EEM, TLT, IEF, GLD, DBC, USO, UUP and the six major USD crosses back to at least 1990, plus DFF (resolves) to convert to excess returns.

<a id="idea-038"></a>
### IDEA-038 · ois-strip-level-vs-pace

`method` · **status: unvalidated** · **10/15**
*source:* [2026/04 · macro_gs_jpy-macro-trading_2026-04-07](2026/04/macro_gs_jpy-macro-trading_2026-04-07.md)
*applies to:* Any policy rate with a liquid meeting-dated OIS or futures strip — Fed (fed funds futures / SOFR), ECB (ESTR), BoE (SONIA), BoJ (TONA/JSCC), plus EM CBs with liquid meeting swaps.
<!-- edges -->
*related:* [IDEA-026](#idea-026) level vs rate, same discipline · [IDEA-029](#idea-029) the reaction function it prices

**Statement.** Invert a meeting-dated OIS strip into cumulative and marginal hike probabilities — P_i = (OIS_i - r_0)/step, marginal = jump/step — to separate whether your disagreement with the market is about the terminal LEVEL or about the PACE. The distinction determines the correct expression: a pure level disagreement is a far-forward or terminal-sector trade, a pace disagreement is a calendar/meeting-dated steepener, and mis-diagnosing it means being right on the view and losing on the structure.

**Mechanism — who pays, why it persists.** There is no counterparty and no edge of its own — an arithmetic identity, scored honestly as such. Its value is diagnostic: it exposes when a note frames a disagreement as being about both level and tempo when the strip shows the market already agrees on tempo. Here the inversion shows the market pricing a smeared ~30% per meeting after April — the same cadence the desks assume — leaving the terminal rate as the only real disagreement. What persists is the tendency of published macro views to be vague about which dimension they are betting on.

| | | |
|---|:--:|---|
| Economic rationale | **2/5** | Downgraded from the extractor's 3. Exactly reproducible arithmetic — the digest re-derived the desk's entire printed probability table to within 1.2pp — but a decomposition, not an edge. No constrained counterparty, no compensated risk; it prevents a construction error and nothing more. |
| Durability | **5/5** | Arithmetic. Holds anywhere a meeting-dated strip exists. The only failure mode is a non-standard hike increment or an inter-meeting move, both handled by changing the step size. |
| Testability | **3/5** | No BoJ meeting-dated OIS, no TONA, no BoJ policy rate anywhere — the JPY version is a hard gap. The Fed version is fully reachable for free: CME 30-day fed funds futures settlements plus DFF (resolves) and EFFR. Verifiable end-to-end in USD today. |

**Evidence so far.** None as an edge — the only evidence is a successful arithmetic reconstruction (every row of the desk's printed table reproduced to within 1.2pp with r_0 = 72.7bp), which validates the formula, not the trade. Explicitly in-sample and non-predictive.

**To test later.** JSCC BoJ meeting-dated OIS fixings (gap, likely paid). Reachable USD version: CME 30-day fed funds futures daily settlements, the FOMC calendar, FRED EFFR/DFF. ECB/BoE: ESTR and SONIA meeting-dated OIS via vendor (partial gap).

<a id="idea-039"></a>
### IDEA-039 · backstop-censors-the-tail

`method` · **status: unvalidated** · **9/15**
*source:* [2026/05 · rates_gs_fed-balance-sheet_2026-05-21](2026/05/rates_gs_fed-balance-sheet_2026-05-21.md)
*applies to:* Any market with an official or quasi-official backstop: repo/funding after a standing-facility redesign, peripheral euro sovereign spreads after OMT/TPI, bank funding under deposit insurance, cleared-derivative tails after a default-fund top-up, equity vol under a perceived central-bank put.
<!-- edges -->
*related:* [IDEA-012](#idea-012) the buffer it silently inflates · [IDEA-014](#idea-014) the crossing it may be masking
*literature:* [bernanke2020](../papers/paper_notes_bernanke2020.md) · [ivashina2015](../papers/paper_notes_ivashina2015.md)

**Statement.** Any estimate of system resilience — or of a tail hedge's payoff — computed from data after a backstop facility was widened is measuring the backstop, not the system. The private-demand story and the facility-subsidy story generate identical observables, so 'how much room is there' silently becomes 'how far can we lean on a facility never tested at scale.' Date every facility change, split the sample there, and if the discriminating event will never be run, report the parameter as unidentified rather than as an estimate. Trading corollary: after a backstop is strengthened, the historical tail both overstates the payoff and invalidates the base rate used to price it.

**Mechanism — who pays, why it persists.** The backstop provider truncates the right tail of the price distribution at the facility rate, so what you observe is a censored distribution, not the underlying demand curve — and the censoring counterparty is mandated and price-insensitive, which is exactly why the truncation is reliable and exactly why it tells you nothing about private behaviour. It persists as an error because the censoring is invisible in the series (both hypotheses fit), and because every institution with an interest in claiming capacity has an incentive to book a quiet tail as resilience rather than as subsidy.

| | | |
|---|:--:|---|
| Economic rationale | **3/5** | Downgraded from the extractor's 4. Censoring by a mandated price-insensitive provider is a real specific mechanism naming who is on the other side of the tail — but as stated it is an inference rule that improves estimates rather than an edge someone pays you to bear. It earns its keep by stopping you selling cheap convexity, not by generating carry. |
| Durability | **4/5** | Backstops proliferate and are almost never withdrawn, and every new facility recreates the censoring problem in a new market. Held below 5 because a genuine regime change — a formalized, stigma-free standing facility — would alter the censoring pattern rather than merely relocate it. |
| Testability | **2/5** | Fundamentally non-identified: the discriminating experiment (a quarter-end with the facility deliberately not backstopping) will not be run. You can bound it — NY Fed standing repo operation volumes and discount-window usage are public but stigma-distorted, low-frequency and lagged — and pre/post split around a dated design change, but the confound cannot be cleanly resolved. Recording the honest 2. |

**Evidence so far.** Anecdotal and non-identified by construction, one episode. The 99th-percentile repo tail vs IORB collapsed from a 2025Q4 max of +38bp to a July-2026 mean of -0.9bp across the mid-Dec-2025 removal of the facility's aggregate operation limit and the dropping of the 'backstop' label, while the reserve share fell to 11.625% — BELOW the 11.65% at which repo broke on 29-Oct-2025. Both the reserve-demand story and the facility-subsidy story predict exactly that. The report concedes the confound in one sentence and never returns to it.

**To test later.** NY Fed standing repo facility operation results (daily volumes, dated); Fed discount-window usage (quarterly, ~2-year lag); FRED TGCRRATE, TGCR99THPERCENTILE, SOFR99, IORB; a dated event log of facility design changes to define the sample split.

<a id="idea-040"></a>
### IDEA-040 · positioning-saturation-one-sided-flow

`regime` · **status: unvalidated** · **9/15**
*source:* [2026/06 · flows_gs_cta-bond-futures_2026-06-09](2026/06/flows_gs_cta-bond-futures_2026-06-09.md)
*applies to:* Bond futures in the source; generalizes to any market with a measurable positioning proxy — equity index futures, FX, energy. The state variable is 'position relative to own capacity bound', not the position sign.
<!-- edges -->
*related:* [IDEA-036](#idea-036) proximity is the other half · [IDEA-022](#idea-022) the flow function it bounds · [IDEA-046](#idea-046) the date it resolves on

**Statement.** When a rule-based cohort's replicated position sits at the extreme of its own trailing range, the forward flow distribution becomes one-sided — it can buy on a rally and also buy on a selloff, because it has no room to add. The disappearance of that asymmetry, the down-scenario flow flipping from positive to negative, is the signal that the crowded state has normalized, and it is more informative than the position level itself.

**Mechanism — who pays, why it persists.** The constrained party is a fund at its risk-budget bound: a vol target plus a maximum gross/net risk allocation means it literally cannot get shorter regardless of conviction, so the left tail of its flow distribution is truncated by mandate, not by view. The other side is whoever supplies covering liquidity into a squeeze. It persists because the bound is a governance artifact changing on a committee cycle, not a price signal that can be arbitraged.

| | | |
|---|:--:|---|
| Economic rationale | **3/5** | Downgraded from the extractor's 4. Capacity truncation is a real nameable constraint, but the bound is never observed — it is inferred from a trailing 1-year range, a statistical artifact that drifts with realized vol rather than a disclosed mandate limit. That gap between the claimed constraint and the measured one keeps it out of the 4s. |
| Durability | **3/5** | Holds within a regime of stable trend AUM and stable vol targets. The reference range itself moves: a vol spike mechanically shrinks position sizes and makes an old extreme look extreme when it no longer is. |
| Testability | **3/5** | Needs a positioning proxy. CFTC Commitments of Traders managed-money net positions for 2Y/5Y/10Y/30Y UST futures are free and weekly via the public CFTC API — verified that no CFTC connector exists anywhere in this repo, so it is a known public source, not a local one — and it is a noisy stand-in (managed money is broader than CTAs, Tuesday-dated with a Friday release lag). A self-built trend proxy on ETF sleeves is the cleaner test. |

**Evidence so far.** Anecdotal and single-observation: one week where the down-scenario flow flipped from +\$3.3m to -\$1.1m (1w) and +\$7.6m to -\$4.5m (1m). The note makes no claim that this transition has predictive value — that inference is the digest reader's, not the desk's.

**To test later.** CFTC CoT Financial Futures managed-money net positions for CBOT UST contracts; own breakout+vol-target position proxy; trailing 1-year percentile of that proxy per market; forward 1w/1m returns as the outcome variable.

<a id="idea-041"></a>
### IDEA-041 · count-independent-estimates-not-outputs

`risk` · **status: unvalidated** · **9/15**
*source:* [2026/01 · economics_gs_japan-outlook_2026-01-06](2026/01/economics_gs_japan-outlook_2026-01-06.md) , [2026/06 · flows_gs_cta-bond-futures_2026-06-09](2026/06/flows_gs_cta-bond-futures_2026-06-09.md) **← independent arrival in 2+ reports**
*applies to:* Not market-specific. Applies to every external research digest, every vendor signal, every multi-scenario table, and most acutely to rates + FX + cyclical-equity packages sold as one theme.
<!-- edges -->
*related:* [IDEA-018](#idea-018) contrast: this one is prose-level only · [IDEA-028](#idea-028) not merged: dependency vs arithmetic · [IDEA-032](#idea-032) the override it audits · [IDEA-043](#idea-043) same publisher-quality family
*study:* [2026-06-17_advances_financial_ml](../studies/2026-06-17_advances_financial_ml/study_hypotheses.md)
*platform:* [cross_validation.py](../../../alpha_research/backtests/stats/cross_validation.py)

**Statement.** Count the number of independent models behind a claim, not the number of numbers in front of it, and size positions to independent estimated nodes rather than to conclusions. Six scenario figures from one undisclosed model corroborate each other by construction and constitute one piece of evidence; several apparently separate conclusions descending from a single fitted regression have perfectly correlated forecast errors, so the trades expressing them are one trade and any scenario analysis built on them overstates diversification.

**Mechanism — who pays, why it persists.** No counterparty and no economic edge — a discipline against over-counting evidence, stated plainly rather than dressed as an anomaly. It survives because the incentive structure is stable: desk notes are rewarded for looking precise and multi-pillar, a single model emitting many numbers is the cheapest way to look precise, and the dependency graph is never published alongside the conclusions. The failure mode it prevents is real — treating internally consistent output as external validation, and being unable to distinguish genuine week-over-week change from silent model recalibration.

| | | |
|---|:--:|---|
| Economic rationale | **2/5** | Deliberately low, and independent arrival from two digests does not change it. This is bias avoidance, not an edge with a payer. Its value is defensive: it stops you sizing on evidence you do not have. Contrast [IDEA-018](#idea-018), which turns the same intuition into a specific statistical adjustment with a code path. |
| Durability | **5/5** | Permanent — a property of how desk research is constructed and incentivized, not of any market regime. As true in 2036 as in 2026. |
| Testability | **2/5** | Barely testable as a market claim. The only real test needs a labelled archive of dated desk calls scored on outcome, split by whether corroborating figures came from independent models — requiring the archive first. book_notes/playground/reports/ is the natural seed (10 digests, verified) but nowhere near large enough. A reachable proxy: Philadelphia Fed SPF individual-forecaster microdata (free) to measure within-forecaster vs across-forecaster cross-variable error correlation, which quantifies how little diversification a single house view provides — adjacent to, not identical with, the claim. |

**Evidence so far.** Anecdotal from the digests' own critiques. Japan note: one corporate wage-response regression (R^2 = 0.88, coefficients significant at 99%) is asked to carry the 2026 shunto settlement forecast, the consumption recovery, the sub-2% core CPI path AND the entire BOJ 1.5%-by-July-2027 rate path — on a single out-of-sample forecast with no confidence interval. CTA note: six scenario numbers that 'corroborate each other by construction rather than serving as independent confirmations'. No test in either.

**To test later.** A structured archive of external research claims with issue date, explicit falsifiable claim, horizon, number of independent models cited, and realized outcome — built forward from the existing reports library. Philadelphia Fed SPF and ECB SPF individual responses (free) for the proxy. Published forecast dependency structures exist in no dataset — permanent gap.

<a id="idea-042"></a>
### IDEA-042 · free-float-denominator-and-market-specific-beta

`method` · **status: unvalidated** · **8/15**
*source:* [2026/07 · flows_gs_japan-savings-jgb-demand_2026-07-20](2026/07/flows_gs_japan-savings-jgb-demand_2026-07-20.md)
*applies to:* Government bond swap spreads, asset swaps and cash-futures bases in any QE-affected market — JGB, UST, Bund, Gilt — and any market where an official holder owns a large disclosed non-trading stock.
<!-- edges -->
*related:* [IDEA-005](#idea-005) tension: shrinks its 3-6bp to ~1.2bp · [IDEA-030](#idea-030) WAM drift reads the same float · [IDEA-016](#idea-016) reserves as the same denominator · [IDEA-007](#idea-007) beta into the global duration pool · [IDEA-026](#idea-026) flow converted to a rate · [IDEA-028](#idea-028) the denominator version
*literature:* [bernanke2020](../papers/paper_notes_bernanke2020.md) · [du_tepper_verdelhan2018](../papers/paper_notes_du_tepper_verdelhan2018.md)
*study:* [2026-03-26_fixed_income_relative_value_analysis_2e](../studies/2026-03-26_fixed_income_relative_value_analysis_2e/firv_book_briefing.md)

**Statement.** Size official-sector flow as a change in free float — outstanding minus price-insensitive holders, above all the central bank — never in absolute terms or as a share of gross outstanding; and estimate the ppt-to-basis-point coefficient in the target market and regime rather than transplanting it, because post-2008 the basis is set by intermediary balance-sheet capacity at least as much as by supply. Corollary: when a headline result is the product of two independently estimated inputs, verify each separately, because errors in opposite directions are invisible in the product.

**Mechanism — who pays, why it persists.** Price-insensitive holders — central-bank QE stock, mandated pensions, liability-matching lifers — remove the elastic part of supply; residual private holders face a downward-sloping demand curve and must be paid inventory risk to absorb flow, so the same absolute quantity moves price more the smaller the free float. The constrained parties are named (BoJ holding ~50% of JGBs, GPIF ~5%, lifers at the ultra-long). Persists because the denominator requires netting officially-disclosed-with-lag holdings and almost nobody rebuilds it. The coefficient caveat has its own mechanism: post-2008 basis deviations are set by dealer balance sheets and G-SIB surcharges, so a free-float-only model omits the dominant variable.

| | | |
|---|:--:|---|
| Economic rationale | **3/5** | Downgraded from the extractor's 4. The inelastic-residual-demand mechanism is well founded and the price-insensitive holders individually nameable, but this is a denominator and modelling discipline — it improves the sizing of other people's claims rather than generating a position of its own. |
| Durability | **3/5** | The denominator logic is structural, but the mapping coefficient is not: beta is set by intermediary balance-sheet capacity, which is regulation- and cycle-dependent, so a beta estimated in one regime cannot be carried into another — and it is the parameter that carries the number. |
| Testability | **2/5** | US leg only, and incompletely. WSHOMCB and TREAST are in fed_liquidity.parquet but raise ValueError; Treasury Fiscal Data and GFDEBTN are public and unregistered; and the swap-rate leg needed to form a swap spread has no clean public feed. JGB side entirely missing: no MoF outstanding-debt series, no BoJ holdings, no JPY swap curve — the claim that GPIF is '~5% of the market' implies a JPY2,060tn market that cannot be checked here at all. |

**Evidence so far.** Arithmetic only, no estimation evidence. Re-deriving the free-float step from the note's own statistics: GPIF JGB holdings ~USD 643bn at '~5% of the market' implies USD 12.9tn, less a ~50% BoJ holding gives free float ~USD 6.4tn, so USD 75bn is 1.17ppt, worth 1.2bp at the stated beta = 1 versus the printed 3-6bp, requiring beta_eff = 2.6-5.1. The beta is invoked twice with no sample period, estimation window, functional form, standard error or citation, and is transplanted from UST/Bund/Gilt against the note's own written concession that JGB supply sensitivity is historically lower.

**To test later.** Outstanding marketable government debt by market (MoF Japan — gap; US Treasury Fiscal Data / FRED GFDEBTN); central-bank holdings (WSHOMCB / TREAST for SOMA, BoJ balance-sheet statistics — gap, ECB PSPP/PEPP public); a swap curve per market for asset swaps (JPY entirely absent); a dealer-capacity proxy such as NY Fed FR2004 primary-dealer positions or cross-currency basis.

<a id="idea-043"></a>
### IDEA-043 · publisher-credibility-ledger

`method` · **status: unvalidated** · **8/15**
*source:* [2026/05 · rates_gs_fed-balance-sheet_2026-05-21](2026/05/rates_gs_fed-balance-sheet_2026-05-21.md) , [2026/07 · flows_gs_japan-savings-jgb-demand_2026-07-20](2026/07/flows_gs_japan-savings-jgb-demand_2026-07-20.md) **← independent arrival in 2+ reports**
*applies to:* Sell-side, broker and consulting research inputs across all asset classes; any publisher maintaining both a narrative product and a tracked idea list.
<!-- edges -->
*related:* [IDEA-010](#idea-010) publication-date discipline, per-house · [IDEA-032](#idea-032) the override as a tell · [IDEA-041](#idea-041) count the models behind the call · [IDEA-002](#idea-002) score the packaging apart from the call · [IDEA-035](#idea-035) the house that published it

**Statement.** Score the publisher, not the prose. Archive every dated forecast alongside a falsifiable pace number and the same publisher's contemporaneous trade book, then score realized-vs-forecast pace and carry the resulting bias forward as an explicit prior. Two tells: a published institutional central path is the SLOW end of the distribution rather than its centre (direction repeatedly right, pace repeatedly understated in the same direction), and a directional conclusion argued at length but absent from the same house's idea list is prose, not a position. Discount any printed reward:risk whose stop has been revised into profit.

**Mechanism — who pays, why it persists.** Research output and recommended risk are produced under different incentives. Writing a directional conclusion is free and generates client engagement; printing it with an entry, target and stop creates a tracked, attributable record — so the book is the revealed preference. Separately, a path that overshoots and reverses is more career-damaging than one that undershoots, and forecasts are further shrunk toward consensus by herding, so pace is systematically understated. Both constraints sit in the information-production market, not the asset market: nobody pays you for holding the debiased view unless the market itself prices off the published path.

| | | |
|---|:--:|---|
| Economic rationale | **2/5** | Two independent arrivals of an input-quality filter with a coherent incentive story, but no compensated risk and no market counterparty at all. It improves what enters the funnel; it earns nothing on its own. |
| Durability | **3/5** | The general anchoring/smoothing bias is one of the more replicated findings in forecast evaluation. The desk-and-genre-specific version scored here is far weaker: personnel change (the lead author differs across this library's own comparisons), house style changes, and n = 3-5 cannot distinguish a bias from a run. |
| Testability | **3/5** | Verified: book_notes/playground/reports/ exists and holds 10 digests (2 factor classics, 8 GS notes, 2012-2026) plus an INDEX.md — the archive seed is real but roughly 3-5 entries are scorable today against a ~30-entry minimum. No proprietary data required; the constraint is sample size and disciplined logging, a fixable process gap. |

**Evidence so far.** Anecdotal, n = 3 on pace and n = 1 publisher on the book tell. Pace: JGB 10y forecast 'flat ~2.0%' against a 2.670% June-2026 print; USD/JPY to 152 against a 163.86 peak; Fed total assets running +\$10.67bn/mo against a \$5bn/mo forecast (2.1x) — direction correct each time, pace wrong in the same direction each time. Book: five pages concluding 20s/30s should richen, then a 13-idea book with zero Japan trades, while the same house ran a CAD 2s10s steepener at a printed 3.86:1. Book quality checks: 12 of 13 carry entry/target/stop, median reward:risk 1.50 but mean 2.16 (skewed by a 5.0:1 EM basket), three carry a revised stop sitting in profit, and of 11 markable, 7 are in profit but median progress to target is only 17%.

**To test later.** A forecast ledger keyed by (publication date, desk, market, horizon, pace/level claim, falsification threshold), joined to the publisher's contemporaneous trade-idea list with entry/target/stop and stop revisions, and to realized FRED/price series for the same identifiers. Partially self-generated by book_notes/playground/reports/; needs ~30+ scorable entries before any inference.

<a id="idea-044"></a>
### IDEA-044 · sentiment-extreme-needs-driver-check

`regime` · **status: unvalidated** · **8/15**
*source:* [2026/07 · crossasset_gs_goal-kickstart_2026-07-27](2026/07/crossasset_gs_goal-kickstart_2026-07-27.md)
*applies to:* Any market with a cross-asset risk-appetite composite — equity index timing, credit beta sizing, cross-asset risk budgeting; maps directly onto the entry filter for this repo's vol_conditioned_reversal_v1.
<!-- edges -->
*related:* [IDEA-027](#idea-027) attribution decides the response · [IDEA-017](#idea-017) the risk-appetite wedge · [IDEA-031](#idea-031) confirmed or unconfirmed extreme
*literature:* [hong_stein_disagreement_2007](../papers/paper_notes_hong_stein_disagreement_2007.md)
*platform:* [vol_conditioned_reversal_v1 manifest](../../../alpha_research/research/pool/vol_conditioned_reversal_v1/manifest.yaml)

**Statement.** A positioning or risk-appetite extreme is only a contrarian signal when it is not confirmed by the underlying growth factor. Decompose the composite into orthogonal drivers — growth, policy/liquidity, currency — and read which one carries the extreme: an extreme carried by the growth component tends to persist and should be held through, while one carried by the policy/liquidity component with growth neutral is a melt-up and is fragile.

**Mechanism — who pays, why it persists.** Weak on counterparty, and worth saying so plainly. This is a false-positive filter on a notoriously unreliable contrarian signal, not an edge with an identifiable payer. The nearest thing to a mechanism: growth-driven risk appetite is continuously validated by realized cash flows, so the marginal buyer keeps being proved right, whereas liquidity- or policy-driven risk appetite depends on a flow with no fundamental anchor and stops when the flow stops. No mandate, regulation or compensated risk is identified on the other side.

| | | |
|---|:--:|---|
| Economic rationale | **2/5** | Downgraded from the extractor's 3. The 'flow without a fundamental anchor' argument is genuine but nothing names a constrained counterparty or compensated risk, and the underlying contrarian sentiment signal is weak enough standalone that essentially all claimed value comes from the filter rather than any edge. |
| Durability | **3/5** | Methodological rather than exploitable, so not arbitraged away, but PC identification is unstable: loadings rotate across samples and the labelling of PC2 as 'monetary policy' or PC3 as 'dollar' is an interpretive choice, not an estimated fact. The component-to-prescription mapping must be re-verified in each sample. |
| Testability | **3/5** | The specific object — GSRAI and its PCA decomposition — is proprietary, cited to 2016 and 2019 editions and never restated, so it is not replicable at all. A public proxy is buildable from series that resolve today (VIXCLS, BAMLH0A0HYM2, HYG, the XL* sector pairs, T10YIE) plus HG=F and GC=F which sit in commodities.parquet but raise ValueError. The proxy is not the thing being read, so any result is a statement about the proxy. |

**Evidence so far.** In-sample descriptive only. A single reading (composite around +1 on a 1y z-score at the upper edge of its band, PC1 growth elevated, PC2 policy and PC3 dollar near neutral) with the 'hedge, don't de-risk' prescription inferred from it. No historical test of whether growth-confirmed extremes actually persist longer than policy-driven ones appears anywhere in the note.

**To test later.** VIXCLS, VIX3M; BAMLH0A0HYM2; HG=F and GC=F for the growth/defensive ratio; XLY/XLP and XLI/XLU for cyclicals-vs-defensives; DXY and an EM FX basket; T5YIE/T10YIE; ISM or USSLIND to validate the growth PC. Gap: the proprietary composite and its published construction; institutional positioning (CFTC COT the free partial substitute).

<a id="idea-045"></a>
### IDEA-045 · premium-scales-with-priced-dispersion

`regime` · **status: unvalidated** · **6/15**
*source:* [2025/11 · rates_gs_vol-strategies_2025-11-13](2025/11/rates_gs_vol-strategies_2025-11-13.md)
*applies to:* Vol-carry in rates first, but the general form — scale carry to the dispersion embedded in the relevant term structure — transfers to FX carry, credit, and commodity carry.
<!-- edges -->
*related:* [IDEA-033](#idea-033) the fair-value model it needs · [IDEA-031](#idea-031) flat regimes read the other way · [IDEA-024](#idea-024) horizon scoping of the same fit
*literature:* [rates_vrp](../papers/paper_notes_rates_vrp.md)
*study:* [2026-06-24_volatility_workstation](../studies/2026-06-24_volatility_workstation/README.md) · [2026-03-29_expected_returns_ilmanen](../studies/2026-03-29_expected_returns_ilmanen/er_book_briefing.md)

**Statement.** The compensation for selling insurance scales with how much dispersion the underlying term structure is actually pricing. When the forward curve is compressed near perceived neutral, the market prices little uncertainty about the path, implied vol trades close to its fundamental fair value, and the risk-premium buffer thins — so the same strategy earns a fraction of its unconditional return-to-vol. Size the sleeve off that state variable, not off trailing P&L.

**Mechanism — who pays, why it persists.** Honest read: no constrained counterparty is identified, and the mechanism is partly definitional — a compressed curve implies low implied vol, so the absolute premium in vol points shrinks with it. The behavioural half (less disagreement about the policy path means fewer hedgers bidding for protection, hence less premium paid) is plausible but unevidenced. A competing and equally consistent reading is that flat curves cluster near turning points where realized vol subsequently spikes, in which case there is no missing premium at all — there is an unmeasured risk being correctly priced.

| | | |
|---|:--:|---|
| Economic rationale | **2/5** | Plausible story, no identified payer, and partly circular: curve flatness drives implied vol which drives the measured premium. Cannot be distinguished from 'flat curves precede vol spikes, so the low return-to-vol is fair compensation for a real risk' with the evidence shown. |
| Durability | **1/5** | THE LOW ANCHOR ON DURABILITY. Thresholds (+/-50bp, >100bp) are ex-post fitted; flat-curve regimes are highly autocorrelated so the effective sample is a handful of episodes; the curve-to-vol link depends on a reaction function that has changed materially since 2003; and there is no way to detect that the regime has ended. Regime-specific with no regime detector is exactly the rubric's 1. |
| Testability | **3/5** | Conditioning variable is free and immediate — DGS2 and DGS10 resolve, T10Y2Y resolves, though DGS1 raises ValueError despite being in treasury_yields.parquet. Dependent side (rates vol-selling P&L) needs both a rates-vol series and options P&L infrastructure, neither of which exists. Testable now only in an equity analogue: condition a VIX-carry proxy on 2s10s distance from flat. |

**Evidence so far.** In-sample bucket statistic (Exhibit 15): return-to-vol ~0.1-0.3 when the curve is within +/-50bp of flat vs ~1.1 when more than 100bp from flat. Single sample, thresholds chosen ex-post, no count of independent flat-curve episodes given.

**To test later.** Available: DGS1, DGS2, DGS10, DFF/SOFR for slope and distance-from-neutral (the 1y/2y1y forward construction is not computed anywhere on the platform and would need building). Missing for the dependent variable: MOVE or a swaption vol series.

<a id="idea-046"></a>
### IDEA-046 · calendar-clustered-trigger-resolution

`structure` · **status: unvalidated** · **5/15**
*source:* [2026/06 · flows_gs_cta-bond-futures_2026-06-09](2026/06/flows_gs_cta-bond-futures_2026-06-09.md)
*applies to:* Rates futures options and swaptions around NFP/CPI/central-bank dates; equally applicable to equity index options around CPI/FOMC.
<!-- edges -->
*related:* [IDEA-036](#idea-036) proximity conditions it · [IDEA-040](#idea-040) saturation conditions it · [IDEA-020](#idea-020) the convexity it would buy

**Statement.** Trend-threshold crossings are not uniformly distributed in time — they cluster on scheduled macro releases, because that is when enough information arrives at once to gap price through a trigger. So when a panel is both positioning-saturated and sitting close to its thresholds, the right expression is convexity into the known release date rather than a directional position: the timing is public, the direction is not.

**Mechanism — who pays, why it persists.** The compensated risk is gap risk created by forced flow. Options sellers harvesting the event-volatility premium price the calendar itself — everyone knows the release date — but generally do not condition on how close the systematic complex is to its triggers or how saturated its positioning is. The buyer of convexity is paid for warehousing the risk that a release pushes price through a threshold and forces synchronized flow through thin books. Genuinely the weakest idea in the pool: event vol premium is heavily traded, so the entire edge lives in the conditioning variable, not the calendar, and that conditioning value is assumed rather than shown.

| | | |
|---|:--:|---|
| Economic rationale | **1/5** | THE ANCHOR FOR 1. The payer is explicitly NOT identified — event vol is already bid into release dates — the premium is among the most competitively traded structures in rates, and the residual edge exists only if the positioning-and-proximity state adds information beyond the calendar, which the source concedes is an assumption rather than a finding. Zero quantitative evidence. A plausible-sounding pattern with no identified transfer. |
| Durability | **2/5** | The calendar half is permanent; the profitable half is not. Any edge compresses as soon as the conditioning variable becomes common knowledge, and there is no mandate or regulation holding it in place. |
| Testability | **2/5** | Split and mostly blocked. The realized half (do saturated-and-near-threshold states produce larger release-day moves?) is testable from prices plus a release calendar. The tradable half needs bond-future implied vol or swaption grids — verified absent: no options data in the lake, no options P&L module in alpha_research/backtests, and the polygon connector implements equity aggregates only. |

**Evidence so far.** None quantitative. One instance — a stronger-than-expected NFP reversing Europe's incipient breakout — described narratively. An anecdote consistent with the idea, not evidence for it.

**To test later.** BLS/FRED-ALFRED release calendar for NFP, CPI and FOMC dates; daily and intraday futures returns to isolate release-day moves; the threshold-proximity and saturation state variables from [IDEA-036](#idea-036) and [IDEA-040](#idea-040); for the structure itself, CME bond-future option implied vols or USD swaption surfaces (gap).

---

## Merges and independent arrivals

*The same mechanism reached from two unrelated reports is one idea with two sources — and the
independent arrival is itself evidence. Deliberate non-merges are recorded too.*

- [IDEA-001](#idea-001) = 'stock-bond-correlation-is-the-position' (Bridgewater 2012 risk-parity) + 'correlation-sign-selects-diversifier' (GS GOAL 2026-07). Same discount-rate mechanism reached from opposite ends: the 2012 note's construction is short the correlation, the 2026 note uses the correlation sign to pick the diversifier. Independent arrival 14 years apart across a product note and an allocation note is strong evidence the mechanism is real, not a narrative. Kept the 2012 'you are the holder of the everything-falls state' compensated-risk framing plus the 2026 mandated-allocator counterparty.

- [IDEA-003](#idea-003) = 'payoff-identity-dictates-the-statistic' (GS rates-vol 2025-11) + 'moment-match-selector-to-premium' (GS EM trader 2026-07). Identical failure: a two-moment statistic applied to a premium that exists to compensate the third moment. Kept the EM note's stronger mechanism (the evaluation metric itself creates the incentive to sell the tail; the hedger buying the insurance is the counterparty) and the rates note's algebraic derivation (the gamma P&L identity). Two GS desks nine months apart making the identical omission argues house methodology, which is itself the finding.

- [IDEA-020](#idea-020) = 'convexity-barbell-inside-the-sleeve' (rates-vol 2025-11) + 'funding-currency-carry-crash-asymmetry' (GOAL 2026-07). One construction principle: buy the tail back inside the same risk factor, at the point of the term or skew structure where mandated protection demand is NOT concentrated. Rates version is horizon segmentation (near gamma rich, far vega cheap); FX version is the carry-crash asymmetry (cheapest convexity exactly when carry is widest and shorts most crowded). Kept both instances; the FX half supplies the named compensated risk the rates half only implies.

- [IDEA-022](#idea-022) = 'vol-target-deleveraging-flow' (Bridgewater 2012) + 'flow-response-function-not-position-level' (GS CTA 2026-06). Same price-insensitive party (a fund executing a pre-committed rule under a vol target and margin agreement) and the same tradable object. Kept the CTA note's general formulation (model the derivative of position with respect to price) and the 2012 note's specific calendar-predictable vol-spike trigger. NOT merged with [IDEA-006](#idea-006) despite superficial similarity: mandate rebalancing carries the OPPOSITE sign (contrarian, cannot trend) and the GPIF digest is explicit that the two must never be aggregated — that sign-convention warning is carried in [IDEA-006](#idea-006)'s statement.

- [IDEA-026](#idea-026) = 'negative-carry-implies-max-holding-period' (JPY desk 2026-04) + 'amortize-valuation-gap-against-carry' (EM trader 2026-07) + 'flow-headline-signal-to-noise-triage' (GPIF flows 2026-07). Three digests independently arrived at one operation: convert a level claim into a per-unit-time rate through its delivery or reversion horizon, then compare it to the competing rate over the same period — carry, valuation drag, or realised noise. Triple independent arrival is the strongest such signal in the pool. Kept all three counterparty accounts (carry receiver paid for patience; horizon mismatch in evaluation windows; headline-chasing liquidity demand).

- [IDEA-031](#idea-031) = 'stretched-and-already-reverting' (rates-vol 2025-11) + 'directional-realized-vol-asymmetry-vs-skew' (JPY desk 2026-04). This is the near-duplicate the calibration brief flagged. Both say the same level is two different states depending on direction of travel — the rates note applies it to the entry filter, the JPY note to the vol estimate. Kept the rates note's flow-exhaustion mechanism (forced hedgers and short-gamma dealers still executing in the widening phase) as the scored mechanism, and demoted the JPY note's positioning-based asymmetry to an explicitly weaker second half. The merge is scored on the stronger half for economic rationale and penalised on the weaker half for durability — it must not launder the weak idea.

- [IDEA-043](#idea-043) = 'gradualist-forecast-prior' (Fed balance sheet 2026-05) + 'publisher-trade-book-conviction-tell' (GPIF flows 2026-07). Two facets of one thing: research output is a reputational product, so its stated conviction and pace are systematically biased, and both debias through the same artefact — an archive of dated claims with falsifiable pace numbers, joined to the publisher's contemporaneous tracked book and to realized outcomes. Same data requirement, same remedy.

- [IDEA-028](#idea-028) = 'annual-average-growth-artifact' (GS Japan 2026-01) + 'reserve-share-not-balance-sheet-size' (GS Fed balance sheet 2026-05) + **'residual-attribution test' (GS CTA 2026-06, added 2026-08-15)**. The third arrival is the same operation carried one step further: the first two say *recompute the headline from its components*, the third says *and when the recomputation misses, read the residual*. Sign-coherent residuals across independent cells mean an omitted component set (keep the claim, discount by the unattributed fraction); sign-random residuals mean transcription noise; large sign-incoherent residuals mean aggregate and breakdown came from different runs. Kept the reserves version's stronger causal account (currency demand and fiscal cash management are exogenous to the asset side) alongside the growth version's cleaner arithmetic, and persisting because the correct series is less convenient than the headline. Kept the growth and reserves halves as the scored content and added the residual test as an extension — **no score change**: three arrivals of a measurement discipline still name no counterparty, and economic rationale stays at 2. NOT merged with [IDEA-041](#idea-041) (count independent estimates, not outputs), which is adjacent but distinct: [IDEA-041](#idea-041) asks *how many models produced these numbers*, [IDEA-028](#idea-028) asks *do these numbers add up and what does the gap mean* — one is about dependency structure, the other about arithmetic completeness, and the CTA note fails both independently.

- [IDEA-041](#idea-041) = 'forecast-tree-node-concentration' (GS Japan 2026-01) + 'count-models-not-numbers' (GS CTA 2026-06). Identical root principle — count independent sources of variation, not outputs — applied to position sizing and to note auditing respectively. NOT merged with [IDEA-018](#idea-018) (effective-breadth discount), which is kept separate because it converts the same intuition into a specific implementable adjustment to the deflated-Sharpe / MinBTL inputs in alpha_research/backtests/stats/cross_validation.py, applied to our own strategies rather than to external prose. The kinship is real and worth noting; the implementable version deserves its own entry and a higher score.

- NOT MERGED, deliberately: [IDEA-008](#idea-008) (leverage-aversion-premium) and [IDEA-025](#idea-025) (sharpe-gain-is-diversification-not-leverage) both concern the financing leg of the same 2012 note, but one is a compensated-risk return source and the other is a diagnostic showing where the return is not. Also not merged: [IDEA-005](#idea-005) (issuance-mix locates the squeezed sector) and [IDEA-042](#idea-042) (free-float denominator sizes the effect) — they are in productive tension, since [IDEA-042](#idea-042)'s discipline is what would have shrunk the GPIF note's own 3-6bp claim to ~1.2bp.

---

## Thin yield — reports that produced little, and why that is the right outcome

- No report yielded zero transferable ideas, but two came close for opposite reasons and should be treated as thin. (1) GS CTA bond-futures flow monitor (2026-06-09, flows_gs_cta-bond-futures_2026-06-09.md). Five raw candidates, and after merging its flow-response method into [IDEA-022](#idea-022) and its 'count models not numbers' into [IDEA-041](#idea-041), only three survive as its own contribution — [IDEA-036](#idea-036) (threshold dispersion, eco 3), [IDEA-040](#idea-040) (positioning saturation, eco 3) and [IDEA-046](#idea-046) (calendar convexity, eco 1, the lowest-scoring idea in the entire pool). The digest's own essence concedes the note contains six scenario numbers descending from one undisclosed model, i.e. one piece of evidence, and the source disclaimer states the simulated backtest carries 'no assurance'. A weekly positioning monitor is a data product, not an idea product; the transferable content was the reader's critique of it rather than its analysis. That is the right outcome, not a harvesting failure. **Update 2026-08-15 (third pass):** it contributed a fourth time, as a third source on [IDEA-028](#idea-028) (the residual-attribution test) — and note *how*: again as a critique, this time of its own arithmetic, not as an argument it makes. Three passes have now produced the same pattern, which upgrades the thin-yield diagnosis from an observation to a settled property of this source. Its own analysis has yielded one buildable mechanism ([IDEA-036](#idea-036)) across three readings; everything else it has given the pool is a rule for auditing documents like it.

- (2) Bridgewater risk-parity note (2012, factor_bridgewater_risk-parity_2012.md). Superficially productive — it contributed to [IDEA-001](#idea-001), [IDEA-004](#idea-004), [IDEA-008](#idea-008), [IDEA-022](#idea-022) and [IDEA-025](#idea-025) — but note what actually happened: its own thesis (equalize risk contribution and lever the low-vol sleeves) survives only as a measurement correction ([IDEA-004](#idea-004), eco 4) and a diagnostic showing the claimed Sharpe gain does not come from leverage ([IDEA-025](#idea-025), eco 3). The two highest-scoring ideas traced to it, [IDEA-001](#idea-001) (the correlation position) and [IDEA-008](#idea-008) (leverage aversion), arrive as CRITIQUES of the note rather than as its argument — the note never articulates the betting-against-beta mechanism that supplies its premium, and never names the correlation assumption its whole construction is collateralized by. A note whose best transferable content is the thing it declined to say is thin in a specific and diagnosable way: it presents only descriptive statistics (vol ratios, quadrant maps, taxonomies) and no inferential ones anywhere.

- Two further observations on yield concentration. The GS Japan macro outlook (2026-01) produced one genuinely strong signal ([IDEA-015](#idea-015), effective-vs-marginal refi runway, eco 4 / dur 5) and then three research-hygiene rules, which is what happens when a note's three pillars rest on a single wage regression — the methodology critique out-yields the content. Conversely the GS JPY desk note (2026-04) was the richest single source in the pool by economic rationale, contributing two 5s ([IDEA-005](#idea-005) issuance-mix, [IDEA-002](#idea-002) structure geometry) plus [IDEA-011](#idea-011) which has the highest testability of any signal here; the sell-side note with the most conflicted incentives produced the most auditable ideas, precisely because its claims rest on public quantities (issuance calendars, absorption capacity, strike placement) that a reader can check.

---

## Calibration record

*Ten agents read one digest each in isolation, so their 1–5 scales drifted. A single pass re-scored
the pool against fixed anchors. Every changed score is listed.*

**Distribution.** 46 ideas from 56 raw candidates after 8 pairwise merges and 1 triple merge. FINAL DISTRIBUTIONS. Economic rationale — 5: 9 ideas (20%), 4: 15 (33%), 3: 14 (30%), 2: 7 (15%), 1: 1 (2%). Discriminating: the 5s are exactly the ideas that name a counterparty who must trade (GPIF's statutory band, LCR-bound banks, solvency-regulated lifers, leverage-barred mandates, the fee-paying allocator, the dealer who sets the strikes, the global duration pool, the crash-insurance buyer), and everything below 4 explicitly lacks one. Durability — 5: 18 (39%), 4: 19 (41%), 3: 7 (15%), 2: 1, 1: 1. Deliberately top-heavy and I am not flattening it: this skew is a real finding, not a calibration failure. Durability 5 was earned two ways — arithmetic identities that cannot decay (variance algebra, roll-down, statistical carryover, the reserve identity, Sharpe scale-invariance, effective-N) and mandate/regulation plumbing on decade clocks. The composition tells you something uncomfortable about the pool: it is long durable METHODS and short durable SIGNALS. Of the 18 durability-5s only 5 are signals or regimes; the rest are methods and risk rules. Testability — 5: 6 (13%), 4: 11 (24%), 3: 22 (48%), 2: 7 (15%), 1: 0. The modal 3 is honest and informative: the binding constraint on this pool is not proprietary data but registry wiring plus a handful of free public connectors (SPF dispersion, HLW r*, CFTC COT, ACM term premium, BIS REER, BIS policy rates, Treasury QRA, NY Fed SOMA maturity ladder, CBOE PPUT/PUTW). Live checks confirmed that WRESBAL, SOFR, T5YIE, DFII10, DGS1, GDPC1, ^N225 and 13 EM FX crosses are physically present in the lake or defined in core/market_data_service.py yet raise ValueError through alpha_research.quant_data.api.get_data — each is one line in ticker_map.py. No idea scored testability 1, and that is itself worth recording: every surviving idea has at least a public-proxy route, which says something about how much sell-side 'proprietary' analysis rests on free data. The two genuine infrastructure walls, not data walls, are the absence of any options pricing/P&L module in alpha_research/backtests (blocks [IDEA-020](#idea-020) and [IDEA-046](#idea-046)) and the absence of any repo/OIS instrument series (blocks the tradeable leg of [IDEA-013](#idea-013)). Totals run 5 to 15 with a median of 11; the top decile ([IDEA-001](#idea-001) through [IDEA-004](#idea-004)) are all either merged-from-two-sources or identity-grade, which is the pattern you would want.

**Housekeeping pass, 2026-08-11 (cross-reference IDs repaired).** During the re-digest of
`flows_gs_cta-bond-futures_2026-06-09` it was confirmed that the prose sections below — the merge
record, the thin-yield notes and this Changes list — still carried **pre-renumbering idea IDs**, so
grepping the pool for an idea landed on an entry belonging to a different report. Sixteen references
were corrected against the canonical `### IDEA-NNN · slug` headings; each was verified mechanically
by slug, so these are transcription repairs, **no score, wording or ranking was altered**. The
corrected pairs: mechanical-replicant 014→013, funding-leg-as-first-order-choice 043→023,
horizon-match-regressors 023→024, sharpe-gain-is-diversification 024→025, fair-value-residual
028→033, positive-carry-hedges 036→034, threshold-proximity-dispersion 033→036, tsmom 032→037,
ois-strip-level-vs-pace 037→038, backstop-censors-the-tail 042→039, positioning-saturation 038→040,
free-float-denominator 039→042, publisher-credibility-ledger 040→043. A slug-vs-ID consistency check
now reports zero mismatches. *If a future pass renumbers the pool again, re-run that check — the
headings are canonical and the prose is not.*

**Interconnection pass, 2026-08-17 (link layer added; nine mis-pointed cross-references repaired).**
The library's citation network was already dense — 105 `IDEA-NNN` citations across the ten digests and
~40 idea-to-idea references in the prose — but stored entirely as plain text, so none of it was
navigable and no backlink existed anywhere. This pass made the existing network clickable and added
the outward edges: 85 idea-to-idea anchor links, 57 `*source:*` links from each entry to its digest,
105 digest back-links to the pool, and per-entry `*literature:*` / `*study:*` / `*platform:*` lines
pointing into `../papers/`, `../studies/` and `alpha_research/`. 588 relative links now resolve, zero
broken. **No score, wording or ranking of any entry's analysis was altered.**

Repairing the references came first, because linkifying a wrong ID only makes it wrong and clickable.
Nine references pointed at the wrong entry — the 2026-08-11 pass above fixed thirteen and left these,
and its claim that "a slug-vs-ID consistency check now reports zero mismatches" did not hold. The
reason it survived two passes is worth recording: `check_ideas_integrity.py` verified only that a
cited ID *exists*, never that it matches the slug the sentence describes, so every one of these passed
a green check. The corrected pairs, each verified by slug against the canonical `### IDEA-NNN ·`
headings: the merge record's `IDEA-027` entry was a pre-renumbering duplicate of the `IDEA-028`
entry below it and was folded into it; direction-of-travel merge 029→031; sharpe-gain-is-diversification
024→025 (twice, in the not-merged note and the thin-yield note); issuance-mix 006→005 (twice, in the
not-merged note and the thin-yield note); free-float-denominator 039→042 (twice); mandate-rebalancing
005→006 (twice, in IDEA-022's non-merge note and as the economic-rationale-5 anchor). Note the
direction of the error: `IDEA-005` and `IDEA-006` were transposed throughout the prose while the
digests carried them correctly, so the digests — not this file — were the reliable copy.
The checker was extended in the same pass to close that blind spot.

**Changes:**

- ANCHORS SET FIRST. Economic rationale 5 = [IDEA-006](#idea-006) (mandate-rebalancing-is-contrarian-flow): a single named entity with a legally defined +/-6ppt band around a 25% target, a statutory mandate, no discretion to abstain, and a sign computable ex ante from public disclosures. Nothing else in the pool has a counterparty this literally forced. Economic rationale 1 = [IDEA-046](#idea-046) (calendar-clustered-trigger-resolution): the payer is explicitly not identified, the event-vol premium is already competitively traded, the residual edge is conceded to be an assumption, and there is zero quantitative evidence. Every other score was set by asking 'is this closer to GPIF's statutory band or to the NFP-convexity assumption?'
- Durability 1 anchor = [IDEA-045](#idea-045) (premium-scales-with-priced-dispersion): ex-post fitted thresholds, highly autocorrelated flat-curve regimes so the effective sample is a handful of episodes, a curve-to-vol link resting on a reaction function that has changed since 2003, and no way to detect regime end. That is the rubric's 1 exactly. Durability 5s were reserved for arithmetic identities and mandate/regulation plumbing.
- Ten extractors ran a compressed 3-5 scale — 47 of 56 raw scores sat at 3 or 4. Twenty-two scores were changed, listed below.
- [IDEA-001](#idea-001) stock-bond-correlation: economic rationale 4 -> 5 for the GOAL half. The extractor docked it because the flexible investor 'avoids a loss rather than monetises a premium', but the merged idea's core claim is a genuine compensated risk (someone must hold the everything-falls state), which the 2012 half states correctly.
- [IDEA-003](#idea-003) moments-must-match-the-premium: economic rationale 5 -> 4. The EM extractor gave 5 for naming the crash-risk counterparty. Downgraded to preserve the distinction between methods that stop you overpaying (this) and methods that capture a literal transfer ([IDEA-014](#idea-014), the fee audit, kept at 5). Testability confirmed at 5 by inspection: performance.py computes skew and excess kurtosis, report.py and professional_report.py render them, and stats/ ships bootstrap, cross_validation, minimum_backtest, multiple_testing, sharpe_tests.
- [IDEA-013](#idea-013) mechanical-replicant: testability 2 -> 3. The extractor scored the manager-index side only. Verified the replicant side is fully buildable (SPY, QQQ, TLT, IEF, GLD, USO and all seven G10 crosses resolve), and DBMF/KMLM are free via yfinance behind one registry line — the licensed index is the residual gap, not the whole test.
- [IDEA-016](#idea-016) flat-balance-sheet-is-tightening: testability 4 -> 3. Verified WRESBAL and WTREGEN raise ValueError through get_data despite sitting in fed_liquidity.parquet, CURRCIR is in neither registry nor lake, and TLAACBW027SBOG is in neither. Three of four inputs are unreachable from the research API — that is a 3, not a 4.
- [IDEA-017](#idea-017) capital-structure-valuation-wedge: testability held at 4 but for a corrected reason. The source digest listed the credit leg as a gap; a live call confirmed BAMLH0A0HYM2 returns data through get_data and BAMLC0A0CM is registered. The credit leg is NOT a gap; the equity forward-P/E leg is.
- [IDEA-018](#idea-018) effective-breadth-discount: testability 3 -> 4. Verified alpha_research/backtests/stats ships cross_validation.py, minimum_backtest.py and multiple_testing.py, and runners/ contains working position-producing entrypoints — the adjustment is implementable against existing code, not merely conceivable.
- [IDEA-022](#idea-022) forced-flow-response-function: testability 4 -> 3. The CTA extractor claimed 'data in the lake covers US Treasury futures (IBKR_RATES_FUTURES: ZB/ZN/ZF/ZT)'. Verified false: those are IBKR live-feed definitions in core/market_data_service.py, ZN raises ValueError through get_data, and no bond-futures price series exists in the Parquet lake. Even the US panel must be ETF-proxied.
- [IDEA-025](#idea-025) sharpe-gain-is-diversification-not-leverage: economic rationale 4 -> 3. It identifies where the edge is NOT — derivative of [IDEA-008](#idea-008) and [IDEA-001](#idea-001) rather than a source of return.
- [IDEA-033](#idea-033) fair-value-residual: economic rationale 4 -> 3. The extractor scored the underlying premium; the idea is the specification technique, and nobody is forced to mis-price a residual.
- [IDEA-024](#idea-024) horizon-match-regressors: economic rationale 4 -> 3, for the same reason — a scoping rule for other people's signals, and the source note does not even make the argument.
- [IDEA-037](#idea-037) tsmom: testability held at 4 with a corrected basis. Verified SPY, QQQ, TLT, IEF, SHY, GLD, USO and all seven G10 crosses resolve with yfinance fallback, so a four-sleeve proxy is buildable today; DBC, UUP, EFA, EEM, TIP do not resolve. Also verified the extractor's claim that fx/commodities/rates_yf bundles start 2024-02 — correct.
- [IDEA-036](#idea-036) threshold-proximity-dispersion: testability 4 held, basis corrected — XLB and XLI were confirmed resolving through the US_ETFS expansion in ticker_map, so the sector panel is live even though those tickers are absent from _ETF_ENTRIES.
- [IDEA-034](#idea-034) positive-carry-hedges: economic rationale 4 -> 3. The named constrained party is your own investment committee — a self-inflicted constraint — and the cost gap it exploits (the VRP) is well known and priced.
- [IDEA-038](#idea-038) ois-strip-level-vs-pace: economic rationale 3 -> 2. An arithmetic decomposition with no counterparty and no compensated risk; the extractor's 3 was generous relative to the anchors.
- [IDEA-040](#idea-040) positioning-saturation: economic rationale 4 -> 3. The capacity bound is never observed — it is inferred from a trailing 1-year range that drifts with realized vol, which is a statistical artifact rather than the disclosed mandate limit the mechanism requires.
- [IDEA-042](#idea-042) free-float-denominator: economic rationale 4 -> 3. A denominator discipline that improves the sizing of other people's claims, not a position.
- [IDEA-043](#idea-043) publisher-credibility-ledger: economic rationale 3 -> 2 (merged). No market counterparty at all. Testability held at 3 on verification that book_notes/playground/reports/ holds 10 digests — the archive seed is real but only ~3-5 entries are scorable against a ~30-entry minimum.
- [IDEA-039](#idea-039) backstop-censors-the-tail: economic rationale 4 -> 3, durability 5 -> 4. It is an inference rule that improves estimates rather than an edge anyone pays you to bear, and a formalized stigma-free standing facility would alter rather than merely relocate the censoring.
- [IDEA-023](#idea-023) funding-leg-as-first-order-choice: durability 5 -> 4, on the idea's own counterexample — TWD's EUR-funded vol was 36% HIGHER, so it is a strong prior, not a law.
- [IDEA-044](#idea-044) sentiment-extreme-needs-driver-check: economic rationale 3 -> 2. Nothing names a constrained counterparty or compensated risk, and the underlying contrarian signal is weak enough standalone that the whole claim rests on the filter.
- [IDEA-045](#idea-045) premium-scales-with-priced-dispersion: durability 3 -> 1 (the new low anchor) and economic rationale 3 -> 2. The extractor's own note conceded it is partly circular and indistinguishable from correct compensation for a real risk; that plus ex-post thresholds and undetectable regime end is the rubric's durability 1.
- [IDEA-046](#idea-046) calendar-clustered-trigger-resolution: economic rationale 3 -> 1 (the new low anchor), durability 3 -> 2.
- Testability corrections applied pool-wide from live checks against get_data: WRESBAL, DFII10, SOFR, T5YIE, DGS1, GDPC1, ^N225, ZN, DBMF, USDBRL=X, TIP, DBC, UUP, EFA and EEM all raise ValueError even where the data physically sits in the Parquet lake — a registry gap, not a data gap, and I scored it as a 1-line fix rather than a hard blocker. Confirmed working: BAMLH0A0HYM2, BAMLC0A0CM, TLT, IEF, SHY, GLD, USO, SPY, QQQ, XLB, XLI, DGS2/5/10/30, T10YIE, VIXCLS, IORB, DFF, GDP, CPIAUCSL, all seven G10 FX crosses. Confirmed absent with no substitute: any options pricing or P&L module in alpha_research/backtests (only a VIX notebook), any CFTC connector, any JGB curve, any repo/OIS instrument series.
