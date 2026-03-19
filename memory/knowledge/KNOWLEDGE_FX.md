# Knowledge Base: FX
_Last updated: 2026-03-19_
_Entry tags: [AUTO] auto-extracted | [PLAYGROUND] from notebook | [BOOK/ARTICLE] from reading | [PM-VERDICT] from strategy review_
_All entries validated by kb-curator agent before write._

---

## Topic: carry

### Market Facts & Structural Observations
- High-carry currencies crash during risk-off episodes (USD spike, equity selloff) | robust across G10 and EM | [BOOK/ARTICLE: Lustig & Verdelhan 2007] | 2026-03-13
- Carry works best in low-vol regimes; drawdowns cluster in vol spikes | [AUTO: LESSONS_LEARNED.md] | 2026-03-15
- Post-publication carry alpha is compressed; realistic expectation 2-4% annualized net of costs | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13
- Pure carry without momentum filter is exposed to crash risk (Sharpe ~0.3 unhedged) | [PM-VERDICT: fx_carry_2026-03-13 CONDITIONAL] | 2026-03-13

### Intermediate Findings
- Carry + momentum filter combination may significantly improve crash-adjusted returns vs pure carry | confidence: med | follow-up: backtest carry × momentum signal interaction | [AUTO: STRATEGY_TRACKER.md] | 2026-03-13
- FX Carry + Momentum is Priority 1 in research pipeline — assigned to Marco | confidence: high | follow-up: full R1 notebook | [AUTO: STRATEGY_TRACKER.md] | 2026-03-17

### Confirmed Signals
- HML_FX factor (high-minus-low carry) has robust multi-paper evidence as a risk premium | Lustig, Roussanov, Verdelhan (2011) | data: G10 FX rates, FRED interest rate differentials | long-standing academic consensus | 2026-03-13

### Known Failure Modes
- Pure carry (no momentum filter) exposed to crash risk; unhedged Sharpe ~0.3; dominated by crash events | [PM-VERDICT: fx_carry_2026-03-13 CONDITIONAL] | 2026-03-13
- CarrySignal in backtests/strategies/signals.py is a short-term momentum proxy, NOT true carry — FXCarrySignal not yet implemented | [AUTO: LESSONS_LEARNED.md framework audit] | 2026-03-15

### Key Papers & Concepts
- "Common Risk Factors in Currency Markets" | Lustig, Roussanov, Verdelhan | 2011 | relevance: 92/100 | HML_FX factor; carry return is compensation for global risk | cited
- "Currency Risk Premia" | Lustig & Verdelhan | 2007 | relevance: 88/100 | carry crash risk during global risk-off | cited
- "Carry" | Koijen, Moskowitz, Pedersen, Vrugt | 2018 | relevance: 85/100 | carry generalization across asset classes | cited

---

## Topic: momentum

### Market Facts & Structural Observations
- FX momentum persists over 1-12 month horizons in G10 and EM | robust across regimes | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13
- Mitsui Commodity Prediction Challenge 3rd place: "directional trends over volatility" — trend signals normalized by vol robust even in commodity/FX markets | [BOOK/ARTICLE: Kaggle 3rd place writeup] | 2026-03-13

### Intermediate Findings
- FX momentum may be enhanced when combined with carry (dual-signal approach) | confidence: med | follow-up: test carry+momentum interaction in R1 | [AUTO: external_ideas.md] | 2026-03-13
- Liu FX Momentum enhancement paper flagged as relevant for FX Carry strategy | confidence: low | follow-up: locate and read paper | [AUTO: external_ideas.md reading list] | 2026-03-13

### Confirmed Signals
- (none confirmed yet — FX Carry + Momentum strategy is CONDITIONAL, pending full research)

### Known Failure Modes
- Vol-scaled momentum (equity) destroyed by MVO with tight constraints; ranking-based allocation preferred | [PM-VERDICT: vol_scaled_momentum_2026-03-13 REJECTED] | 2026-03-13
- Momentum overlay doesn't fix crash risk for long-only equity; backward-looking vol can't react to shocks | [PM-VERDICT: vol_scaled_momentum_2026-03-13 REJECTED] | 2026-03-15

### Key Papers & Concepts
- "FX Momentum" | Menkhoff, Sarno, Schmeling, Schrimpf | 2012 | relevance: 87/100 | momentum in FX markets; cross-sectional and time-series | cited

---

## Topic: real-exchange-rates

### Market Facts & Structural Observations
- PPP deviations can persist for years to decades; mean reversion is slow | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13
- Real exchange rate mean reversion has no reliable short-term predictive power | [AUTO: marco expertise] | 2026-03-13

### Intermediate Findings
- (none)

### Confirmed Signals
- (none — PPP not a tradeable signal at monthly horizon)

### Known Failure Modes
- Geographic rotation strategy (non-US equities, currency exposure) rejected — no international equity data, IBKR account lacks intl permissions | [PM-VERDICT: GS Geographic Rotation REJECTED] | 2026-03-17

### Key Papers & Concepts
- "Purchasing Power Parity" | Rogoff | 1996 | relevance: 60/100 | PPP puzzle; deviations persist despite theoretical reversion | cited

---

## Topic: regime

### Market Facts & Structural Observations
- Risk-on/risk-off regimes are the dominant driver of FX returns in the short run | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13
- USD acts as global safe-haven; appreciates during risk-off episodes | [AUTO: marco expertise] | 2026-03-13
- JPY and CHF are geopolitical hedges; Quality + Safe-Haven overlay uses them as hedge legs | [AUTO: STRATEGY_TRACKER.md] | 2026-03-17

### Intermediate Findings
- (none)

### Confirmed Signals
- (none)

### Known Failure Modes
- Regime-based position-sizing overlays have structural headwind in secular bull markets; drawdown reduction is mechanical from lower exposure, not alpha | [PM-VERDICT: vix_regime_2026-03-15 REJECTED] | 2026-03-15

### Key Papers & Concepts
- (see KNOWLEDGE_VOL.md for VIX/regime literature)
