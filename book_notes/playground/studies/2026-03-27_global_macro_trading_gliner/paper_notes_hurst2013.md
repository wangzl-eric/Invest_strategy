# Paper Notes: "Trend-Following with Managed Futures" — Hurst, Ooi, Pedersen (2013)

**Citation:** Hurst, B., Ooi, Y., Pedersen, L. (2013). Demystifying Managed Futures. *Journal of Investment Management*, 11(3), 42–58. (Also circulated as AQR working paper, SSRN 2324288.)
**SSRN:** 2324288
**Scores:** C:5 / R:5 / A:5

---

## Core Thesis

Managed futures returns are almost entirely explained by a simple time-series momentum (trend-following) strategy applied systematically across asset classes. The premium is robust over 135 years, across all economic environments, and provides genuine crisis-alpha — performing best when equities crash.

---

## Key Findings

- **Time-series momentum:** A 1-year lookback signal (long if past 12-month return positive, short if negative) captures the bulk of managed futures returns across all asset classes.
- **135-year evidence:** Strategy works from 1880 to 2012 across equities, bonds, currencies, and commodities — ruling out data mining in the modern futures era.
- **Crisis alpha:** TSMOM earns its highest returns during the worst equity drawdowns (e.g., 1929–32, 2000–02, 2008). This is a genuine diversifier, not just a momentum bet.
- **Sharpe ratio:** ~0.7 across the full 135-year sample; ~0.9 in the modern era (post-1985).
- **Diversification across asset classes:** Signal works in each of the four asset classes independently; combining them roughly doubles the Sharpe ratio versus any single class.
- **Simple implementation:** The 12-month return sign is sufficient; more complex signals add marginal improvement.
- **Managed futures replication:** A regression of CTA returns on TSMOM yields R² > 0.9, confirming trend-following as the primary driver of the CTA industry.

---

## Methodology

- Universe: 67 markets across equities, bonds, currencies, commodities.
- Signal: sign of past 12-month return, applied at monthly rebalance.
- Volatility-scaled positions (target annualized vol of 40% per instrument).
- Transaction cost adjustment using bid-ask estimates.
- 135-year sample constructed from cash markets and early futures data.

---

## Connection to Gliner (GMT)

- Ch3 (back-tests and analogs): Hurst et al. is the gold standard for long-horizon trend-following backtests — the methodology Gliner recommends for validating strategies.
- Ch5 (technical analysis): TSMOM is the quantitative implementation of Gliner's moving average / trend-following discussion.
- Ch6 (systematic trading): Managed futures / CTA strategies are the primary institutional form of systematic trend-following.
- Ch2 (risk management): The crisis-alpha property makes TSMOM a key portfolio hedge — relevant to Gliner's stress-testing discussion.

---

## Implementation Notes

- **Signal:** Sign of past 12-month return. Simple and robust — refinements add little.
- **Position sizing:** Scale each position to target a fixed annualized volatility (e.g., 1% per position). This is the volatility-adjusted sizing Gliner emphasizes in Ch2.
- **Universe:** Apply across equity index futures, bond futures, FX futures/forwards, commodity futures. More instruments = better diversification.
- **Rebalance:** Monthly is sufficient. Daily rebalancing adds transaction costs with minimal benefit.
- **Crisis hedging:** Maintain TSMOM allocation as a portfolio offset to equity long book — it earns most during equity crises.

---

## Validation Path

1. Build 12-month TSMOM signal on available ETF proxies (SPY, TLT, GLD, UUP).
2. Apply vol-scaling and measure rolling Sharpe.
3. Check correlation with equity returns — should be near zero or negative during drawdowns.
4. Compare performance during 2008, 2020 equity drawdowns as crisis-alpha check.

---

*Notes compiled 2026-03-28 | Global Macro Trading (Gliner) study*