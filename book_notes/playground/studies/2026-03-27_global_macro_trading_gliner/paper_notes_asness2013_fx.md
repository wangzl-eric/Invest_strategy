# Paper Notes: "Currency Value" — Asness, Moskowitz, Pedersen (2013)

**Citation:** Asness, C., Moskowitz, T., Pedersen, L. (2013). Currency Value. Published alongside "Value and Momentum Everywhere". *Journal of Finance*, 68(3).
**DOI:** 10.1111/jofi.12021
**Scores:** C:5 / R:5 / A:5

---

## Core Thesis

A systematic real-exchange-rate / PPP-based value signal in FX earns a reliable positive premium across developed and emerging currencies. FX value is negatively correlated with FX carry and FX momentum — making a three-way combination the most efficient currency strategy.

---

## Key Findings

- **PPP value signal:** Long currencies trading below PPP fair value, short those above. Earns ~3% annualized with Sharpe ~0.4.
- **Negative correlation with carry:** FX value loads on currencies with low yields (undervalued safe havens); carry loads on high-yielders. The two are natural diversifiers.
- **Negative correlation with momentum:** Value is a mean-reversion signal; momentum is a trend signal. Both earn positive returns but offset each other's drawdowns.
- **Three-way combination (value + carry + momentum):** Sharpe ratio ~1.2 — far superior to any single FX strategy.
- **Works in EM and DM:** Premium is consistent across both developed and emerging market currencies, though EM has higher transaction costs.

---

## Connection to Gliner (GMT)

- **Ch7 (FX):** Directly implements Gliner's PPP/REER valuation framework as a quantitative signal.
- **Ch6 (systematic):** The three-way FX factor combination is a complete systematic currency strategy.
- **Ch11 (central banks):** PPP deviations are partly driven by divergent monetary policy — links CB analysis to FX value trades.

---

## Implementation Notes

- **Signal:** REER deviation from long-run mean (BIS REER data, available free) or CPI-adjusted bilateral rates.
- **Rebalance:** Monthly or quarterly — value signals are slow-moving.
- **Combine with carry and momentum:** Equal vol-weight all three. The negative correlations give large diversification benefit.
- **Data:** BIS publishes REER indices for 60+ currencies. FRED has bilateral exchange rates.

---

*Notes compiled 2026-03-28 | Global Macro Trading (Gliner) study*