# Paper Notes: Estimation and Hypothesis Testing of Cointegration Vectors in Gaussian Vector Autoregressive Models

**Authors:** Søren Johansen
**Year:** 1991
**Journal:** Econometrica, Vol. 59, No. 6, pp. 1551–1580
**Scores:** Credibility: 5 | Relevance: 5 | Actionability: 4

---

## Core Claim

When multiple non-stationary (I(1)) time series share a common stochastic
trend, they are **cointegrated** — meaning certain linear combinations of
them are stationary (I(0)). Johansen derives the **maximum likelihood
estimator** for cointegrating vectors in a **Vector Error Correction Model
(VECM)**, and provides likelihood ratio tests — the **trace test** and
**maximum eigenvalue test** — for determining the **cointegration rank**
(number of independent cointegrating relationships). This is the canonical
econometric framework for multi-asset mean reversion and the backbone of
the multivariate OU process in FIRV Ch4.

---

## 1. Cointegration: The Concept

### Non-Stationarity and the Problem

Yield spreads between bonds, sovereign markets, and funding rates are
non-stationary individually (unit root processes) but often mean-revert
**relative to each other**. Standard OLS regression on non-stationary
series produces **spurious regressions** — high $R^2$ with no economic
meaning.

Cointegration formalizes the idea of a long-run equilibrium relationship:

**Definition:** $n$ I(1) series $y_t = (y_{1t}, ..., y_{nt})'$ are
cointegrated of rank $r$ if there exist $r$ linearly independent vectors
$\beta_1, ..., \beta_r$ such that $\beta_i' y_t$ is I(0) for each $i$.

The matrix $\beta = [\beta_1, ..., \beta_r]$ contains the **cointegrating
vectors** — the long-run equilibrium relationships.

### Fixed Income Examples

| Series | Cointegrating Relationship | Spread Name |
|--------|---------------------------|-------------|
| 10Y UST, 2Y UST | $y_{10} - y_2$ | 2s10s spread |
| 10Y Bund, 10Y OAT | $y_{Bund} - y_{OAT}$ | Bund-OAT spread |
| SOFR, EFFR | $r_{SOFR} - r_{EFFR}$ | SOFR-EFFR basis |
| 5Y5Y EUR, 5Y5Y GBP | $f_{EUR} - f_{GBP}$ | Cross-market forward spread |

---

## 2. The VECM Representation

### From VAR to VECM

A VAR(p) in levels for I(1) series can be re-written as a VECM:

$$\Delta y_t = \Pi y_{t-1} + \sum_{i=1}^{p-1} \Gamma_i \Delta y_{t-i} + \mu + \varepsilon_t$$

where:
- $\Delta y_t$ = first differences (stationary)
- $\Pi = \alpha \beta'$ = the **long-run impact matrix**
  - $\beta$ = cointegrating vectors (long-run equilibrium relationships)
  - $\alpha$ = adjustment speed matrix (how fast each series corrects toward equilibrium)
- $\Gamma_i$ = short-run dynamics
- $\varepsilon_t \sim N(0, \Omega)$

### The Rank of $\Pi$

| Rank of $\Pi$ | Interpretation |
|--------------|----------------|
| $r = 0$ | No cointegration — all series are pure random walks, no equilibrium |
| $0 < r < n$ | $r$ cointegrating relationships — partial cointegration, VECM applies |
| $r = n$ | Full rank — all series are stationary (contradicts I(1) assumption) |

For fixed income spreads, we typically expect $r = 1$ to $r = n-1$.

---

## 3. Johansen's MLE and Tests

### Maximum Likelihood Estimation

Johansen derives the MLE for $\alpha$, $\beta$, and $\Gamma_i$ by solving a
**reduced rank regression** problem. The estimator reduces to a generalized
eigenvalue problem:

$$|\lambda S_{11} - S_{10} S_{00}^{-1} S_{01}| = 0$$

where $S_{ij}$ are cross-product matrices of residuals from auxiliary
regressions. The eigenvalues $\hat{\lambda}_1 \geq \hat{\lambda}_2 \geq ... \geq \hat{\lambda}_n$
and their associated eigenvectors give the cointegrating vectors $\hat{\beta}$.

The largest eigenvalues correspond to the strongest cointegrating relationships.

### Two Likelihood Ratio Tests for Rank

**Trace test** — tests $H_0: r \leq r_0$ vs $H_1: r > r_0$:

$$\lambda_{\text{trace}}(r_0) = -T \sum_{i=r_0+1}^{n} \ln(1 - \hat{\lambda}_i)$$

**Maximum eigenvalue test** — tests $H_0: r = r_0$ vs $H_1: r = r_0 + 1$:

$$\lambda_{\max}(r_0) = -T \ln(1 - \hat{\lambda}_{r_0+1})$$

Critical values are non-standard (not chi-squared) — depend on $n - r$ and
the deterministic specification (constant, trend). Johansen (1991) provides
tabulated critical values; `statsmodels` implements them.

### Python Implementation

```python
import pandas as pd
import numpy as np
from statsmodels.tsa.vector_ar.vecm import coint_johansen, VECM

def johansen_rank_test(series_df, det_order=0, k_ar_diff=1):
    """
    series_df: DataFrame of I(1) time series (columns = series)
    det_order: -1 (no constant), 0 (constant in CE), 1 (constant + trend)
    k_ar_diff: number of lagged differences in VECM
    Returns: cointegration rank summary
    """
    result = coint_johansen(series_df, det_order=det_order, k_ar_diff=k_ar_diff)
    print("Eigenvalues:", result.eig)
    print("Trace stats:", result.lr1)
    print("Trace critical values (90/95/99%):", result.cvt)
    print("Max-eig stats:", result.lr2)
    print("Max-eig critical values:", result.cvm)
    # Cointegrating vectors (columns)
    beta_hat = result.evec
    return result, beta_hat

# Example: 2s5s10s Treasury yields
# yields_df = pd.DataFrame({'y2': ..., 'y5': ..., 'y10': ...})
# result, beta = johansen_rank_test(yields_df, det_order=0, k_ar_diff=2)
```

---

## 4. VECM as Multivariate OU Process

### The Connection to Ch4 (Multivariate Mean Reversion)

The VECM error correction term $\alpha \beta' y_{t-1}$ is the discrete-time
counterpart of the continuous-time multivariate OU process in Ch4:

| VECM | Multivariate OU |
|------|-----------------|
| $\beta' y_t$ = cointegrating spread | $z_t = \beta' y_t$ = stationary spread |
| $\alpha$ = adjustment speed matrix | $K$ = mean reversion matrix |
| $-\alpha \beta' y_{t-1}$ = error correction pull | $-K z_t dt$ = OU drift |
| Rank $r$ = number of stable spreads | $r$ independent mean-reverting combinations |

**Key insight:** If the Johansen test finds rank $r$, there are exactly $r$
independent mean-reverting spreads that can be traded. The cointegrating
vectors $\beta$ give the hedge ratios for constructing those spreads.

### Estimation Flow for Fixed Income RV

1. **Unit root test** (ADF or PP) — confirm each yield series is I(1)
2. **Johansen rank test** — determine $r$ (number of cointegrating vectors)
3. **Estimate VECM** — get $\hat{\beta}$ (hedge ratios) and $\hat{\alpha}$ (speeds)
4. **Construct spreads** $z_t = \hat{\beta}' y_t$ — these are the stationary RV signals
5. **Fit OU to each spread** — calibrate half-life, mean, vol for trade sizing
6. **Trade when $|z_t - \bar{z}| > k\sigma$** — z-score entry/exit rules

---

## 5. Fixed Income RV Applications

### 2s5s10s Butterfly

For three yield series $(y_2, y_5, y_{10})$, if rank = 2, there are two
cointegrating vectors. The first typically approximates the slope ($y_{10} - y_2$)
and the second the curvature ($2y_5 - y_2 - y_{10}$) — the butterfly spread.

Johansen MLE gives the **optimal linear combination** that maximizes the
speed of mean reversion — potentially better than the simple butterfly.

### Cross-Market Cointegration

For multi-currency RV (Ch16–17), apply Johansen to USD-equivalent yields:
- $(y^{\text{UST}}_{10}, y^{\text{Bund,USD}}_{10}, y^{\text{Gilt,USD}}_{10})$
- If rank = 2, there are two stable cross-market spread combinations
- $\hat{\beta}$ gives the cross-market hedge ratios that are historically stable

### SOFR vs EFFR Basis

SOFR and EFFR are both near the policy rate — cointegrated by construction.
VECM rank = 1, single cointegrating vector $\approx (1, -1)$. The VECM
adjustment speeds tell you which rate adjusts to the other faster.

---

## 6. Key Takeaways

1. **Johansen is the rigorous foundation for Ch4's multivariate OU.**
   Before trading any multi-leg fixed income spread, test for cointegration.
   If the Johansen test rejects rank $\geq 1$, the spread is not mean-reverting
   in-sample — do not trade it as a mean reversion strategy.

2. **Cointegrating vectors give the hedge ratios.** Instead of using DV01
   or duration weighting by hand, let Johansen estimate the linear combination
   that produces the most stationary spread. This is statistically optimal.

3. **Rank determines the number of independent trades.** For $n$ yield series
   with rank $r$, there are $r$ independent mean-reverting combinations and
   $n - r$ unit root components (common trends). You can only trade the $r$
   cointegrating directions with mean-reversion logic.

4. **Structural breaks destroy cointegration.** Regime changes (Fed pivot,
   QE announcement, regulatory shift) can break cointegrating relationships.
   Re-test rank periodically (quarterly). Use rolling VECM estimation to
   detect instability.

5. **Half-life from VECM eigenvalues.** The eigenvalues of $\alpha \beta'$
   (the companion matrix) determine the speed of adjustment. Half-life
   $\approx \ln(2) / |\lambda_{\min}|$ where $\lambda_{\min}$ is the smallest
   eigenvalue of the adjustment matrix.

---

## Caveats

- **Power of Johansen tests is low in short samples.** With fewer than 100
  observations, the trace/max-eig tests are unreliable. Need 5–10 years of
  weekly data minimum for stable rank estimation.
- **Lag selection matters.** Use AIC or BIC to select $p$; mis-specified lags
  produce incorrect rank estimates.
- **Critical values assume no structural breaks.** Gregory-Hansen (1996)
  extends Johansen to allow for one structural break in the cointegrating
  vector — important for multi-decade fixed income data.
- **Near-cointegration is common.** Many spreads appear cointegrated in short
  windows but are not globally stationary. Use out-of-sample validation.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch4 — Multivariate Mean Reversion** | VECM is the econometric implementation of Ch4's multivariate OU framework; Johansen gives the rank and vectors |
| **Ch2 — Mean Reversion** | Johansen generalizes the univariate OU (Ch2) to multiple series; the bivariate case reduces to a single spread |
| **Ch9 — Analytic Process** | Cointegrating vectors provide statistically optimal hedge ratios for factor-neutral trades |
| **Ch16/17 — Global RV** | Cross-market cointegration tests validate whether sovereign spread pairs are stable trading relationships |

---

## Notebook Connection

This paper is the theoretical backbone for
`06_multivariate_mean_reversion.ipynb` in the FIRV study folder.
The notebook should implement:
1. ADF unit root tests on individual yield series
2. Johansen rank test on 2s5s10s Treasury yields
3. VECM estimation and spread extraction
4. OU calibration on the cointegrating spread
5. Z-score signal and hypothetical trade history

---

## Adjacent Papers to Read Next

- **Engle & Granger (1987)** — original two-step cointegration test; simpler
  than Johansen but less powerful for $n > 2$ series
- **Gregory & Hansen (1996)** — cointegration with structural breaks
- **Avellaneda & Lee (2010)** — applies cointegration/PCA to equity pairs;
  methodology transfers directly to bond pairs

---

*Cerebro — 2026-03-26 | FIRV study: Johansen (1991)*