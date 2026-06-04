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

## Topic: vol-cross-section

### Market Facts & Structural Observations
- Stocks with high sensitivity to VIX innovations (high VIX-beta) earn ~−1% lower monthly returns — they are priced as vol insurance and are structurally expensive | [BOOK/ARTICLE: Ang et al. 2006] | 2026-03-30
- Stocks with high idiosyncratic volatility (IVOL, residual from FF3) earn ~−1.06% lower monthly returns — the idiosyncratic volatility puzzle; opposite of Merton (1987) prediction | [BOOK/ARTICLE: Ang et al. 2006] | 2026-03-30
- VIX-beta effect and IVOL effect are empirically distinct — both significant in horse-race regressions; different mechanisms | [BOOK/ARTICLE: Ang et al. 2006] | 2026-03-30
- IVOL puzzle holds in all G7 markets — not a US data-mining artifact | [BOOK/ARTICLE: Ang et al. 2006] | 2026-03-30
- Price of aggregate vol risk is negative: bearing vol risk earns a positive premium; hedging against it costs a negative premium | [BOOK/ARTICLE: Ang et al. 2006] | 2026-03-30

### Intermediate Findings
- IVOL computable from equities.parquet: regress daily returns on FF3 within each month, take residual std dev — data infrastructure ready | confidence: high | follow-up: implement IVOLSignal in backtests/strategies/signals.py | [PLAYGROUND] | 2026-03-30
- VIX-beta computable from vix_daily.parquet + equities.parquet: rolling 60-month regression of monthly stock returns on market + ΔVIX — data infrastructure ready | confidence: high | follow-up: implement VIXBetaSignal | [PLAYGROUND] | 2026-03-30
- VolatilitySignal in signals.py (line 116) is total realised vol, not factor-adjusted IVOL — directionally consistent but theoretically imprecise | [PLAYGROUND] | 2026-03-30

### Confirmed Signals
- (none yet — IVOL and VIX-beta signals not yet implemented or backtested in this codebase)

### Known Failure Modes
- IVOL effect is concentrated in small-cap, illiquid stocks; large-cap-only universe will attenuate the effect significantly | [BOOK/ARTICLE: Bali & Cakici 2008] | 2026-03-30
- Short leg (high-IVOL) drives most of the long-short return — long-only implementation loses most of the alpha | [BOOK/ARTICLE: Stambaugh et al. 2015] | 2026-03-30
- After realistic transaction costs and short-borrow rates, net alpha is substantially smaller than gross spread | [BOOK/ARTICLE: Ang et al. 2006 limitation] | 2026-03-30
- VIX-beta estimates from rolling 5-year individual stock regressions are noisy — high classification error month-to-month | [BOOK/ARTICLE: Ang et al. 2006] | 2026-03-30
- Do NOT confuse VIX-level regime overlay (our rejected vix_regime strategy) with VIX-beta cross-sectional sort — these are different constructs | [PM-VERDICT: vix_regime_2026-03-15 REJECTED] | 2026-03-30

### Key Papers & Concepts
- "The Cross-Section of Volatility and Expected Returns" | Ang, Hodrick, Xing, Zhang | 2006 | JoF | Two-effect paper: VIX-beta pricing + IVOL puzzle | credibility: 5/5
- "High Idiosyncratic Volatility and Low Returns: International Evidence" | Ang, Hodrick, Xing, Zhang | 2009 | JFE | G7 follow-up
- "Idiosyncratic Volatility and the Cross-Section of Expected Returns" | Bali & Cakici | 2008 | JFQA | Robustness checks; value-weighting weakens effect
- "Arbitrage Asymmetry and the Idiosyncratic Volatility Puzzle" | Stambaugh, Yu & Yuan | 2015 | JoF | Short-leg mechanism
- "Have We Solved the Idiosyncratic Volatility Puzzle?" | Hou & Loh | 2016 | JFE | Lottery demand explains ~50%

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
