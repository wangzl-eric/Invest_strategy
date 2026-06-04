# Paper Notes: "Carry" — Koijen, Moskowitz, Pedersen, Vrugt (2018)

**Citation:** Koijen, R., Moskowitz, T., Pedersen, L., Vrugt, E. (2018). Carry. *Journal of Financial Economics*, 127(2), 197–225.
**DOI:** 10.1016/j.jfineco.2018.04.002
**Scores:** C:5 / R:5 / A:5

---

## Core Thesis

Carry — defined as the return an investor earns if prices stay the same — is a pervasive, positive expected-return premium across all major asset classes: equities, bonds, FX, commodities, credit, and options. A unified carry factor explains significant return variation everywhere and is distinct from other known premia.

---

## Key Findings

- **Universal carry premium:** Long-high-carry / short-low-carry portfolios earn positive average returns in every asset class studied.
- **Carry definition by asset class:**
  - FX: interest rate differential (forward discount)
  - Commodities: roll yield (spot minus futures price, adjusted for storage)
  - Fixed income: term spread adjusted for duration
  - Equities: dividend yield minus risk-free rate
- **Carry predicts returns:** The carry signal has predictive power for future returns both cross-sectionally and in time-series.
- **Global carry factor:** A diversified multi-asset carry portfolio has a Sharpe ratio of ~0.8 and is only weakly correlated with traditional risk factors (market, value, momentum).
- **Crash risk:** Carry strategies load on crash risk (negative skewness) — particularly in FX — but even after accounting for this, risk-adjusted returns remain positive.
- **Co-movement:** Carry returns across asset classes are positively correlated, suggesting a common global factor drives them.

---

## Methodology

- Sample: 1972–2012 across global equities (18 countries), bonds (10 countries), FX (36 currencies), commodities (26 futures), credit (6 markets), options (5 equity indices).
- Long-short portfolios formed by sorting on carry within each asset class.
- Factor model spanning regressions to test whether carry is explained by existing factors (Fama-French, momentum, value).
- Crash risk measured via realized skewness, tail beta, and option-implied measures.

---

## Connection to Gliner (GMT)

- Ch4 (building blocks): Carry is the unifying signal across all four asset classes Gliner covers.
- Ch6 (systematic trading): The multi-asset carry factor is a direct implementation of Gliner's systematic framework.
- Ch7 (FX): Interest rate differentials = FX carry. The most liquid and widely traded carry strategy.
- Ch10 (commodities): Roll yield = commodity carry. Backwardation signals high expected carry.
- Ch11 (central banks): Rate policy directly sets FX carry levels; QE compressed carry by flattening yield curves.

---

## Implementation Notes

- **FX carry:** Long high-yielders (AUD, NZD, EM), short low-yielders (JPY, CHF). Data: FRED rates + spot FX.
- **Commodity carry:** Roll yield = (spot − near futures) / spot. Data: front/second contract prices.
- **Bond carry:** Yield-to-maturity minus risk-free rate, duration-adjusted. Data: FRED yield curves.
- **Equity carry:** Dividend yield minus cash rate. Data: Bloomberg/yfinance dividend yield series.
- **Risk management:** Carry strategies have crash risk (negative skew). Apply vol-targeting and tail hedges during risk-off regimes (VIX > 25).

---

## Validation Path

1. Replicate FX carry with FRED rates + spot FX data (available in quant_data).
2. Replicate commodity carry with roll yield from front/second contract data.
3. Combine into diversified multi-asset carry portfolio, measure Sharpe and skewness.
4. Compare to Koijen et al. reported results as sanity check.

---

*Notes compiled 2026-03-28 | Global Macro Trading (Gliner) study*