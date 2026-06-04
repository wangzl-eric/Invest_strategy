# Paper Notes: "Two Centuries of Multi-Asset Momentum" — Geczy & Samonov (2017)

**Citation:** Geczy, C., Samonov, M. (2017). Two Centuries of Multi-Asset Momentum. *Financial Analysts Journal*, 73(3).
**DOI:** 10.2469/faj.v73.n3.3
**Scores:** C:4 / R:4 / A:4

---

## Core Thesis

Time-series and cross-sectional momentum strategies earn positive returns across equities, bonds, currencies, and commodities from 1800 to 2012 — 212 years of evidence. Momentum is not a product of modern financial markets or data mining in the post-1926 period.

---

## Key Findings

- **212-year evidence:** Momentum works in every asset class and every 50-year sub-period from 1800 onwards.
- **Cross-sectional momentum:** Long recent winners, short recent losers within each asset class — earns ~4–6% annualized.
- **Time-series momentum:** Sign of past 12-month return determines long/short — earns ~3–5% annualized.
- **Crisis persistence:** Momentum strategies experienced drawdowns in the 1800s and 1900s (e.g., post-WWI reversals) but recovered. No regime permanently kills the premium.
- **Correlation across asset classes:** Momentum returns co-move across asset classes — suggesting a common liquidity/behavioral driver.
- **Not explained by risk factors:** Standard market, size, and value factors do not account for momentum returns across the 212-year sample.

---

## Connection to Gliner (GMT)

- **Ch3 (back-tests):** 212-year sample provides the deepest available out-of-sample evidence for trend-following — directly relevant to Gliner's historical analogs discussion.
- **Ch5 (technical analysis):** Confirms that moving average and momentum signals are not modern artifacts but reflect persistent behavioral patterns.
- **Ch6 (systematic trading):** Supports multi-asset momentum as a robust systematic strategy component.

---

## Implementation Notes

- Use as robustness check: if a momentum signal doesn't work in the 19th century data, be cautious about it in live trading.
- Sub-period analysis: check that your signal earns positive returns in each 25-year window, not just the full sample.
- Cross-asset momentum combination: equal vol-weight momentum signals across equity, bond, FX, commodity for maximum diversification.

---

*Notes compiled 2026-03-28 | Global Macro Trading (Gliner) study*