# Paper Notes: Forecasting the Term Structure of Government Bond Yields

**Authors:** Francis X. Diebold, Calin Li
**Year:** 2006
**Journal:** Journal of Econometrics, Vol. 130, No. 2, pp. 337–364
**Scores:** Credibility: 5 | Relevance: 5 | Actionability: 5

---

## Core Claim

The Nelson-Siegel (1987) yield curve parameterization can be reinterpreted as a
**dynamic three-factor model** in which the factors evolve over time as AR(1) processes.
This "Dynamic Nelson-Siegel" (DNS) model produces superior out-of-sample yield curve
forecasts compared to random walks, unrestricted VARs, and static PCA at 6–12 month
horizons. The three factors have natural interpretations as **level, slope, and curvature**
— bridging statistical PCA (Litterman-Scheinkman) and macroeconomic intuition.

---

## The Model

### Static Nelson-Siegel (1987)

The yield at maturity $\tau$ is:

$$y_t(\tau) = \beta_{1t} + \beta_{2t}\left(\frac{1 - e^{-\lambda\tau}}{\lambda\tau}\right)
+ \beta_{3t}\left(\frac{1 - e^{-\lambda\tau}}{\lambda\tau} - e^{-\lambda\tau}\right)$$

The three **factor loadings** are:
- $\beta_{1t}$: loading = 1 (constant across all $\tau$) → **Level**
- $\beta_{2t}$: loading starts at 1, decays to 0 as $\tau \to \infty$ → **Slope**
- $\beta_{3t}$: loading is hump-shaped, peaks at medium $\tau$, decays to 0 → **Curvature**

$\lambda$ controls where the curvature loading peaks. Diebold-Li fix $\lambda = 0.0609$
(peaking at ~30-month maturity for monthly data) and treat $\beta_{1t}, \beta_{2t},
\beta_{3t}$ as **time-varying factors**.

### Dynamic Extension

Diebold-Li model each factor as an **AR(1)**:

$$\begin{pmatrix} \beta_{1,t+1} \\ \beta_{2,t+1} \\ \beta_{3,t+1} \end{pmatrix}
= \begin{pmatrix} \mu_1 \\ \mu_2 \\ \mu_3 \end{pmatrix}
+ \begin{pmatrix} a_1 & 0 & 0 \\ 0 & a_2 & 0 \\ 0 & 0 & a_3 \end{pmatrix}
\begin{pmatrix} \beta_{1t} - \mu_1 \\ \beta_{2t} - \mu_2 \\ \beta_{3t} - \mu_3 \end{pmatrix}
+ \varepsilon_t$$

Estimation is two-step: (1) OLS cross-section to extract $\beta_t$ at each date,
(2) AR(1) time-series on each $\beta_t$ sequence to get forecasts.

---

## Key Findings

### Factor Interpretations

| Factor | NS Loading | Macro Interpretation | Empirical Behavior |
|--------|-----------|---------------------|-------------------|
| $\beta_1$ (Level) | 1 at all $\tau$ | Long-run inflation expectations | High persistence ($a_1 \approx 0.99$), near unit root |
| $\beta_2$ (Slope) | Decays from 1 to 0 | Monetary policy cycle | Mean-reverting ($a_2 \approx 0.94$); inverts in recessions |
| $\beta_3$ (Curvature) | Hump-shaped | Medium-term business cycle | Least persistent ($a_3 \approx 0.71$), fastest mean-reversion |

Note: $\beta_2$ is often measured as the negative of the conventional slope
(short minus long). An inverted curve means $\beta_2 < 0$ in their notation.

### Forecasting Results

- **Benchmark:** Random walk, unrestricted VAR(1) on yields, and forward rate regressions.
- **Finding:** DNS beats all benchmarks at **6- and 12-month horizons** for most maturities.
- DNS is competitive with the random walk at 1-month horizons (where level persistence dominates).
- The key advantage: factor parsimony prevents overfitting that plagues unrestricted VARs.

### Connection to Litterman-Scheinkman

The NS loadings produce factors with the same **shape** as PCA eigenvectors from L&S:
- NS $\beta_1$ loading (flat) ≈ PCA Factor 1 (level)
- NS $\beta_2$ loading (monotone decay) ≈ PCA Factor 2 (slope)
- NS $\beta_3$ loading (hump) ≈ PCA Factor 3 (curvature)

But NS imposes the shape analytically; PCA extracts it from data.
Advantage of NS: interpretable, fewer parameters, no rotation ambiguity.
Advantage of PCA: data-driven, no functional form assumption.

---

## Key Takeaways

1. **DNS is the practitioner's bridge between statistics and economics.** It gives the
   L&S PCA factors an economic interpretation (level = inflation, slope = monetary
   policy, curvature = medium cycle) without losing the parsimony of a 3-parameter fit.

2. **Fix $\lambda$, estimate $\beta_t$ by OLS cross-section.** At each date, regress
   observed yields on the three fixed loadings. The resulting $\hat{\beta}_t$ time
   series is the factor history. This two-step approach is simple and robust.

3. **Curvature mean-reverts fastest** ($a_3 \approx 0.71$) — most tradeable from a
   pure statistical RV perspective. Level is near-unit-root — not mean-reverting on
   short horizons. Slope is intermediate — tied to the rate cycle.

4. **Forecasting horizon matters.** DNS wins at 6–12 months because the AR(1) factor
   dynamics capture medium-run mean reversion. At 1-month horizon the random walk
   is competitive. This maps directly to Ch2's point about selecting the right
   horizon for mean reversion signals.

5. **$\lambda$ choice affects curvature peak maturity.** $\lambda = 0.0609$ puts the
   hump at ~30M for monthly data. For the book's 5Y5Y forward rate analysis, a
   different $\lambda$ may be more appropriate. This is a calibration choice.

---

## Caveats

- **Diagonal AR(1) assumption.** Diebold-Li assume independent AR(1) for each factor.
  In reality, level and slope are correlated (rate hikes flatten the curve). The
  Diebold, Rudebusch & Aruoba (2006) VAR extension relaxes this.
- **No arbitrage.** The DNS model as formulated does not impose no-arbitrage across
  maturities. The Christensen, Diebold & Rudebusch (2011) AFNS model fixes this.
- **Fixed $\lambda$.** Diebold-Li fix $\lambda$ rather than estimate it jointly.
  Estimating $\lambda$ by NLS often improves fit but introduces instability.
- **Out-of-sample regime shifts.** The 2022 hiking cycle (fastest since 1980) and
  2020 COVID shock stress-test all forecasting models. DNS would have large errors
  around regime breaks.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch3 — PCA** | DNS provides the parametric counterpart to Ch3's data-driven PCA. The book uses both: PCA for risk decomposition, NS/DNS for curve fitting and forecasting. |
| **Ch8 — Fitted Bond Curves** | The NS parameterisation is one of the primary fitted curve approaches in Ch8. DNS adds the time-series dimension — how to update the fitted curve as rates evolve. |
| **Ch9 — Analytic Process** | The three DNS factors serve as the "state" in Ch9's systematic RV process: identify cheap/rich bonds relative to the fitted DNS curve, trade the residual. |
| **Ch6 — Yield Curve Models** | DNS is a reduced-form forecasting model, not a no-arb pricing model. Ch6's affine models (Vasicek, CIR, Hull-White) are the pricing counterparts. |

---

## Replication Notes

**Data:** US Treasury par yields from Fed H.15 (2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y).
Or Gürkaynak-Sack-Wright zero-coupon yields (preferred — avoids coupon distortions).

```python
import numpy as np
from scipy.optimize import least_squares

def ns_loadings(tau, lam=0.0609):
    """Nelson-Siegel factor loadings for maturity tau (in years)."""
    l = lam * tau
    L = np.ones_like(tau)                        # level
    S = (1 - np.exp(-l)) / l                    # slope
    C = S - np.exp(-l)                           # curvature
    return np.column_stack([L, S, C])

def fit_dns(yields, maturities, lam=0.0609):
    """Two-step DNS: OLS betas at each date."""
    X = ns_loadings(np.array(maturities), lam)
    # yields: (n_dates, n_maturities)
    betas = np.linalg.lstsq(X, yields.T, rcond=None)[0].T
    return betas  # (n_dates, 3): level, slope, curvature
```

**Expected output:** $\beta_1 \approx$ long-end yield level (e.g. 4–5% in 2024),
$\beta_2 \approx$ negative of slope (negative when curve is inverted),
$\beta_3 \approx$ curvature (positive when belly is rich).

---

## Adjacent Papers to Read Next

- **Nelson & Siegel (1987)** — the static version this paper extends
- **Svensson (1994)** — adds a fourth factor for double-hump curves
- **Christensen, Diebold & Rudebusch (2011)** — AFNS: imposes no-arb on DNS
- **Diebold, Rudebusch & Aruoba (2006)** — adds macro variables (GDP, inflation,
  fed funds) to a VAR with DNS factors; bridges yield curve and macroeconomics

---

*Cerebro — 2026-03-26 | FIRV study: Diebold & Li (2006)*
