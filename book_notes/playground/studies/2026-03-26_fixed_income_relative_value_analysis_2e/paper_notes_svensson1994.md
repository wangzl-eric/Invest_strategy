# Paper Notes: Estimating and Interpreting Forward Interest Rates

**Authors:** Lars E.O. Svensson
**Year:** 1994
**Source:** IMF Working Paper WP/94/114; also published as BIS Working Paper No. 22
**Scores:** Credibility: 5 | Relevance: 5 | Actionability: 5

---

## Core Claim

The Nelson-Siegel (1987) yield curve parameterization can be extended with a **second
curvature term** to fit a wider range of yield curve shapes — including double-humped
curves that Nelson-Siegel cannot capture. The **Svensson (or Nelson-Siegel-Svensson)
model** uses six parameters and is the yield curve fitting method adopted by the ECB,
Riksbank, Bundesbank, and most other central banks for official curve publication.

---

## The Model

### Nelson-Siegel Recap (3 parameters + $\lambda$)

$$y(\tau) = \beta_1 + \beta_2\frac{1-e^{-\lambda_1\tau}}{\lambda_1\tau}
+ \beta_3\left(\frac{1-e^{-\lambda_1\tau}}{\lambda_1\tau} - e^{-\lambda_1\tau}\right)$$

Three factors: level ($\beta_1$), slope ($\beta_2$), curvature ($\beta_3$).
One shape parameter: $\lambda_1$ (location of curvature hump).

### Svensson Extension (4 parameters + $\lambda_1$, $\lambda_2$)

$$y(\tau) = \beta_1 + \beta_2\frac{1-e^{-\lambda_1\tau}}{\lambda_1\tau}
+ \beta_3\left(\frac{1-e^{-\lambda_1\tau}}{\lambda_1\tau} - e^{-\lambda_1\tau}\right)
+ \beta_4\left(\frac{1-e^{-\lambda_2\tau}}{\lambda_2\tau} - e^{-\lambda_2\tau}\right)$$

The additional term ($\beta_4$, $\lambda_2$) adds a **second curvature hump** at a
different maturity location. This allows the model to fit:
- U-shaped curves (inverted with a belly)
- Curves with humps at both the short end and medium term
- Complex post-crisis curves with QE distortions at specific tenors

---

## Key Findings

### Improved Fit for Complex Curve Shapes

Svensson demonstrates on Swedish government bond data (1992–1993) that his
extension fits the observed yield curve significantly better than Nelson-Siegel
alone — particularly in:
- The short end (1–3Y): NS often poorly fits the short end when monetary policy
  is in transition
- The belly (5–7Y): double-hump shapes from two distinct demand segments
- Post-QE curves: central bank purchases at specific tenors create local distortions
  that require a second curvature parameter

### Central Bank Adoption

The Svensson model is officially used by:
- **ECB** — publishes daily AAA-rated euro area yield curve parameters
- **Riksbank** (Sweden)
- **Deutsche Bundesbank** (Germany)
- **Bank of England** (uses a variant)
- **BIS** — publishes fitted curve parameters for 13 countries

This means Svensson parameters are publicly available daily for most major
government bond markets — directly usable in RV research without requiring
full bond-by-bond pricing.

### Forward Rate Curve

The key insight from the paper's title: the Svensson model is best understood
in **forward rate** space, not yield space. The instantaneous forward rate:

$$f(\tau) = \beta_1 + \beta_2 e^{-\lambda_1\tau}
+ \beta_3 \lambda_1\tau e^{-\lambda_1\tau}
+ \beta_4 \lambda_2\tau e^{-\lambda_2\tau}$$

Forward rates are more informative than yields for identifying RV:
- A cheap bond shows as a local spike in the forward curve
- The smoothness of the forward curve is the fitting quality criterion

---

## Key Takeaways

1. **Svensson is the production standard for fitted curves.** Use it (not NS) when
   fitting real government bond curves — ECB data is downloadable and provides a
   free daily benchmark to compare your fitted curve against.

2. **Six parameters, two shape parameters.** Estimation requires nonlinear
   optimization (NLS). The extra $\lambda_2$ makes the optimization non-convex —
   good starting values (e.g. from NS fit) are essential to avoid local minima.

3. **Forward rates are the cleanest RV diagnostic.** Plot the fitted forward curve
   and look for kinks or bumps — these indicate poorly-fitted bonds (potential
   RV candidates) or model misspecification.

4. **BIS parameter data is a free daily signal.** Download Svensson parameters
   from the BIS website for USD, EUR, GBP, JPY, CAD, CHF, AUD. Reconstruct the
   fitted yield at any maturity instantly — no bond data required.

5. **Svensson forward curve richness/cheapness is the entry point for Ch8.**
   The analytic process in Ch9 uses the forward curve residuals from the fitted
   Svensson curve as the primary RV signal for individual bonds.

---

## Caveats

- **Identification issues:** $\lambda_1$ and $\lambda_2$ can be hard to distinguish
  empirically when data is sparse at certain maturities. Regularization or
  Bayesian priors help.
- **Overfitting risk:** With 6 parameters, Svensson can fit idiosyncratic bonds
  that should be treated as outliers. Always check smoothness of the forward curve.
- **Not no-arbitrage:** Like NS, Svensson is purely a fitting exercise — it does
  not impose no-arbitrage across maturities. The AFNS model (Christensen et al.
  2011) adds this constraint at the cost of some fit quality.

---

## Replication Notes

**BIS data:** Download from bis.org/statistics/ltrates.htm — daily Svensson
parameters for 13 countries including US, Germany, UK, Japan.

```python
import numpy as np

def svensson_yield(tau, b1, b2, b3, b4, l1, l2):
    """Svensson yield for maturity tau (years)."""
    e1 = np.exp(-l1 * tau)
    e2 = np.exp(-l2 * tau)
    L = b1
    S = b2 * (1 - e1) / (l1 * tau)
    C1 = b3 * ((1 - e1) / (l1 * tau) - e1)
    C2 = b4 * ((1 - e2) / (l2 * tau) - e2)
    return L + S + C1 + C2

def svensson_forward(tau, b1, b2, b3, b4, l1, l2):
    """Instantaneous forward rate at maturity tau."""
    e1 = np.exp(-l1 * tau)
    e2 = np.exp(-l2 * tau)
    return (b1 + b2 * e1 + b3 * l1 * tau * e1 + b4 * l2 * tau * e2)
```

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch8 — Fitted Bond Curves** | Svensson is the primary fitted curve model; the book's discount factor optimization is calibrated against the Svensson forward curve |
| **Ch9 — Analytic Process** | Forward curve residuals from the Svensson fit are the RV signal for individual government bond selection |
| **Ch3 — PCA** | The Svensson factors (level, slope, 2× curvature) approximate the PCA factors from L&S — both decompose the curve into the same shape components |

---

## Adjacent Papers to Read Next

- **Nelson & Siegel (1987)** — the simpler predecessor
- **Diebold & Li (2006)** — dynamic version of NS; DNS applies analogously to Svensson
- **Christensen, Diebold & Rudebusch (2011)** — AFNS: no-arbitrage version of NS/Svensson

---

*Cerebro — 2026-03-26 | FIRV study: Svensson (1994)*
