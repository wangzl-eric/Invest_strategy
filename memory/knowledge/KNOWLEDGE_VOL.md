# Knowledge Base: Volatility
_Last updated: 2026-03-19_
_Entry tags: [AUTO] auto-extracted | [PLAYGROUND] from notebook | [BOOK/ARTICLE] from reading | [PM-VERDICT] from strategy review_
_All entries validated by kb-curator agent before write._

---

## Topic: vrp

### Market Facts & Structural Observations
- Implied volatility (VIX) systematically exceeds realized volatility — the volatility risk premium (VRP) is empirically robust | [AUTO: LESSONS_LEARNED.md] | 2026-03-15
- VRP reflects compensation for variance risk, not a pure alpha signal; it is a crisis insurance premium | [AUTO: LESSONS_LEARNED.md] | 2026-03-15
- VRP is highest in crisis regimes — precisely when it is most dangerous to be short vol | [AUTO: LESSONS_LEARNED.md] | 2026-03-15

### Intermediate Findings
- (none — VRP as standalone strategy rejected; crisis monitoring use-case possible)

### Confirmed Signals
- (none — VRP is crisis signal, not alpha signal)

### Known Failure Modes
- VRP strategy: spanning alpha t=-0.18 after controlling for market beta and momentum — no incremental alpha | REJECTED Round 2 | [PM-VERDICT: vix_regime_2026-03-15 REJECTED] | 2026-03-15
- Predictive signal content (Q5 t=9.45) does NOT guarantee tradeable alpha; beta reduction != alpha generation | [AUTO: LESSONS_LEARNED.md] | 2026-03-15
- VRP is crisis signal not alpha signal: useful for risk monitoring dashboard (alert triggers), not standalone strategy | [AUTO: LESSONS_LEARNED.md] | 2026-03-15
- MinBTL = 3,968 years for VIX Regime strategy — statistically indistinguishable from chance | [PM-VERDICT: vix_regime_2026-03-15 REJECTED] | 2026-03-15

### Key Papers & Concepts
- "The Price of Variance Risk" | Carr & Wu | 2009 | relevance: 88/100 | VRP measurement; variance swap returns | cited
- "Variance Risk Premiums" | Bollerslev, Tauchen, Zhou | 2009 | relevance: 85/100 | VRP as predictor of equity returns | cited

---

## Topic: vix-regime

### Market Facts & Structural Observations
- VIX is the most widely used regime indicator; low VIX (<15) = risk-on, high VIX (>25) = risk-off | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13
- VIX regimes are correlated with momentum strategy returns — momentum works better in low-vol regimes | [AUTO: LESSONS_LEARNED.md] | 2026-03-15
- VIX term structure (VIX3M/VIX ratio) provides additional regime information beyond spot VIX level | [AUTO: external_ideas.md] | 2026-03-15
- VIX data available locally: data/market_data/prices/vix_daily.parquet and vix3m_daily.parquet | [AUTO: git status untracked files] | 2026-03-19

### Intermediate Findings
- VIX regime as overlay on other strategies (not standalone): may improve risk-adjusted returns without requiring standalone alpha | confidence: low | follow-up: test as filter on Quality strategy | [AUTO: LESSONS_LEARNED.md] | 2026-03-15

### Confirmed Signals
- (none — VIX regime as standalone rejected; use as filter TBD)

### Known Failure Modes
- VIX Regime strategy REJECTED after 2 rounds: MinBTL 3,968yr, spanning alpha t=-0.18, dominated by simple trailing vol | [PM-VERDICT: vix_regime_2026-03-15 REJECTED] | 2026-03-15
- Position-sizing overlays have structural headwind in secular bull markets: VIX overlay destroyed Sharpe from 0.503 to 0.206 (-59%) | [PM-VERDICT: vix_regime_2026-03-15 REJECTED] | 2026-03-15
- Overlay must ADD alpha (require +0.15 Sharpe improvement minimum), not just reduce risk | [AUTO: LESSONS_LEARNED.md] | 2026-03-15
- Always compare regime signal vs trailing vol baseline — VRP lost to trailing vol on ALL metrics | [AUTO: LESSONS_LEARNED.md] | 2026-03-15

### Key Papers & Concepts
- "VIX and More" | various | relevance: 70/100 | VIX term structure, regime interpretation | read

---

## Topic: vol-targeting

### Market Facts & Structural Observations
- Vol targeting scales position size inversely with recent realized volatility | mechanical, not alpha-generating | [AUTO: LESSONS_LEARNED.md] | 2026-03-15
- Backward-looking vol measures can't react to sudden shocks; vol targeting starts reducing after drawdown begins | [AUTO: LESSONS_LEARNED.md] | 2026-03-15

### Intermediate Findings
- Vol targeting useful for leverage control (prevent over-leveraging in low-vol regimes) but not crash protection | confidence: high | follow-up: use only as leverage cap, not timing signal | [AUTO: LESSONS_LEARNED.md] | 2026-03-15

### Confirmed Signals
- (none — vol targeting as alpha source rejected)

### Known Failure Modes
- Vol targeting doesn't fix crash risk for equity long-only; backward-looking vol can't react to sudden shocks | [PM-VERDICT: vol_scaled_momentum_2026-03-13 REJECTED] | 2026-03-15
- Using vol targeting as a crash protection mechanism is a known failure; drawdown reduction is mechanical from lower exposure | [AUTO: LESSONS_LEARNED.md] | 2026-03-15
- Drawdown reduction does NOT equal alpha: cash allocation achieves same mechanical effect | [AUTO: LESSONS_LEARNED.md research process] | 2026-03-15

### Key Papers & Concepts
- "Volatility-Managed Portfolios" | Moreira & Muir | 2017 | relevance: 82/100 | vol targeting improves Sharpe in theory; contested in practice | cited

---

## Topic: realized-vs-implied

### Market Facts & Structural Observations
- Implied vol (VIX) > realized vol on average — the VRP exists across regimes | [AUTO: LESSONS_LEARNED.md] | 2026-03-15
- The gap between implied and realized vol (VRP) widens before crises and narrows after | [AUTO: LESSONS_LEARNED.md] | 2026-03-15
- Crisis detection capability of VRP does NOT translate to investable alpha after costs | [AUTO: LESSONS_LEARNED.md] | 2026-03-15

### Intermediate Findings
- VRP as risk monitoring signal (alert system) — worth building as dashboard indicator, not strategy | confidence: high | follow-up: add VRP to market monitoring dashboard | [AUTO: LESSONS_LEARNED.md] | 2026-03-15

### Confirmed Signals
- (none)

### Known Failure Modes
- Crisis detection != investable alpha: VRP crisis interaction t=-3.77 but strategy rejected on spanning alpha | [PM-VERDICT: vix_regime_2026-03-15 REJECTED] | 2026-03-15

### Key Papers & Concepts
- (see vrp topic above)

---

## Topic: tail-risk

### Market Facts & Structural Observations
- Tail risk hedging has persistent negative carry cost; pays off only in severe drawdowns | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13
- For crash protection, need forward-looking signals (VIX spikes, credit spread widening) or hard stops — not backward-looking vol | [AUTO: LESSONS_LEARNED.md] | 2026-03-15

### Intermediate Findings
- (none)

### Confirmed Signals
- (none)

### Known Failure Modes
- Tail risk overlays using backward-looking vol fail to protect in sudden shock scenarios | [AUTO: LESSONS_LEARNED.md] | 2026-03-15

### Key Papers & Concepts
- (none yet)
