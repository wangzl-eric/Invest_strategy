# Paper Notes: "Commodity Risk Premiums" — Bhardwaj, Gorton, Rouwenhorst (2015)

**Citation:** Bhardwaj, G., Gorton, G., Rouwenhorst, K. (2015). Fooling Some of the People All of the Time: The Inefficient Performance and Persistence of Commodity Trading Advisors. *Review of Financial Studies* / NBER Working Paper. SSRN: 2344848.
**SSRN:** 2344848
**Scores:** C:5 / R:5 / A:5

---

## Core Thesis

The positive commodity futures risk premium documented in Gorton & Rouwenhorst (2006) persists through 2013 but is concentrated in the roll yield component. Spot price appreciation contributes negatively in the post-2005 period. The paper updates and extends the original facts, adds granular return decomposition, and examines whether financialization eroded the premium.

---

## Key Findings

- **Roll yield remains dominant:** Even in the post-financialization era (2005–2013), roll yield drives commodity futures returns. Spot returns were negative on average in this period.
- **Collateral yield matters more in high-rate environments:** In the low-rate post-2008 era, collateral return near zero — making roll yield the only reliable source of return.
- **Financialization did not eliminate the premium:** Despite the large influx of passive commodity investment (index funds), the risk premium persists — though it became more volatile.
- **Cross-sectional variation:** Roll yield varies significantly across commodities. Energy (crude oil, nat gas) and metals have different term structure dynamics than agriculture.
- **Return decomposition (1959–2013):**
  - Spot return: ~1% annualized (near zero real)
  - Roll yield: ~3–4% annualized (dominant driver)
  - Collateral: ~4% annualized (rate-environment dependent)
- **No alpha from active CTAs:** A parallel finding is that commodity trading advisors (CTAs) do not systematically outperform simple passive roll-yield strategies after fees.

---

## Methodology

- Sample: 1959–2013, extending Gorton & Rouwenhorst's original dataset.
- Same 36-commodity equal-weighted fully-collateralized portfolio.
- Decomposition into spot, roll, and collateral components at individual commodity level.
- Sub-period analysis: pre/post-2005 financialization break.
- CTA performance comparison using CFTC data.

---

## Connection to Gliner (GMT)

- **Ch10 (commodities):** Directly updates the quantitative underpinning of Gliner's commodity discussion with 9 more years of data.
- **Ch6 (systematic trading):** Confirms roll yield as the systematic signal to use in commodity factor portfolios.
- **Ch3 (back-tests):** Sub-period analysis is an example of the regime-aware backtesting Gliner advocates — returns shifted post-2005 and knowing why matters.

---

## Key Differences from Gorton & Rouwenhorst (2006)

| Dimension | Gorton 2006 | Bhardwaj 2015 |
|-----------|-------------|----------------|
| Sample end | 2004 | 2013 |
| Spot return | Modest positive | Negative post-2005 |
| Roll yield | Dominant | Still dominant |
| Financialization | Pre-event | Includes full episode |
| CTA analysis | Not included | Included |

---

## Implementation Notes

- **Signal:** Same roll yield signal as Gorton 2006: (F1 − F2) / F1.
- **Regime awareness:** In contango-heavy environments (post-2008 energy glut), passive long exposure destroys value. Only go long commodities in backwardation.
- **Collateral:** In near-zero rate environments, total return ≈ spot + roll yield only. Model collateral yield explicitly using current T-bill rate.
- **Cross-commodity:** Sort commodities by roll yield each month — long top tercile, short bottom tercile for a carry-style approach.

---

## Validation Path

1. Extend gorton2006 replication to 2013–present with current futures data.
2. Decompose returns into spot, roll, collateral for energy vs metals vs agriculture.
3. Verify roll yield dominance persists post-2013.
4. Build cross-sectional roll yield sort across commodity futures.

---

*Notes compiled 2026-03-28 | Global Macro Trading (Gliner) study*