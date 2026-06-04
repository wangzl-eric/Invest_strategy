# Paper Notes: "Value and Momentum Everywhere" — Asness, Moskowitz, Pedersen (2013)

**Citation:** Asness, C., Moskowitz, T., Pedersen, L. (2013). Value and Momentum Everywhere. *Journal of Finance*, 68(3), 929–985.
**DOI:** 10.1111/jofi.12021
**Scores:** C:5 / R:5 / A:5

---

## Core Thesis

Value and momentum premia exist in every asset class and every geography studied. Crucially, they are negatively correlated with each other within and across asset classes — making their combination far more efficient than either alone. A unified multi-asset value-momentum portfolio achieves Sharpe ratios not attainable by any single-asset strategy.

---

## Key Findings

- **Pervasive value premium:** Long-cheap / short-expensive portfolios earn positive returns in all 8 asset classes (equities, bonds, FX, commodities, country indices, credit, etc.).
- **Pervasive momentum premium:** Long-past-winner / short-past-loser portfolios also earn positive returns in all 8 asset classes.
- **Negative correlation:** Value and momentum are negatively correlated (~−0.5) within and across asset classes. This is the key diversification insight.
- **Combined portfolio:** A 50/50 value-momentum combination achieves Sharpe ratios of ~1.0–1.6 across most asset classes, well above either strategy alone.
- **Co-movement across classes:** Value returns in equities co-move with value returns in FX and bonds; same for momentum. Suggests common global funding/liquidity factors drive both.
- **Funding liquidity:** Both premia worsen during funding crises (2008, LTCM). Liquidity risk is a partial explanation but does not fully account for returns.
- **Signal construction:**
  - Value: book-to-market (equities), PPP deviation (FX), 5y yield change (bonds), spot-vs-average (commodities)
  - Momentum: 12-1 month return (equities), 12-1 (FX, bonds, commodities)

---

## Methodology

- Sample: 1972–2011, 8 asset classes, ~50 markets total.
- Equal-risk (volatility-scaled) long-short portfolios within each asset class.
- Cross-asset portfolio formed by equal-weighting volatility-scaled positions across all classes.
- Spanning regressions, correlation analysis, liquidity/funding risk betas.

---

## Connection to Gliner (GMT)

- Ch4 (building blocks): Value and momentum are the two most fundamental cross-asset signals underlying discretionary macro.
- Ch5 (technical analysis): Momentum is the quantitative formalization of Gliner's trend-following discussion.
- Ch6 (systematic trading): Combined value-momentum is the backbone of any multi-asset systematic factor approach.
- Ch7–10 (asset classes): Each asset class has its own value and momentum signal with consistent positive premia.

---

## Implementation Notes

- **Equity momentum:** 12-1 month return on country ETFs or sector indices.
- **FX value:** PPP deviation or REER (BIS data or FRED). Long undervalued, short overvalued currencies.
- **FX momentum:** 12-1 month return on spot FX.
- **Commodity momentum:** 12-1 month return on front-month futures.
- **Bond momentum:** 12-1 month return on duration-adjusted bond indices.
- **Key insight for portfolio construction:** Always combine value and momentum — the negative correlation gives ~40% reduction in portfolio volatility for free.

---

## Validation Path

1. Build 12-1 momentum signal on available ETF/index data (equity, FX, commodity).
2. Build PPP/REER value signal for FX using FRED or BIS REER data.
3. Measure correlation between value and momentum returns — verify negative sign.
4. Combine 50/50 and compare Sharpe to individual strategies.

---

*Notes compiled 2026-03-28 | Global Macro Trading (Gliner) study*