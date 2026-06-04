# FIRV Chapter 3 Notes: Principal Component Analysis

## Core Concept and Author Intent

Chapter 3 presents PCA as a way to decompose a market into a small number of orthogonal factors, interpret those factors economically, and then use factor-neutral residuals to design relative-value trades and hedges.

The authorial intent is broader than a textbook PCA introduction. The chapter appears to connect:

- covariance structure
- eigenvector interpretation
- factor exposure management
- residual screening
- trade construction
- risk and hedge design

In other words, PCA is treated as both:

- a descriptive tool for market structure
- an operational tool for generating and hedging trade ideas

## Chapter Structure Cues

From the TOC and figure list, the chapter covers:

- intuitive PCA
- factor-model structure
- PCA mathematics
- eigenvector interpretation
- decomposition into uncorrelated factors
- embedding PCA in trade ideas
- appropriate hedging
- exposure analysis for positions and portfolios
- market screening
- a concrete PCA-based trade idea
- pitfalls:
  - factor correlation during subperiods
  - instability of eigenvectors over time

The figure list suggests examples across:

- Bund yields
- CDS curves
- currencies
- curve butterflies and steepeners
- comparisons of PCA-neutral trades versus OU forecasts

## Key Technicalities

### 1. Covariance and Eigen Decomposition

Given a data matrix $X$ with centered observations, PCA starts from the covariance matrix:

$$
\Sigma = \mathrm{Cov}(X)
$$

and solves:

$$
\Sigma v_i = \lambda_i v_i
$$

where:

- $v_i$ are eigenvectors
- $\lambda_i$ are eigenvalues

The eigenvectors define factor directions, and eigenvalues measure how much variance each factor explains.

### 2. Factor Representation

If $V_k$ collects the first $k$ eigenvectors, factor scores are:

$$
F = X V_k
$$

and the rank-$k$ reconstruction is:

$$
\hat{X} = F V_k^\top = X V_k V_k^\top
$$

Residual structure is then:

$$
R = X - \hat{X}
$$

This residual is the basis for PCA-neutral trade ideas: what remains after stripping out the major common factors.

### 3. Explained Variance

The importance of component $i$ is measured by:

$$
\text{ExplainedVarianceRatio}_i =
\frac{\lambda_i}{\sum_j \lambda_j}
$$

In fixed income, the first few components are often interpreted as:

- level
- slope
- curvature

But the chapter seems to emphasize that this interpretation should be checked, not assumed blindly.

### 4. PCA as a Factor Model

The chapter explicitly frames PCA as a factor model, which means the market can be viewed as:

$$
X_t = B f_t + \varepsilon_t
$$

where:

- $f_t$ are the latent factors
- $B$ are factor loadings
- $\varepsilon_t$ are residual or idiosyncratic components

In practice:

- $B$ comes from eigenvectors
- $f_t$ comes from projecting observations onto those eigenvectors

This matters because RV trades often want:

- controlled exposure to dominant factors
- concentrated exposure to residual mispricing

### 5. PCA-Neutral Trade Construction

The figure list strongly suggests the chapter moves from pure decomposition to PCA-neutral butterflies and steepeners.

In practical terms, weights $w$ may be chosen so that the trade is neutral to the first $k$ components:

$$
w^\top v_1 = 0,\quad
w^\top v_2 = 0,\quad
\dots,\quad
w^\top v_k = 0
$$

Optionally, the trade may also be duration- or BPV-neutral:

$$
w^\top \mathrm{BPV} = 0
$$

This is one of the chapter's most practical contributions: use PCA not just to observe the market, but to engineer better hedged structures.

### 6. Residual-Based Screening

The chapter appears to use PCA residuals as a screening device:

- fit factors to the market
- remove systematic structure
- rank the residuals or residual portfolios
- search for outliers worth mean-reversion analysis

This is a natural bridge back to Chapter 2:

- Chapter 3 generates candidate dislocation series
- Chapter 2 tests whether those dislocations mean revert and how to trade them

### 7. Pitfalls the Authors Emphasize

The TOC calls out two specific pitfalls:

#### Factor correlation during subperiods

Even if factors are orthogonal over the estimation sample, they may not stay uncorrelated in subperiods.

Implication:

- PCA orthogonality is sample-specific
- risk can re-couple under stress

#### Eigenvector instability over time

Loadings may drift materially across:

- market regimes
- policy periods
- liquidity environments

Implication:

- static PCA hedges can become stale
- rolling or regime-aware PCA may be necessary

## Framework Summary

The chapter's operational workflow looks like:

1. define a market cross-section or curve panel
2. compute covariance structure
3. extract leading factors
4. interpret those factors economically
5. build residuals or PCA-neutral structures
6. screen for dislocations
7. test the dislocations with Chapter 2 style mean-reversion logic

This makes PCA a front-end idea generator and hedge constructor, not just a descriptive statistic.

## How It Connects to Our Practical Notebooks

Primary notebook:

- [02_pca_yield_curve.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/02_pca_yield_curve.ipynb)

Secondary connections:

- [01_mean_reversion.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/01_mean_reversion.ipynb)
  for turning PCA residuals into OU-style trade candidates
- [03_fitted_curves.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/03_fitted_curves.ipynb)
  because fitted curves and PCA are combined later in the book's government-bond workflow

Current notebook scope:

- load local Treasury curve points from FRED
- run PCA on daily changes
- inspect eigenvalues and eigenvectors
- scaffold residual and PCA-neutral trade construction
- scaffold rolling-stability checks

What remains to implement:

- explicit BPV-neutral and PCA-neutral weight solving
- residual ranking and screening logic
- rolling-window PCA stability plots
- comparison of PCA-neutral trades against OU expected paths

## Open Questions and Things to Verify Empirically

### Data Choice

- Should PCA be run on yield levels, changes, forwards, or spread-transformed data?
- Are local Treasury constant-maturity series sufficient, or do we need instrument-level or swap-level data to match the chapter's intended use?

### Factor Interpretation

- Do the first three Treasury factors in our local sample actually correspond to level, slope, and curvature?
- How stable is that interpretation across the sample window we currently have?

### Trade Construction

- Does a PCA-neutral `2Y-5Y-7Y` or `2Y-5Y-10Y` butterfly create cleaner residuals than a simpler duration-neutral structure?
- Are PCA-neutral steepeners materially different from level-neutral steepeners in realized behavior?

### Stability

- How unstable are eigenvectors over rolling windows?
- Is factor drift large enough that a trade should be re-hedged on a rolling basis?
- Are factor correlations really near zero in stressed subperiods?

### Cross-Chapter Link

- When PCA flags a residual dislocation, does Chapter 2 style OU modeling confirm mean reversion?
- Are the best PCA residuals also the best OU candidates, or do some residuals remain structurally nonstationary?

### Broader Market Applicability

- Do the same PCA workflows apply cleanly to:
  - CDS curves
  - currencies
  - basis markets
  - volatility surfaces
- If not, what needs to change in preprocessing and interpretation?

## Immediate Next Steps

1. Extend `02_pca_yield_curve.ipynb` with explicit factor-neutral weight solving.
2. Add rolling-window PCA stability diagnostics.
3. Build a residual handoff from `02_pca_yield_curve.ipynb` into `01_mean_reversion.ipynb`.
4. Compare PCA on Treasury levels vs changes vs curve spreads.
