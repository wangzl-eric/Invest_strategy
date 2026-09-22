# Fixed Income Relative Value Analysis (2nd ed.) Book Map

## Material Scoring

This book clears the implementation threshold for deeper follow-up.

| Dimension | Score | Reason |
|-----------|-------|--------|
| Credibility | 5/5 | Practitioner-focused Wiley book by recognized fixed-income RV specialists |
| Relevance | 5/5 | Directly aligned with fixed-income relative-value, curve, spread, and swap-based research |
| Actionability | 5/5 | Techniques are implementable as study notebooks, factor decompositions, and pricing workflows |

## Central Argument

Relative value analysis identifies mispricings across fixed-income instruments by combining:

- statistical models for dislocation detection
- financial models for pricing and risk decomposition
- market-specific frameworks for translating model output into trade ideas

The book moves from statistical structure to instrument pricing to market application.

## Argument Arc By Chapter Cluster

### Part I: Statistical Models

- **Chapter 2: Mean Reversion**
  Introduces OU-style thinking, diagnostics, and execution logic for mean-reverting spreads.
- **Chapter 3: PCA**
  Decomposes markets into orthogonal factors and turns factor-neutral residuals into trade structures.
- **Chapter 4: Multivariate Mean Reversion**
  Extends mean reversion into cross-market and multi-series settings.

### Part II: Financial Models

- **Chapters 5-6**
  Practical caution around duration/convexity and yield-curve model selection.
- **Chapter 7**
  Futures delivery-option modeling.
- **Chapter 8**
  Fitted curves and optimization setup.
- **Chapter 9**
  Integrates fitted curves and PCA into a government-bond analytic workflow.

### Part III: Market Applications

- **Chapter 11**
  Reference-rate and repo-market plumbing.
- **Chapter 12**
  Asset swaps and swap-spread drivers.
- **Chapters 13-18**
  CDS, intra-currency basis, cross-currency basis, and related equilibria.
- **Chapter 19**
  Option RV and vega-sector factor structures.

## Extracted Technicalities To Preserve Across Sessions

- OU / mean-reversion estimation
- drift and diffusion diagnostics
- first-passage-time style reasoning
- PCA factor extraction and eigenvector interpretation
- factor-neutral residual construction
- fitted discount/yield curves
- asset-swap spread decomposition
- cross-currency-basis decomposition

## Notebook Mapping

- `01_mean_reversion.ipynb`
  Chapter 2 scaffold using a local Treasury `2s5s10s` butterfly proxy and OU fitting.
- `02_pca_yield_curve.ipynb`
  Chapter 3 scaffold for yield-curve PCA, residuals, and PCA-neutral structures.
- `03_fitted_curves.ipynb`
  Chapter 8 scaffold for Nelson-Siegel-style fitted curves and residual analysis.
- `04_asset_swaps.ipynb`
  Chapter 12 scaffold for asset-swap pricing inputs and spread-driver placeholders.
- `05_cross_currency_basis.ipynb`
  Chapter 15 scaffold for FX spot/funding inputs and CCBS data-gap planning.

## Current Data Reality

Already available locally:

- Treasury curve FRED series
- real-yield / inflation-expectation series
- SOFR and policy proxies
- Yahoo rate proxies (`^IRX`, `^FVX`, `^TNX`, `^TYX`)
- major FX spot pairs

Still missing for deeper implementation:

- USD swap curve history
- OIS curves across currencies
- asset swap spread quotes
- cross-currency basis quotes
- repo specialness and collateral data
- bond-level cashflow / coupon / dirty-price histories

## Next Dev-Support Steps

1. Run the notebooks in `ibkr-analytics` and validate imports and local data loading end-to-end.
2. Add reusable helper functions for:
   - OU parameter reporting
   - rolling PCA stability
   - curve-fit residual comparison
3. Decide which missing datasets justify ingestion work versus placeholder-only documentation.
