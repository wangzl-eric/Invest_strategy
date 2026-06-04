# Chapter 16 Notes: Cross-Market Bond RV via Fitted Curves and SOFR ASW Spreads

**Book:** Fixed Income Relative Value Analysis (Huggins & Schaller, 2nd ed., 2024)
**Chapter:** 16 — Cross-Market Relative Value
*Notes by Cerebro — 2026-03-26*

---

## Chapter Argument Arc

Ch16 extends the single-market analytic process (Ch9) to **cross-market** relative
value — comparing bonds across different sovereign issuers, currencies, and yield
curve regimes. The tools are the same (fitted curves, PCA, ASW spreads) but the
challenges multiply: exchange rate risk, different day-count conventions, regulatory
differences across jurisdictions, and the cross-currency basis (Ch13–14) all create
noise that must be stripped out before a genuine RV signal can be identified.

---

## 1. Why Cross-Market RV Is Harder Than Single-Market

### Sources of Complexity

| Challenge | Impact |
|-----------|--------|
| **Currency risk** | Must hedge FX exposure; hedging cost = cross-currency basis (Ch13) |
| **Different rate benchmarks** | USD uses SOFR; EUR uses ESTR/EURIBOR; JPY uses TONA |
| **Different day-count** | ACT/360 (USD, EUR money market) vs ACT/365 (GBP, JPY) |
| **Different credit regimes** | UST = risk-free; Bund = AAA; BTP = BBB — spread includes credit premium |
| **Regulatory fragmentation** | Basel III applies differently across jurisdictions |
| **Settlement differences** | T+1 (UST) vs T+2 (EUR govts); affects carry calculation |

### The Common Currency Framework

The standard approach: **convert all bonds to a common currency** (usually USD or EUR)
using cross-currency asset swaps, then compare ASW spreads on a like-for-like basis.

A USD investor comparing 10Y Bund vs 10Y UST:
1. Buy Bund, enter EUR/USD cross-currency swap (pay EUR ESTR, receive USD SOFR + basis)
2. The all-in USD yield = Bund yield + EUR/USD cross-currency basis
3. Compare this to 10Y UST yield on same basis

---

## 2. The Cross-Market RV Framework

### Step 1: Hedge the Currency Risk

Convert the foreign bond to domestic currency using a cross-currency swap:
$$\text{USD yield equivalent} = y_{\text{foreign}} + x_{\text{FX basis}}$$
where $x_{\text{FX basis}}$ is the cross-currency basis (negative for EUR/USD,
meaning EUR investors pay a premium to access USD). This is the Du-Tepper-Verdelhan
(2018) adjustment that makes cross-market comparison valid.

### Step 2: Fit Sovereign Curves in a Common Space

Two approaches:

**A. Common Fitted Curve**
Fit a single NS/Svensson curve to all sovereign bonds from target countries
after FX-hedging to common currency. Residuals from the common curve identify
bonds that are cheap/rich relative to the global curve.

**B. Spread Curve**
Fit individual sovereign curves, then analyze the **spread curve** between them
(e.g. OAT yield minus Bund yield at each maturity). PCA on the spread curve
extract level/slope/curvature of the spread — used to identify butterfly
opportunities within the spread.

### Step 3: ASW-Based Cross-Market Comparison

Convert all bonds to ASW spreads in common currency:
$$\text{ASW}_{\text{USD-equiv}} = \text{ASW}_{\text{local}} + x_{\text{FX basis}}$$

Now compare ASW spreads directly:
- **Bund ASW** (typically negative, -20 to -60bps): scarcity + safe haven
- **OAT ASW** (wider, near 0): credit premium for France vs. Germany
- **BTP ASW** (positive, 50–200bps): Italian credit risk
- **UST ASW** (slightly negative to flat): dollar safe haven, but less scarce

The spread between Bund ASW and OAT ASW (in common currency) is the **Franco-German
sovereign spread** expressed in swap-adjusted terms — the core cross-market RV signal
for EUR sovereign relative value trading.

---

## 3. PCA on Cross-Market Spread Curves

Applying PCA to the **spread curve** (e.g. BTP-Bund spread at each maturity)
extracts three factors:
1. **Level of spread** — overall credit/risk premium for Italy vs. Germany
2. **Slope of spread** — whether the spread is steeper at short end (acute crisis)
   or long end (structural concern)
3. **Curvature of spread** — whether the spread is concentrated at medium maturities

A rich signal: the spread at a specific maturity (e.g. 10Y BTP-Bund)
deviates from its fitted value on the spread curve → butterfly trade on the
sovereign spread (long 10Y BTP-Bund, short 5Y and 30Y BTP-Bund in proportion).

---

## 4. SOFR ASW Spreads as the Cross-Market RV Metric

Post-LIBOR, SOFR ASW spreads are the cleanest cross-market metric because:
- All bonds swapped to SOFR floating strip out the risk-free rate
- Remaining spread = credit + liquidity + scarcity premium
- Comparable across currencies once FX basis is applied

### Practical Cross-Market Signal Construction

1. For each bond: compute ASW spread in local currency
2. Add cross-currency basis to convert to common currency (USD or EUR)
3. Fit a smooth curve through converted ASW spreads for each issuer
4. Compute residuals from each issuer's fitted ASW curve
5. Compare residuals across issuers at same maturity — identifies bonds that
   are rich or cheap vs. cross-market peers on a swap-adjusted basis

### Example: 10Y Bund vs. 10Y OAT ASW in USD Terms

| Bond | Local ASW | FX Basis (EUR/USD) | USD-equiv ASW |
|------|-----------|-------------------|---------------|
| 10Y Bund | -45bps | -25bps | -70bps |
| 10Y OAT | -10bps | -25bps | -35bps |
| **Spread** | **35bps** | 0 | **35bps** |

The 35bps spread is the Franco-German sovereign credit/political premium.
If this spread widens beyond its historical mean (say 40bps), the trade is:
long OAT ASW / short Bund ASW in USD terms (bet on spread compression).

---

## 5. Key Takeaways

1. **Cross-market RV requires a complete cost-of-carry framework.** Yield comparison
   alone is meaningless without FX hedging cost (cross-currency basis), different
   day-count conventions, and repo/financing adjustments.

2. **The SOFR ASW spread in common currency is the right metric.** It strips out
   the risk-free rate, the FX rate, and coupon effects — leaving only the
   credit/liquidity premium that is the true RV signal.

3. **Sovereign spread PCA surfaces butterfly trades.** Level trades on sovereign
   spreads (long/short overall BTP-Bund) are macro directional. Butterfly trades
   (based on curvature of the spread curve) are more idiosyncratic and lower beta.

4. **The cross-currency basis is the key friction.** In benign markets the basis
   is small and stable; in stress it widens sharply, eroding cross-market carry.
   Always stress-test cross-market RV trades against a basis widening scenario.

5. **Regulatory fragmentation creates persistent cross-market mispricings.** Different
   SLR, FRTB, and leverage ratio rules across US, EU, and Japan mean that the
   same bond can be priced differently by dealers in each jurisdiction — a
   structural source of cross-market basis.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch9 — Analytic Process** | Ch16 is the cross-market extension of Ch9; same five-step process, more complex cost-of-carry |
| **Ch12 — Asset Swaps** | ASW spreads are the basic unit of Ch16's cross-market comparison |
| **Ch13–15 — Basis** | Cross-currency basis is the FX hedging cost that must be added to convert local ASW to common-currency ASW |
| **Ch4 — Multivariate Mean Reversion** | Sovereign spread PCA + mean reversion on the spread = the statistical model for cross-market RV |
| **Ch8 — Fitted Curves** | Fitting ASW spread curves per issuer uses the same NS/Svensson machinery as yield curve fitting |

---

*Cerebro — 2026-03-26 | FIRV study: Ch16 Cross-Market Bond RV*
