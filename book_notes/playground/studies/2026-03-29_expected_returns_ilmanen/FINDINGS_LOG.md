# FINDINGS LOG — Expected Returns (Antti Ilmanen)

This file tracks actionable ideas, tradeable signals, risk premia findings, and replicable results discovered during the study.

## Log Format

```
### [DATE] [CHAPTER] — [FINDING TITLE]
- **Type**: signal / methodology / risk premium / data insight / trade idea
- **Source**: chapter / paper
- **Finding**: what was found
- **Actionability**: how to implement or test it
- **Status**: idea / scaffolded / tested / promoted
```

---

## Entries

### [2026-03-30] [Paper: Ang et al. 2006] — Two Distinct Vol Effects in Equity Cross-Section
- **Type**: risk premium / signal idea
- **Source**: Ang, Hodrick, Xing, Zhang (2006) — "The Cross-Section of Volatility and Expected Returns", JoF
- **Finding**: (1) High VIX-beta stocks earn ~−1%/month lower returns — they are expensive vol hedges. (2) High IVOL stocks earn ~−1.06%/month lower returns — the idiosyncratic vol puzzle. Both effects are distinct and survive full controls. Hold in all G7 markets.
- **Actionability**: IVOL implementable now from equities.parquet (FF3 residual std dev within each month). VIX-beta implementable from vix_daily.parquet + equities.parquet (rolling 60-month regression). Neither signal exists in backtests/strategies/signals.py yet. Universe constraint: effect strongest in small-caps — current equities.parquet universe may attenuate.
- **Status**: idea

### [2026-03-30] [Paper: Ang et al. 2006] — VolatilitySignal is Total Vol, Not IVOL
- **Type**: data insight / codebase gap
- **Source**: signals.py line 116 vs Ang et al. 2006 methodology
- **Finding**: The existing VolatilitySignal computes raw 21-day realised vol and inverts it (low vol = buy). This is directionally consistent with the IVOL puzzle but is theoretically imprecise — it conflates systematic and idiosyncratic vol. True IVOL requires FF3 factor regression residuals.
- **Actionability**: Add IVOLSignal class to backtests/strategies/signals.py. Requires FF3 daily factor data pipeline (Ken French library).
- **Status**: idea

