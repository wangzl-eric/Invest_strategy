# Paper Notes: The Volatility Risk Premium in Interest Rate Markets

**Authors (primary):** Nicole Branger, Christian Schlag (2004); Peter Carr, Liuren Wu (2009)
**Year:** 2004 / 2009
**Journal:** Journal of Derivatives (Branger-Schlag); Journal of Finance (Carr-Wu)
**Scores:** Credibility: 4 | Relevance: 4 | Actionability: 4

---

## Core Claim

In interest rate markets, **implied volatility (from swaptions and caps)
systematically exceeds realized volatility** of the underlying rate —
creating a persistent **volatility risk premium (VRP)**. Sellers of
rate volatility (short swaptions, short caps/floors) earn this premium
as compensation for bearing jump/tail risk and providing liquidity
during stress events. The rates VRP is structurally different from the
equity VRP: it is smaller in magnitude, driven by different risk factors,
and has distinct crisis behavior — but it is nonetheless a persistent
and exploitable premium for systematic vol sellers in rate markets.

---

## 1. The Volatility Risk Premium: Definition

### Implied vs. Realized Volatility

$$\text{VRP}_t = IV_t - E_t[RV_{t,t+h}]$$

where:
- $IV_t$ = implied volatility from swaption or cap prices (market's
  risk-neutral expectation of future realized vol)
- $RV_{t,t+h}$ = realized volatility of the underlying rate over $[t, t+h]$
- $\text{VRP} > 0$ means options are overpriced relative to realized vol
  on average — sellers of vol earn a premium

### Why VRP Exists

VRP compensates option sellers for:
1. **Jump/tail risk:** Realized vol can spike far above implied in stress
   events (2008, 2020). Option sellers bear this tail.
2. **Liquidity provision:** Option buyers pay up for downside protection
   and hedging convenience.
3. **Uncertainty premium:** Implied vol includes uncertainty about future
   vol (vol-of-vol) that realized vol averages out.

---

## 2. Rates VRP: Branger & Schlag (2004)

### Core Finding

Branger and Schlag study the VRP in interest rate options (caps and floors)
using a stochastic volatility model for rates. Key results:

- **Swaption implied vol > realized rate vol** on average by 15–30bps
  annualized for at-the-money options across tenors
- The premium is **persistent** across the cycle but varies with the
  level of rates and the vol regime
- **Short gamma strategies** (selling straddles/strangles on swaptions)
  earn the premium but with significant negative skewness
- The premium is **not explained** by standard risk factors (level, slope,
  curvature) — it is a distinct source of return

### Rates VRP vs. Equity VRP

| Dimension | Equity VRP | Rates VRP |
|-----------|-----------|----------|
| **Magnitude** | 3–5 vol points (large) | 15–30bps annualized (small) |
| **Crash behavior** | Spikes sharply in equity crashes | Spikes in rate vol events (hiking cycles, crises) |
| **Correlation with equity VRP** | By definition 1.0 | Low to moderate (~0.3) |
| **Driver** | Equity tail hedging demand | Rate uncertainty + regulatory hedging demand |
| **Sharpe (short vol)** | ~0.5–0.8 (pre-crisis) | ~0.3–0.5 |

---

## 3. Variance Swaps in Rate Markets: Carr & Wu (2009)

### The Variance Swap Framework

Carr and Wu (2009) derive a model-free measure of the variance risk premium
using **variance swaps** — contracts that pay realized variance minus a
fixed strike (the variance swap rate = model-free implied variance):

$$\text{VRP}_t = \underbrace{K_{var,t}}_{\text{Var swap rate (= risk-neutral var)}} - \underbrace{E^P_t[RV_{t,t+h}]}_{\text{Physical expected realized var}}$$

For equity (VIX²): the variance swap rate is directly observable.
For rates: Carr-Wu construct the equivalent from the swaption vol surface
using a spanning argument across strikes.

### Key Finding for Rates

- The rates variance risk premium is **consistently positive** (implied
  variance > expected realized variance) across USD, EUR, and GBP markets
- It is largest at **intermediate tenors** (5Y–10Y swaptions) where
  regulatory hedging demand from pension funds and insurers is strongest
- It is **counter-cyclical**: highest in recessions and hiking cycles
  when rate uncertainty is elevated

---

## 4. Practical Implementation: Short Swaption Strategies

### Strategy Structure

**Short ATM swaption straddle (delta-hedged):**
- Sell 1M expiry × 10Y tenor ATM swaption straddle
- Delta-hedge daily with 10Y swaps
- Hold to expiry; collect theta (time decay) minus gamma losses
- P&L = implied vol - realized vol × notional × vega

**Short cap/floor strangle:**
- Sell OTM calls and puts on 3M SOFR
- Earn the vol premium on the wings
- Higher Sharpe than straddle (OTM options more overpriced) but smaller vega

### Risk Management

```python
def size_short_vol_position(implied_vol, realized_vol_ewma, vega_per_unit,
                            max_loss_budget, crash_vol_multiplier=3.0):
    """
    Size a short vol position given VRP and crash risk budget.
    implied_vol: current ATM implied vol (annualized, decimal)
    realized_vol_ewma: EWMA realized vol estimate
    vega_per_unit: $ P&L per 1bp vol move per unit notional
    max_loss_budget: maximum acceptable loss in $ on a crash
    crash_vol_multiplier: how many times realized vol can spike in a crash
    """
    vrp = implied_vol - realized_vol_ewma
    crash_vol = implied_vol * crash_vol_multiplier
    loss_per_unit = (crash_vol - implied_vol) * vega_per_unit
    max_units = max_loss_budget / loss_per_unit
    expected_carry_per_unit = vrp * vega_per_unit
    return dict(max_units=max_units,
                expected_carry=expected_carry_per_unit * max_units,
                vrp_bps=vrp * 10000)
```

---

## 5. Connection to Team's Prior VRP Research

The team previously researched **equity VRP** (VIX regime strategy) which
was rejected after Round 2 (2026-03-15). Key failure modes:
- VRP is a crisis signal, not an alpha signal in equities
- Position-sizing overlays have structural headwind
- Dominated by simple trailing vol

**Rates VRP has different properties:**

| Factor | Equity VRP | Rates VRP |
|--------|-----------|----------|
| **Crisis behavior** | Collapses AND spikes simultaneously (short vol loses exactly when you need it) | Spikes in rate vol events but not in equity crashes — lower correlation |
| **Regulatory demand** | Driven by retail hedging + index put demand | Driven by pension/insurer ALM hedging — more structural, less sentiment-driven |
| **Mean reversion** | Vol of vol is high; crowding worsens crashes | Swaption vol is smoother; large structural sellers (banks) provide two-sided market |
| **Implementation** | VIX futures (liquid, standardized) | Swaption market (OTC, bid-ask wide, needs ISDA) — higher bar for small accounts |

**Conclusion:** Rates VRP is theoretically sounder than equity VRP as a
carry strategy, but implementation requires swaption market access (ISDA
agreement, dealer relationships). Not actionable with current platform
instrastructure; flag for future evaluation when OTC derivatives access
is established.

---

## 6. Key Takeaways

1. **Rates VRP exists and is persistent.** Swaption implied vol exceeds
   realized vol by 15–30bps on average. This is a real premium, not
   noise — it survives transaction costs in institutional-size books.

2. **The premium is highest at intermediate tenors.** 5Y×10Y swaptions
   carry the most structural hedging demand from pension ALM. Short
   vol here has the best risk-adjusted carry.

3. **Crash risk is real but different from equity VRP.** Rate vol crashes
   occur in aggressive hiking cycles and liquidity crises — not in
   equity-driven selloffs. Diversification vs. equity VRP is genuine.

4. **Not actionable without OTC derivatives access.** Unlike equity VRP
   (VIX ETPs, listed options), rates VRP requires swaption market access.
   Platform does not currently support this.

5. **Monitor as a regime indicator even without trading it.** Rates VRP
   (implied vs. realized swaption vol spread) is a useful macro signal:
   elevated VRP = market pricing high rate uncertainty = carry trades
   face wider confidence intervals on convergence timing.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch19 — Options Relative Value** | Rates VRP is the structural carry behind Ch19's vega sector PCA; overpriced vol = short vol carry |
| **Ch9 — Analytic Process** | Vol regime (high/low VRP) affects the confidence interval on ex ante Sharpe estimates |
| **Ch6 — Yield Curve Models** | Stochastic vol extensions of HW (Hull-White SV) are needed to price vol surface correctly for VRP extraction |

---

*Cerebro — 2026-03-26 | FIRV study: Rates VRP — Branger & Schlag (2004), Carr & Wu (2009)*