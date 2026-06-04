# Paper Notes: "A Century of Global Factor Premiums" — Baltussen et al. (2021)

**Citation:** Baltussen, G., Swinkels, L., Van Vliet, P. (2021). Global Factor Premiums. *Review of Financial Studies*, 34(8), 3225–3268.
**DOI:** 10.1093/rfs/hhab019
**Scores:** C:5 / R:4 / A:5

---

## Core Thesis

Trend, value, carry, and seasonality factors each earn statistically significant positive returns across equities, bonds, FX, and commodities over 1800–2016 — 215 years of out-of-sample evidence. The premiums are not explained by risk, data mining, or transaction costs.

---

## Key Findings

- **Four factors, four asset classes:** All 16 factor-asset class combinations earn positive returns. Sharpe ratios range from 0.3 to 0.9.
- **Trend (TSMOM):** Most consistent factor. Earns positive returns in every asset class in every sub-century.
- **Carry:** Second most consistent. Strong in FX and commodities; weaker in bonds.
- **Value:** Slower but persistent. Works best in equities and FX over long horizons.
- **Seasonality:** Smallest but statistically significant in commodities and equities.
- **Transaction cost robustness:** Even after realistic historical transaction cost estimates, all four factors remain profitable.
- **No risk-based explanation:** Factor returns are not explained by traditional risk factors (market, size, value, momentum in standard models).
- **Regime robustness:** Premiums survive WWI, WWII, Great Depression, oil shocks, financial crisis — no single macro regime kills any factor.

---

## Connection to Gliner (GMT)

- **Ch3 (back-tests):** 215 years is the ultimate robustness test — directly relevant to Gliner's historical analogs discussion.
- **Ch6 (systematic):** Validates that the systematic factor premia Gliner describes are not modern artifacts.
- **Ch5 (technical analysis):** Trend following confirmed as the most robust and universal technical signal.

---

## Implementation Notes

- Use as out-of-sample validation for any factor strategy before live trading.
- Sub-period analysis framework: test your signal in each 25-year window to check robustness.
- Seasonality signal: simple to add to any model — same calendar month return over trailing 5 years.

---

*Notes compiled 2026-03-28 | Global Macro Trading (Gliner) study*