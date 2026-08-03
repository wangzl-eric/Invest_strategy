# Report Digest: Goldman Sachs Japan Macro Trading — 2026 Top Trades (Dec 2025) + 2026 Q2 Trade Ideas (Apr 2026)

- **Source:**
  - `book_notes/playground/reports/2025/12/macro_gs_jpy-macro-trading_2025-12-26.pdf` — 26 December 2025, 12:09 SGT, Tasuku Nishihara + 17 authors
  - `book_notes/playground/reports/2026/04/macro_gs_jpy-macro-trading_2026-04-07.pdf` — 7 April 2026, 16:30 SGT, Aya Shimada + 17 authors
- **Type / issuer:** Goldman Sachs Japan, **FICC & Equities desk color** distributed via the "Japan Macro Trading" Marquee channel — six trading desks (G10 FX Spot, JGB, Short Macro, STIR, Swaps, JPY Volex, APAC Exotics) each publishing their own axe. **Explicitly not GIR:** *"is not the product of Global Investment Research. It is not a research report and is not intended as such."*
- **Read on:** 2026-08-02 (digested as a pair — the April note is the mark-to-market and revision of the December note, and the delta is where the content is)
- **One-line claim:** Every JPY desk at GS is expressing one trade — **the 10-year JGB sector is the designated loser** — via a curve flattener/body-short, short 5y and 10y swap spreads, a 1s10s payer, a meeting-OIS steepener, and payer ladders; the shared premise is that the BoJ's terminal rate is 1.75–2.0%, well above the ~1.32% the OIS strip priced in April, with a weak yen and an intervention reaction function as the FX side of the same coin.
- **Decision it changes:** Whether to treat "BoJ normalization" as a *front-end/terminal-rate* story (as the market priced it) or as a **belly-supply and collateral story** (the desks' claim). If the desks are right, the trade is not long the front end — it is short the 10y against everything else, and the yen stays weak until an intervention/RSI trigger fires. It also changes how much weight to put on GS desk color relative to GS's own research house: on both the JGB and the yen calls, **the desks beat GIR** (see *Scorecard*).
- **Scores (1–5):** **Credibility 3** · **Relevance 4** · **Actionability 4**
  - *Credibility 3* — desk axes, not research: not one estimated model, not one confidence interval, not one backtest in either note; the central terminal-rate number is inferred from a verbal cue in an Ueda press conference. Sales desks publish what they want the other side of. Offsetting this: the numbers they *do* give are internally consistent and independently reconcilable (I re-derived their entire OIS probability table below to ±1pp), and the calls have worked.
  - *Relevance 4* — directly on Japan rates/FX; the platform holds the FX leg (`USDJPY=X`, daily) and the cash 10y (`IRLTLT01JPM156N`, monthly), but none of the swap, OIS, or JGB curve legs.
  - *Actionability 4* — split, and worth naming: **~8 of the 12 trades are unimplementable here** (no swaptions, no JPY swap curve, no JGB curve points). But the December note's **intervention reaction function is a fully specified, codeable rule set** requiring only `USDJPY=X`, which is already in the lake — and it fired live on 2026-07-30, three sessions before this reading.

---

## 1. Executive summary

Goldman Sachs' Japan FICC & Equities trading desks published these two Marquee notes on 26 December 2025 and 7 April 2026 to circulate each desk's own book to institutional clients — the first as a year-ahead trade list, the second as the new-fiscal-year update — covering how to position across JGBs, JPY swaps and swap spreads, meeting-dated OIS, swaptions, and the yen. Neither note contains an estimated model: the method is desk reasoning from three quantifiable inputs — the BoJ's terminal rate inferred from Governor Ueda's own language via a Fisher-identity argument, the FY2026 JGB issuance mix set against BoJ *rinban* tapering and life-insurer buying capacity, and BoJ balance-sheet redemption schedules driving collateral and repo — with option structures priced off quoted skew and conditional realized-vol statistics. The desks argue that the terminal rate is materially higher than priced (a fair value revised up from "at least 1.5%" in December to **1.75%** by April, with the swaps desk at **1.75–2.0%**, against roughly **1.32%** implied by the January-2027 OIS), that supply and *rinban* reduction concentrate the pain in the **10-year sector** specifically rather than the front end or the super-long, and that the yen keeps depreciating on negative real rates and structural outflows until the MoF intervenes on a rule the December note spells out precisely. Confidence is asserted rather than quantified throughout — there are no error bands, no probabilities on the terminal-rate estimate, and one trade (the 5y swap spread short) is retained in April with the desk's own admission that it has been **range-bound since mid-2025** despite what they call a favorable macro backdrop.

---

## 2. Methodology & reasoning

Five pillars carry both notes. Pillars 1–3 are the rates view (shared by every desk); pillar 4 is the FX side; pillar 5 is how the views get packaged into structures — and it is where the structures quietly contradict the views.

### Pillar 1 — The terminal rate: a Fisher identity fed one asserted number

- **Point:** Every rates trade in both notes is, at root, a bet that the BoJ's equilibrium real rate is about **−0.25%**, not the roughly **−0.68%** the market priced.
- **Evidence:** December — Ueda said the terminal-rate range is "wide" and that 75bp is "still some distance from the lower end"; the desk reads *"some distance"* as more than one 25bp increment, hence lower bound $\geq 1.25\%$, and "given wide distribution the medium value is at least 1.5%", with risks skewed up because "there is no need for real rate to be at −0.50% when 2% price stability target is declared to be achieved." April — fair value raised to **1.75%**, described as "a level that would imply a slightly negative real rate once the 2% price stability target is achieved"; the swaps desk carries **1.75–2.0%**. Hiking pace assumed at **one hike per ~6 months** in both notes.
- **Chain:** Ueda's verbal hedge → decode "some distance" as $\geq 2$ increments → lower bound of neutral $\geq 1.25\%$ → take the midpoint of a "wide" distribution → nominal terminal $\geq 1.5\%$ (Dec), revised to $1.75\%$ (Apr) → market prices only ~1.32% by Jan-27 → **a ~43bp gap = ~1.7 unpriced hikes, which is the entire P&L of the Apr-BoJ/Z6-1y steepener and the 1s10s payer.**
- **Read:** Inferential in form, assertion in substance. The identity is trivially correct; everything rests on the assumed $r^*$, which is never estimated, never given a range, and never sourced to anything but a press-conference adjective. April's revision from ~1.5% to 1.75% is presented without any new evidence — a 25bp move in the number carrying every trade in the book, justified by a sentence.

$$i^{*} \;=\; r^{*} + \pi^{*}$$

where $i^*$ is the nominal terminal policy rate, $r^*$ the equilibrium real rate, $\pi^*$ the BoJ's 2% target. December rejects $r^*=-0.50\%$ (→ $i^*\geq1.5\%$); April asserts $r^*\approx-0.25\%$ (→ $i^*=1.75\%$); the swaps desk allows $r^*\in[-0.25\%,\,0\%]$ (→ $1.75$–$2.0\%$). The April OIS strip implies $r^*\approx-0.68\%$. **The whole book is a 43bp bet on an unestimated parameter.**

**Their OIS table, fully reconciled.** The April note prints a meeting-probability table without saying how it is built. It is:

$$P_i \;=\; \frac{\mathrm{OIS}_i - r_0}{25\,\mathrm{bp}}, \qquad r_0 \approx 72.7\,\mathrm{bp}$$

with $\mathrm{OIS}_i$ the JSCC meeting-dated OIS (bp), $r_0$ the effective overnight rate under a 0.75% policy rate, and $P_i$ *cumulative* hikes priced. Reproduced against their printed figures:

| Meeting | JSCC OIS (bp) | "Jump" (bp) | GS Prob | Re-derived $P_i$ | Marginal hike prob (Jump/25) |
|---|--:|--:|--:|--:|--:|
| Apr-26 | 88.2 | 15.5 | 62% | 62.8% | 62% |
| Jun-26 | 95.0 | 6.8 | 89% | 90.0% | 27% |
| Jul-26 | 101.4 | 6.4 | 115% | 115.6% | 26% |
| Sep-26 | 109.3 | 7.9 | 146% | 147.2% | 32% |
| Oct-26 | 118.0 | 8.7 | 181% | 182.0% | 35% |
| Dec-26 | 125.6 | 7.6 | 212% | 212.4% | 30% |
| Jan-27 | 132.3 | 6.7 | 238% | 239.2% | 27% |

Every row ties to ±1.2pp, and the "Jump" column is exactly $25\,\mathrm{bp}\times$ the *marginal* probability. Two things fall straight out that the note never states: the market priced **~30% per meeting after April** (a smeared 6-monthly cadence, i.e. the market already agreed with GS on *pace*), and the Jan-27 terminal of **1.32%** is the only real disagreement. The trade is about level, not tempo — the note frames it as both.

### Pillar 2 — The 10y sector as the designated loser (supply/demand plumbing)

- **Point:** FY2026 issuance and *rinban* reduction push net supply into the 10y bucket while the super-long is being starved — so the pain is sector-specific, not a parallel bear steepening.
- **Evidence:** December — 10s40s at **148bp**, target **100bp**, negative carry **0.83bp/month**; ultra-long issuance cut of **¥0.75trn/month** vs the maximum historical lifer buying pace of **¥0.6trn/month**; 10y net issuance rises as BoJ *rinban* falls. April — 40y issuance down to **¥300bn every other month**; liquidity-tap bucket changes add 10y supply; "diminishing stock effect" from continued *rinban* cuts; 2y "has already priced in aggressive rate hikes, leaving little room for further upside of yield."
- **Chain:** Cut ultra-long issuance by ¥0.75trn/month → that cut alone exceeds the ¥0.6trn/month lifers can absorb at full tilt → the 40y is structurally over-bid → meanwhile *rinban* tapering plus tap-bucket reallocation dumps net supply into the 10y → the 2y is pinned by already-aggressive hike pricing → **the 10y is squeezed from both ends: it is short a buyer the 40y has and short the pricing cushion the 2y has** → express as 10s40s flattener (Dec), upgraded to a 2s10s40s body short (Apr) once the 2y leg is added.
- **Read:** This is the strongest pillar in either note and the only one built on quantities that could in principle be audited — issuance schedules and *rinban* plans are public. The supply/absorption comparison (¥0.75trn cut vs ¥0.6trn capacity) is a genuine, falsifiable claim, not a narrative. **The leap is the carry:** at 0.83bp/month against a 48bp target, the flattener burns **~10bp/year, or 21% of its entire target P&L per year of holding**. Net of carry the trade returns 38bp at a 12-month horizon and 28bp at 24 months. Neither note states a horizon, so the carry drag is never netted against the target anywhere in the analysis.

### Pillar 3 — Collateral and swap spreads (the pillar that did not work)

- **Point:** BoJ balance-sheet shrinkage frees collateral and removes the belly's structural buyer, so JGB asset swap spreads should cheapen.
- **Evidence:** December — BoJ balance-sheet drivers (JGB purchases + loan-support-program redemption + JGB redemption) totalled **−¥36trn in 2H25**, forecast **−¥41trn in 1H26**; 5y swap spread at **−6bp**, target **−12bp**; best entry timed to **Mar–Apr** on dealer inventory around supplementary-budget issuance. April — GC repo "at or slightly above IOER"; **¥11.7trn** of loan-support redemption scheduled for June; cross-currency basis pressured lower by a projected **\$500bn investment into the US**.
- **Chain:** BoJ shrinks its balance sheet → JGBs return to the market as collateral and repo firms above IOER → the belly loses its price-insensitive buyer → dealers carry heavier inventory into the Q1 supplementary-budget issuance → **ASW cheapens, so short the 5y (and 10y) swap spread.**
- **Read:** The chain is clean and the mechanism is real, and **the trade still did not pay** — April's own words: *"Despite these tailwinds, spread have remained range-bound since mid-2025."* That is a desk restating a thesis unchanged after roughly ten months of it not working, with the only modification being "manage the risk nimbly." It is also the one place either note names a competing mechanism honestly: the risk that the legacy swap-spread/cross-currency-basis correlation re-emerges — i.e. an admission that a variable outside the thesis has historically dominated it. **A correct mechanism that has not moved the price for ten months is evidence the mechanism is not the marginal driver.** Neither note draws that inference.

### Pillar 4 — Yen weakness and the intervention reaction function (December only)

- **Point:** The yen depreciates structurally, and the tradable edge is not the direction but the **MoF's reaction function**, which the desk specifies numerically.
- **Evidence:** Long AUD/EUR/MXN vs USD, short JPY; targets MXN **16.5** (2024 low), AUD **0.70**, EUR **1.20**. Intervention rules, quoted: authorities are "trying to make the market wary at the **160** level"; the market watches the prior high of **161.96**; if intervention occurs there is "a risk of continuous intervention for about **three days**"; "the price range on the first day of intervention is estimated to be approximately **4 yen**"; "when the daily **RSI exceeds 80**, the risk of intervention increases, so long positions should be avoided"; and — the forward-looking rule — "there is a tendency for the market to hit a low and rebound approximately **one month after intervention**, making it easier to build long positions at a favorable cost during that timing." Structural drivers named: negative real rates, outward direct investment, the services deficit, retail overseas investment, and a diminished safe-haven bid.
- **Chain:** Negative real rates + structural outflows → yen grinds weaker on cross-yen, not just USD/JPY → MoF tolerates *level* but not *volatility* (the G7 formulation, "when volatility increases") → so intervention is triggered by realized-vol and momentum extremes rather than by a line in the sand → therefore the position rule is not "short JPY" but **"short JPY, flat into RSI>80, re-enter ~1 month after the shock"** → hence "making cash a primary focus" and "flexible positioning changes will be required."
- **Read:** This is the most useful passage in either note and the only genuinely *systematic* content — a stated trigger set with numeric thresholds and a stated post-event holding rule. It is also, per the live data, **the one framework that can be validated from this platform, and it just fired** (see *Scorecard*). Note the leap: the "rebound one month after intervention" rule is asserted from "past currency intervention cases" with no sample size, no list of episodes, and no dispersion — a backtestable claim presented as folklore. **Also flag the omission:** the April note has *no G10 FX spot section at all.* The desk that published the most concrete framework in December dropped out of the April list entirely, leaving only an implicit weak-yen expression buried in an exotic (a range-accrual note requiring USD/JPY > 125). A desk going quiet on its own theme is information.

### Pillar 5 — Vol structure selection, where the packaging contradicts the view

- **Point:** Both notes' option trades are sold as expressions of a bearish rates view, but each one is structured so that being *very* right loses money.
- **Evidence:**
  - Dec — buy 2y10y ATM/ATM−50 **1x2 receiver spread** for 95c (mid 90c), "downside break-even vs outright at 1.35%", worth "135c in 1yr time if nothing happens", framed as a "protected bear position."
  - Apr — buy 6m20y/1y20y A−20 receivers with delta exchange: **175c at 4.32/day** and **285c at 4.28/day** (refs 6m20y 2.93%, 1y20y 3.00%), justified by conditional realized vol: unconditional 10-day realized **2.75bp/day**; in a rally regime (>15bp below the 20-day peak) **4.81bp/day**; in a sell-off regime (>15bp above the 20-day trough) **3.65bp/day**; skew trades payer-over-receiver.
  - Apr — **3m10y A+10/A+20/A+30 payer ladder for zero cost**, ref 3m10y JSCC **2.261%**, "risk is unlimited."
- **Chain (receivers):** Skew is positive, so receivers are cheap in premium → but rates realize **1.75×** their unconditional vol in rallies vs **1.33×** in sell-offs → so receiver gamma is systematically under-priced relative to what it actually delivers → **own receivers as the hedge on a short/steepener, and sell back the richened implieds when the rally comes.**
- **Read — the arithmetic the notes do not do:**
  - **Receivers.** The desk's own quoted breakeven of **4.32bp/day** sits *above* the unconditional realized (2.75) and *above* the sell-off regime (3.65), and *below* only the rally regime (4.81). Margin over breakeven in the good state: **0.49bp/day, ~11%**. So this is not "cheap convexity" — it is a **conditional bet that a sustained rally regime materializes**, losing in both other states the desk itself measured. The note's framing ("owning the receiver vol will give you the flexibility to enjoy the rates convexity") sells the payoff and omits the breakeven test that its own three statistics fail two out of three times.
  - **Payer ladder.** Buy A+10, sell A+20, sell A+30 at zero cost. With payoff $\max(S-K_1,0)-\max(S-K_2,0)-\max(S-K_3,0)$ and $K=\{2.361,\,2.461,\,2.561\}$: max profit is **10bp**, flat across 2.461–2.561, decaying to **zero at 2.661% (= +40bp over the 3m10y forward)** and unbounded loss beyond. **A trade sold under "core view remains bearish on the belly" caps the bear case at 10bp and starts losing if you are right by more than 40bp.** It is a skew-and-vol monetisation dressed as a directional short — the note half-admits this ("monetizing the recently heightened swaption volatility and skew") while filing it under a bearish header.
- **This is the conflict of interest showing up in the geometry, not the prose.** The *direction* calls in these notes are cheap for GS to publish and have been good. The *structures* — 1x2 spreads, ladders, delta-exchanged receivers, a 10yNC1y range-accrual note explicitly citing "competitive GS funding level" — are inventory and margin. Direction and packaging deserve separate credibility scores.

### Delta: what actually changed, December → April

| Desk | Dec 2025 | Apr 2026 | What the change means |
|---|---|---|---|
| Terminal rate | "at least 1.5%" | **1.75%** (swaps desk 1.75–2.0%) | +25bp with no new evidence cited — the single biggest revision, and it re-levers every trade |
| Short Macro | Pay Apr BoJ vs Z6-1y **<50bp** | Pay **<60bp**; "moved 10bps higher since our last note" | Trade worked, +10bp; conviction reiterated at a worse entry |
| JGB | 10s40s flattener | **2s10s40s body short** (adds 2s10s steepener) | Same view (10y is the loser), sharper expression — the 2y leg removes the parallel-shift risk in the flattener |
| STIR | Short 5y swap spread, −6bp → −12bp | Unchanged target, + "manage the risk nimbly" | The honest miss: range-bound since mid-2025, thesis restated rather than revised |
| Swaps | Short 10y swap spread | Short 10y ASW **+ pay 1s10s** (alt: 1s3s5s fly) | Escalation — the same view now expressed twice in one desk's book |
| JPY Volex | 2y10y 1x2 receiver spread | 6m20y/1y20y A−20 receivers w/ DX | Structure changed, logic identical: own receivers *against* a bearish core |
| G10 FX Spot | Long AUD/EUR/MXN vs USD, short JPY + full intervention playbook | **Section absent** | The FX desk withdrew from the published list; only an exotic RA note (USD/JPY > 125) carries the weak-yen view |
| APAC Exotics | — | Payer ladder + GSFCI 10yNC1y RA note | New desk added; both are premium/funding products, not views |

**Weakest link (across all five pillars):** not any single trade, but that **there is only one trade.** The 10s40s flattener, the 2s10s40s body short, the short 5y ASW, the short 10y ASW, the 1s10s payer, the Apr/Z6-1y steepener, and the payer ladder are seven expressions of one position — short the JPY belly against an unestimated $r^*=-0.25\%$ — and the receivers are a hedge *on* that same position, not a diversifier from it. Book-level correlation is close to 1. A single event that neither note prices — the BoJ pausing under the political pressure the April note itself flags ("government pressure"), or a global risk-off rally out of the Middle East situation both notes name — takes every line down together, with the receiver hedge needing a *sustained* rally (>4.32bp/day realized) rather than merely a sharp one to pay for itself.

---

## 3. Keywords

`BoJ terminal rate`, `meeting-dated OIS probability`, `JGB 10s40s flattener`, `2s10s40s body short`, `JGB swap spread / ASW`, `rinban taper & stock effect`, `MoF intervention reaction function`, `RSI-80 intervention trigger`, `conditional realized vol asymmetry`, `payer ladder skew monetisation`, `sell-side desk axe vs GIR`

---

## Scorecard as of 2026-08-02 (added on read — not in the reports)

Seven months of data are now available. Both notes' central calls can be marked to market from the platform.

**JGB 10y — the desks were right, and beat their own research house.** `IRLTLT01JPM156N` (monthly, 45-day PIT lag):

| Reference month | 10y JGB yield | vs Dec note |
|---|--:|--:|
| Dec-2025 (note published) | 2.060% | — |
| Mar-2026 (Q2 note published) | 2.345% | +29bp |
| Apr-2026 | 2.515% | +46bp |
| May-2026 | 2.650% | +59bp |
| Jun-2026 (latest) | **2.670%** | **+61bp** |

The GIR *2026 Japan Economic Outlook* base case was a 10y holding near **2.0%** through 2026. It is at 2.67% and monotonically rising. The desks' supply/*rinban* pillar called this; the research house did not.

**A caution that comes with being right:** the payer ladder illustrates the pillar-5 problem live. Between the April note and June, the cash 10y proxy moved **+32bp** — that lands inside the ladder's flat, capped **10bp** zone and close to its **+40bp** breakeven. Being right by 32bp on an outright short paid roughly three times what the "leveraged" zero-cost structure did. (Caveat: the cash 10y monthly average is a proxy for the 3m10y JSCC forward the ladder actually references, and the option expired ~7 July.)

**USD/JPY — the desks were right on direction, and the December intervention playbook then fired almost exactly to spec on 2026-07-30.** From `USDJPY=X` (daily):

| Date | Open | High | Low | Close | Daily range | RSI(14) |
|---|--:|--:|--:|--:|--:|--:|
| 2026-07-24 | 163.88 | 163.93 | 163.65 | 163.83 | 0.29 | 71.9 |
| 2026-07-29 | 163.86 | 163.88 | 163.29 | **163.86** | 0.59 | 70.2 |
| **2026-07-30** | 163.25 | 163.73 | **157.99** | 163.30 | **5.74** | 60.9 |
| 2026-07-31 | 160.18 | 160.84 | 158.67 | **160.18** | 2.17 | 34.0 |

Against the December note's stated rules:

| Rule (Dec 2025) | Outcome |
|---|---|
| Watch above the 161.96 prior high | Breached; peak close **163.86** on 29-Jul |
| RSI > 80 → avoid longs | RSI(14) peaked at **80.5** on 2026-07-01, a month before the event |
| First-day range "approximately 4 yen" | Actual **5.74 yen** — largest daily range in the sample, exceeding the estimate |
| Intervention runs "about three days" | 30-Jul (5.74) and 31-Jul (2.17) both far above normal range; day 3 falls after the data cut |
| Authorities "buying time at the 160 level" | Spot closed **160.18** on 31-Jul — parked exactly on the stated line |

**The live, forward-looking part:** the December note's rule is that the market "hits a low and rebounds approximately one month after intervention," making that the favorable entry for re-establishing long-high-yielder/short-JPY. That dates a testable window to **late August / early September 2026** — starting from today, this is a prediction, not a postdiction, and it is checkable with data already in the lake.

**Net:** on the two calls this platform can observe, the FICC desk color beat GS Global Investment Research **twice** — GIR had the 10y flat at 2.0% (actual 2.67%) and USD/JPY grinding to 152 in 2026 (actual 163.86 peak). That is a reason to weight this channel more, and a caution against reading the GIR *Japan Outlook* digest as the house view on Japan rates.

---

## What to watch

| Observable | Series | Level now (2026-08-02) | Confirms if | Breaks if |
|---|---|---|---|---|
| USD/JPY spot | `USDJPY=X` — daily, in lake | **160.18** (31-Jul close), post-shock from a 163.86 peak | Stabilises then resumes higher after ~1 month, per the Dec rebound rule → short-JPY carry re-entry late Aug/early Sep | Sustained break below ~155 (would mean intervention *plus* a BoJ hike changed the level, not just the vol) — or a re-break above 163.9 within days, which would mean intervention failed outright |
| USD/JPY 14-day RSI | derived from `USDJPY=X` | **34.0** (31-Jul), down from an 80.5 peak on 01-Jul | Recovery back through 50–60 without hitting 80 = clean carry window | Back above **80** = the Dec note's stated stand-aside trigger fires again |
| JGB 10y yield | `IRLTLT01JPM156N` — **monthly, 45-day PIT lag** (too slow for any trade here; resolution gap) | **2.670%** (Jun-26 reference, published 16-Jul) | Keeps climbing → pillar-2 supply thesis intact | Rolls back under ~2.3% → *rinban*/supply story has been overwhelmed by a global rally or a BoJ pause |
| BoJ policy rate + meeting OIS | **Not in lake — gap.** No BoJ policy rate, no TONA, no JSCC meeting-dated OIS | 0.75% policy ($r_0\approx0.727\%$); Jan-27 OIS **132.3bp** as of 07-Apr | Strip repricing toward 1.75% = the desks' 43bp gap closing | Strip stalls below ~1.35% into 2027 = the market never bought $r^*=-0.25\%$ |
| JGB 10s40s + 5y/10y swap spreads | **Not in lake — gap.** No JGB curve points (2y/5y/20y/40y), no JPY swap curve, no ASW | 10s40s **148bp** (25-Dec-25); 5y ASW **−6bp**, target −12bp | 10s40s → 100bp; 5y ASW → −12bp | 5y ASW still range-bound (as it has been since mid-2025) → pillar 3 is a mechanism that is not the marginal price driver |

---

## Connection to our platform

- **`book_notes/playground/reports/2026/01/economics_gs_japan-outlook_2026-01-06.md`** — **direct contradiction, now resolved against GIR.** GIR's base case: 10y JGB flat ~2.0%, USD/JPY to 152 (2026E) / 139 (2027E), BoJ to 1.0% in Jul-26 and 1.5% neutral by Jul-27. These desks: 10y sells off hard, yen stays weak, terminal 1.75–2.0%. Live: 10y at **2.67%**, USD/JPY peaked at **163.86**. The desks won both. The earlier digest's *What to watch* already flagged the JGB row as "already breaking" — this pair explains *why*, and supplies the mechanism (supply mix + *rinban* stock effect) GIR's demand-side model had no channel for.
- **`book_notes/playground/reports/2026/06/flows_gs_cta-bond-futures_2026-06-09.md`** — **corroborates, and is the crowding warning.** That note's CTA model (data 08-Jun-26) has JGB futures **net short and below its momentum threshold** while Europe covers. These desks are short 10y JGB duration seven different ways. Same side of the same trade as the systematic community — which makes the CTA note's short-covering-squeeze branch the precise tail that would take down every position in both notes simultaneously. Worth reading the two together as a single positioning picture rather than as separate digests.
- **`book_notes/playground/reports/2025/11/rates_gs_vol-strategies_2025-11-13.md`** — **validates from the opposite direction.** That GIR piece found raw implied-vol valuation is a poor timing signal while *macro-conditioned* fair value works. The April desk arrives at the same lesson empirically: it ignores IV levels and conditions on a **realized-vol regime** (rally 4.81 vs sell-off 3.65 vs unconditional 2.75 bp/day). Same principle — condition on regime, don't trade raw valuation — reached from the trading side. Also note the JPY 20y swaption sits inside that paper's USD/EUR/GBP/JPY sample, so the two are describing the same surface.
- **`alpha_research/research/strategies/fx_carry_2026-03-13_conditional/proposal.md`** — **could improve, and this is the most actionable item in the pair.** That proposal has an open PM challenge ("add proper risk-off overlay (VIX threshold or credit spread widening trigger)") and lists "JPY short rate (TONAR) — MISSING" as a blocking data gap. The December note supplies a JPY-specific overlay that needs **no new data at all**: cut or flat short-JPY carry when USD/JPY 14-day RSI > 80, exit on a >4-yen daily range, re-enter ~1 month later. Fully codeable today from `USDJPY=X`, and it has one clean live event (2026-07-30) plus prior MoF episodes to test on. This is a concrete overlay for a specific named weakness in an existing proposal — recording it here for Zelin to decide on rather than implementing.
- **`alpha_research/backtests/runners/` and `alpha_research/research/pool/`** — **gap, unchanged from the Japan Outlook digest.** Neither runner (`sector_rotation.py`, `vol_conditioned_reversal.py`) nor either pool manifest touches JPY, JGB, or Japan. The intervention overlay above is the most plausible first JPY-touching node, since it is the only idea in these notes implementable with data already in the lake.
- **`core/market_data_service.py` / `alpha_research/quant_data/ticker_map.py`** — **gap, quantified.** Of the 12 trades across both notes, only the FX leg and the cash 10y are observable here. Missing: JGB curve points (2y/5y/20y/40y), the JPY swap and OIS curves, JSCC meeting-dated OIS, and any swap-spread series. Separately, `IRLTLT01JPM156N` is **monthly with a 45-day PIT lag** — usable for a slow thesis check, useless for anything these desks actually trade. A daily JGB yield source is a distinct gap from the Japan CPI gap already logged.
- **Cross-cutting, for how we read this channel:** these are FICC desk axes, not research — and they outperformed the research product twice on the calls we can measure. The reusable lesson is to score **direction** and **structure** separately: the direction calls were good and free to publish; the structures (1x2 spreads, zero-cost ladders, delta-exchanged receivers, a range-accrual note citing "competitive GS funding level") are inventory, and at least one of them caps the very view it claims to express.

---

## Commentary — value to our investment learning

**`direct` · `useful`**  ·  ranked **1 of 10** in the library by contribution to learning

> The only note here whose two economic-rationale 5s are both its own argument and both rest on quantities a reader can independently check — public issuance calendars and published strike placement — which is why the most conflicted document in the library is also its most auditable.

**Why.** 6 ideas, 71 points (tied first), and 50 exclusive points — highest of any GS note, second only to the AQR classic. Two of the pool's nine econ-5s, and IDEA-002 at 14/15 is the joint-highest sole-source entry: the only thing above it (IDEA-001, 15) is merged from two reports. IDEA-011 carries testability 5 and IDEAS.md calls it 'the single most implementable idea in the pool', with a live 2026-07-30 event already partly marked (RSI>80 fired a month early; the 161.96 high was breached; spot parked on the stated 160 line). Crucially IDEA-005 (0.75trn/mo issuance cut vs 0.6trn/mo lifer absorption) and IDEA-011 (the numeric intervention trigger set) are the desks' OWN content, not corrections to it — the exact inverse of the Bridgewater pattern. Honest limit: two of five pillars produced nothing of weight — the terminal-rate pillar yielded only IDEA-038 at econ 2, and the swap-spread pillar, range-bound for ten months, yielded no pool idea at all — so roughly 40% of the note is a 43bp bet on an unestimated r*.

**Take.** (1) IDEA-011 as an actual build: flat short-JPY carry at 14d RSI > 80, exit on a >4-yen daily range, re-enter ~1 month later. Needs only USDJPY=X, which resolves and has a dedicated parquet, and it answers the named open PM challenge in fx_carry_2026-03-13_conditional/proposal.md ('add proper risk-off overlay') without touching the blocking TONAR gap. (2) IDEA-002 as a permanent reading rule: compute a packaged trade's max profit, the point where being right stops paying, and the breakeven in the seller's OWN vol units, before accepting its label — score direction and structure separately, because direction is free for a dealer to publish and structure is inventory. The zero-cost payer ladder capped at 10bp and losing beyond +40bp, filed under a bearish header, is the library's cleanest worked instance, and the +32bp live move proved it: an outright short paid ~3x the 'leveraged' structure. (3) IDEA-005 as method, not a Japan call: issuance calendar plus taper schedule identify WHICH curve sector loses its price-insensitive buyer, independent of the level view; express as a fly shorting the squeezed body. Transpose to QRA tables, SOMA redemption caps and DGS2/5/10/30, since no JGB curve points exist here. (4) One unharvested lesson worth keeping separately: a clean mechanism that has not moved the price for ten months is evidence it is not the marginal driver, and restating it is not analysis.

**Ignore.** Everything levered to the 43bp terminal-rate gap — 1.75% vs 1.32%, the Fisher-identity decoding of 'some distance' from an Ueda press conference, April's unexplained +25bp revision. One asserted parameter carrying seven of twelve trades, resolving by Jan-2027. All trade levels and term-sheet specifics: 10s40s 148→100bp, 5y ASW −6→−12bp, pay Apr-BoJ vs Z6-1y <60bp, the 2.361/2.461/2.561 ladder (expired ~7 Jul 2026, dead before the digest was written), the 175c/285c receiver premiums, MXN 16.5 / AUD 0.70 / EUR 1.20. The Dec→Apr delta table is desk archaeology past its single use as a revision-without-evidence tell. Around eight of twelve trades are unimplementable here anyway — no swaptions, no JPY swap or OIS curve, no JGB curve points. Also discount its IDEA-031 contribution: the conditional realized-vol asymmetry (4.81/3.65/2.75 bp/day) lost the merge to the rates-vol note's flow-exhaustion mechanism and was explicitly demoted to the weaker half.

**Second read.** Yes, and the window is now. The December note's rebound rule dates a testable entry to late August / early September 2026, so Pillar 4 and the USD/JPY scorecard should be marked against live data in the next few weeks to score a genuinely ex-ante prediction. That is a one-time trigger. After it resolves the document is spent and survives only through IDEA-002 (durability 5, permanent because it follows from the dealer business model) and IDEA-005 transposed to USTs. Do not re-read for the rates view; re-read Pillar 5's arithmetic when a structured product or packaged trade next crosses the desk.

*Axes are independent: `indirect` means it contributes through method or context rather than
directly investable content — not that it is weak. Verdicts were calibrated across all 10
digests together, ranked by exclusive idea-yield in [`IDEAS.md`](../../IDEAS.md) and by whether
the report's best contributions were its own argument or critiques of it.*
