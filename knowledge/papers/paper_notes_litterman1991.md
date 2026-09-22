# Paper Notes: Common Factors Affecting Bond Returns

**Authors:** Robert Litterman, José Scheinkman
**Year:** 1991
**Journal:** Journal of Fixed Income, Vol. 1, No. 1
**Scores:** Credibility: 5 | Relevance: 5 | Actionability: 5

---

## Core Claim

A small number of common factors — extracted via PCA from the covariance matrix of US
Treasury returns — explain nearly all variation in bond returns across maturities.
Three factors suffice: **level, slope, and curvature**. Risk management and relative value
trading must hedge against all three, not just duration (a level-only hedge).

---

## Methodology

- **Data:** Weekly returns on US Treasury zero-coupon bonds across maturities
  (3M, 1Y, 2Y, 3Y, 5Y, 7Y, 10Y, 30Y), 1984–1988.
- **Method:** Principal Component Analysis on the return covariance matrix.
  Eigenvectors ordered by eigenvalue magnitude — largest = most variance explained.
- **Output:** Factor loadings (how each maturity loads on each factor) + variance
  explained by each factor.

---

## Key Findings

### Factor 1 — Level (~89% of variance)
- All maturities load positively and with roughly equal magnitude.
- Represents a **parallel shift** of the entire yield curve up or down.
- Interpretation: the overall rate environment (long-run inflation, central bank stance).
- Hedge: conventional duration immunization hedges this factor only.

### Factor 2 — Slope (~8% of variance)
- Short maturities load negatively; long maturities load positively (or vice versa).
- Represents a **twist** or tilt of the curve — short end moves opposite to long end.
- Interpretation: the monetary policy cycle (rate hike cycle steepens/flattens the curve).
- Hedge: requires a **DV01-neutral curve position** (e.g. 2s10s steepener).

### Factor 3 — Curvature (~3% of variance)
- Short and long maturities load one way; medium maturities load the opposite way.
- Represents a **butterfly** or bow — the belly of the curve moves relative to wings.
- Interpretation: excess demand at intermediate maturities, convexity demand.
- Hedge: requires a **butterfly position** (e.g. short 5Y, long 2Y and 10Y).

### Total variance explained: >99% with 3 factors.
Remaining factors are largely noise — adding a 4th factor adds little.

---

## Key Takeaways

1. **Duration is not enough.** A duration-hedged portfolio still has large exposure to
   slope and curvature factors. A 2s10s flattener that is DV01-neutral is exposed to
   curvature. Most practitioner hedging ignores this.

2. **PCA defines the natural trade basis.** Level trades = outright duration. Slope trades
   = curve steepeners/flatteners. Curvature trades = butterflies. These three decompose
   all yield curve P&L — any bond position is a combination of all three exposures.

3. **Factor stability.** The level/slope/curvature structure is remarkably stable over time
   and across countries (US, UK, Germany, Japan all show the same three-factor structure).
   This makes PCA a durable framework, not a data-mining artifact.

4. **Risk budgeting.** Knowing factor loadings lets you decompose portfolio risk into
   contributions from each factor — essential for relative value books where you want to
   be slope-long without level or curvature exposure.

5. **Residuals are the RV signal.** Once you project bond returns onto the three factors,
   the residual captures idiosyncratic richness/cheapness relative to the fitted curve.
   This is the foundation of the "fitting residuals" approach in Ch8–Ch9 of the book.

---

## Caveats

- **Sample period is short** (1984–1988, ~5 years). Factor loadings may shift across
  different rate regimes. Post-2008 ZLB period and 2022 hiking cycle both stress-test
  the stability of the three-factor structure.
- **Returns, not yields.** The PCA is on return covariances, not yield levels. Factor
  loadings in yield-space (Diebold-Li) differ slightly from return-space (L&S).
- **No economic interpretation forced.** The factors are statistical — the macro
  interpretation (level = inflation, slope = monetary policy) is layered on afterward
  by Diebold-Li (2006), not present in this paper.
- **US Treasuries only.** Cross-market PCA (EUR vs. USD) requires multivariate
  extension — covered in Ch4 of the book (Multivariate Mean Reversion).

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch3 — PCA** | This paper IS Ch3. The book's entire PCA framework is an extended practitioner treatment of L&S. Read this paper to understand why Ch3 makes the choices it does. |
| **Ch9 — Analytic Process for Govt Bonds** | The fitted-curve residuals approach in Ch9 uses PCA factor neutrality to construct RV trades. L&S provides the theoretical basis for what "factor-neutral" means. |
| **Ch4 — Multivariate Mean Reversion** | Cross-market PCA (e.g. EUR 5Y5Y vs GBP 5Y5Y) extends L&S to multiple yield curves simultaneously. Ch4 is the multivariate analog of Ch3. |
| **Ch19 — Options / Vega Sector PCA** | The book applies PCA to implied volatility surfaces (vega sector PCA) — the same eigenvector logic applied to swaption vol matrices instead of yield returns. |

---

## Replication Notes

**Data needed:** US Treasury zero-coupon yields (or par yields) across maturities.
Publicly available from:
- Federal Reserve H.15 release (constant maturity Treasuries)
- Gürkaynak, Sack & Wright (2007) zero-coupon yield dataset (Fed website, daily, 1961+)

**Implementation:**
```python
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

# yields: DataFrame, rows = dates, columns = maturities
returns = yields.diff()  # or use log-price returns

pca = PCA(n_components=3)
factors = pca.fit_transform(returns.dropna())
loadings = pca.components_  # shape: (3, n_maturities)
var_explained = pca.explained_variance_ratio_

# loadings[0] = level, loadings[1] = slope, loadings[2] = curvature
```

**Expected output:** First three eigenvalues should explain ~89%, ~8%, ~3% of variance.
Factor 1 loadings should be roughly flat across maturities.
Factor 2 loadings should slope from negative (short end) to positive (long end).
Factor 3 loadings should show a hump at intermediate maturities.

---

## Adjacent Papers to Read Next

- **Diebold & Li (2006)** — gives the PCA factors a dynamic forecasting interpretation
- **Nelson & Siegel (1987)** — parametric alternative; factors have the same shape but
  are imposed analytically rather than extracted from data
- **Svensson (1994)** — extends NS with a second curvature term for more complex curve shapes

---

*Cerebro — 2026-03-26 | FIRV study: Litterman & Scheinkman (1991)*
