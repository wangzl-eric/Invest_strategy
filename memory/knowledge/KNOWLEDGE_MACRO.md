# Knowledge Base: Macro
_Last updated: 2026-03-19_
_Entry tags: [AUTO] auto-extracted | [PLAYGROUND] from notebook | [BOOK/ARTICLE] from reading | [PM-VERDICT] from strategy review_
_All entries validated by kb-curator agent before write._

---

## Topic: yield-curve

### Market Facts & Structural Observations
- Yield curve inversion has historically preceded recessions by 6-18 months | not a precise timing signal | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13
- Carry & roll-down is the primary return driver for fixed income in normal regimes | [AUTO: marco expertise] | 2026-03-13
- Duration management requires central bank policy views; not a purely quantitative signal | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13

### Intermediate Findings
- (none)

### Confirmed Signals
- (none — Yield Curve strategy REJECTED)

### Known Failure Modes
- Yield Curve Steepener/Flattener strategy REJECTED — insufficient data depth, unclear alpha source beyond macro timing | [PM-VERDICT: yield_curve_2026-03-13 REJECTED] | 2026-03-13
- Yield curve as pure quant signal lacks edge vs macro discretionary; signal content dominated by macro regime | [AUTO: STRATEGY_TRACKER.md] | 2026-03-13

### Key Papers & Concepts
- "Yield Curve Predictors" | Campbell & Shiller | 1991 | relevance: 75/100 | yield spread as recession predictor | cited
- "Carry" | Koijen, Moskowitz, Pedersen, Vrugt | 2018 | relevance: 82/100 | carry generalization to rates/bonds | cited

---

## Topic: commodity-momentum

### Market Facts & Structural Observations
- Commodity momentum is driven by term structure (contango/backwardation) as much as price trend | [AUTO: marco expertise] | 2026-03-13
- Inflation hedging properties of commodities are regime-dependent; strong in supply-shock inflation, weak in demand-driven | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13
- Seasonality is significant in energy and agricultural commodities | [AUTO: marco expertise] | 2026-03-13
- Mitsui challenge: directional trends normalized by vol robust in commodity markets | [BOOK/ARTICLE: Kaggle Mitsui 3rd place] | 2026-03-13

### Intermediate Findings
- (none)

### Confirmed Signals
- (none — Commodity Momentum strategy REJECTED)

### Known Failure Modes
- Commodity Momentum + Inflation strategy REJECTED — insufficient data, implementation complexity | [PM-VERDICT: commodity_momentum_2026-03-13 REJECTED] | 2026-03-13
- Commodity signals require term structure data (front vs back contracts), not just price momentum | [AUTO: LESSONS_LEARNED.md] | 2026-03-13

### Key Papers & Concepts
- "Facts and Fantasies About Commodity Futures" | Erb & Harvey | 2006 | relevance: 85/100 | roll yield, term structure, momentum in commodities | cited
- "The Strategic and Tactical Value of Commodity Futures" | Gorton & Rouwenhorst | 2006 | relevance: 80/100 | commodity risk premium sources | cited

---

## Topic: inflation-regime

### Market Facts & Structural Observations
- Inflation regimes (rising/falling/stable) materially affect cross-asset correlations | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13
- FRED data has publication lags (1-4 weeks); must apply in backtesting to avoid look-ahead bias | [AUTO: GOTCHAS.md] | 2026-03-13
- Inflation-driven regimes favor commodities, TIPS, and real assets over nominal bonds | [AUTO: marco expertise] | 2026-03-13

### Intermediate Findings
- (none)

### Confirmed Signals
- (none)

### Known Failure Modes
- Using FRED data without publication lag offset introduces look-ahead bias in macro strategies | [AUTO: GOTCHAS.md] | 2026-03-13

### Key Papers & Concepts
- (none yet)

---

## Topic: credit

### Market Facts & Structural Observations
- Credit spreads (HYG-LQD) are leading indicators for equity risk-off; widen before equity drawdowns | [AUTO: external_ideas.md Quality overlay] | 2026-03-17
- HYG and LQD as credit spread proxies flagged as data requirements for Quality + Safe-Haven strategy | [AUTO: STRATEGY_TRACKER.md] | 2026-03-17

### Intermediate Findings
- Credit spreads as risk-off signal for Quality + Safe-Haven overlay — worth testing as regime filter | confidence: med | follow-up: include in Elena's R1 notebook | [AUTO: STRATEGY_TRACKER.md] | 2026-03-17

### Confirmed Signals
- (none)

### Known Failure Modes
- (none specific yet)

### Key Papers & Concepts
- (none yet)

---

## Topic: cross-asset

### Market Facts & Structural Observations
- Cross-asset correlations are regime-dependent; diversification benefits collapse during crises | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13
- Risk parity assumes stable cross-asset correlations — fails in liquidity crises | [AUTO: LESSONS_LEARNED.md portfolio construction] | 2026-03-15
- GLD (gold) as safe-haven asset in geopolitical risk overlay; USO (oil) for inflation hedge | [AUTO: STRATEGY_TRACKER.md Quality overlay] | 2026-03-17

### Intermediate Findings
- Quality + Safe-Haven uses JPY/CHF + GLD as geopolitical hedge legs alongside QUAL/USMV equity | confidence: med | follow-up: Elena R1 | [AUTO: STRATEGY_TRACKER.md] | 2026-03-17

### Confirmed Signals
- (none)

### Known Failure Modes
- Geographic rotation (non-US) rejected — no international equity data, IBKR account lacks intl permissions | [PM-VERDICT: GS Geographic Rotation REJECTED] | 2026-03-17

### Key Papers & Concepts
- "Global Tactical Asset Allocation" | Faber | 2007 | relevance: 78/100 | cross-asset momentum and trend following | cited

---

## Topic: central-bank

### Market Facts & Structural Observations
- Central bank policy divergence drives FX carry returns over medium term | [AUTO: marco expertise] | 2026-03-13
- Fed policy cycles (hiking/cutting) create predictable duration risk | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13

### Intermediate Findings
- (none)

### Confirmed Signals
- (none)

### Known Failure Modes
- (none specific yet)

### Key Papers & Concepts
- (none yet)
