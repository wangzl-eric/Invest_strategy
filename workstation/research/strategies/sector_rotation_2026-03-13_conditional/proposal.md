# Strategy: Sector Rotation via Macro-Linked Momentum

> **Researcher:** Elena | **Asset Class:** Equity/Macro | **Verdict:** CONDITIONAL

## Economic Rationale

- Moskowitz & Grinblatt (1999) — industry-level momentum is economically large and distinct from stock-level
- Fama & French (1997) — sector-level return predictability
- Asness et al. (2015) — combining momentum with value/macro signals increases Sharpe
- Novy-Marx (2012) — intermediate-horizon momentum (6-12 months) is stronger

## Signal Construction (3-Factor Composite)

1. **Price Momentum** (weight 0.50): 6-1 month return on each sector ETF, cross-sectionally ranked
2. **Macro Regime Tilt** (weight 0.30): FRED-based rules:
   - Rising rates (T10Y2Y steepening) → overweight XLF, underweight XLRE/XLU
   - High inflation (CPI acceleration) → overweight XLE/XLB, underweight XLY/XLC
   - Credit stress (BAMLH0A0HYM2 widening) → underweight XLF/XLY, overweight XLV/XLP
3. **Relative Strength** (weight 0.20): 3-month return vs SPY (beta-adjusted)

**Alpha formula:**
```python
alpha_sector = 0.5 * zscore(mom_6_1) + 0.3 * macro_tilt_score + 0.2 * zscore(rel_strength_3m)
```

## Specification

- **Universe:** 11 SPDR sector ETFs (XLK, XLF, XLE, XLV, XLC, XLY, XLP, XLB, XLRE, XLU + SPY benchmark)
  - Note: XLI (Industrials) missing from ticker_universe.py — needs to be added
- **Rebalancing:** Monthly
- **Long-only:** Top 3-4 sectors overweight, bottom 3-4 underweight
- **Existing signals:** `MomentumSignal(lookback=126, skip=21)`, `compute_macro_features()`
- **New signals needed:** `MacroTiltSignal`, `RelativeStrengthSignal`
- **FRED data available:** T10Y2Y, T10YIE, BAMLH0A0HYM2 (all in catalog)

## Expected Risk/Return

| Metric | Elena's Estimate | PM's Realistic Estimate |
|--------|-----------------|------------------------|
| Annual Alpha vs SPY | 3-5% | 1-2% |
| Strategy Vol | 12-15% | Same |
| Sharpe (gross) | 0.6-0.8 | 0.4-0.6 |
| Max Drawdown | 20-30% | Same |

## PM Challenges

1. **Alpha is aggressive.** Long-only sector rotation realistically delivers 1-2% net of costs.
2. **Macro regime overlay is underspecified.** How exactly are T10Y2Y, CPI, HY spreads combined? The 0.30 weight is arbitrary.
3. **FRED data timing is dangerous.** CPI has publication lag (Jan CPI released mid-Feb). No safeguard in platform.
4. **Low signal-to-noise** at monthly frequency for macro-sector linkages.
5. **Missing XLI** from ticker universe.

## Requirements for Approval

- [ ] Implement publication-lag handling for FRED data (min 1-month lag for CPI)
- [ ] Build MacroTiltSignal and RelativeStrengthSignal classes
- [ ] Reduce expected alpha to 1-2%
- [ ] Pre-commit regime identification rules BEFORE backtesting (avoid data-mining)
- [ ] Fix CRITICAL-3 (GridSearch) for walk-forward with proper train/test split
- [ ] Compare against naive equal-weight sector rotation benchmark
- [ ] Paper trade 6 months minimum

---
*Last updated: 2026-03-13*
