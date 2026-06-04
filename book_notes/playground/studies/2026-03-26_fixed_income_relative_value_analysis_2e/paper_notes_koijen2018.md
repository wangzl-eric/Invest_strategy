# Paper Notes: Carry

**Authors:** Ralph S.J. Koijen, Tobias J. Moskowitz, Lasse Heje Pedersen, Evert B. Vrugt
**Year:** 2018
**Journal:** Journal of Finance, Vol. 73, No. 2, pp. 911–959
**Scores:** Credibility: 5 | Relevance: 5 | Actionability: 5

---

## Core Claim

**Carry** — the return to an asset if prices remain unchanged — is a pervasive
and robust return predictor across all major asset classes: equities, government
bonds, currencies, commodities, credit, and options. Long-carry/short-low-carry
portfolios earn significant risk-adjusted returns in every asset class studied.
Moreover, carry strategies are **positively correlated across asset classes**,
suggesting a common global carry factor that prices a common risk.

---

## The Carry Definition

### General Definition

For any asset, carry is defined as the expected return if the **price does not change**:

$$C_t = \frac{\text{Income}_t + \text{Roll Return}_t}{P_t}$$

where:
- **Income** = dividends, coupons, or convenience yield
- **Roll Return** = gain/loss from the passage of time on the futures curve
  (positive if backwardation, negative if contango)

Carry is observable today — no forecast of future prices required.

### Asset-Class Specific Carry Definitions

| Asset Class | Carry Measure |
|-------------|---------------|
| **Bonds** | Yield + roll-down (yield change from aging 1 period on the curve) |
| **Currencies** | Interest rate differential (forward premium, FX carry trade) |
| **Equities** | Dividend yield + earnings yield component |
| **Commodities** | Convenience yield = spot/futures basis |
| **Options** | Volatility risk premium (implied vol - realized vol) |

---

## Bond Carry: The Fixed Income Application

### Definition for Government Bonds

For a bond with yield $y(\tau)$ at maturity $\tau$:

$$\text{Bond Carry} = y(\tau) + \underbrace{\frac{\partial y}{\partial \tau}\Big|_{\tau} \cdot (-1)}_\text{roll-down} - r_f$$

where:
- $y(\tau)$ = current yield (income component)
- Roll-down = yield change as bond ages by one period along a static curve
  (positive if curve is upward sloping — bond rolls to lower yield = price gain)
- $r_f$ = financing rate (repo/SOFR)

**Example:** A 10Y Treasury yielding 4.5%, with the 9Y yield at 4.3% (normal curve):
- Income carry = 4.5%
- Roll-down = +20bps (yield drops 20bps as bond ages to 9Y)
- Financing = 5.3% (SOFR)
- **Net carry = 4.5% + 0.20% - 5.3% = -0.6%** (negative carry — funding cost exceeds income)

In an inverted yield curve environment, both income and roll-down are negative
for long-duration bonds — double-negative carry. This is why carry was deeply
negative for US Treasuries in 2022–2023.

---

## Key Findings

### 1. Carry Predicts Returns Across All Asset Classes

| Asset Class | Carry Sharpe (long-short) | t-stat |
|-------------|--------------------------|--------|
| Currencies | 0.70 | 3.8 |
| Global bonds | 0.50 | 2.9 |
| Equities | 0.45 | 2.6 |
| Commodities | 0.40 | 2.3 |
| Combined | 0.80 | 5.1 |

Results hold out-of-sample and across different sample periods.

### 2. Carry Strategies Are Positively Correlated Across Asset Classes

Carry returns in equities, bonds, FX, and commodities are all positively
correlated (average ~0.15–0.25 pairwise). This **global carry factor** suggests
a common underlying risk — likely a crash/liquidity risk that all carry strategies
load on simultaneously.

### 3. Crash Risk: Carry Strategies Have Negative Skewness

All carry strategies exhibit:
- Positive mean returns (the carry premium)
- Negative skewness (occasional large losses)
- High kurtosis (fat left tail)

The 2008 FX carry crash (carry currencies collapsed simultaneously) is the
canonical example. Bond carry strategies crashed in 1994 and 2022.

### 4. Carry Is Not Explained by Standard Risk Factors

Carry returns are not explained by:
- CAPM beta
- Fama-French factors (value, size)
- Momentum

Carry is a distinct source of expected return — an independent risk premia.

---

## Key Takeaways

1. **Carry is the primary return driver in fixed income.** Before searching for
   mean reversion or RV signals, compute the carry on every trade. Trades with
   negative carry require convergence to overcome the drag — higher bar.

2. **Roll-down is part of carry, not a separate concept.** Many practitioners
   separate income and roll-down, but the paper unifies them: both are returns
   if prices don't change. The combined carry is the correct signal.

3. **Cross-asset carry diversification is powerful.** The combined Sharpe of 0.80
   vs. single-asset ~0.50 shows significant diversification from holding carry
   strategies across bonds, FX, equities, and commodities simultaneously.

4. **Crash risk is the price.** All carry strategies have negative skewness.
   Position sizing must account for tail risk — Kelly criterion or vol-targeting
   with drawdown stops. This connects to the team's earlier VRP work: carry
   premia are compensation for crash exposure.

5. **For fixed income RV:** Carry should be the first screen. Among bonds with
   similar fitting residuals (similarly cheap on the yield curve), prefer the one
   with higher carry. This aligns convergence and carry — the strongest signal.

---

## Caveats

- **Sample period bias:** Results are strongest in the pre-2008 sample. Post-GFC
  low-rate environment compressed carry premia globally.
- **Crowding:** As carry strategies became mainstream (2010s hedge fund adoption),
  the premium compressed and crash risk increased.
- **Transaction costs:** Carry signals require rebalancing; high-turnover
  implementations may not survive realistic cost estimates.
- **Regime dependence:** Bond carry is deeply negative in hiking cycles. The paper
  covers a mostly declining-rate sample — real-world carry in 2022 was a disaster.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch12 — Asset Swaps** | ASW spread = carry component of a bond position; swap spread tightness = negative carry. Koijen unifies this into a single carry framework. |
| **Ch9 — Analytic Process** | Carry is the second pillar of the Ch9 process (alongside fitting residuals). Bonds with both positive carry and cheap fitting residual are highest-conviction trades. |
| **Ch5 — Yield/Duration/Convexity** | Roll-down requires understanding how duration changes as a bond ages — convexity affects the roll-down calculation for long-dated bonds. |
| **Ch20 — Broader Perspective** | The global carry factor connects FIRV to multi-asset portfolio construction — carry in rates, FX, and credit can be combined. |

---

## Replication Notes

**Bond carry calculation:**
```python
def bond_carry(yield_tau, yield_tau_minus_1, repo_rate, dt=1/12):
    """
    yield_tau: current yield at maturity tau
    yield_tau_minus_1: yield at maturity (tau - dt) — for roll-down
    repo_rate: financing rate (SOFR or GC repo)
    dt: time step in years (default: 1 month)
    Returns annualized carry in decimal
    """
    income = yield_tau
    roll_down = yield_tau - yield_tau_minus_1  # positive if curve upward sloping
    financing = repo_rate
    return income + roll_down - financing
```

**Cross-asset carry portfolio:** Long top-tercile carry, short bottom-tercile
within each asset class. Combine across asset classes with equal vol weighting.

---

## Adjacent Papers to Read Next

- **Fama & Bliss (1987)** — forward rates predict excess bond returns; early carry evidence
- **Cochrane & Piazzesi (2005)** — single tent-shaped factor from forward rates predicts
  bond returns; closely related to carry
- **Asness, Moskowitz & Pedersen (2013)** — value and momentum everywhere; cross-asset
  evidence parallel to Koijen et al. on carry

---

*Cerebro — 2026-03-26 | FIRV study: Koijen, Moskowitz, Pedersen & Vrugt (2018)*
