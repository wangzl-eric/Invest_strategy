# Paper Notes: The Information in the Term Structure

**Authors:** Eugene F. Fama
**Year:** 1984
**Journal:** Journal of Financial Economics, Vol. 13, No. 4, pp. 509–528
**Scores:** Credibility: 5 | Relevance: 4 | Actionability: 3

---

## Core Claim

Forward interest rates contain two components: **(1) forecasts of future
spot rates** and **(2) time-varying term premia**. Using regressions of
realized future spot rates on forward rates, Fama shows that forward rates
are partially but imperfectly efficient predictors of future rates — the
forecast component is real but the term premium component is large and
time-varying. For short maturities (1–6 months), forward rates primarily
reflect term premia; for longer horizons, both components matter. This
paper is the empirical foundation for the bond futures basis relationship
and the term premium literature that culminates in Kim-Wright (2005).

---

## 1. The Decomposition of Forward Rates

### Forward Rate = Expected Future Spot + Term Premium

$$f_t(t, t+h) = E_t[r_{t+h}] + TP_t(h)$$

where:
- $f_t(t, t+h)$ = forward rate set at time $t$ for period $[t, t+h]$
- $E_t[r_{t+h}]$ = market's expectation of future spot rate
- $TP_t(h)$ = term (liquidity) premium for maturity $h$

### The Pure Expectations Hypothesis

If $TP_t(h) = 0$ (pure expectations hypothesis, PEH):
- Forward rates are unbiased predictors of future spot rates
- The yield curve slope purely reflects expected rate changes
- No excess return from riding the yield curve

Fama's tests **reject PEH**: term premia are large, positive on average,
and time-varying — they vary with the business cycle.

---

## 2. Key Findings

### Regression Evidence

Fama runs two complementary regressions:

**Regression 1:** Future spot rate on current forward rate:
$$r_{t+h} = \alpha + \beta f_t(t, t+h) + \varepsilon_{t+h}$$
- If PEH holds: $\beta = 1$
- Fama finds: $\beta < 1$ for short maturities; $\beta$ closer to 1 for longer
- Interpretation: forward rates are **partially** informative about future rates

**Regression 2:** Excess return on forward premium:
$$rx_{t+h} = \alpha + \gamma (f_t - r_t) + \varepsilon_{t+h}$$
- $rx$ = realized excess return of holding a longer bond vs. rolling short
- If PEH holds: $\gamma = 0$ (no predictable excess return)
- Fama finds: $\gamma > 0$ and significant — **the forward premium predicts
  excess bond returns**. Higher forward premium = higher subsequent return.

### The Term Premium Is Time-Varying

| Horizon | Forward Rate Informativeness | Term Premium Behavior |
|---------|-----------------------------|-----------------------|
| 1 month | Almost entirely term premium | Varies with business cycle |
| 3 months | Mix of TP and expectations | Counter-cyclical |
| 1 year | Mostly expectations | Smoother, trend-following |
| 5+ years | Primarily expectations | Slow-moving level |

At short maturities, forward rates contain **almost no information**
about future spot rates — they are almost entirely term premium.
This is the basis for carry trades: the short end of the forward curve
is predominantly carry, not rate expectations.

---

## 3. Connection to Bond Futures and the Basis

### Futures Price and the Basis

Fama's framework maps directly to bond futures pricing via the cost-of-carry:

$$F_t = S_t \cdot e^{(r_t - y_t)T}$$

where:
- $F_t$ = futures price
- $S_t$ = spot price of the bond
- $r_t$ = financing rate (repo)
- $y_t$ = bond yield (coupon income)
- $T$ = time to futures expiry

The **gross basis** = $S_t - F_t \cdot CF$ reflects carry (coupon minus repo)
plus the delivery option value — exactly Fama's term premium in the futures
context. The carry component is predictable; the option component is not.

### Riding the Yield Curve

Fama's finding that the forward premium predicts excess returns validates
**yield curve riding** as a strategy:
- Buy a bond at maturity $\tau$; hold for period $h$; sell at maturity $\tau - h$
- Expected excess return = forward premium $f_t(\tau-h, \tau) - r_t$
- Positive when the curve is upward sloping (normal shape)

This is the empirical foundation for the roll-down component of carry
in Koijen et al. (2018).

---

## 4. Key Takeaways

1. **Forward rates are not efficient predictors of future spot rates.**
   The PEH is rejected. This means the yield curve slope contains
   alpha — it is not purely about rate expectations.

2. **The forward premium is a carry signal.** High forward premium
   (steep curve) predicts high excess bond returns. This is the
   theoretical justification for yield curve carry strategies.

3. **Short-end forward rates are mostly term premium.** At 1–3 month
   horizons, almost all of the forward rate is carry, not an expectation
   of future rates. Money market instruments trade at rates that are
   almost entirely compensation for holding risk — not forecasts.

4. **Carry is predictable; price changes are not.** The carry component
   of bond returns (coupon + roll-down) is observable today and largely
   predictable. Capital gains are not. Always compute carry first before
   relying on any convergence thesis.

5. **The bond futures basis is a carry trade.** Long bond / short futures
   (long basis) earns carry minus financing cost — this is exactly Fama's
   forward premium in the futures context. Net basis (= delivery option)
   is the only non-carry residual.

---

## Caveats

- **Sample is 1959–1982** — predominantly a rising-rate era with high and
  volatile inflation. Term premia in low-inflation regimes (post-1990)
  behave differently.
- **Peso problem:** The high term premia of the 1970s may partly reflect
  a peso problem (small probability of hyperinflation that never occurred).
- **Expectations hypothesis not fully dead:** Cochrane & Piazzesi (2005)
  show a single factor from forward rates predicts excess returns at all
  horizons — refinement of Fama's result, not contradiction.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch7 — Bond Futures** | Futures basis = carry + delivery option; Fama provides the carry foundation |
| **Ch12 — Asset Swaps** | ASW carry = forward premium minus swap spread; Fama validates carry as a return predictor |
| **Ch9 — Analytic Process** | Carry is Step 2 of Ch9 process; Fama shows why carry predicts returns even without convergence |
| **Ch5 — Duration/Convexity** | Roll-down calculation requires forward rates; Fama shows forward rates = carry + expectation |

---

*Cerebro — 2026-03-26 | FIRV study: Fama (1984)*