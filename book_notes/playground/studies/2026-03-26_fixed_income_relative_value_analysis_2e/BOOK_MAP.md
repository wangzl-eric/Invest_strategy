# Book Map: Fixed Income Relative Value Analysis (2nd ed.)

This note follows the briefing in [firv_book_briefing.md](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/briefings/firv_book_briefing.md#L1):

- track the argument arc chapter by chapter
- extract technicalities, models, and frameworks
- note how chapters build on prior chapters
- preserve structured context for future sessions

## Material Scoring

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Credibility | 5/5 | Practitioner-oriented Wiley book by established fixed-income RV authors; coherent modeling stack and explicit market applications |
| Relevance | 5/5 | Directly aligned with rates, curve, swap-spread, asset-swap, and basis-study workflows in the playground |
| Actionability | 5/5 | Multiple chapters map directly into reproducible notebook studies using local Treasury/rates data or explicit data-gap placeholders |

This book clears the $\ge 3/5$ threshold on all dimensions and warrants deeper implementation support.

## Central Argument

Relative value in fixed income is not one isolated technique. It is a workflow:

1. model dislocations statistically
2. interpret them economically
3. translate them into instrument-specific pricing relationships
4. map them into concrete market structures such as bonds, swaps, basis swaps, and options

The book starts from statistical tools like mean reversion and PCA, then layers on financial-model structure such as fitted curves and asset-swap logic, and finally applies those tools across reference rates, basis, and cross-market RV.

## Argument Arc By Chapter Group

### Chapter 1: Relative Value

**Role in argument**
- Defines relative value as mispricing across linked instruments or maturities
- Frames RV as both a trading lens and a risk-management lens
- Establishes that edge comes from structural relationships, not just directional views

**Technicalities to retain**
- RV requires comparison sets, fair-value logic, and hedge-aware construction
- Mispricing can come from segmentation, funding constraints, regulatory frictions, or transient order flow

**Builds into**
- Chapter 2 mean reversion as the simplest statistical way to model temporary dislocations
- Chapter 3 PCA as a way to separate systematic curve factors from local anomalies

### Chapter 2: Mean Reversion

**Role in argument**
- Introduces the statistical template for RV trades: identify dislocation, estimate pull-to-mean dynamics, and translate that into expected return and risk

**Technicalities to retain**
- Ornstein-Uhlenbeck style mean-reverting process
- drift and diffusion diagnostics
- conditional expectation and conditional density
- ex ante risk-adjusted return
- first-passage or holding-period style reasoning for execution

**Practical proxy already scaffolded**
- Treasury $2s5s10s$ butterfly proxy in [01_mean_reversion.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/01_mean_reversion.ipynb)

**Builds into**
- Chapter 3, where residuals created by PCA become candidate mean-reversion series
- Chapter 4, where mean reversion is generalized to multiple linked variables

### Chapter 3: Principal Component Analysis

**Role in argument**
- Turns a yield curve or spread universe into a factor model
- Separates broad market moves from local residual dislocations
- Provides a hedge-aware language for trade construction

**Technicalities to retain**
- covariance matrix and eigen decomposition
- factors as level / slope / curvature style structures
- PCA-neutral hedging
- factor exposure decomposition
- residual screening for RV opportunities
- eigenvector instability and subperiod sensitivity

**Practical proxy already scaffolded**
- Treasury PCA and PCA-neutral trade placeholders in [02_pca_yield_curve.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/02_pca_yield_curve.ipynb)

**Builds into**
- Chapter 8 fitted curves and Chapter 9 bond-market process
- Chapter 13 CDS-curve and sovereign-universe factor work
- Chapter 19 vega-sector PCA

### Chapter 4: Multivariate Mean Reversion

**Role in argument**
- Extends the single-series OU idea to related markets or jointly evolving variables
- Makes RV less about one spread and more about system dynamics

**Technicalities to retain**
- vector autoregressive / multivariate OU style reasoning
- horizon-dependent correlation and expected spread evolution
- cross-market joint dynamics

**Builds into**
- spread trades across currencies or markets
- cross-market volatility relationships
- richer pair/triple structures than simple one-dimensional OU

### Chapters 5-7: Fixed-Income Mechanics and Yield-Curve Models

**Role in argument**
- Provides the instrument and curve-model mechanics needed before the book moves into fitted curves and instrument-specific RV

**Technicalities to retain**
- yield, duration, convexity caveats
- practical yield-curve model concerns
- delivery-option logic in bond futures

**Builds into**
- Chapter 8 fitted curves
- Chapter 9 bond-market analytic process

### Chapter 8: Fitted Bond Curves

**Role in argument**
- Moves from factor decomposition to explicit fair-value fitting
- Gives a way to compare actual instrument prices with a modeled curve-consistent value

**Technicalities to retain**
- discount-factor parameterization
- weighting choices
- optimization setup
- residual interpretation from fitted versus observed prices/yields

**Practical proxy already scaffolded**
- Nelson-Siegel-style curve fit placeholder in [03_fitted_curves.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/03_fitted_curves.ipynb)

**Builds into**
- Chapter 9 government-bond analytic process
- Chapter 17 global bond RV via fitted curves

### Chapter 9: Analytic Process for Government Bond Markets

**Role in argument**
- Assembles the book’s statistical and financial tools into one practical workflow

**Workflow**
1. fitted curves for fair value
2. PCA for maturity selection and curve-trade structure
3. fitted-curve residuals for bond selection

**Why it matters**
- This chapter is the book’s clearest bridge from methods to an implementable research process

### Chapter 11: Reference Rates

**Role in argument**
- Updates the fixed-income RV toolkit for the post-LIBOR world
- Shows that reference-rate spreads are themselves driven by balance-sheet, credit, and collateral mechanisms

**Technicalities to retain**
- SOFR and repo-market structure
- secured versus unsecured funding spreads
- term versus overnight spread logic
- capital requirement effects

**Relevant local data**
- `SOFR`, `DFEDTARU`, `T10Y2Y`, `T10Y3M`, inflation expectations

**Builds into**
- asset swaps
- basis swaps
- cross-currency basis logic

### Chapter 12: Asset Swaps

**Role in argument**
- Introduces the core fixed-income relative-value package trade
- Connects cash bonds, swap curves, and funding structure

**Technicalities to retain**
- general concept of an asset swap
- term structure of swap spreads
- cyclicality of swap spreads
- model-captured versus not-captured spread drivers

**Practical scaffold**
- [04_asset_swaps.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/04_asset_swaps.ipynb)

**Current blocker**
- no local asset-swap spread history or bond cashflow package inputs yet

### Chapters 13-16: CDS, Intra-Currency Basis, Cross-Currency Basis, and Interactions

**Role in argument**
- Generalizes RV from single markets to linked spread systems
- Highlights arbitrage equalities and inequalities across credit, asset-swap, and basis structures

**Technicalities to retain**
- PCA on CDS curves / sovereign universes
- intra-currency basis as a building block
- cross-currency basis decomposition
- asset/basis/CDS equilibrium relationships

**Practical scaffold**
- Chapter 15 placeholder in [05_cross_currency_basis.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/05_cross_currency_basis.ipynb)

**Current blockers**
- no CCBS quotes
- no foreign OIS curves
- no FX forward points
- no CDS curve data

### Chapter 17: Global Bond RV via Fitted Curves and SOFR Asset Swap Spreads

**Role in argument**
- Combines fitted curves and swap-spread logic into a cross-market RV lens
- This is one of the strongest “integration” chapters in the book

**Technicalities to retain**
- fitted-curve dislocations as one signal family
- SOFR asset-swap spreads as another
- comparison between pure curve richness/cheapness and funding-adjusted richness/cheapness

### Chapter 19: Options

**Role in argument**
- Extends RV logic into implied-volatility and option-structure space
- Keeps the same conceptual workflow: factor decomposition, residuals, and structure-aware pricing

**Technicalities to retain**
- single-underlying versus multi-underlying option RV
- factor model for the vega sector
- PCA on implied-vol surfaces / sectors
- caveats and pitfalls for vega-factor trades

### Chapter 20: Broader Perspective

**Role in argument**
- Reframes RV as part of market functioning, not just trade selection
- Places arbitrage and balance-sheet intermediation in a macro and political context

## Implementation Mapping To Current Playground Study

| Book Chapter | Current Study Artifact | Status |
|--------------|------------------------|--------|
| Ch. 2 Mean Reversion | `01_mean_reversion.ipynb` | scaffolded with Treasury proxy |
| Ch. 3 PCA | `02_pca_yield_curve.ipynb` | scaffolded with Treasury curve PCA |
| Ch. 8 Fitted Curves | `03_fitted_curves.ipynb` | scaffolded with curve-fit placeholder |
| Ch. 12 Asset Swaps | `04_asset_swaps.ipynb` | scaffolded, awaiting market inputs |
| Ch. 15 CCBS | `05_cross_currency_basis.ipynb` | scaffolded, major data gaps remain |

## Data Availability Summary

### Already local
- Treasury constant-maturity yields via FRED
- real yields (`DFII5`, `DFII10`, `DFII30`)
- SOFR and policy/reference-rate proxies
- basic FX spot pairs from yfinance cache

### Missing for deeper FIRVA implementation
- swap curve tenors
- OIS curves by currency
- cash bond prices with coupons and accrued interest
- asset swap spread history
- cross-currency basis quotes
- FX forward points
- repo specialness / haircut schedules
- CDS curves

## Recommended Next Reading / Build Order

1. Chapter 2
   Use the OU notebook to make the mean-reversion workflow executable.
2. Chapter 3
   Turn PCA into a reusable factor-decomposition and residual-screening template.
3. Chapters 8-9
   Translate fitted curves into a bond-selection process.
4. Chapters 11-12
   Extend from Treasury proxies into reference-rate and swap-spread logic.
5. Chapter 15 and Chapter 17
   Move to basis and global RV once the necessary data is ingested.

## Session Continuity Notes

- The book’s logic is cumulative. Do not treat Chapters 12, 15, or 17 as stand-alone trade chapters.
- The notebook scaffolds should evolve in the same order as the argument:
  - statistical dislocation modeling
  - factor decomposition
  - fair-value curve fitting
  - instrument-package pricing
  - cross-market relative value
- Future sessions should update this file before expanding into new chapters so the argument chain stays explicit.
