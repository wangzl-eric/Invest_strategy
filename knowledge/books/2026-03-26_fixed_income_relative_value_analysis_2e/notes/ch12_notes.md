# Chapter 12 Notes: Asset Swaps

**Book:** Fixed Income Relative Value Analysis (Huggins & Schaller, 2nd ed., 2024)
**Chapter:** 12 — Asset Swaps
*Notes by Cerebro — 2026-03-26*

---

## Chapter Argument Arc

An asset swap transforms a fixed-rate bond into a synthetic floating-rate instrument
by coupling it with an interest rate swap. The **asset swap spread (ASW)** is the spread
over the floating reference rate (SOFR/EURIBOR) that equates the package to par. It
provides a unified metric for comparing bonds of different coupons, maturities, and
credit quality on an apples-to-apples floating-rate basis. Ch12 covers the mechanics,
the three main ASW types, what drives ASW spreads, and how practitioners use them in RV.

---

## 1. The Asset Swap Mechanics

### What an Asset Swap Does

An investor buys a bond at a (possibly non-par) dirty price and simultaneously enters
an interest rate swap where:
- **Investor pays:** the bond's fixed coupon (received from the bond) to the swap dealer
- **Investor receives:** floating rate (SOFR flat or + spread) from the swap dealer

The net result: the investor holds a **synthetic floater** — cashflows equivalent to
a floating-rate note paying SOFR + ASW spread.

### Why at Par?

The asset swap is typically structured so the package starts at **par value** regardless
of the bond's market price. If the bond is priced at 98, the investor pays 98 but the
swap is sized on 100 notional, creating an upfront exchange of the 2-point difference.
This par structure makes the ASW spread cleanly comparable across bonds.

### The ASW Spread Formula (par-par structure)

The ASW spread $s$ satisfies:

$$P_{\text{bond}} - 100 = \sum_{i} \frac{(c - s) \cdot \Delta t_i}{(1+r_i)^{t_i}}
+ \frac{100}{(1+r_n)^{T}}$$

where $c$ is the fixed coupon, $r_i$ are swap zero rates, and the LHS adjustment
accounts for the bond being off-par. In practice, ASW spreads are solved numerically.

---

## 2. The Three Types of Asset Swap

### Type 1: Par-Par Asset Swap
- Bond purchased at **par** regardless of market price
- Swap notional = bond face value = 100
- Upfront payment adjusts for any price difference: investor pays/receives $(P - 100)$
- ASW spread $s$ is the spread over floating that makes the package worth par
- Most common in Europe (Bund/OAT/BTP asset swap market)

### Type 2: Market-Value Asset Swap
- Bond purchased at **market price** $P$
- Swap notional = $P$ (not 100)
- No upfront exchange — investor pays full dirty price
- ASW spread adjusted so fixed leg PV = floating leg PV at inception
- More common for US corporate bond asset swaps

### Type 3: Z-Spread (Zero-Volatility Spread)
- Not a swap structure — a static spread measure
- The constant spread $z$ added to every point on the swap zero curve such that
  the discounted cashflows equal the bond's market price:
  $$P = \sum_i \frac{CF_i}{(1 + r_i + z)^{t_i}}$$
- No optionality; purely a yield decomposition tool
- Z-spread $\approx$ ASW spread for near-par bonds; diverges for distressed or
  deeply discounted bonds

---

## 3. Drivers of Asset Swap Spreads

### Structural Drivers

| Driver | Direction | Mechanism |
|--------|-----------|----------|
| **Credit risk** | Wider ASW | Bond issuer default risk above swap counterparty risk |
| **Liquidity premium** | Wider ASW | Less liquid bonds demand yield premium; swap leg is liquid |
| **Regulatory supply** | Tighter ASW | QE (central bank buying) compresses govt bond yields vs swaps |
| **Convexity demand** | Tighter ASW | Long-duration bond buyers (insurers, pension funds) accept tight ASW for convexity |
| **Repo specialness** | Tighter ASW | Cheap financing for the bond reduces effective carry cost |

### The Swap Spread vs. ASW Spread Distinction

- **Swap spread** = fixed swap rate minus same-maturity Treasury yield
  (e.g. 10Y USD swap rate minus 10Y UST yield)
- **ASW spread** = floating spread on the specific bond's asset swap
- For on-the-run Treasuries trading near par: ASW spread $\approx$ minus the swap spread
- For off-the-run or non-par bonds: the two diverge due to coupon and price effects

---

## 4. Asset Swap Spreads as RV Signals

### Government Bond ASW Spreads

For government bonds (Bunds, OATs, USTs), the ASW spread reflects:
- **Collateral premium:** Govt bonds used as repo collateral command a financing
  advantage, compressing their ASW spreads relative to non-govt bonds
- **Scarcity:** QE reduces free float; high ECB/Fed ownership tightens ASW spreads
  on purchased bonds vs. non-purchased maturities
- **Cross-market demand:** Foreign investors paying fixed in swaps while buying
  govt bonds tightens ASW spreads in their target maturity range

### Relative Value Application

ASW spreads can substitute for yield fitting residuals (Ch9) as the RV signal:

1. Fit a smooth curve through ASW spreads across maturities for a single issuer
2. Identify bonds whose ASW spread is rich (tight) or cheap (wide) vs. the fitted spread curve
3. Trade cheap vs. rich in a DV01-neutral pair — convergence of ASW residual is the P&L driver

Advantage over yield-space RV: ASW spreads **strip out the risk-free rate**, isolating
credit and liquidity premia. Two bonds from the same issuer with different coupons will
have the same ASW spread if priced fairly — coupon effects are removed.

### Cross-Issuer ASW Spread Trades (Sovereign Spreads)

The spread between OAT ASW and Bund ASW is a credit/political risk premium for France
vs. Germany. This is the basis of sovereign spread trading in Europe:
- Bund ASW tight (negative) = Bunds rich vs. swaps (safe haven, QE, scarcity)
- OAT ASW wider = OATs cheap vs. swaps (credit risk, political uncertainty)
- Spread trade: long OAT ASW, short Bund ASW = bet on French-German spread compression

---

## 5. Key Takeaways

1. **ASW spreads provide a cleaner RV signal than raw yields** for bonds with
   different coupons, since the swap leg strips out the rate level.

2. **Negative Bund ASW is structural.** German Bund ASW spreads are persistently
   negative (Bunds yield less than swaps) due to scarcity (low net supply post-QE)
   and safe-haven demand. This is not a mispricing — it is a risk premium.

3. **Par-par vs. market-value matters for carry.** A bond purchased above par in
   a par-par swap has negative carry from the upfront payment amortization.
   Always compute the full carry (coupon + roll-down - financing) before trading.

4. **Z-spread is a static snapshot; ASW is a funded position.** Z-spread is useful
   for comparing bonds across currencies; the actual P&L of an asset swap includes
   financing and roll effects that Z-spread ignores.

5. **SOFR transition changed historical comparability.** Pre-2023 ASW spreads used
   LIBOR as the floating leg. Post-2023 they use Term SOFR. The structural level
   of ASW spreads shifted by roughly the LIBOR-SOFR basis (~26bps for 3M).

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch9 — Analytic Process** | ASW residuals can replace yield residuals as the RV signal in the Ch9 process |
| **Ch11 — Reference Rates** | The floating leg of all asset swaps is now SOFR-based; understanding SOFR mechanics is prerequisite |
| **Ch13–18 — Spreads** | Cross-currency asset swap basis = cross-currency basis swap spread; connects Ch12 to the CIP deviation literature |
| **Ch8 — Fitted Curves** | A fitted ASW curve (analogous to a fitted yield curve) is the benchmark for identifying ASW spread residuals |

---

*Cerebro — 2026-03-26 | FIRV study: Ch12 Asset Swaps*
