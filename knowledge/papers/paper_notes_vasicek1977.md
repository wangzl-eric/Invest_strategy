# Paper Notes: An Equilibrium Characterization of the Term Structure

**Authors:** Oldřich Vasicek
**Year:** 1977
**Journal:** Journal of Financial Economics, Vol. 5, No. 2, pp. 177–188
**Scores:** Credibility: 5 | Relevance: 5 | Actionability: 4

---

## Core Claim

If the short-term interest rate follows a mean-reverting diffusion process (the
Ornstein-Uhlenbeck process), the entire term structure of interest rates is completely
determined by the current level of the short rate. Bond prices have closed-form analytic
expressions. This is the first tractable equilibrium model of the term structure.

---

## The Model

### Short Rate Dynamics (Physical Measure)

The short rate $r_t$ follows:

$$dr_t = \kappa(\theta - r_t)\,dt + \sigma\,dW_t$$

where:
- $\kappa > 0$ — speed of mean reversion (how fast $r$ returns to long-run mean)
- $\theta$ — long-run mean (unconditional expectation of $r$ as $t \to \infty$)
- $\sigma$ — instantaneous volatility of the short rate
- $W_t$ — standard Brownian motion

This is the **Ornstein-Uhlenbeck (OU) process**. Key properties:
- Mean-reverting: if $r > \theta$, drift is negative (pulls back down)
- Gaussian: $r_t | r_0 \sim N(\cdot)$ at all horizons
- Stationary: unconditional distribution is $N(\theta, \sigma^2 / 2\kappa)$

### Market Price of Risk

Vasicek assumes a **constant market price of risk** $\lambda$ (the Sharpe ratio of
a bond in excess of the short rate per unit of volatility). Under the risk-neutral
measure $\mathbb{Q}$, the short rate follows:

$$dr_t = \kappa(\theta^* - r_t)\,dt + \sigma\,d\tilde{W}_t$$

where $\theta^* = \theta - \lambda\sigma/\kappa$ is the risk-adjusted long-run mean.

### Bond Pricing Formula

Under the risk-neutral measure, the price of a zero-coupon bond maturing at time $T$ is:

$$P(t, T) = A(t,T)\, e^{-B(t,T)\, r_t}$$

where $\tau = T - t$ and:

$$B(t,T) = \frac{1 - e^{-\kappa\tau}}{\kappa}$$

$$\ln A(t,T) = \left(\theta^* - \frac{\sigma^2}{2\kappa^2}\right)(B(t,T) - \tau)
- \frac{\sigma^2}{4\kappa} B(t,T)^2$$

The **yield** on a zero-coupon bond is therefore affine in $r_t$:

$$y(t,T) = -\frac{\ln P(t,T)}{\tau} = \frac{-\ln A(t,T) + B(t,T)\,r_t}{\tau}$$

This is the defining property of **affine term structure models**: yields are linear
functions of the state variable(s).

---

## Key Findings

1. **Mean reversion generates an upward-sloping term structure on average.** Because
   investors require compensation for rate uncertainty over longer horizons, and because
   mean reversion reduces that uncertainty at very long horizons, the model implies a
   humped or upward-sloping yield curve under reasonable parameters.

2. **The risk premium is embedded in $\theta^*$ vs $\theta$.** The gap between the
   physical long-run mean $\theta$ and the risk-neutral mean $\theta^*$ represents the
   **term premium** — extra yield investors demand for holding long-duration bonds.

3. **$B(t,T)$ saturates as $\tau \to \infty$.** Duration sensitivity to short rate
   changes tops out at $1/\kappa$ — long bonds are not infinitely sensitive to rate
   moves. This is important for hedging very long-dated bonds.

4. **Possible negative rates.** Because $r_t$ is Gaussian, there is a non-zero
   probability of $r_t < 0$. This was considered unrealistic in 1977 but became
   empirically relevant in Europe and Japan post-2014. (The fix: CIR's sqrt-diffusion,
   or shadow rate models as in Wu-Xia 2016.)

5. **Closed-form option pricing.** Because $r_t$ is Gaussian and bond prices are
   log-normal (given $r$), caps, floors, and swaptions have analytic pricing formulae
   under Vasicek — a major practical advantage.

---

## Key Takeaways

1. **The OU process is the canonical mean reversion model.** Three parameters ($\kappa$,
   $\theta$, $\sigma$) fully characterize it. Estimating these from data is the core
   task of Ch2 of the book. The book's nonparametric drift estimation is a direct
   generalization of Vasicek's parametric assumption.

2. **Mean reversion speed $\kappa$ determines the half-life.** Half-life $= \ln(2)/\kappa$.
   For typical rate spreads (e.g. 2s10s), $\kappa$ corresponds to a half-life of
   weeks to months — fast enough to be tradeable.

3. **Affine = tractable.** The affine structure (yields linear in state) makes
   everything analytic: prices, durations, option values. The entire Ch5–Ch6 machinery
   of the book rests on affine model logic.

4. **Risk-neutral vs. physical measure.** The distinction between $\theta$ (physical)
   and $\theta^*$ (risk-neutral) is the formal basis for separating **expectations**
   from **term premia** — a decomposition the book uses throughout Ch6 and Ch9.

5. **Limitation: constant volatility.** The model assumes $\sigma$ is constant, which
   is inconsistent with observed vol clustering and smiles. This motivates the
   jump-diffusion and stochastic vol extensions mentioned in Ch6.

---

## Caveats

- **Negative rates:** Gaussian short rate allows $r_t < 0$ with positive probability.
  Not a problem for RV spread trading but breaks derivative pricing at ZLB.
- **Constant volatility:** $\sigma$ is fixed, inconsistent with vol clustering. Real
  rate volatility is regime-dependent (high in 1980–81, low in 2010–19).
- **Single factor:** One state variable cannot generate humped yield curves or
  independent slope/curvature dynamics. Multi-factor extensions (Hull-White 2F,
  G2++) are needed for more realistic curve shapes.
- **Stationary parameters:** $\kappa$, $\theta$, $\sigma$ are assumed constant.
  In practice they shift across monetary regimes.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch2 — Mean Reversion** | Direct source. The OU process is Ch2's core model. The book extends Vasicek to nonparametric drift/diffusion estimation and conditional risk-adjusted expected returns. |
| **Ch4 — Multivariate Mean Reversion** | Extends the single-factor OU to a system of correlated spreads (e.g. EUR vs GBP forward rates). The matrix $\kappa$ becomes a mean-reversion matrix. |
| **Ch6 — Yield Curve Models** | Vasicek is the simplest affine model. Ch6 discusses jump-diffusion and shadow rate extensions that address the negative-rate and vol-smile limitations. |
| **Ch9 — Analytic Process** | Ex ante risk-adjusted return $= E[\Delta P]/\sigma[\Delta P]$ is computed using Vasicek's conditional expectation and variance formulae. |
| **Ch19 — Options** | Vasicek's Gaussian short rate implies analytic cap/floor pricing (Jamshidian 1989). Ch19 builds on this for swaption Greeks. |

---

## Replication Notes

**Parameter estimation** via OLS on discretised OU:

$$r_{t+1} - r_t = a + b\,r_t + \varepsilon_t$$

where $b = -\kappa\Delta t$, $a = \kappa\theta\Delta t$, $\sigma^2 = \text{Var}(\varepsilon)/\Delta t$.

```python
import numpy as np
from scipy.stats import linregress

# r: array of short rate observations, dt: time step (e.g. 1/252)
def fit_vasicek(r, dt):
    slope, intercept, _, _, _ = linregress(r[:-1], np.diff(r))
    kappa = -slope / dt
    theta = intercept / (kappa * dt)
    sigma = np.std(np.diff(r) - intercept - slope * r[:-1]) / np.sqrt(dt)
    half_life = np.log(2) / kappa
    return dict(kappa=kappa, theta=theta, sigma=sigma, half_life_days=half_life/dt)
```

**Expected output for 2s10s Treasury spread:** half-life ~60–120 days,
$\kappa \approx 2$–$4$ (annualised), $\theta \approx$ current long-run mean of spread.

---

## Adjacent Papers to Read Next

- **Cox, Ingersoll & Ross (1985)** — fixes negative-rate problem with sqrt-diffusion
- **Hull & White (1990)** — extends Vasicek to fit the current yield curve exactly
- **Aït-Sahalia (1996)** — tests empirically whether short rates actually mean-revert
- **Wu & Xia (2016)** — shadow rate model for ZLB regimes

---

*Cerebro — 2026-03-26 | FIRV study: Vasicek (1977)*
