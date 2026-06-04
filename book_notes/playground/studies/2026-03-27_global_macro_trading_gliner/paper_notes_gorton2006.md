# Paper Notes: "Facts and Fantasies about Commodity Futures" — Gorton & Rouwenhorst (2006)

**Citation:** Gorton, G., Rouwenhorst, K. (2006). Facts and Fantasies about Commodity Futures. *Financial Analysts Journal*, 62(2), 47–68.
**DOI:** 10.2469/faj.v62.n2.4083
**Scores:** C:5 / R:5 / A:5

---

## Core Thesis

Commodity futures have historically delivered equity-like returns with low correlation to equities and bonds — but the source of return is roll yield (the term structure premium), not spot price appreciation. Commodities are a distinct asset class with unique risk premia driven by hedging pressure and storage dynamics.

---

## Key Findings

- **Return decomposition — three components:**
  1. **Spot return:** Change in commodity spot prices. Historically modest and highly cyclical.
  2. **Roll yield:** Return from rolling futures contracts — the dominant performance driver. Positive when the market is in backwardation (futures below spot), negative in contango.
  3. **Collateral yield:** T-bill return on the margin posted. Adds ~4–5% annually in the historical period.
- **Equity-like total returns:** Commodity futures returned ~5% real annually (1959–2004), comparable to equities.
- **Low correlation with equities and bonds:** ~0 correlation with S&P 500 and US bonds, making commodities a genuine diversifier.
- **Inflation hedge:** Commodity futures returns are positively correlated with unexpected inflation — unlike equities and bonds which suffer during inflation surprises.
- **Negative correlation with equities in recessions:** Commodity futures tend to be negatively correlated with equities precisely when equities are weak (recessions), enhancing diversification benefit.
- **Backwardation = hedging pressure:** When producers hedge by shorting futures, the futures price is below expected spot — backwardation. Speculators earn a risk premium for taking the other side.
- **Contango = storage costs dominant:** When storage costs exceed hedging demand, futures trade above spot. Expected roll yield is negative.
- **The fantasy debunked:** Passive long-only commodity exposure (spot price) earns near-zero real returns. The positive historical returns come from roll yield + collateral, not from commodity prices rising.

---

## Methodology

- Sample: July 1959 – December 2004, 36 commodity futures.
- Equal-weighted, fully collateralized long-only portfolio.
- Return decomposition: total return = spot return + roll yield + collateral yield.
- Comparison to equities (S&P 500) and bonds (Ibbotson long-term government).

---

## Connection to Gliner (GMT)

- Ch10 (commodities): This paper is the quantitative foundation for every claim Gliner makes about commodity supply/demand and contango/backwardation.
- Ch4 (building blocks): Establishes commodities as a distinct asset class with genuine diversification properties.
- Ch6 (systematic trading): Roll yield signal is the commodity carry signal — directly feeds into systematic multi-asset carry strategies (see Koijen 2018).

---

## Implementation Notes

- **Roll yield signal:** (F1 − F2) / F1 where F1 = front-month, F2 = second-month futures price. Positive = backwardation (go long). Negative = contango (reduce/avoid).
- **Data source:** CME futures via Quandl/Nasdaq Data Link or direct brokerage feed.
- **Collateral:** In a real implementation, cash collateral earns short-term rates — relevant in high-rate environments; near-zero in post-2008 era.
- **Long-short:** Long backwardated commodities, avoid/short contango commodities for a carry-style approach.

---

## Validation Path

1. Download front/second-month futures prices for crude oil, gold, copper, corn.
2. Compute roll yield = (F1 − F2) / F1 monthly.
3. Compare returns in backwardation vs contango sub-periods.
4. Decompose total return into spot + roll + collateral to verify roll yield dominance.

---

*Notes compiled 2026-03-28 | Global Macro Trading (Gliner) study*