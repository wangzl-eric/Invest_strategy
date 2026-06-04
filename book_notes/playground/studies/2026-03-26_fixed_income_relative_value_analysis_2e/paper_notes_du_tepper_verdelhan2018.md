# Paper Notes: Deviations from Covered Interest Rate Parity

**Authors:** Wenxin Du, Alexander Tepper, Adrien Verdelhan
**Year:** 2018
**Journal:** Journal of Finance, Vol. 73, No. 3, pp. 915–957
**Scores:** Credibility: 5 | Relevance: 5 | Actionability: 5

---

## Core Claim

Covered interest rate parity (CIP) — one of the most fundamental no-arbitrage
conditions in international finance — has been **persistently and significantly
violated** since the 2008 financial crisis. The deviations are large (up to 100bps
for major G10 currency pairs), systematic, and driven primarily by **regulatory
capital constraints** (Basel III leverage ratio, G-SIB surcharges) that prevent
banks from arbitraging the deviations away. This is the cross-currency basis.

---

## What Is Covered Interest Rate Parity?

### The CIP Condition

CIP states that borrowing in currency A, converting to currency B spot, investing
at currency B rates, and locking in the forward exchange rate should yield exactly
the same return as borrowing in currency A directly:

$$F_{t,T} = S_t \cdot \frac{1 + r^B_{t,T}}{1 + r^A_{t,T}}$$

where $S_t$ = spot rate (A per B), $F_{t,T}$ = forward rate, $r^A, r^B$ = risk-free
rates in each currency for maturity $T-t$.

Equivalently, the **CIP deviation** (cross-currency basis $x$) is:

$$x_{t,T} = r^B_{t,T} - r^A_{t,T} - \rho_{t,T}$$

where $\rho_{t,T} = (F_{t,T}/S_t - 1)$ is the forward premium. Under CIP: $x = 0$.

### Pre-Crisis: CIP Held

Before 2008, CIP deviations were negligible (<5bps) — banks arbitraged them
instantaneously via FX swap desks. The mechanism: borrow cheap currency, swap
into expensive currency, earn the spread, unwind at maturity.

---

## Key Findings

### 1. CIP Deviations Are Large and Persistent Post-2008

- EUR/USD 3M basis: persistently -20 to -80bps (dollar expensive in FX swap market)
- JPY/USD 3M basis: -30 to -100bps at times
- GBP/USD, AUD/USD: similar magnitudes
- Deviations are **not explained by credit risk** — they persist even using OIS
  rates (near risk-free) on both legs

### 2. Regulatory Capital Is the Primary Driver

The paper's key regression:
$$x_{t,T} = \alpha + \beta_1 \cdot \text{LeverageRatio}_t + \beta_2 \cdot \text{GSIB}_t + \varepsilon_t$$

Findings:
- **Leverage ratio constraints** (Basel III): banks must hold equity against gross
  balance sheet assets. An FX swap arbitrage expands the balance sheet → consumes
  leverage ratio capacity → only worth doing if the spread exceeds the capital cost.
- **G-SIB surcharge**: the largest arbitrageurs (major dealer banks) face the
  highest surcharges, further limiting their arbitrage capacity.
- **Quarter-end spikes**: CIP deviations widen sharply at quarter-end when banks
  window-dress balance sheets — direct evidence of regulatory constraint.

### 3. The Basis Is Compensation for Balance Sheet Cost

The CIP deviation is not free money — it is the **equilibrium price of balance
sheet capacity**. The marginal arbitrageur earns exactly their cost of capital;
no abnormal profit remains after accounting for regulatory capital charges.

### 4. Dollar Is Structurally Expensive in FX Swaps

The USD cross-currency basis is consistently negative: borrowing dollars via FX
swaps costs more than the interest rate differential implies. This reflects:
- Strong global demand for USD funding (dollar dominance)
- U.S. money market fund reform (2016) reduced prime MMF supply of USD
- Structural USD shortage for non-U.S. banks needing dollar funding

---

## Key Takeaways

1. **CIP is a regulatory constraint story, not a credit story.** Using OIS rates
   (credit-free) still shows large deviations. The no-arb condition is broken
   by balance sheet costs, not counterparty risk.

2. **Quarter-end patterns are exploitable.** CIP deviations reliably widen at
   quarter-end and year-end. This creates a predictable seasonal in FX swap basis
   that can be positioned around — a rare structural edge in liquid markets.

3. **Implication for cross-currency asset swaps.** The cross-currency basis directly
   affects the cost of hedging foreign bond investments back to domestic currency.
   A EUR investor buying USTs and swapping USD coupons to EUR pays the negative
   USD basis — must incorporate this into carry calculations.

4. **Basis varies by currency pair and tenor.** JPY and EUR bases are largest;
   CAD and GBP smaller. Longer tenors generally show wider deviations than short.

5. **Not arbitrageable for most investors.** Only banks with FX swap infrastructure
   can exploit the basis efficiently. For asset managers, the basis is a cost to
   be managed, not an alpha source.

---

## Caveats

- **Sample period:** Mainly 2010–2016 in the original paper. Post-2020 behavior
  (COVID spike, 2022 Fed hikes) suggests the basis remains structural.
- **Causality:** The paper shows correlation between regulatory constraints and
  basis; causal identification relies on quasi-natural experiments (regulatory
  implementation dates).
- **Currency pair selection:** Focus on G10; EM cross-currency basis has additional
  political risk, capital controls, and liquidity premia layered on top.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch13–18 — Cross-Currency Basis** | This paper is the theoretical backbone. The book's cross-currency basis chapters use exactly the Du-Tepper-Verdelhan framework to explain why basis persists and when it widens. |
| **Ch11 — Reference Rates** | SOFR vs. ESTR basis in FX swaps is the post-LIBOR version of the CIP deviation studied here |
| **Ch12 — Asset Swaps** | Cross-currency asset swaps embed the CIP basis; a USD bond swapped to EUR carries the EUR/USD basis as a funding cost |
| **Ch20 — Broader Perspective** | The paper exemplifies the book's theme: apparent arbitrages in fixed income often reflect regulatory/structural limits, not free alpha |

---

## Replication Notes

**Data sources:**
- OIS rates: Bloomberg (USSOFR, EUSWEC, JYSWC tickers) or Fed H.15
- FX spot and forward rates: Bloomberg or BIS FX statistics
- Leverage ratio data: Bank regulatory filings (FDIC, ECB supervisory data)

**CIP deviation calculation:**
```python
# x = OIS_foreign - OIS_USD - forward_premium
# All rates annualized, same tenor (e.g. 3M)
basis_eur_usd = ois_eur_3m - ois_usd_3m - forward_premium_eurusd_3m
# Negative value = USD expensive in FX swap market
```

**Quarter-end signal:**
Basis typically widens 5–20bps in the final 2 weeks of each quarter.
Positioning: receive fixed in cross-currency basis swap (pay foreign OIS,
receive USD OIS + basis) ahead of quarter-end, unwind post-turn.

---

## Adjacent Papers to Read Next

- **Ivashina, Scharfstein & Stein (2015)** — dollar funding channel; complements
  Du-Tepper-Verdelhan's regulatory story with the banking channel
- **Avdjiev et al. (2019, BIS)** — dollar funding costs and cross-border bank lending;
  extends the basis to EM currencies
- **Liao (2020)** — corporate bond issuance in foreign currencies exploits the basis;
  another non-bank channel

---

*Cerebro — 2026-03-26 | FIRV study: Du, Tepper & Verdelhan (2018)*
