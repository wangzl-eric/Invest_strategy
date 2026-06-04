# Chapter Context

This file follows the briefing protocol in [firv_book_briefing.md](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/briefings/firv_book_briefing.md#L39): track the argument arc, extract technicalities, note how chapters build on each other, and preserve context across sessions.

## Book-Level Material Score

| Dimension | Score | Reason |
|-----------|-------|--------|
| Credibility | 5/5 | Practitioner-oriented Wiley text by domain specialists; structured methodology and market examples |
| Relevance | 5/5 | Directly aligned with fixed-income RV, rates, swaps, fitted curves, and cross-market quant workflows |
| Actionability | 5/5 | Contains techniques that can be scaffolded, tested, and progressively implemented in playground notebooks |

The book clears the $\ge 3/5$ threshold on all dimensions, so deeper implementation support is warranted.

## Argument Arc

### Chapter 2: Mean Reversion

- **Role in the book**: establishes the basic statistical lens for identifying dislocations that may converge
- **Core technicalities**:
  - Ornstein-Uhlenbeck dynamics
  - drift and diffusion estimation
  - conditional expectations and conditional densities
  - first-passage / horizon-aware risk-return thinking
- **Notebook mapping**: `01_mean_reversion.ipynb`
- **How it feeds later chapters**:
  - provides the dynamic model used to evaluate spread normalization after trade entry
  - supports residual-based screening once PCA or fitted-curve residuals are defined

### Chapter 3: Principal Component Analysis

- **Role in the book**: decomposes curve or market moves into uncorrelated factors, making trade construction and hedging more systematic
- **Core technicalities**:
  - covariance / factor model framing
  - eigenvalues and eigenvectors
  - level / slope / curvature interpretation
  - PCA-neutral structures and residuals
- **Notebook mapping**: `02_pca_yield_curve.ipynb`
- **How it builds on Chapter 2**:
  - defines cleaner residuals and factor-neutral structures that can then be evaluated using mean-reversion logic

### Chapter 8: Fitted Bond Curves

- **Role in the book**: shifts from statistical decomposition to financial-model-based pricing consistency
- **Core technicalities**:
  - discount factor parameterization
  - weighted optimization / fit objective
  - residual analysis relative to a fitted curve
- **Notebook mapping**: `03_fitted_curves.ipynb`
- **How it builds on Chapters 2-3**:
  - fitted-curve residuals become another input into screening and trade selection
  - creates a pricing-consistency layer beyond pure covariance-factor methods

### Chapter 12: Asset Swaps

- **Role in the book**: moves from curve structure into tradeable market packages and spread drivers
- **Core technicalities**:
  - asset swap package setup
  - swap spread intuition
  - cyclical and structural spread drivers
- **Notebook mapping**: `04_asset_swaps.ipynb`
- **How it builds on earlier chapters**:
  - requires fitted curves and reference-rate structure for pricing consistency
  - can use statistical overlays to detect spread dislocations

### Chapter 15: Cross-Currency Basis Swaps

- **Role in the book**: extends RV analysis across currencies, funding curves, and FX hedging
- **Core technicalities**:
  - cross-currency basis definition
  - CIP-style decomposition
  - hedged foreign issuance / investment logic
- **Notebook mapping**: `05_cross_currency_basis.ipynb`
- **How it builds on earlier chapters**:
  - depends on curve construction, reference rates, and spread decomposition
  - offers a global extension of the same RV logic introduced in the earlier statistical and financial chapters

## Local Data Fit

### Directly Usable Now

- Treasury constant-maturity yields from local FRED parquet files
- SOFR and Fed target proxies
- inflation-expectation series
- major FX spot pairs from local price parquet files

### Still Missing For Full Fidelity

- swap curve tenors
- bond-level cashflow and price history
- asset swap spread history
- FX forwards and actual cross-currency basis quotes
- repo specialness / collateral data

## Suggested Session Order

1. `01_mean_reversion.ipynb`
2. `02_pca_yield_curve.ipynb`
3. `03_fitted_curves.ipynb`
4. `04_asset_swaps.ipynb`
5. `05_cross_currency_basis.ipynb`

This order respects the book's build-up from statistical dislocation models to financial-model structure to concrete market applications.
