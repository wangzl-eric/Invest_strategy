# Reading Queue — Global Macro Trading (Gliner)

**Date:** 2026-03-27
**Anchor:** *Global Macro Trading: Profiting in a New World Economy* — Greg Gliner (Wiley, 2014)
**Scope:** Up to 15 papers, all scoring ≥ 4 on every dimension. Books excluded.

---

## Summary Table

| # | Paper | Domain | C | R | A |
|---|-------|--------|---|---|---|
| 1 | "Carry" — Koijen, Moskowitz, Pedersen, Vrugt (2018) | Cross-Asset Factors | 5 | 5 | 5 |
| 2 | "Value and Momentum Everywhere" — Asness et al. (2013) | Cross-Asset Factors | 5 | 5 | 5 |
| 3 | "Trend-Following with Managed Futures" — Hurst, Ooi, Pedersen (2013) | Cross-Asset Factors | 5 | 5 | 5 |
| 4 | "Facts and Fantasies about Commodity Futures" — Gorton & Rouwenhorst (2006) | Commodity Macro | 5 | 5 | 5 |
| 5 | "Commodity Risk Premiums" — Bhardwaj, Gorton, Rouwenhorst (2015) | Commodity Macro | 5 | 5 | 5 |
| 6 | "A Century of Commodity Returns" — Levine et al. (2018) | Commodity Macro | 5 | 5 | 5 |
| 7 | "Currency Value" — Asness, Moskowitz, Pedersen (2013) | FX Regime | 5 | 5 | 5 |
| 8 | "A Century of Global Factor Premiums" — Baltussen et al. (2021) | Cross-Asset Factors | 5 | 4 | 5 |
| 9 | "The Trilemma in History" — Obstfeld, Shambaugh, Taylor (2005) | Central Bank / FX | 5 | 5 | 4 |
| 10 | "Banking, Trade, and a Dominant Currency" — Gopinath & Stein (2021) | FX Regime | 5 | 5 | 4 |
| 11 | "Hedge Fund Benchmarks: A Risk-Based Approach" — Fung & Hsieh (2004) | Global Macro Strategy | 5 | 5 | 4 |
| 12 | "Risk Parity Is about Balance" — Bridgewater (2012) | Risk Parity | 4 | 5 | 5 |
| 13 | "Measuring Monetary Policy" — Wu & Xia (2016) | Central Bank Policy | 5 | 4 | 4 |
| 14 | "The Effects of QE on Financial Conditions" — Bernanke (2020) | Central Bank Policy | 5 | 4 | 4 |
| 15 | "Two Centuries of Multi-Asset Momentum" — Geczy & Samonov (2017) | Cross-Asset Factors | 4 | 4 | 4 |

---

## Domain Sections

### Cross-Asset Factors

**1. "Carry" — Koijen, Moskowitz, Pedersen, Vrugt (2018)**
Unifies the carry premium across equities, bonds, FX, and commodities under one framework. The single paper that systematizes the most important signal in Gliner's book. Implementable with FRED and price data.
DOI: 10.1016/j.jfineco.2018.04.002
`C:5 / R:5 / A:5`

**2. "Value and Momentum Everywhere" — Asness, Moskowitz, Pedersen (2013)**
Shows value and momentum premia exist in 8 asset classes simultaneously and are negatively correlated — the systematic basis for Gliner's multi-asset discretionary trades.
DOI: 10.1111/jofi.12021
`C:5 / R:5 / A:5`

**3. "Trend-Following with Managed Futures" — Hurst, Ooi, Pedersen (2013)**
Empirical evidence for time-series momentum across 67 instruments over 135 years. Explicit signal construction methodology directly replicable with futures data.
SSRN: 2324288
`C:5 / R:5 / A:5`

**8. "A Century of Global Factor Premiums" — Baltussen et al. (2021)**
100+ year evidence for trend, value, carry, and seasonality across asset classes. Stress-tests factor robustness across multiple macro regimes and provides deep out-of-sample validation.
DOI: 10.1093/rfs/hhab019
`C:5 / R:4 / A:5`

**15. "Two Centuries of Multi-Asset Momentum" — Geczy & Samonov (2017)**
Extends time-series and cross-sectional momentum evidence to 1800–2012 across equities, bonds, currencies, and commodities. Confirms momentum is not a data-mining artifact.
DOI: 10.2469/faj.v73.n3.3
`C:4 / R:4 / A:4`

---

### Commodity Macro

**4. "Facts and Fantasies about Commodity Futures" — Gorton & Rouwenhorst (2006)**
Establishes roll yield / term structure as the primary commodity futures return driver. The contango/backwardation signal Gliner covers qualitatively (Ch10) becomes a rigorous quantitative strategy.
DOI: 10.2469/faj.v62.n2.4083
`C:5 / R:5 / A:5`

**5. "Commodity Risk Premiums" — Bhardwaj, Gorton, Rouwenhorst (2015)**
Updates the 2006 paper through 2013, decomposing returns into spot, roll yield, and collateral components. Adds contract selection details and confirms roll yield dominance persists.
SSRN: 2344848
`C:5 / R:5 / A:5`

**6. "A Century of Commodity Returns" — Levine et al. (2018)**
Trend, carry, value, and seasonality signals across 230+ commodity markets over 100+ years. The most comprehensive cross-sectional commodity factor study available.
SSRN: 2690232
`C:5 / R:5 / A:5`

---

### FX Regime & Valuation

**7. "Currency Value" — Asness, Moskowitz, Pedersen (2013)**
Builds a systematic PPP/REER-based FX valuation signal testable across developed and emerging currencies. The quantitative implementation of Gliner's Ch7 valuation framework.
DOI: 10.1111/jofi.12021
`C:5 / R:5 / A:5`

**10. "Banking, Trade, and the Making of a Dominant Currency" — Gopinath & Stein (2021)**
Explains structurally why the USD holds its dominant reserve and invoicing role. Essential context for why DXY dynamics differ from bilateral pairs — directly relevant to Gliner Ch7.
DOI: 10.1093/qje/qjab002
`C:5 / R:5 / A:4`

---

### Central Bank Policy

**9. "The Trilemma in History" — Obstfeld, Shambaugh, Taylor (2005)**
Empirically validates the impossible trinity across 130+ years and 21 countries. Foundational for understanding how central bank regime choice constrains FX and rates (Gliner Ch11).
DOI: 10.1162/0034653054638340
`C:5 / R:5 / A:4`

**13. "Measuring the Macroeconomic Impact of Monetary Policy at the Zero Lower Bound" — Wu & Xia (2016)**
Constructs a shadow federal funds rate extending conventional rate analysis through the ZLB period. Directly actionable: shadow rate series is publicly downloadable and usable as a regime variable.
DOI: 10.1162/REST_a_00549
`C:5 / R:4 / A:4`

**14. "The Effects of Quantitative Easing on Financial Conditions" — Bernanke (2020)**
Systematic review of QE transmission channels (portfolio balance, signaling, liquidity). Maps directly to Gliner Ch11 on non-standard monetary policy tools.
Brookings Papers on Economic Activity, Spring 2020.
`C:5 / R:4 / A:4`

---

### Global Macro Strategy

**11. "Hedge Fund Benchmarks: A Risk-Based Approach" — Fung & Hsieh (2004)**
Decomposes hedge fund and global macro returns into systematic risk factors (trend, carry, equity, bond). Shows macro returns are largely explained by a small set of replicable premia.
DOI: 10.2469/faj.v60.n5.2657
`C:5 / R:5 / A:4`

---

### Risk Parity

**12. "Risk Parity Is about Balance" — Bridgewater Associates (2012)**
Original practitioner exposition of risk parity from its inventors. Explains the all-weather portfolio construction philosophy underlying Gliner's Ch6 systematic framework. Concrete enough to implement directly.
https://www.bridgewater.com/research-and-insights/risk-parity-is-about-balance
`C:4 / R:5 / A:5`

---

## Recommended Reading Order

**Start with the core signals (read alongside Gliner Ch4–6):**
1. "Carry" (Koijen et al.) — the central multi-asset signal
2. "Value and Momentum Everywhere" (Asness et al.) — cross-asset factor foundation
3. "Trend-Following with Managed Futures" (Hurst et al.) — systematic trend methodology

**Domain depth (read alongside Gliner Ch7–10):**
4. "Facts and Fantasies about Commodity Futures" (Gorton & Rouwenhorst)
5. "Currency Value" (Asness et al.)
6. "The Trilemma in History" (Obstfeld et al.)
7. "Risk Parity Is about Balance" (Bridgewater)

**Longer-run evidence:**
8. "A Century of Global Factor Premiums" (Baltussen et al.)
9. "A Century of Commodity Returns" (Levine et al.)
10. "Two Centuries of Multi-Asset Momentum" (Geczy & Samonov)

**Supplementary:**
11. Fung & Hsieh (2004) — macro return decomposition
12. Bhardwaj et al. (2015) — commodity roll yield update
13. Gopinath & Stein (2021) — USD dominance
14. Wu & Xia (2016) — shadow rate
15. Bernanke (2020) — QE transmission

---

*Compiled 2026-03-28 | Anchor: Gliner, Greg. Global Macro Trading. Wiley, 2014.*