# Paper Notes: "Risk Parity Is about Balance" — Bridgewater Associates (2012)

**Citation:** Bridgewater Associates (2012). Risk Parity Is about Balance. Bridgewater Research.
**URL:** https://www.bridgewater.com/research-and-insights/risk-parity-is-about-balance
**Scores:** C:4 / R:5 / A:5

---

## Core Thesis

Traditional 60/40 portfolios are not balanced — they are dominated by equity risk (~90% of total portfolio risk). Risk parity achieves true balance by allocating risk equally across asset classes (equities, bonds, commodities, inflation-linked), producing better risk-adjusted returns across all economic environments.

---

## Key Findings

- **60/40 is unbalanced:** Equities have ~3x the volatility of bonds. A 60/40 portfolio has ~90% of its risk in equities — it is essentially a levered equity position with a bond rounding error.
- **Four economic environments:** Asset returns are driven by growth (rising/falling) and inflation (rising/falling). Each asset class performs well in 2 of 4 quadrants:
  - Rising growth: equities, credit
  - Falling growth: bonds, cash
  - Rising inflation: commodities, TIPS, gold
  - Falling inflation: bonds, equities
- **Risk parity = 25% risk in each quadrant:** Equal allocation to each environment via volatility-weighted positions across asset classes.
- **Leverage improves Sharpe, not just return:** Levering low-vol assets (bonds) to match equity risk improves portfolio efficiency — the key theoretical insight.
- **All-weather portfolio:** Delivers consistent risk-adjusted returns across economic regimes because no single macro environment dominates the risk budget.

---

## Connection to Gliner (GMT)

- **Ch6 (systematic trading):** Risk parity is the canonical systematic portfolio construction framework underlying Gliner's multi-asset approach.
- **Ch4 (building blocks):** The four-quadrant model explains why each asset class exists in a portfolio — each hedges a specific macro environment.
- **Ch2 (risk management):** Vol-weighted position sizing is exactly the approach Gliner recommends for cross-asset position management.

---

## Implementation Notes

- **Vol-weight positions:** Each asset class target weight = (target vol) / (asset vol). Rebalance monthly.
- **Four asset classes:** Equities (SPY), nominal bonds (TLT), commodities (DJP/PDBC), inflation-linked bonds (TIP).
- **Leverage:** To match equity-like returns, the bond allocation requires 2–3x leverage. In practice, use bond futures or leveraged ETFs.
- **2022 caveat:** Risk parity suffered heavily in 2022 when equities and bonds fell simultaneously — a reminder that the model assumes bonds hedge equity risk, which failed during inflation shocks.

---

*Notes compiled 2026-03-28 | Global Macro Trading (Gliner) study*