# Paper Notes: "A Century of Commodity Returns" — Levine et al. (2018)

**Citation:** Levine, A., Ooi, Y., Richardson, M., Sasseville, C. (2018). Commodities for the Long Run. *Financial Analysts Journal*, 74(2). SSRN: 2690232.
**Scores:** C:5 / R:5 / A:5

---

## Core Thesis

Four commodity factors — carry (roll yield), momentum, value, and seasonality — each earn positive risk premia over 100+ years across 230+ individual commodity markets. The premia are robust across sub-periods and not explained by spot price exposure alone.

---

## Key Findings

- **Carry:** Roll yield signal earns ~4–5% annualized with Sharpe ~0.5. Most consistent factor across time.
- **Momentum:** 12-1 month return signal earns ~3–4% annualized. Works across energy, metals, agriculture.
- **Value:** Mean-reversion in spot prices relative to long-run average. Slower signal (~3–5 year horizon).
- **Seasonality:** Predictable seasonal patterns in agricultural and energy commodities. Implementable with calendar dummies.
- **Diversification:** Combining all four factors into an equal-risk portfolio roughly doubles the Sharpe ratio vs any single factor.
- **Long-run robustness:** All four factors survive across WWI, WWII, Great Depression, oil shocks, financialization.

---

## Connection to Gliner (GMT)

- **Ch10 (commodities):** Quantifies all the commodity dynamics Gliner describes qualitatively — adds seasonality and value which Gliner only touches on.
- **Ch6 (systematic):** Four-factor commodity model is a complete systematic commodity strategy.
- **Ch3 (back-tests):** 100-year sample is the highest standard for robustness testing.

---

## Implementation Notes

- Carry: roll yield (F1−F2)/F1 — data from front/second month futures.
- Momentum: 12-1 month return on front-month contracts.
- Seasonality: same-calendar-month average return over past 5 years.
- Combine signals with equal vol-weighting across all four.

---

*Notes compiled 2026-03-28 | Global Macro Trading (Gliner) study*