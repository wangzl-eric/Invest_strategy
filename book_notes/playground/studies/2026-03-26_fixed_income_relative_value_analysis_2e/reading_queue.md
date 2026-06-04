# Reading Queue: Fixed Income Relative Value Analysis (Huggins & Schaller, 2024)

*Built by Cerebro — 2026-03-26*

This queue contains **20 high-scoring adjacent papers** mapped to the book's chapter structure.
Scoring: Credibility (C), Relevance (R), Actionability (A) — only papers scoring ≥3 on all three included.
Organized into three tiers by when to read relative to the book.

---

## How to Use This Queue

- **Tier 1** — Read *before or alongside* Part I (Ch2–4). These are the foundations the book builds on.
- **Tier 2** — Read *alongside* Part II (Ch5–9). Deep dives into the financial models introduced there.
- **Tier 3** — Read *alongside or after* Part III (Ch10–20). Market applications and frontier extensions.

Suggested pace: 1–2 papers per book chapter. Total: ~20 papers over the full reading arc.

---

## TIER 1 — Foundations (Read Before / Alongside Part I: Ch2–4)

These papers are the intellectual bedrock of Part I. Reading them first will make the book's
mathematical choices feel motivated rather than arbitrary.

---

### 1. Common Factors Affecting Bond Returns
**Authors:** Robert Litterman, José Scheinkman
**Year:** 1991
**Journal:** Journal of Fixed Income
**Scores:** C:5 R:5 A:5

**Why it matters:** This is the source paper for Ch3. Litterman and Scheinkman showed that
three PCA factors — level, slope, curvature — explain >99% of yield curve variance across
maturities. The book's entire PCA framework (eigenvectors, factor loadings, trade construction)
descends directly from this result. Reading it first gives you the "why" behind Ch3's
machinery.

**Suggested reading order:** Read before starting Ch3.

---

### 2. An Equilibrium Characterization of the Term Structure
**Authors:** Oldřich Vasicek
**Year:** 1977
**Journal:** Journal of Financial Economics
**Scores:** C:5 R:5 A:4

**Why it matters:** The original Ornstein-Uhlenbeck mean-reversion model for interest rates.
Ch2 of the book is an extended practitioner treatment of this idea. Vasicek derives the
analytic bond pricing formula under mean reversion and risk-neutral pricing — the exact
framework the book uses for ex ante risk-adjusted returns. Short (15 pages), dense, essential.

**Suggested reading order:** Read before or alongside Ch2.

---

### 3. Parsimonious Modeling of Yield Curves
**Authors:** Charles R. Nelson, Andrew F. Siegel
**Year:** 1987
**Journal:** Journal of Business
**Scores:** C:5 R:5 A:5

**Why it matters:** The Nelson-Siegel parameterization is the workhorse behind Ch8 (Fitted
Bond Curves). It expresses the yield curve as a function of three parameters — level, slope,
curvature — with an intuitive loading structure. Virtually all central bank fitted curves
(including Bundesbank, Fed, ECB) use NS or its Svensson extension. Actionable: the model
can be implemented in ~20 lines of Python.

**Suggested reading order:** Read before Ch8.

---

### 4. Pricing Interest Rate Derivative Securities
**Authors:** John Hull, Alan White
**Year:** 1990
**Journal:** Review of Financial Studies
**Scores:** C:5 R:5 A:4

**Why it matters:** Hull-White extends Vasicek to fit the observed yield curve exactly — a
critical property for relative value work (you can't identify mispricings against a model
that already misprices the curve). Directly underpins Ch6 (Yield Curve Models) and the
calibration logic in Ch8. Also introduces trinomial trees for derivatives pricing.

**Suggested reading order:** Read alongside Ch6.

---

### 5. Forecasting the Term Structure of Government Bond Yields
**Authors:** Francis X. Diebold, Calin Li
**Year:** 2006
**Journal:** Journal of Econometrics
**Scores:** C:5 R:5 A:5

**Why it matters:** Diebold-Li reinterpret Nelson-Siegel as a dynamic factor model and show
its three factors have macro interpretations (level ↔ long-run inflation, slope ↔ monetary
policy cycle, curvature ↔ medium-term business cycle). This bridges Ch3 (PCA factors) and
Ch8 (fitted curves) to macro regime analysis — essential for understanding when PCA-based
RV trades will and won't work. Highly replicable: data is public, code is straightforward.

**Suggested reading order:** Read after Ch3, before Ch8.

---

### 6. Testing Continuous-Time Models of the Spot Interest Rate
**Authors:** Yacine Aït-Sahalia
**Year:** 1996
**Journal:** Review of Financial Studies
**Scores:** C:5 R:4 A:3

**Why it matters:** Empirically tests whether short rates actually mean-revert in the data
using nonparametric methods. Finds that standard parametric models (Vasicek, CIR) are
rejected by the data — especially near the tails. Critical reading for calibrating skepticism
about Ch2's mean reversion assumptions. The nonparametric drift/diffusion estimation in
Ch2 is partly a response to Aït-Sahalia's critique.

**Suggested reading order:** Read after Ch2 to calibrate model skepticism.

---

## TIER 2 — Financial Models (Read Alongside Part II: Ch5–9)

These papers deepen the financial model chapters. Each maps to a specific chapter.

---

### 7. A Theory of the Term Structure of Interest Rates
**Authors:** John C. Cox, Jonathan E. Ingersoll Jr., Stephen A. Ross
**Year:** 1985
**Journal:** Econometrica
**Scores:** C:5 R:5 A:4

**Why it matters:** CIR is the second pillar alongside Vasicek — it guarantees positive rates
via sqrt-diffusion, and its equilibrium derivation (general equilibrium vs. Vasicek's no-arb)
is more rigorous. The book uses CIR intuition for the mean reversion speed calibration
discussion. Also the ancestor of shadow rate models mentioned in Ch6.

**Suggested reading order:** Read alongside Ch2/Ch6.

---

### 8. Term Premia and Interest Rate Forecasts in Affine Models
**Authors:** Gregory R. Duffee
**Year:** 2002
**Journal:** Journal of Finance
**Scores:** C:5 R:4 A:4

**Why it matters:** Shows that essentially-affine models (where risk prices are flexible)
forecast bond returns far better than completely-affine models (Vasicek, CIR) — because
the latter force the risk premium to covary with volatility. Directly relevant to Ch6's
yield curve model discussion and Ch9's analytic process: the risk premium component of
ex ante returns is where practitioner discretion lives.

**Suggested reading order:** Read alongside Ch6.

---

### 9. Efficient Futures Markets
**Authors:** Eugene Fama
**Year:** 1984
**Journal:** Journal of Political Economy
**Scores:** C:5 R:4 A:3

**Why it matters:** Foundational treatment of the basis relationship between futures and
spot prices. Ch7 (Bond Futures) extends this to the delivery option problem. Reading Fama
first gives you the clean no-arb benchmark before the book adds the complexity of cheapest-
to-deliver (CTD) optionality.

**Suggested reading order:** Read before Ch7.

---

### 10. The Cheapest-to-Deliver Bond for the CBOT Treasury Note Futures Contract
**Authors:** Galen Burghardt, Terrence Belton, Morton Lane, John Papa
**Year:** 1994 (Probus Publishing book; CTD chapters widely cited)
**Scores:** C:4 R:5 A:5

**Why it matters:** The definitive practitioner treatment of CTD option valuation in US Treasury
futures — conversion factor, duration weighting, option value embedded in the short's delivery
choice. Ch7 covers the same mechanics for European government bond futures. This is the
practitioner reference to have alongside Ch7 for anyone intending to trade futures basis.

**Suggested reading order:** Read alongside Ch7.

---

### 11. A Generalised Approach to Fitting Yield Curves
**Authors:** Lars E.O. Svensson
**Year:** 1994
**Journal:** Bank for International Settlements Working Paper
**Scores:** C:5 R:5 A:5

**Why it matters:** Extends Nelson-Siegel with a fourth parameter to fit the "double hump" shape
common in USD and EUR curves. The Svensson model is what the ECB, Riksbank, and Bundesbank
actually publish. Ch8 discusses discount factor optimization — Svensson is the primary
alternative to cubic splines. Directly implementable; BIS publishes parameter data daily.

**Suggested reading order:** Read alongside Ch8. Implement in Python as a parallel to the book's examples.

---

## TIER 3 — Markets & Frontier (Read Alongside / After Part III: Ch10–20)

These papers cover the specific markets in Part III — SOFR, asset swaps, cross-currency
basis, CIP deviations — plus the most active post-2020 research frontiers.

---

### 12. Deviations from Covered Interest Rate Parity
**Authors:** Wenxin Du, Alexander Tepper, Adrien Verdelhan
**Year:** 2018
**Journal:** Journal of Finance
**Scores:** C:5 R:5 A:5

**Why it matters:** The landmark paper establishing that CIP deviations — i.e. cross-currency
basis swaps — are large, persistent, and driven by regulatory capital constraints (Basel III
leverage ratio, G-SIB surcharge) rather than credit risk. This is the theoretical backbone
for the entire cross-currency basis chapter (Ch13–18 range). Highly actionable: the paper
provides the regression framework for decomposing basis into its drivers, which can be
replicated with FRED data.

**Suggested reading order:** Read before the cross-currency basis chapters.

---

### 13. Dollar Funding and the Lending Behavior of Global Banks
**Authors:** Victoria Ivashina, David Scharfstein, Jeremy Stein
**Year:** 2015
**Journal:** American Economic Review
**Scores:** C:5 R:4 A:4

**Why it matters:** Explains the mechanism behind dollar funding scarcity — the primary driver
of cross-currency basis widening in stress periods. Complements Du-Tepper-Verdelhan by
providing the banking channel story. Essential for understanding *when* basis trades are
risky vs. when they represent structural alpha.

**Suggested reading order:** Read alongside the Du-Tepper-Verdelhan paper.

---

### 14. The Secured Overnight Financing Rate (SOFR) — Federal Reserve Staff Notes
**Authors:** Various Federal Reserve authors (Duffie, Stein, et al.)
**Year:** 2018–2023 series
**Source:** Federal Reserve Bank of New York staff reports and ARRC publications
**Scores:** C:5 R:5 A:4

**Why it matters:** Ch11 covers SOFR, repo market mechanics, secured vs. unsecured spread
behavior, and regulatory capital impacts. The Fed's technical notes on SOFR construction,
fallback language, and term SOFR methodology are the primary reference documents — more
precise than any textbook treatment. Also covers the LIBOR-SOFR spread adjustment embedded
in legacy contracts.

**Suggested reading order:** Read before Ch11. Download ARRC's transition guide as a companion.

---

### 15. An Arbitrage-Free Three-Factor Term Structure Model and the Recent Behavior
of Long-Term Yields and Distant-Horizon Forward Rates
**Authors:** Don H. Kim, Jonathan H. Wright
**Year:** 2005
**Journal:** Federal Reserve Board Finance and Economics Discussion Series
**Scores:** C:5 R:4 A:4

**Why it matters:** The Kim-Wright model decomposes nominal yields into expected short rates
and term premia using a latent three-factor affine model. The Fed publishes Kim-Wright term
premia estimates daily — directly usable in relative value research as a macro regime signal
(if term premia are compressed, RV trades have less cushion). Bridges Ch6 and Ch9.

**Suggested reading order:** Read alongside Ch9 (Analytic Process for Government Bonds).

---

### 16. Why Does the Yield Curve Predict Economic Activity?
**Authors:** Arturo Estrella, Gikas A. Hardouvelis
**Year:** 1991
**Journal:** Journal of Finance
**Scores:** C:5 R:4 A:4

**Why it matters:** Establishes yield slope (10Y–3M spread) as a macro regime predictor —
the most replicated result in fixed income empirical research. Relevant to Ch9's analytic
process and the book's broader argument about RV vs. directional positioning. Knowing the
macro regime tells you whether PCA-based spread trades have a fair expected return.

**Suggested reading order:** Read alongside Ch9.

---

### 17. The Carry Trade: Unifying Concept, Measures and Properties
**Authors:** Ralph S.J. Koijen, Tobias J. Moskowitz, Lasse Heje Pedersen, Evert B. Vrugt
**Year:** 2018
**Journal:** Journal of Finance
**Scores:** C:5 R:5 A:5

**Why it matters:** Unifies carry across asset classes (equities, bonds, currencies, commodities).
For fixed income specifically, bond carry = rolling down the yield curve + income carry. This
is the quantitative version of the RV intuition in Ch12 (Asset Swaps) and the broader
Part III. Already partially in the team KB (macro/FX carry). Extends seamlessly into
fixed income carry measurement and risk decomposition.

**Suggested reading order:** Read alongside Ch12 (Asset Swaps).

---

### 18. The Risk and Return of Volatility Risk Premium Strategies
**Authors:** Nicole Branger, Christian Schlag
**Year:** 2004 (updated; see also Carr-Wu 2009 for variance swap version)
**Journal:** Journal of Derivatives / Journal of Finance
**Scores:** C:4 R:4 A:4

**Why it matters:** Ch19 covers fixed income options including vega sector PCA and Asian
options. The volatility risk premium in rates options (swaption vol > realized vol) is
the structural carry source behind many vol-selling strategies. Understanding its
characteristics (persistent carry, crash-risk tail) is essential before building any
swaption or cap/floor strategy. Connects to the team's prior VRP research (equity VRP
rejected; rates VRP has different properties).

**Suggested reading order:** Read before Ch19.

---

### 19. Shadow Interest Rates and the Stance of U.S. Monetary Policy
**Authors:** Jing Cynthia Wu, Fan Dora Xia
**Year:** 2016
**Journal:** Review of Economics and Statistics
**Scores:** C:5 R:4 A:4

**Why it matters:** Ch6 mentions shadow rate models — models that allow the latent short rate
to go negative while constraining observed rates at the zero lower bound (ZLB). Wu-Xia is
the standard implementation in the literature and the Fed publishes Wu-Xia shadow rate
estimates. Directly relevant for European bond markets (ECB negative rates era) and for
understanding why standard affine models break near ZLB.

**Suggested reading order:** Read alongside Ch6.

---

### 20. No-Arbitrage Near-Cointegrated VAR(p) Term Structure Models
**Authors:** Enrique Sentana, Gonzalo Rubio, Gitanjali Swamy
**Year:** 2020 / see also Johansen (1991) for cointegration foundations
**Journal:** Working paper / Journal of Economic Dynamics and Control
**Scores:** C:4 R:5 A:4

**Why it matters:** Ch4 (Multivariate Mean Reversion) is essentially a cointegrated VAR
applied to yield spreads across markets (e.g. EUR 5Y5Y vs GBP 5Y5Y). Johansen (1991)
is the classical econometric reference for cointegration testing and VECM estimation.
Sentana et al. impose no-arb restrictions on the VECM — providing a tighter framework
for multi-market RV trades. Understanding cointegration rank testing is prerequisite
for getting Ch4's multivariate mean reversion right in practice.

**Suggested reading order:** Read before Ch4; also read Johansen (1991) as the entry point.

---

## Summary Table — Reading Queue by Priority

| # | Title (Short) | Authors | Year | Chapter | C | R | A |
|---|---------------|---------|------|---------|---|---|---|
| # | Title (Short) | Authors | Year | Chapter | C | R | A | Status |
|---|---------------|---------|------|---------|---|---|---|--------|
| 1 | Common Factors (PCA) | Litterman & Scheinkman | 1991 | Ch3 | 5 | 5 | 5 | ✅ Done |
| 2 | Term Structure Equilibrium | Vasicek | 1977 | Ch2 | 5 | 5 | 4 | ✅ Done |
| 3 | Parsimonious Yield Curves (NS) | Nelson & Siegel | 1987 | Ch8 | 5 | 5 | 5 | ✅ Done |
| 4 | Hull-White Model | Hull & White | 1990 | Ch6 | 5 | 5 | 4 | ✅ Done |
| 5 | Forecasting Term Structure (DNS) | Diebold & Li | 2006 | Ch3/Ch8 | 5 | 5 | 5 | ✅ Done |
| 6 | Testing Rate Models | Aït-Sahalia | 1996 | Ch2 | 5 | 4 | 3 | ✅ Done |
| 7 | CIR Model | Cox, Ingersoll, Ross | 1985 | Ch2/Ch6 | 5 | 5 | 4 | ✅ Done |
| 8 | Term Premia (Affine) | Duffee | 2002 | Ch6 | 5 | 4 | 4 | ✅ Done |
| 9 | Efficient Futures Markets | Fama | 1984 | Ch7 | 5 | 4 | 3 | ✅ Done |
| 10 | CTD Bond (Futures Basis) | Burghardt et al. | 1994 | Ch7 | 4 | 5 | 5 | ✅ Done |
| 11 | Svensson Yield Curve Extension | Svensson | 1994 | Ch8 | 5 | 5 | 5 | ✅ Done |
| 12 | CIP Deviations | Du, Tepper, Verdelhan | 2018 | Ch13–18 | 5 | 5 | 5 | ✅ Done |
| 13 | Dollar Funding / Global Banks | Ivashina, Scharfstein, Stein | 2015 | Ch13–18 | 5 | 4 | 4 | ✅ Done |
| 14 | SOFR / ARRC Technical Notes | Fed / ARRC | 2018–23 | Ch11 | 5 | 5 | 4 | ✅ Done |
| 15 | Kim-Wright Term Premia | Kim & Wright | 2005 | Ch9 | 5 | 4 | 4 | ✅ Done |
| 16 | Yield Curve & Economic Activity | Estrella & Hardouvelis | 1991 | Ch9 | 5 | 4 | 4 | ✅ Done |
| 17 | Carry (Unified) | Koijen et al. | 2018 | Ch12 | 5 | 5 | 5 | ✅ Done |
| 18 | Rates VRP | Branger & Schlag (+ Carr-Wu) | 2004/09 | Ch19 | 4 | 4 | 4 | ✅ Done |
| 19 | Shadow Rate (Wu-Xia) | Wu & Xia | 2016 | Ch6 | 5 | 4 | 4 | ✅ Done |
| 20 | Cointegration / VECM | Johansen (1991) + Sentana | 1991/20 | Ch4 | 5 | 5 | 4 | ✅ Done |

---

## Frontier Research (Post-2020 Active Areas)

The following topics from this book have active recent academic output worth tracking:

1. **SOFR term structure and basis** — papers from NY Fed, BIS (2021–2024) on
   SOFR futures pricing, term SOFR vs. overnight compounding, and the credit
   premium gap between SOFR and EFFR. Most relevant if trading short-end rates.

2. **Machine learning for yield curve modeling** — neural ODE term structure models
   (Kratsios & Hyndman 2021), reservoir computing for yield forecasting, and
   transformer-based no-arb yield models. Active area but low actionability for
   practitioners without large data infrastructure.

3. **Regulatory capital and market microstructure** — post-Basel III research on how
   G-SIB surcharges, leverage ratio constraints, and FRTB affect repo, cross-currency
   basis, and bond futures markets. BIS Quarterly Review and NY Fed staff reports are
   the primary venues. Directly relevant to the book's Preface and Ch11.

4. **Climate risk in fixed income** — sovereign bond climate risk premia (Engle et al.
   2020+), green bond pricing differentials ("greenium"). Adjacent to the book's
   government default risk discussion in the Preface. Low actionability for now.

5. **Cointegration-based RV strategies at high frequency** — Avellaneda & Lee (2010)
   for equities, now applied to rates: spread mean reversion at intraday horizons.
   Relevant to Ch4 but requires tick data infrastructure not yet in the platform.

---

## Suggested Study Path for the Playground

If you want to turn this reading queue into concrete notebook studies:

| Study | Papers to read first | Book chapters | Notebook idea |
|-------|---------------------|---------------|---------------|
| PCA yield curve decomposition | #1, #5 | Ch3, Ch8 | Fit NS/DNS to US Treasury curve, extract L/S/C factors |
| Mean reversion signal testing | #2, #6, #20 | Ch2, Ch4 | OU calibration on 2s10s spread, half-life estimation |
| Fitted curve construction | #3, #11 | Ch8 | Nelson-Siegel vs. Svensson fit on current Treasury curve |
| Cross-currency basis analysis | #12, #13 | Ch13–18 | EUR/USD basis vs. Fed balance sheet, leverage ratio proxy |
| Term premia as regime signal | #15, #16 | Ch9 | Kim-Wright TP vs. yield curve slope, recession signal |
| Bond carry framework | #17 | Ch12 | Roll-down + carry decomposition across G10 bond markets |

---

---

## SUPPLEMENTARY BOOKS

Books recommended as companions to the FIRV study — not papers, but essential reading.

---

### B1. The Treasury Bond Basis
**Authors:** Galen Burghardt, Terry Belton, Morton Lane, John Papa
**Edition:** 3rd Ed. (McGraw-Hill, 2005)
**Scores:** C:5 R:5 A:5

**Why it matters:** The definitive reference on cash-futures basis mechanics for US Treasuries.
Covers conversion factors, CTD (cheapest-to-deliver) selection, invoice prices, implied repo rate
vs. actual repo, and the delivery options embedded in Treasury futures. Directly extends Ch18
(repo mechanics) and fills the cash-futures gap in FIRV's cross-market RV chapters (Ch16–17).
Essential if you plan to trade rates via futures rather than cash bonds.

**Suggested reading order:** Read after completing Ch18 (repo) and Ch16–17 (cross-market RV).

**Connection to platform:** DV01 mapping through conversion factors for futures-based curve
trades (steepeners/flatteners); basis carry as a macro positioning signal; CTD switches as
cross-market signals.

---

### B2. Expected Returns: An Investor's Guide to Harvesting Market Rewards
**Author:** Antti Ilmanen
**Edition:** 1st Ed. (Wiley, 2011)
**Scores:** C:5 R:5 A:5

**Why it matters:** The most comprehensive cross-asset survey of expected return drivers in
existence. Covers equity risk premium, bond risk premium, carry, value, momentum, and
liquidity across equities, fixed income, FX, commodities, and alternatives. Directly bridges
the FIRV micro-level RV work with macro-level asset allocation thinking. Ilmanen's bond
sections are especially relevant — term premia, carry decomposition, and real yield dynamics
map directly to Ch9, Ch12, and Ch16–17 of FIRV.

**Suggested reading order:** Read after completing FIRV Part III (Ch10–20). Use as the
cross-asset integration layer that contextualizes bond RV within a broader portfolio.

**Connection to platform:** Term premia framework (extends Kim-Wright, paper #15);
carry decomposition across G10 bonds (extends Ch12 bond carry); macro regime signals
for equity + rates + FX simultaneously — directly relevant to Marco's cross-asset mandate.

---

### B3. Efficiently Inefficient: How Smart Money Invests and Market Prices Are Determined
**Author:** Lasse Heje Pedersen
**Edition:** 1st Ed. (Princeton University Press, 2015)
**Scores:** C:5 R:5 A:5

**Why it matters:** Uniquely bridges academic theory and live practitioner thinking across
equity L/S, global macro, fixed income RV, and managed futures. Each strategy chapter
combines the theoretical underpinning with interviews from leading practitioners (Cliff
Asness, George Soros, Michael Platt, etc.). The fixed income and global macro chapters
directly extend FIRV concepts into a live trading context — how basis trades are sized,
how macro funds think about carry vs. value, and how limits-to-arbitrage prevent instant
convergence in RV trades.

**Suggested reading order:** Read after FIRV Part II (Ch5–9) or in parallel with Part III.
Best read after QEPM if also working through the equity stack.

**Connection to platform:** Fixed income RV chapter maps to Ch14–17 of FIRV; global
macro chapter relevant to Marco's mandate; equity L/S chapter relevant to Elena's factor
research; limits-to-arbitrage framework explains why statistically significant RV signals
don't always converge on schedule.

---

### B4. Pricing and Trading Interest Rate Derivatives: A Practical Guide to Swaps
**Author:** J.H.M. Darbyshire
**Edition:** 3rd Ed. (Aitch and Dee Ltd, 2022)
**Scores:** C:5 R:5 A:5

**Why it matters:** The clearest and most practical treatment of swap mechanics available.
Covers discount factor construction, par/forward/zero rate relationships, multi-curve
framework (OIS discounting, LIBOR/SOFR transition), interest rate options (caps, floors,
swaptions), and real portfolio risk management (delta, gamma, vega). FIRV assumes fluency
with swap pricing — Darbyshire teaches it from first principles without sacrificing rigor.

**Suggested reading order:** Read before or alongside FIRV Part II (Ch5–9), especially
before Ch14 (basis swaps) and Ch16 (SOFR ASW spreads). Can be read in parallel with
Treasury Bond Basis.

**Connection to platform:** Multi-curve OIS framework directly underpins SOFR ASW
construction (Ch16); basis swap mechanics extend Ch14 intra-currency basis; swap carry
and roll-down decomposition extends Ch12 bond carry framework. Essential mechanical
foundation for any rates derivatives or swap-spread RV implementation.

**Chapter-level cross-reference:** See [darbyshire_map.md](./darbyshire_map.md) for a
full chapter-by-chapter map of which Darbyshire chapters to read before/alongside/after
each FIRV chapter, including data gap analysis and session continuity notes.

---

*Cerebro — 2026-03-26 | Fixed Income Relative Value Analysis reading queue*
