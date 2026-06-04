# FINDINGS LOG — Global Macro Trading (Greg Gliner)

This file tracks actionable ideas, tradeable signals, mental models, and replicable findings discovered during the study.

## Log Format

```
### [DATE] [CHAPTER] — [FINDING TITLE]
- **Type**: signal / methodology / mental model / data insight / trade idea
- **Source**: chapter / paper
- **Finding**: what was found
- **Actionability**: how to implement or test it
- **Status**: idea / scaffolded / tested / promoted
```

---

## Entries

### 2026-03-28 Ch7 — USD Slightly Overvalued vs Fair Value
- **Type**: signal
- **Source**: 02_fx_valuation.ipynb
- **Finding**: DXY actual 97.65 vs fair value 95.94 as of 2026-02-27. Misvaluation +1.78% — USD modestly rich vs a real-rates-differential and PPP-proxy model.
- **Actionability**: monitor DXY misvaluation for mean reversion. At +1.78% the signal is directional but not extreme. Threshold for trade consideration: >3% misvaluation.
- **Status**: tested

### 2026-03-28 Ch11 — Fed Policy Gap Elevated But Not Extreme
- **Type**: signal
- **Source**: 04_central_bank_policy.ipynb
- **Finding**: Fed policy gap (DFEDTARU - T10Y2Y) = 3.16 as of 2026-02-27, z-score 0.745. Sample max was 5.97. Elevated gap suggests curve pricing in cuts but Fed still above neutral.
- **Actionability**: use policy gap z-score as a CB-1 regime signal. Gap > 1.5 z-score historically correlates with risk-off. Current reading is moderate — watch for further compression.
- **Status**: tested

### 2026-03-28 Ch10 — Commodity Proxy Levels (2026-02-27)
- **Type**: data insight
- **Source**: 05_commodities_macro.ipynb
- **Finding**: CRB-equivalent proxy at 168.61. Energy sub-index 109.83, metals 258.87. Metals materially outperforming energy in recent period.
- **Actionability**: use commodity proxy as an inflation leading indicator and cross-asset risk appetite gauge. Metals/energy divergence may signal demand-driven vs supply-driven inflation.
- **Status**: tested

### 2026-03-28 Ch4 — GMT vs FIRV Macro Regime Divergence
- **Type**: methodology
- **Source**: 03_macro_regime_indicators.ipynb vs FIRV 08_macro_regime_panel.ipynb
- **Finding**: GMT regime panel classifies 2026-02-27 as stable carry (441 days, counts: stable carry=167, inflation shock=139, funding stress=100, growth scare=35). FIRV panel classifies same date as funding stress. Different input variable weighting and threshold choices drive the divergence.
- **Actionability**: reconcile the two methodologies into a single canonical regime panel. The FIRV panel uses SOFR/DFEDTARU/T10Y2Y/T10Y3M/T5YIE/T10YIE. GMT adds broader macro inputs. Investigate which better predicts signal hit rates.
- **Status**: idea

### 2026-03-28 Paper — Koijen et al. (2018) Unified Carry Framework
- **Type**: methodology
- **Source**: paper_notes_koijen2018.md
- **Finding**: Carry premium is pervasive across equities, bonds, FX, and commodities. In FX: carry = interest rate differential. In bonds: carry = yield - duration-adjusted rate change. Unified framework enables cross-asset carry signal construction.
- **Actionability**: implement unified carry signal using available FRED rates and price data. Cross-asset carry composite is the XA-1 hypothesis.
- **Status**: idea

### 2026-03-28 Paper — Fung & Hsieh (2004) Global Macro Factor Decomposition
- **Type**: methodology
- **Source**: paper_notes_funghsieh2004.md
- **Finding**: Global macro hedge fund returns are largely explained by 7 systematic risk factors: equity, bond, currency, commodity trend, and 3 option-based factors. Pure alpha is small.
- **Actionability**: use as a benchmark for evaluating whether GMT-derived signals add alpha beyond replicable systematic premia.
- **Status**: idea

