# Paper Notes: The Treasury Bond Basis (CTD Delivery Options)

**Authors:** Galen Burghardt, Terrence Belton, Morton Lane, John Papa
**Year:** 1994 (Probus Publishing; updated editions 2005, McGraw-Hill)
**Source:** Practitioner book; chapters on CTD option valuation widely cited
**Scores:** Credibility: 4 | Relevance: 5 | Actionability: 5

---

## Core Claim

Treasury bond (and note) futures contracts embed a **short delivery option**: the
short position can choose *which* eligible bond to deliver at expiry from a basket
of qualifying bonds. This option has real economic value, suppresses futures prices
below naive theoretical values, and creates a rich/cheap dynamic across deliverable
bonds known as **the basis**. Properly modeling the CTD option is essential for
bond futures pricing, hedging, and relative value between cash bonds and futures.

---

## 1. Bond Futures Mechanics

### The Delivery Basket

UST futures (e.g. 10Y Note futures, Ultra Bond futures) allow delivery of any
qualifying Treasury bond within a defined maturity range (e.g. 6.5–10 years
for 10Y Note futures). The short chooses which bond to deliver — this is the
**delivery option**.

### The Conversion Factor

To make bonds with different coupons and maturities comparable, each bond has
a **conversion factor (CF)** based on its yield at a notional 6% coupon:

$$\text{Invoice Price} = \text{Futures Price} \times CF_i + \text{Accrued Interest}_i$$

The conversion factor is fixed at contract inception for each deliverable bond.
It roughly equals the bond's price if the yield curve were flat at 6%.

### The Cheapest-to-Deliver (CTD) Bond

The short delivers the bond that **maximizes their profit** (or minimizes cost):

$$\text{CTD} = \arg\min_i \left[P_i - F \times CF_i\right]$$

where $P_i$ = cash price of bond $i$, $F$ = futures price.
The quantity $P_i - F \times CF_i$ is the **invoice basis** (or "the basis").
The CTD bond has the smallest (most negative) basis — it is the cheapest to acquire
and deliver against the futures contract.

---

## 2. Why the CTD Changes

The CTD is not fixed — it changes as yield levels and the shape of the yield curve evolve:

| Rate Environment | CTD Tends To Be |
|-----------------|----------------|
| **Yields > 6% (above notional coupon)** | Long-duration, low-coupon bonds (higher modified duration → bigger CF discount) |
| **Yields < 6% (below notional coupon)** | Short-duration, high-coupon bonds |
| **Yield curve steepens** | Short-end bond (shorter maturity in the basket becomes cheapest) |
| **Yield curve flattens** | Long-end bond (longer maturity bond gains relative value) |

This means **the CTD option is equivalent to a set of options to switch delivery**
between bonds in the basket as market conditions change.

---

## 3. The Basis and Its Components

The **gross basis** of a bond:
$$\text{Gross Basis}_i = P_i - F \times CF_i$$

The **carry** of holding the bond and delivering at expiry:
$$\text{Carry}_i = \text{Accrued coupon} - \text{Financing cost (repo)}$$

The **net basis** (= delivery option value):
$$\text{Net Basis}_i = \text{Gross Basis}_i - \text{Carry}_i$$

For the CTD bond, net basis $\approx 0$ (it is cheapest to deliver and the option
has been exercised). For non-CTD bonds, net basis $> 0$ — it equals the value
of the option to switch to delivering that bond if it becomes CTD.

---

## 4. Modeling the Delivery Option Value

### Why the Option Has Value

The short can deliver any bond in the basket — this flexibility is valuable.
The futures price must reflect the **cheapest possible delivery** (CTD), but the
short also holds an option to switch CTD if rates move. This **quality option**
suppresses futures prices below the naive forward price of the CTD bond.

### Binomial / Monte Carlo Approach

Burghardt advocates a **term structure model** approach:
1. Simulate rate paths (e.g. Ho-Lee or Hull-White)
2. At each node, identify the CTD bond and compute invoice basis
3. The short delivers optimally at each node
4. Futures price = expected discounted value of optimal delivery across all paths

The option value = Naive futures price (assuming CTD fixed) - Model futures price

### The Wildcard Option

For UST futures, delivery can be made on any business day during delivery month
at the **afternoon's futures price** but the **evening's spot prices**.
If bond prices rise after 2pm, the short benefits — this **wildcard option** adds
additional value to the delivery option complex. Estimated value: 2–5 ticks.

### End-of-Month Option

The last 7 days of delivery month have no futures trading but delivery continues.
The short can observe final price moves before choosing delivery date.
Additional option value: 1–3 ticks typically.

---

## 5. Basis Trading Strategies

### Long Basis Trade (Long bond, Short futures)
- Buy the CTD bond in cash market
- Short equivalent futures (hedge ratio = $1/CF_{CTD}$)
- P&L = net basis convergence + carry - financing cost
- Profit if: net basis compresses to zero at delivery (as it must for CTD)
- Risk: bond loses CTD status; new CTD has different basis

### Short Basis Trade (Short bond, Long futures)
- Short the non-CTD bond, long futures
- Bet: non-CTD bond becomes CTD (its net basis collapses)
- Higher risk — requires predicting CTD switch

### Butterfly in the Delivery Basket
- Identify rich and cheap bonds relative to the futures price
- Long cheap bond (via long basis), short rich bond (via short basis)
- Factor-neutral: DV01 matched across both legs

---

## 6. Key Takeaways

1. **Futures price $\neq$ forward price of CTD.** The delivery option depresses
   futures prices. Always value the option before using futures as a hedge.

2. **The basis is not zero even for the CTD.** Carry (coupon income minus repo
   cost) creates a positive gross basis that decays to zero at delivery.
   The net basis (= option value) is what matters for RV.

3. **CTD switches are the primary risk.** When yields cross the 6% notional
   coupon, the CTD flips from short to long duration bonds — a large P&L event
   for basis traders who are not prepared.

4. **Hedge ratio = $1/CF_{CTD}$, not DV01 ratio.** The conversion factor
   determines how many futures contracts hedge one bond position. Using DV01
   alone introduces basis risk.

5. **Wildcard and end-of-month options are small but real.** They add ~3–8 ticks
   of option value in a 32nds-quoted market. Relevant for high-precision basis
   traders but negligible for yield curve hedging purposes.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch7 — Bond Futures** | Burghardt is the practitioner reference that Ch7 is built on; the book covers European equivalents (Bund futures, Gilt futures) using the same CTD option framework |
| **Ch9 — Analytic Process** | Basis trades are an alternative RV vehicle to outright bond positions; net basis residuals substitute for yield fitting residuals |
| **Ch2 — Mean Reversion** | Net basis mean-reverts to zero at delivery — a time-bounded mean reversion ideal for the OU calibration in Ch2 |

---

## Adjacent Papers to Read Next

- **Fama (1984)** — theoretical basis for futures pricing and the basis relationship
- **Ho & Lee (1986)** — simplest term structure model used to value delivery options
- **Hull & White (1990)** — more realistic model for delivery option Monte Carlo

---

*Cerebro — 2026-03-26 | FIRV study: Burghardt et al. (1994)*
