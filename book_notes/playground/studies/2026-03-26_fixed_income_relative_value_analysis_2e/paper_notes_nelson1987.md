# Paper Notes: Parsimonious Modeling of Yield Curves

**Authors:** Charles R. Nelson, Andrew F. Siegel
**Year:** 1987
**Journal:** Journal of Business, Vol. 60, No. 4, pp. 473–489
**Scores:** Credibility: 5 | Relevance: 5 | Actionability: 5

---

## Core Claim

Yield curves can be represented with just **four parameters** using a functional
form derived from the solution to a second-order differential equation for forward
rates. The model is **parsimonious** (avoids overfitting), **flexible** (fits all
commonly observed shapes), and **interpretable** (each parameter has an economic
meaning). It became the standard fitted curve model for central banks and
practitioners globally.

---

## The Nelson-Siegel Model

### Forward Rate Representation

The instantaneous forward rate at maturity $\tau$:

$$f(\tau) = \beta_1 + \beta_2 \exp\left(-\frac{\tau}{\lambda}\right) + \beta_3 \frac{\tau}{\lambda} \exp\left(-\frac{\tau}{\lambda}\right)$$

where:
- $\beta_1$ = long-run level (as $\tau \to \infty$, $f(\tau) \to \beta_1$)
- $\beta_2$ = short-rate deviation from long-run (slope component)
- $\beta_3$ = medium-term hump/trough (curvature component)
- $\lambda$ = decay parameter controlling where the hump peaks

### Yield Representation

The zero-coupon yield at maturity $\tau$ is the average of forward rates:

$$y(\tau) = \beta_1 + \beta_2 \cdot \frac{1 - e^{-\tau/\lambda}}{\tau/\lambda} + \beta_3 \left[\frac{1 - e^{-\tau/\lambda}}{\tau/\lambda} - e^{-\tau/\lambda}\right]$$

### Loading Structure

| Parameter | Loading $L_i(\tau)$ | Behavior | Interpretation |
|-----------|-------------------|----------|----------------|
| $\beta_1$ | $1$ | Constant across all maturities | **Level** — parallel shift |
| $\beta_2$ | $(1-e^{-\tau/\lambda})/(\tau/\lambda)$ | Starts at 1, decays monotonically to 0 | **Slope** — short vs. long end |
| $\beta_3$ | $(1-e^{-\tau/\lambda})/(\tau/\lambda) - e^{-\tau/\lambda}$ | Starts at 0, humps, returns to 0 | **Curvature** — medium-term hump |


---

## Curve Shapes the Model Can Fit

| Shape | Conditions | Example |
|-------|-----------|--------|
| **Monotone increasing** | $\beta_2 < 0$, $\beta_3$ small | Normal steep curve |
| **Monotone decreasing** | $\beta_2 > 0$, $\beta_3$ small | Inverted curve (hiking cycle) |
| **Humped** | $\beta_3 > 0$ | Classic bell — peak at 5–7Y |
| **S-shaped** | $\beta_3 < 0$ | Inverted hump — trough in medium term |
| **Flat** | $\beta_2 \approx 0$, $\beta_3 \approx 0$ | Late-cycle plateaued curve |

All five common shapes are achievable with 3 free parameters (fixing $\lambda$).
This is why Nelson-Siegel dominated alternative approaches like cubic splines:
it doesn't overfit by passing through every data point; it fits the
underlying shape with interpretable parameters.

---

## Estimation

### Two-Step Procedure

1. **Fix $\lambda$** (or grid-search to minimize RMSE). Nelson-Siegel found
   $\lambda \approx 30$ months optimal for US data. Diebold-Li (2006) fixed
   $\lambda = 0.0609$ (monthly) to match the peak of the $\beta_3$ loading at ~30M.

2. **OLS regression** of observed yields on the three loadings:

$$y(\tau_i) = \beta_1 L_1(\tau_i) + \beta_2 L_2(\tau_i) + \beta_3 L_3(\tau_i) + \varepsilon_i$$

For a given $\lambda$, the loadings $L_1, L_2, L_3$ are fixed numbers for each
maturity $\tau_i$. OLS is then a simple 3-parameter linear regression.
Residue $\varepsilon_i$ = fitting error for bond $i$ — the RV signal.

### Python Implementation

```python
import numpy as np
from scipy.optimize import minimize_scalar
from sklearn.linear_model import LinearRegression

def ns_loadings(tau, lam):
    """Nelson-Siegel factor loadings for maturity tau (years) and decay lam."""
    x = lam * tau
    L1 = np.ones_like(tau)
    L2 = (1 - np.exp(-x)) / x
    L3 = L2 - np.exp(-x)
    return np.column_stack([L1, L2, L3])

def fit_ns(maturities, yields, lam=0.0609):
    """Fit Nelson-Siegel to observed (maturity, yield) pairs.
    Returns betas and fitted yields."""
    X = ns_loadings(np.array(maturities), lam)
    reg = LinearRegression(fit_intercept=False).fit(X, yields)
    beta1, beta2, beta3 = reg.coef_
    fitted = reg.predict(X)
    residuals = yields - fitted
    return dict(beta1=beta1, beta2=beta2, beta3=beta3,
                lam=lam, fitted=fitted, residuals=residuals)

# Example: fit to on-the-run Treasury yields
maturities = [0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]  # years
yields = [5.30, 5.28, 5.10, 4.80, 4.60, 4.45, 4.42, 4.40, 4.65, 4.50]  # percent
result = fit_ns(maturities, yields)
print(f"Level={result['beta1']:.2f}, Slope={result['beta2']:.2f}, Curvature={result['beta3']:.2f}")
print(f"Fitting residuals (bps): {result['residuals'] * 100}")
```

---

## Key Findings from the Paper

1. **Four parameters suffice.** NS fits US Treasury curves (1981–1983 sample)
   with RMSE of ~10bps — competitive with cubic splines using far fewer parameters.

2. **Parameters are stable over time.** Unlike spline knot coefficients, NS
   parameters have low serial correlation and interpretable ranges.

3. **$\beta_1$ ≈ long-run yield expectation.** In their sample, $\beta_1$ tracked
   long-run inflation expectations closely — an early empirical validation
   of the macro interpretation formalized by Diebold-Li (2006).

4. **The model cannot fit all shapes perfectly.** The single $\lambda$ parameter
   limits flexibility — Svensson (1994) adds $\beta_4$ and $\lambda_2$ to handle
   double humps. Central banks that need tighter fits use Svensson.

---

## Key Takeaways

1. **NS residuals are the RV signal for Ch8.** The fitting residual $\varepsilon_i$
   for each bond is the core output of the Ch8 process. Bonds with
   $\varepsilon > 0$ (yield above fitted curve) are cheap candidates for longs;
   $\varepsilon < 0$ bonds are rich candidates for shorts.

2. **$\lambda$ is the most important hyperparameter.** Changing $\lambda$ shifts
   where the curvature factor peaks — a $\lambda$ tuned to the short end
   gives different residuals than one tuned to the belly. Fix it or
   cross-validate; don't refit $\lambda$ each day (instability).

3. **NS is the benchmark; Svensson is the upgrade.** Use NS as the starting
   model. If fitting errors at the short or medium end are systematically
   large, switch to Svensson.

4. **The three factors map directly to PCA factors.** Litterman-Scheinkman
   (1991) showed PCA gives level/slope/curvature empirically; NS parameterizes
   the same structure theoretically. The two frameworks are complementary:
   PCA describes the covariance structure of yield changes; NS describes
   the cross-sectional shape of yield levels.

5. **Directly implementable in 20 lines of Python.** The OLS estimation
   (for fixed $\lambda$) requires only `numpy` and `sklearn`. BIS and Fed
   publish daily NS/Svensson parameters for major markets.

---

## Caveats

- **Cannot fit humped AND inverted shapes simultaneously** with one $\lambda$.
  Svensson or cubic splines needed for complex shapes.
- **OLS ignores bond-level liquidity and maturity gaps.** In practice,
  weight observations by DV01 or bid-ask spread to avoid off-the-run outliers
  distorting the fit.
- **Static model — no dynamics.** NS describes yield levels at a single date.
  Diebold-Li (2006) extends it to a time-series model for forecasting.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch8 — Fitted Bond Curves** | NS is the primary model; Ch8 estimates NS on sovereign curves and uses residuals as bond-level RV signals |
| **Ch3 — PCA** | NS $\beta_1/\beta_2/\beta_3$ are the theoretical counterpart of the level/slope/curvature PCA factors |
| **Ch9 — Analytic Process** | Step 1 of Ch9 is computing the NS fit; residuals feed into trade selection |
| **Ch17 — Global RV** | NS is applied within each sovereign market; cross-market comparison uses NS residuals + XCCY basis |

---

## Adjacent Papers to Read Next

- **Svensson (1994)** — already read; adds $\beta_4$/$\lambda_2$ for double-hump fits
- **Diebold & Li (2006)** — already read; adds AR(1) dynamics to NS factors
- **Gürkaynak, Sack & Wright (2007)** — Fed's published NS/Svensson parameters;
  daily data going back to 1961 available from FRED

---

*Cerebro — 2026-03-26 | FIRV study: Nelson & Siegel (1987)*