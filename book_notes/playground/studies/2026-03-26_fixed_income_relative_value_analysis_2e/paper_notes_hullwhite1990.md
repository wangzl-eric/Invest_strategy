# Paper Notes: Pricing Interest Rate Derivative Securities

**Authors:** John C. Hull, Alan White
**Year:** 1990
**Journal:** Review of Financial Studies, Vol. 3, No. 4, pp. 573–592
**Scores:** Credibility: 5 | Relevance: 5 | Actionability: 4

---

## Core Claim

Vasicek and CIR are theoretically elegant but have a fatal practical defect:
they **cannot be calibrated to fit the observed yield curve exactly**. Any
pricing done with a miscalibrated model produces model-implied mispricings
that are actually model errors, not market dislocations. Hull-White extend
Vasicek and CIR to **time-dependent parameters** that force the model to
match the observed initial yield curve exactly — making them usable for
relative value and derivatives pricing without systematic curve misfit.

The Hull-White model (also called the **extended Vasicek** model) became
the industry standard for interest rate derivatives pricing through the 1990s
and 2000s, and remains the benchmark no-arb model for yield curve fitting.

---

## 1. The Problem with Vasicek and CIR

### Vasicek's Constant Parameters

Vasicek (1977) specifies:
$$dr_t = \kappa(\theta - r_t)dt + \sigma dW_t$$

With constant $\kappa$, $\theta$, $\sigma$, the model implies a specific
yield curve shape determined entirely by these three parameters. The
observed yield curve will generically **not match** this shape.

**Consequence for RV:** If you fit Vasicek to the observed curve by
minimizing RMSE, the resulting fitting residuals conflate genuine
bond-level richness/cheapness with systematic model misfit. You cannot
distinguish "this bond is cheap" from "this model is wrong."

### The Hull-White Solution

Replace the constant long-run mean $\theta$ with a **time-varying function
$\theta(t)$** chosen to match the observed forward curve exactly:

$$dr_t = [\theta(t) - \kappa r_t]dt + \sigma dW_t$$

where $\theta(t)$ is determined by:
$$\theta(t) = f^M(0,t) + \kappa f^M(0,t) \cdot t + \frac{\sigma^2}{2\kappa}(1 - e^{-2\kappa t})$$

and $f^M(0,t)$ = observed instantaneous forward rate at time $t$.

This makes the model **exactly consistent** with the observed forward curve
by construction, while retaining the mean-reversion and lognormal/normal
volatility structure of Vasicek.

---

## 2. Two Hull-White Variants

### Hull-White Model 1 (Extended Vasicek)

$$dr_t = [\theta(t) - \kappa r_t]dt + \sigma dW_t$$

- **Normal (Gaussian) short rate:** $r_t$ can go negative
- **Analytic bond prices:** $P(t,T) = A(t,T)e^{-B(t,T)r_t}$ where $A$, $B$
  are functions of $\kappa$, $\sigma$, and the initial forward curve
- **Analytic swaption/cap prices:** closed-form via normal distribution
- **Two free parameters:** $\kappa$ (mean reversion speed) and $\sigma$ (vol)
  calibrated to swaption prices; $\theta(t)$ determined by the yield curve

### Hull-White Model 2 (Extended CIR)

$$dr_t = [\theta(t) - \kappa r_t]dt + \sigma\sqrt{r_t} dW_t$$

- **Lognormal short rate:** $r_t \geq 0$ always (Feller condition permitting)
- **No closed-form bond prices** under time-varying $\theta(t)$ — requires
  numerical methods (trinomial tree)
- Less widely used in practice because of computational cost

**Practitioner consensus:** Hull-White 1 (extended Vasicek) is the standard.
Allows negative rates (a feature post-2014 in EUR/JPY markets) and has
closed-form solutions for all standard derivatives.

---

## 3. The Trinomial Tree

The paper's second major contribution is a **trinomial tree** implementation
that discretizes the Hull-White process for pricing path-dependent derivatives
(callable bonds, mortgage-backed securities, Bermudan swaptions):

- At each node, the short rate can move up, stay flat, or move down
- Branch probabilities and step sizes are chosen to match the HW drift and vol
- The tree is built to **exactly reprice** the initial yield curve at every node
- Callable bond price = trinomial tree price with early exercise at each node

```python
# Hull-White bond price formula (extended Vasicek)
import numpy as np

def hw_bond_price(t, T, r_t, kappa, sigma, fwd_curve_fn):
    """
    Analytic zero-coupon bond price under Hull-White extended Vasicek.
    t: current time, T: maturity, r_t: current short rate
    kappa: mean reversion speed, sigma: short rate vol
    fwd_curve_fn: callable f(tau) -> instantaneous forward rate
    """
    tau = T - t
    B = (1 - np.exp(-kappa * tau)) / kappa
    # A(t,T) via integral of forward curve and variance terms
    # (simplified; full formula requires integral of theta(s))
    var_term = (sigma**2 / (2 * kappa**2)) * (
        tau + 2/kappa * np.exp(-kappa*tau)
        - 1/(2*kappa) * np.exp(-2*kappa*tau) - 3/(2*kappa)
    )
    # ln A = integral of f^M - 0.5 * sigma^2 * B^2 * ... (omitted for brevity)
    # In practice: use QuantLib or a pre-built calibration library
    return np.exp(-B * r_t + var_term)  # approximate; full formula is longer
```

---

## 4. Calibration to Swaption Prices

### Two-Step Calibration

1. **Step 1 — Yield curve fit:** Set $\theta(t)$ analytically from the
   observed instantaneous forward curve. This is not a free parameter —
   it is determined by the data. The model now reprices all zero-coupon
   bonds exactly.

2. **Step 2 — Volatility calibration:** Fit $\kappa$ and $\sigma$ to
   at-the-money swaption prices (or cap prices). This determines the
   shape and level of the vol surface.

**Practical note:** $\kappa$ controls the decay of vol across maturities
(high $\kappa$ = vol decays fast; short-expiry swaptions dominate).
$\sigma$ sets the overall vol level. In practice, $\kappa$ is often
fixed at 0.05–0.10 and $\sigma$ is fit to the vol surface.

### Why This Matters for RV

- **No-arb fitting:** After HW calibration, any bond residual is a genuine
  market pricing anomaly, not a model artifact. This is the key property
  that makes the model usable for RV.
- **Consistent option pricing:** Callable bond spreads, MBS OAS, and
  swaption PnL can all be computed consistently within the same model.
- **Scenario analysis:** Simulate rate paths from HW to stress-test RV
  trade P&L under different yield curve evolution scenarios.

---

## 5. HW vs. Nelson-Siegel for RV Work

| Dimension | Nelson-Siegel | Hull-White |
|-----------|--------------|------------|
| **Purpose** | Cross-sectional curve fitting | No-arb dynamic model |
| **Fitting** | OLS on yields (4 params) | Analytic forward curve inversion + 2 vol params |
| **No-arbitrage** | Not imposed | Exactly imposed |
| **Dynamics** | Static (per-date fit) | Explicit rate dynamics under P and Q |
| **Option pricing** | Not applicable | Closed-form caps/floors/swaptions |
| **RV residuals** | Direct: $y_i - \hat{y}_i$ | Via OAS or model-implied spreads |
| **Complexity** | Very low (sklearn) | Moderate (QuantLib or custom) |

**For FIRV Ch8 (fitted curves):** NS is the right tool — simple, transparent,
and produces interpretable residuals. HW is the right tool for Ch6 (yield
curve models for derivatives pricing) and for delivery option valuation (Ch7).

---

## 6. Key Takeaways

1. **HW solves the calibration problem that Vasicek cannot.** For any RV
   framework that uses a dynamic term structure model, HW is the minimum
   viable model — it at least fits the starting curve by construction.

2. **$\theta(t)$ is not a parameter — it is implied by the market.**
   Only $\kappa$ and $\sigma$ require calibration to volatility instruments.
   This makes HW parsimonious despite its theoretical generality.

3. **Trinomial trees extend HW to path-dependent products.** Callable
   bonds, Bermudan swaptions, and CMO tranches all require the tree.
   This is where HW's practical dominance over closed-form models comes from.

4. **For ZLB/negative rates:** HW Model 1 (Gaussian) allows negative rates
   naturally — no shadow rate extension needed. This is why it remained
   useful in Europe during the ECB negative rate era (2014–2022).

5. **QuantLib implements HW fully.** The Python QuantLib wrapper provides
   `HullWhite` process, `TreeSwaptionEngine`, and `BlackCalibrationHelper`
   for full calibration pipelines without hand-coding the Riccati ODEs.

---

## Caveats

- **Single-factor model.** HW has only one source of randomness — the short
  rate. It cannot reproduce realistic correlation structures between different
  maturities (all yields are perfectly correlated conditionally on $r_t$).
  For multi-factor needs: G2++ (two-factor HW) or LMM.
- **Gaussian rates can go negative.** In pre-2014 high-rate environments,
  this was a theoretical concern. Post-2014 it became a feature.
- **Vol smile not captured.** HW produces a flat vol surface (no skew/smile).
  For swaption RV involving smile, SABR or LMM-SABR needed.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch6 — Yield Curve Models** | HW is the primary no-arb model discussed; extended Vasicek is Ch6's implementation reference |
| **Ch7 — Bond Futures** | HW trinomial tree is used to value the CTD delivery option (quality option, wildcard option) |
| **Ch8 — Fitted Bond Curves** | NS is used for static fitting; HW provides the dynamic no-arb foundation that validates NS residuals as genuine mispricings |
| **Ch2 — Mean Reversion** | HW is the no-arb extension of Vasicek's OU process; same $\kappa$ and $\sigma$ parameters |

---

## Adjacent Papers to Read Next

- **Vasicek (1977)** — already read; HW is the direct extension
- **CIR (1985)** — already read; HW also extends CIR (Model 2)
- **Black, Derman & Toy (1990)** — alternative one-factor no-arb model;
  lognormal rates (no negative rates); less analytically tractable than HW
- **Heath, Jarrow & Morton (1992)** — general no-arb framework for forward
  rate processes; HW is a special case of HJM

---

*Cerebro — 2026-03-26 | FIRV study: Hull & White (1990)*