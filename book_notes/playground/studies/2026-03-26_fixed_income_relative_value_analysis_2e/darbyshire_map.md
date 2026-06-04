# Darbyshire Map: Pricing and Trading Interest Rate Derivatives (3rd Ed., 2022)

*Created: 2026-03-28 | Cross-reference to FIRV (Huggins & Schaller, 2nd Ed.)*

---

## Role of This Book

Darbyshire is the **mechanical prerequisite** to FIRV. FIRV teaches where mispricings are;
Darbyshire teaches how the instruments price, how curves are built, and how risk is measured.
The two books are complementary by design — FIRV assumes the fluency Darbyshire instills.

**Reading posture:** Darbyshire Ch1–5 before FIRV. Ch6–13 in parallel with the FIRV chapter
they support. Ch20–24 after FIRV as an extension layer.

---

## Scoring

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Credibility | 5/5 | Standard practitioner reference; widely used by rates desks |
| Relevance | 5/5 | Every chapter maps directly into FIRV mechanical assumptions |
| Actionability | 5/5 | Swap pricing, curve bootstrapping, and delta decomposition are immediately implementable |

---

## Chapter Map

### Part A — Pre-Reading (Read Before FIRV Part I: Ch1–4)

---

#### Ch1 · Mathematical Review
**Pages:** 1–8
**FIRV connection:** FIRV Ch2 (OU/mean reversion), Ch3 (PCA)
**What it covers:**
- Stochastic calculus foundations: Brownian motion, Itô's lemma, SDEs
- Linear algebra: eigendecomposition, matrix inversion
- Probability: expectations, conditional distributions, change of measure

**Why read first:**
FIRV's OU model (Ch2) and PCA machinery (Ch3) use this math without deriving it.
Darbyshire derives it cleanly. Aligns with reading queue paper #2 (Vasicek 1977) which
uses the same SDE framework.

---

#### Ch2 · Interest Rates
**Pages:** 9–20
**FIRV connection:** FIRV Ch5 (carry/roll), Ch8 (fitted curves), Ch11 (swap spreads)
**What it covers:**
- Discount factors, zero rates, forward rates, par rates
- Day count conventions and compounding
- Yield-to-maturity and its limitations
- Par/forward/zero duality and conversion formulas

**Why read first:**
FIRV's carry decomposition (Ch5) and fitted-curve fair value (Ch8) both require fluency
with the par/forward/zero framework. This chapter makes those relationships mechanical
rather than assumed.

---

#### Ch3 · Basics of Interest Rate Derivatives
**Pages:** 21–42
**FIRV connection:** FIRV Ch11 (swap spreads), Ch14 (basis swaps), Ch16 (SOFR ASW)
**What it covers:**
- IRS mechanics: fixed vs floating, payment conventions, reset dates
- FRA pricing and convexity adjustments
- Futures vs forwards basis
- Swap DV01 and sensitivity basics

**Why read first:**
FIRV assumes swap mechanics from chapter 1. Darbyshire derives them from first principles.
Essential before FIRV Ch11 (swap spreads) and Ch14 (basis swaps).

---

#### Ch4 · Users of Interest Rate Derivatives
**Pages:** 43–52
**FIRV connection:** FIRV Ch1 (RV framework), Ch18–19 (trade lifecycle)
**What it covers:**
- End-user demand: asset managers, corporates, banks, insurers
- Hedging vs speculation vs RV positioning
- How structural demand creates persistent mispricings
- Regulatory constraints on dealer balance sheets

**Why read first:**
FIRV's RV framework (Ch1) relies on structural explanations for why mispricings persist.
Darbyshire Ch4 provides the market-structure context — who is on the other side and why.
Aligns with reading queue paper #B3 (Ivashina 2015: limits to arbitrage).

---

#### Ch5 · Cash, Collateral and Credit
**Pages:** 53–74
**FIRV connection:** FIRV Ch5 (carry decomposition), Ch12 (bond carry and roll)
**What it covers:**
- Repo mechanics: haircuts, specialness, GC vs specific
- OIS discounting rationale: collateral = risk-free funding
- Credit valuation adjustment (CVA) basics
- Funding valuation adjustment (FVA)

**Why read first:**
FIRV's carry decomposition (Ch5, Ch12) treats repo as a mechanical input. Darbyshire
explains why the funding rate matters and how collateral agreements affect pricing.
Critical for understanding specialness effects in Treasury RV.

---

### Part B — Parallel Reading (Read Alongside FIRV Part I–III)

---

#### Ch6 · Single Currency Curve Modelling
**Pages:** 75–88
**FIRV connection:** FIRV Ch8 (fitted curves), Ch9 (bond selection)
**What it covers:**
- Bootstrapping zero curves from market instruments
- Interpolation methods: linear, log-linear, cubic spline, monotone convex
- Smoothness vs fit trade-off
- Overnight index swap (OIS) curve construction

**Read alongside:** FIRV Ch8–9
**Why:** FIRV's fitted-curve fair value logic (Ch8) and bond-selection residuals (Ch9) depend
on a correctly bootstrapped curve. Darbyshire explains how that curve is built and where
interpolation choices create apparent mispricings that are artifacts, not signals.
Aligns with reading queue paper #3 (Diebold-Li 2006: Nelson-Siegel factor model).

---

#### Ch7 · Multi-Currency Curve Modelling
**Pages:** 89–102
**FIRV connection:** FIRV Ch15 (cross-currency basis), Ch17 (global RV)
**What it covers:**
- Multi-curve framework: OIS discounting + LIBOR/SOFR projection
- Why pre-2008 single-curve pricing broke down
- Cross-currency basis swap mechanics and curve construction
- FX forward points and covered interest parity deviations

**Read alongside:** FIRV Ch15
**Why:** FIRV's cross-currency RV chapter assumes multi-curve fluency. Darbyshire derives
why basis exists mechanically (balance sheet constraints, CIP deviations) and how
cross-currency curves are built. Directly extends reading queue paper #B4 (this book)
and aligns with KNOWLEDGE_FX.md carry/basis entries.

---

#### Ch8 · Term Structure of Interest Rate Curves
**Pages:** 103–114
**FIRV connection:** FIRV Ch3 (PCA), Ch9 (bond selection)
**What it covers:**
- Term premium decomposition
- Expectations hypothesis and its failures
- Factor structure of yield curves (level, slope, curvature)
- Empirical properties: mean reversion, volatility term structure

**Read alongside:** FIRV Ch3
**Why:** Bridges the statistical PCA factors in FIRV Ch3 (Litterman-Scheinkman) to the
economic term structure literature. Reading both gives the full picture: PCA as a
statistical fact AND as an economic model of expectations + risk premium.
Aligns with reading queue papers #1 (Litterman 1991) and #2 (Vasicek 1977).

---

#### Ch9 · Delta and Basis Risk
**Pages:** 115–136
**FIRV connection:** FIRV Ch6 (hedging RV trades), Ch11 (swap spreads), Ch14 (basis)
**What it covers:**
- DV01/PV01 by instrument and by tenor bucket
- Basis risk between hedging instrument and underlying
- Risk ladder construction
- Hedge ratio calculation under basis uncertainty

**Read alongside:** FIRV Ch6, Ch11
**Why:** FIRV's hedge construction for swap-spread and basis trades requires bucket-level
risk decomposition. Darbyshire explains how DV01 is allocated across the curve and
why naive hedges carry residual basis risk — directly relevant to FIRV Ch11 and Ch14.

---

#### Ch10 · Risk Models
**Pages:** 137–152
**FIRV connection:** FIRV Ch6 (hedge sizing), Ch13 (portfolio RV)
**What it covers:**
- Full PV01 risk model construction
- Risk aggregation across currencies and instruments
- Scenario analysis and stress testing
- Greeks hierarchy: delta → gamma → vega

**Read alongside:** FIRV Ch6, Ch13
**Why:** FIRV's portfolio RV chapter (Ch13) requires aggregating risk across positions.
Darbyshire provides the risk model architecture — how sensitivities are computed,
bucketed, and aggregated across a real rates book.

---

#### Ch11 · Quant Library and Automatic Differentiation
**Pages:** 153–174
**FIRV connection:** FIRV Ch6 (Greeks in hedge sizing)
**What it covers:**
- Algorithmic / automatic differentiation (AAD)
- Bump-and-reprice vs analytic Greeks
- Building a quant library for live risk computation
- Performance considerations for real-time Greeks

**Read alongside:** FIRV Ch6 (optional — implementation detail)
**Why:** Relevant when building live RV monitors that require fast Greeks. Not needed
for conceptual understanding of FIRV but important for any implementation that
calculates hedge ratios in real time.

---

#### Ch12 · Advanced Curve Building
**Pages:** 175–198
**FIRV connection:** FIRV Ch8 (fitted curves), Ch16 (SOFR ASW)
**What it covers:**
- Turn-of-year effects and jumps in short-end curves
- Simultaneous curve solving (OIS + LIBOR/SOFR joint calibration)
- Convexity adjustments for futures
- SOFR compounding conventions and fallback rates

**Read alongside:** FIRV Ch8, Ch16
**Why:** FIRV's SOFR ASW spread analysis (Ch16) requires understanding SOFR curve
construction details. Darbyshire covers the SOFR-specific conventions and calibration
challenges that create apparent dislocations in SOFR-linked instruments.
Aligns with reading queue paper #B2 (ARRC SOFR transition).

---

#### Ch13 · Multi-Currency Risk
**Pages:** 199–204
**FIRV connection:** FIRV Ch15 (cross-currency basis), Ch17 (global RV)
**What it covers:**
- Cross-currency delta and how to decompose it
- FX risk embedded in cross-currency swaps
- Funding basis translation across currencies
- Risk reporting for multi-currency books

**Read alongside:** FIRV Ch15, Ch17
**Why:** FIRV's global RV chapter requires understanding how risk is measured and
aggregated across currencies. Darbyshire provides the mechanical risk framework;
FIRV provides the alpha signal. Together they cover the full trade lifecycle.

---

#### Ch14 · Value at Risk
**Pages:** 205–224
**FIRV connection:** FIRV Ch13 (portfolio construction), Ch6 (position sizing)
**What it covers:**
- Historical simulation VaR for rates portfolios
- Parametric VaR and covariance matrix estimation
- Expected shortfall (CVaR)
- Limitations of VaR for tail risk in rates

**Read alongside:** FIRV Ch13 (optional — risk management complement)
**Why:** FIRV focuses on signal generation and hedge construction. Darbyshire's VaR
chapter adds the portfolio-level risk budget framework. Useful context but not a
direct mechanical dependency for FIRV implementation.

---

#### Ch15 · Principal Component Analysis
**Pages:** 225–238
**FIRV connection:** FIRV Ch3 (PCA as alpha signal)
**What it covers:**
- PCA applied to a swap portfolio's risk ladder
- Eigenvectors as hedging instruments
- Residual risk after factor hedging
- PCA-based risk compression for large books

**Read alongside:** FIRV Ch3
**Why:** FIRV uses PCA to generate alpha signals (yield curve residuals as mispricings).
Darbyshire uses PCA to manage risk (compress a swap book into factor hedges).
Reading both gives the full duality: PCA as signal AND as risk tool.
Aligns with reading queue paper #1 (Litterman & Scheinkman 1991).

---

#### Ch16 · Customised Risk Management
**Pages:** 239–258
**FIRV connection:** FIRV Ch6 (hedging), Ch18 (trade construction)
**What it covers:**
- Key rate durations and custom risk buckets
- Jacobian transformations between risk representations
- Constructing hedge portfolios with constraints
- Risk decomposition for exotic structures

**Read alongside:** FIRV Ch6, Ch18
**Why:** FIRV's butterfly and box trade construction requires mapping positions into
custom risk buckets. Darbyshire's Jacobian framework explains how to translate between
standard DV01 and bespoke risk representations — essential for multi-leg RV trades.

---

#### Ch17 · Regulatory Capital, Leverage, and Liquidity
**Pages:** 259–282
**FIRV connection:** FIRV Ch4 (users), Ch19 (trade unwinding)
**What it covers:**
- Basel III/IV: SA-CCR, FRTB, leverage ratio
- How regulatory constraints reshape dealer risk appetite
- Liquidity coverage ratio effects on repo and funding
- Implications for swap spreads and basis persistence

**Read alongside:** FIRV Ch4, Ch19 (background context)
**Why:** FIRV argues that regulatory constraints explain persistent swap-spread and
basis dislocations. Darbyshire quantifies how those constraints actually bind —
giving the economic mechanism behind FIRV's structural alpha argument.
Aligns with reading queue paper #4 (Darbyshire Ch4 → users).

---

#### Ch18 · Market-Making and Price-Taking
**Pages:** 283–292
**FIRV connection:** FIRV Ch18–19 (trade entry, exit, and lifecycle)
**What it covers:**
- Bid-offer spread construction for swaps
- Inventory management and hedging costs
- Price-taking execution strategies
- Market impact and information asymmetry

**Read alongside:** FIRV Ch18–19
**Why:** FIRV treats transaction costs and market impact as inputs to trade sizing.
Darbyshire explains how those costs are constructed by the dealer — giving the
mechanical foundation for FIRV's execution cost assumptions.

---

#### Ch19 · Electronic Trading
**Pages:** 293–316
**FIRV connection:** FIRV Ch19 (trade execution and unwinding)
**What it covers:**
- Electronic trading venues for rates (SEF, D2D, D2C)
- Algo execution for swaps and bonds
- Liquidity fragmentation and best execution
- Real-time risk management in electronic markets

**Read alongside:** FIRV Ch19 (optional — execution detail)
**Why:** Relevant for live implementation of RV strategies. Not a mechanical
prerequisite for FIRV understanding but important context for execution quality.

---

### Part C — Post-Reading (Extensions Beyond FIRV Scope)

---

#### Ch20 · Swaptions and Volatility
**Pages:** 317–340
**FIRV connection:** Not in FIRV — fills a gap
**What it covers:**
- Swaption mechanics: payer vs receiver, physical vs cash settlement
- Black's model and SABR vol surface construction
- Vol surface interpolation and smile dynamics
- Gamma and vega risk for swaption books

**Read after:** FIRV completion
**Why:** FIRV covers linear RV (bonds, swaps, basis). Swaptions introduce optionality,
convexity, and vol-adjusted carry. Essential for any rates strategy that involves
caps, floors, or vol-adjusted duration. Also needed before Ch21–22.
Aligns with reading queue paper on rates VRP.

---

#### Ch21 · Gamma and Cross-Gamma Risk
**Pages:** 341–358
**FIRV connection:** Not in FIRV — natural extension
**What it covers:**
- Second-order rate risk: gamma (same instrument) and cross-gamma (across instruments)
- How convexity creates P&L in trending markets
- Cross-gamma between rates and FX in cross-currency books
- Managing gamma in a multi-asset rates book

**Read after:** FIRV + Ch20
**Why:** Once FIRV's linear RV framework is mastered, gamma risk is the next layer.
Cross-gamma matters when running multi-currency RV with FX overlay.

---

#### Ch22 · Analytic Cross-Gamma
**Pages:** 359–386
**FIRV connection:** Not in FIRV — quantitative extension
**What it covers:**
- Closed-form cross-gamma expressions for standard swap structures
- How analytic Greeks reduce model dependency
- Practical applications in risk systems

**Read after:** Ch21
**Why:** Technical extension of Ch21. Relevant for building a robust risk engine
that computes cross-gamma analytically rather than by bumping.

---

#### Ch23 · Constructing Trade Strategies
**Pages:** 387–408
**FIRV connection:** FIRV Ch18–19 (trade construction from alpha signal perspective)
**What it covers:**
- Trade construction from a *pricing* perspective: carry, roll, breakeven
- Entry/exit criteria based on instrument mechanics
- Hedging residual risks in a multi-leg trade
- Trade documentation and lifecycle management

**Read after:** FIRV
**Why:** FIRV constructs trades from a statistical signal perspective (z-score entry,
cointegration hedge ratios). Darbyshire constructs trades from a pricing perspective
(carry + roll breakeven, Greeks-based hedging). Reading both gives the full
strategy lifecycle from signal to execution to risk management.

---

#### Ch24 · Reset Risk
**Pages:** 409–420
**FIRV connection:** Not in FIRV — SOFR extension
**What it covers:**
- Reset risk in floating-rate instruments at fixing dates
- SOFR compounding in arrears: late-fixing uncertainty
- Hedging reset risk with futures or short-dated swaps
- Implications for ASW spreads near fixing dates

**Read after:** FIRV Ch16 (SOFR ASW)
**Why:** FIRV's SOFR ASW chapter does not cover reset risk. As SOFR-linked instruments
become standard, reset risk at compounding periods creates short-lived mispricings
that are mechanically predictable — a natural extension of FIRV's RV framework.
Aligns with reading queue paper #B2 (ARRC SOFR transition).

---

## Quick Reference: FIRV Chapter → Read Darbyshire First

| FIRV Chapter | Topic | Darbyshire Prerequisite |
|-------------|-------|--------------------------|
| Ch2 | Ornstein-Uhlenbeck / mean reversion | Ch1 (math), Ch2 (rates) |
| Ch3 | PCA factor decomposition | Ch8 (term structure), Ch15 (PCA risk) |
| Ch5 | Carry and roll decomposition | Ch2 (rates), Ch5 (collateral/repo) |
| Ch6 | Hedging RV trades | Ch9 (delta/basis), Ch10 (risk models) |
| Ch8 | Fitted curves and fair value | Ch6 (curve building), Ch12 (advanced curves) |
| Ch9 | Bond selection via residuals | Ch6 (curve building), Ch8 (term structure) |
| Ch11 | Swap spreads | Ch3 (swap mechanics), Ch9 (delta/basis) |
| Ch12 | Bond carry and roll | Ch2 (rates), Ch5 (repo/collateral) |
| Ch13 | Portfolio RV | Ch10 (risk models), Ch16 (customised risk) |
| Ch14 | Intra-currency basis | Ch3 (swap mechanics), Ch7 (multi-currency) |
| Ch15 | Cross-currency basis | Ch7 (multi-currency), Ch13 (FX risk) |
| Ch16 | SOFR ASW spreads | Ch12 (advanced curves), Ch24 (reset risk) |
| Ch17 | Global RV | Ch7 (multi-currency), Ch13 (FX risk), Ch17 (regulation) |
| Ch18–19 | Trade construction and execution | Ch23 (trade strategies), Ch18–19 (market structure) |

---

## Data Gaps: What Darbyshire Needs That We Don't Have

Same gaps as FIRV, slightly extended:

| Data | Status | Needed For |
|------|--------|------------|
| Swap curve tenors (OIS, SOFR) | Missing | Ch6, Ch7, Ch12 |
| Swaption vol surface | Missing | Ch20 |
| Repo specialness rates | Missing | Ch5 |
| CDS curves | Missing | Ch5 (CVA) |
| FX forward points | Missing | Ch7, Ch13 |
| Cross-currency basis quotes | Missing | Ch7, Ch15 |

---

## Session Continuity Notes

- Update this file before starting any new Darbyshire chapter session.
- Always note which FIRV chapter you are reading in parallel.
- When Darbyshire reveals a mechanical detail that changes how a FIRV signal should
  be constructed, log it in FINDINGS_LOG.md with tag `[DARBYSHIRE]`.
- Swaptions (Ch20–22) open a separate research thread — flag Cerebro when starting
  to surface vol-adjusted carry and rates VRP literature.

---

*Darbyshire map — 2026-03-28 | Paired study: FIRV (Huggins & Schaller, 2nd Ed.)*


