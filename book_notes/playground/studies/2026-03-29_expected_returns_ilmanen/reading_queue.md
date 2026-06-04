# Reading Queue: Adjacent Papers to Expected Returns (Ilmanen 2011)

_Built: 2026-03-29_
_Scope: equity risk premium, bond risk premium, carry, momentum, value, volatility risk premium, behavioral finance_
_Scoring: Credibility (1–5) | Relevance (1–5) | Actionability (1–5). Only papers ≥ 3 on all three included._

---

## Tier 1 — Must-Read (All scores ≥ 4)

### 1. Value and Momentum Everywhere
**Authors:** Asness, Moskowitz, Pedersen
**Year:** 2013 | **Journal:** Journal of Finance
**Domains:** Equity, FX, Macro, Multi-asset
**Scores:** Credibility 5 | Relevance 5 | Actionability 5
**Key Insight:** Value and momentum premia exist across eight diverse asset classes. Their co-movement within and across asset classes suggests a common factor, likely related to liquidity risk and investor sentiment cycles.
**Ilmanen Connection:** Ch12 (value) + Ch13 (carry) + Ch14 (momentum) — the multi-asset synthesis of all three chapters.
**Priority:** Read first — provides unified framework for ~40% of the book.

---

### 2. Time Series Momentum
**Authors:** Moskowitz, Ooi, Pedersen
**Year:** 2012 | **Journal:** Journal of Financial Economics
**Domains:** Equity, FX, Macro, Multi-asset
**Scores:** Credibility 5 | Relevance 5 | Actionability 5
**Key Insight:** Past 12-month returns positively predict next-month returns across 58 futures markets. TSMOM explains much of CTA/trend-following returns and provides strong crisis-alpha properties.
**Ilmanen Connection:** Ch14 (momentum) + Ch18 (tail risk / crisis alpha).
**Priority:** High — directly implementable with futures data.

---

### 3. Returns to Buying Winners and Selling Losers
**Authors:** Jegadeesh, Titman
**Year:** 1993 | **Journal:** Journal of Finance
**Domain:** Equity
**Scores:** Credibility 5 | Relevance 5 | Actionability 5
**Key Insight:** Stocks with best (worst) returns over past 3–12 months continue to outperform (underperform) over the next 3–12 months. The foundational cross-sectional momentum paper.
**Ilmanen Connection:** Ch14 (momentum) — this is the paper Ilmanen builds from.
**Priority:** High — essential baseline before reading any extensions.

### 4. Bond Risk Premia
**Authors:** Cochrane, Piazzesi
**Year:** 2005 | **Journal:** American Economic Review
**Domain:** Macro (Rates)
**Scores:** Credibility 5 | Relevance 5 | Actionability 4
**Key Insight:** A single tent-shaped linear combination of forward rates predicts excess returns on 2–5 year bonds with R² up to 44%. The CP factor captures time-varying term premia missed by yield-curve level/slope alone.
**Ilmanen Connection:** Ch9 (bond risk premium) — quantitative BRP forecasting signal beyond simple yield curve slope.
**Priority:** High — provides implementable BRP timing signal.

---

### 5. Variance Risk Premiums
**Authors:** Carr, Wu
**Year:** 2009 | **Journal:** Review of Financial Studies
**Domain:** Volatility
**Scores:** Credibility 5 | Relevance 5 | Actionability 4
**Key Insight:** Model-free implied variance consistently exceeds realized variance — the VRP is economically large (~15 vol points annualized), persistent, and negatively skewed. VRP is compensation for variance/jump risk, not forecasting skill.
**Ilmanen Connection:** Ch15 (volatility selling / VRP) — foundational VRP measurement paper.
**Priority:** High — directly relevant to our volatility premium research (see rejected VIX Regime strategy).

---

### 6. Carry (Universal Carry Factor)
**Authors:** Koijen, Moskowitz, Pedersen, Vrugt
**Year:** 2018 | **Journal:** Journal of Financial Economics
**Domain:** FX, Equity, Macro, Multi-asset
**Scores:** Credibility 5 | Relevance 5 | Actionability 5
**Key Insight:** Carry — return assuming prices stay flat — predicts returns across all major asset classes. A universal carry factor spans equities, bonds, FX, and commodities; partly explained by funding liquidity and crash risk.
**Ilmanen Connection:** Ch13 (carry strategies across assets) — the modern academic synthesis of that chapter.
**Note:** Already in GMT reading queue. Review after GMT study completes.
**Priority:** High — cross-study reference.

---

### 7. Momentum Crashes
**Authors:** Daniel, Moskowitz
**Year:** 2016 | **Journal:** Journal of Financial Economics
**Domain:** Equity
**Scores:** Credibility 5 | Relevance 5 | Actionability 4
**Key Insight:** Momentum strategies suffer infrequent but severe crashes (avg –91% in 2 months) coinciding with market rebounds from panic states. Dynamic scaling by predicted volatility nearly doubles Sharpe ratio.
**Ilmanen Connection:** Ch14 (momentum) + Ch18 (tail risk) — explains why our Vol-Scaled Momentum strategy failed and how to design it properly.
**Priority:** High — directly relevant to team's rejected strategies.

---

### 8. Common Risk Factors in the Returns on Stocks and Bonds
**Authors:** Fama, French
**Year:** 1993 | **Journal:** Journal of Financial Economics
**Domain:** Equity
**Scores:** Credibility 5 | Relevance 5 | Actionability 4
**Key Insight:** Three-factor model (market, SMB, HML) explains the cross-section of stock returns. Value and size are systematic risk factors demanding compensation. Baseline model for all subsequent factor work.
**Ilmanen Connection:** Ch5 (rational theories) + Ch12 (value) + Ch16 (growth/other equity factors).
**Priority:** High — essential reference for multi-factor framework.

---

## Tier 2 — Important (Mix of 4s and 3s)

### 9. Betting Against Beta
**Authors:** Frazzini, Pedersen
**Year:** 2014 | **Journal:** Journal of Financial Economics
**Domain:** Equity
**Scores:** Credibility 5 | Relevance 4 | Actionability 4
**Key Insight:** Low-beta assets deliver higher risk-adjusted returns than high-beta assets. Leverage-constrained investors bid up high-beta assets, creating a persistent low-beta premium. BAB factor earns ~0.70 Sharpe across asset classes.
**Ilmanen Connection:** Ch5 (rational theories) + Ch16 (equity factors) — explains the low-vol anomaly via a funding friction mechanism.
**Priority:** Medium-High — relevant to Quality + Safe-Haven overlay (active strategy).

---

### 10. Disagreement and the Stock Market
**Authors:** Hong, Stein
**Year:** 2007 | **Journal:** Journal of Economic Perspectives
**Domain:** Equity (Behavioral)
**Scores:** Credibility 4 | Relevance 4 | Actionability 3
**Key Insight:** Short-sale constraints prevent bearish investors from trading, so prices reflect only optimistic views. When constraints bind, overpricing follows. Unified framework for momentum (gradual information diffusion) and overreaction (crashes).
**Ilmanen Connection:** Ch6 (behavioral finance) + Ch14 (momentum) — provides behavioral micro-foundation for why momentum exists and crashes.
**Priority:** Medium — important for understanding momentum's behavioral driver.

---

### 11. The Cross-Section of Volatility and Expected Returns
**Authors:** Ang, Hodrick, Xing, Zhang
**Year:** 2006 | **Journal:** Journal of Finance
**Domain:** Equity, Volatility
**Scores:** Credibility 5 | Relevance 4 | Actionability 4
**Key Insight:** Stocks with high sensitivity to innovations in aggregate volatility (VIX) earn low average returns — they are expensive hedges. Idiosyncratic volatility is also negatively priced cross-sectionally, a puzzle vs. standard models.
**Ilmanen Connection:** Ch15 (VRP) + Ch16 (equity factors) — links volatility risk to equity cross-section.
**Priority:** Medium-High — directly relevant to VRP and equity factor strategies.

---

### 12. The Equity Premium: A Puzzle
**Authors:** Mehra, Prescott
**Year:** 1985 | **Journal:** Journal of Monetary Economics
**Domain:** Equity (Macro)
**Scores:** Credibility 5 | Relevance 4 | Actionability 3
**Key Insight:** The observed equity risk premium (~6%) is far too large to be explained by standard consumption-based asset pricing with reasonable risk aversion. This "puzzle" spawned 40 years of ERP theory and motivates behavioral/habit/disaster-risk explanations.
**Ilmanen Connection:** Ch5 (rational theories) + Ch7 (equity risk premium) — the conceptual anchor for the entire ERP debate Ilmanen surveys.
**Priority:** Medium — essential theoretical grounding, low direct actionability.

---

### 13. Shiller P/E and Long-Run Equity Returns
**Authors:** Campbell, Shiller
**Year:** 1988 | **Journal:** Journal of Finance
**Domain:** Equity
**Scores:** Credibility 5 | Relevance 4 | Actionability 4
**Key Insight:** The cyclically adjusted price-earnings ratio (CAPE/Shiller P/E) strongly predicts long-horizon (10-year) stock returns. High CAPE → low subsequent returns, low CAPE → high returns. The primary forward-looking ERP signal.
**Ilmanen Connection:** Ch7 (equity risk premium — forward-looking ERP measures, tactical forecasting) — Ilmanen uses CAPE as the central ERP predictor.
**Priority:** Medium-High — directly implements a tactical ERP signal.

---

### 14. Fact, Fiction and Momentum Investing
**Authors:** Asness, Frazzini, Israel, Moskowitz
**Year:** 2014 | **Journal:** Journal of Portfolio Management
**Domain:** Equity
**Scores:** Credibility 5 | Relevance 4 | Actionability 4
**Key Insight:** Debunks nine common critiques of momentum: it survives transaction costs at scale, is not explained by risk, persists internationally, and remains robust to varying look-back windows. Practitioner-oriented implementation guide.
**Ilmanen Connection:** Ch14 (momentum) + Ch17 (combining strategies) — answers the "does it survive in practice?" question Ilmanen raises but doesn't fully resolve.
**Priority:** Medium — critical for implementation confidence before building momentum strategies.

---

### 15. Volatility Risk Premia and the Cross-Section of Stock Returns
**Authors:** Cremers, Halling, Weinbaum
**Year:** 2015 | **Journal:** Journal of Finance
**Domain:** Volatility, Equity
**Scores:** Credibility 4 | Relevance 4 | Actionability 4
**Key Insight:** Individual stock VRP (implied minus realized vol) predicts cross-sectional returns — stocks with large negative VRP (expensive puts) earn lower future returns. VRP is a priced factor in the equity cross-section, not just an index-level phenomenon.
**Ilmanen Connection:** Ch15 (VRP) + Ch12 (value equity selection) — extends index-level VRP analysis to the equity cross-section, opening stock-selection applications.
**Priority:** Medium — extends VRP concept to equity factor context.

---

## Summary Table

| # | Paper | Authors | Year | Cred | Rel | Act | Domain | Ilmanen Chapter |
|---|-------|---------|------|------|-----|-----|--------|-----------------|
| 1 | Value and Momentum Everywhere | Asness et al. | 2013 | 5 | 5 | 5 | Multi-asset | Ch12,13,14 |
| 2 | Time Series Momentum | Moskowitz et al. | 2012 | 5 | 5 | 5 | Multi-asset | Ch14,18 |
| 3 | Returns to Buying Winners and Selling Losers | Jegadeesh, Titman | 1993 | 5 | 5 | 5 | Equity | Ch14 |
| 4 | Bond Risk Premia | Cochrane, Piazzesi | 2005 | 5 | 5 | 4 | Rates | Ch9 |
| 5 | Variance Risk Premiums | Carr, Wu | 2009 | 5 | 5 | 4 | Vol | Ch15 |
| 6 | Carry (Universal) | Koijen et al. | 2018 | 5 | 5 | 5 | Multi-asset | Ch13 |
| 7 | Momentum Crashes | Daniel, Moskowitz | 2016 | 5 | 5 | 4 | Equity | Ch14,18 |
| 8 | Common Risk Factors | Fama, French | 1993 | 5 | 5 | 4 | Equity | Ch5,12,16 |
| 9 | Betting Against Beta | Frazzini, Pedersen | 2014 | 5 | 4 | 4 | Equity | Ch5,16 |
| 10 | Disagreement and the Stock Market | Hong, Stein | 2007 | 4 | 4 | 3 | Behavioral | Ch6,14 |
| 11 | Cross-Section of Volatility | Ang et al. | 2006 | 5 | 4 | 4 | Equity/Vol | Ch15,16 |
| 12 | Equity Premium: A Puzzle | Mehra, Prescott | 1985 | 5 | 4 | 3 | Macro/Equity | Ch5,7 |
| 13 | Shiller P/E and Long-Run Returns | Campbell, Shiller | 1988 | 5 | 4 | 4 | Equity | Ch7 |
| 14 | Fact, Fiction and Momentum | Asness et al. | 2014 | 5 | 4 | 4 | Equity | Ch14,17 |
| 15 | VRP and Cross-Section of Stocks | Cremers et al. | 2015 | 4 | 4 | 4 | Vol/Equity | Ch15,12 |

---

## Suggested Reading Order

1. **Papers 3, 8** — Foundational (Jegadeesh-Titman, Fama-French): establish baseline cross-section facts
2. **Paper 12** — Conceptual anchor (Mehra-Prescott ERP puzzle): frames why premia exist
3. **Papers 1, 2** — Unified multi-asset framework (Asness VME + TSMOM): bridges Ilmanen's chapters
4. **Papers 4, 13** — Bond and equity forward-looking signals (CP factor, CAPE): tactical forecasting tools
5. **Papers 5, 11** — Volatility risk premium papers: framework + equity cross-section
6. **Paper 6** — Universal carry (already in GMT queue): revisit after GMT study
7. **Papers 7, 14** — Momentum implementation (crashes + practitioner guide): before any momentum build
8. **Papers 9, 10, 15** — Factor extensions (BAB, behavioral micro-foundation, VRP cross-section)

---

_Next action: Use `/market-intelligence-synthesizer` on Tier 1 papers as they are read to route findings to domain KBs._



