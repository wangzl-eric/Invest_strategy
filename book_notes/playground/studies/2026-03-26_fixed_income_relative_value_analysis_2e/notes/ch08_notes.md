# FIRV Chapter 8 Notes: Fitted Bond Curves

## Core Concept and Author Intent

Chapter 8 appears to be one of the book's central implementation chapters. Its role is to move the reader from rough yield summaries toward a curve-consistent pricing framework that can identify rich and cheap bonds through residual analysis.

The authorial intent seems to be:

1. define the fitted-curve problem rigorously
2. choose a discount-factor functional form
3. choose weighting and optimization criteria
4. use fitted residuals as relative-value signals

This is likely the chapter where the book's fixed-income RV framework becomes operational for cash bonds.

## Chapter Structure Cues

From the TOC and figure list, Chapter 8 covers:

- introduction
- framework of analysis
- specifying a function for discount factors
- weights
- setting up the optimization
- conclusions

Illustrations suggest:

- Bund yields on a given date
- regression residuals in EUR
- regression residuals in basis points

That points to a practical pipeline:

- fit a smooth curve
- compare market prices or yields to the fitted curve
- interpret residuals in economic units

## Key Technicalities

### 1. Discount Factors as the Primary Curve Object

Instead of fitting yields directly, a common robust framework fits discount factors $D(t)$, from which prices, zero rates, and forwards are derived.

For a bond with cash flows $CF_{ij}$ at times $t_{ij}$, model price is:

$$
P_i^{\text{model}} = \sum_j CF_{ij} D(t_{ij})
$$

This is conceptually cleaner than fitting a scalar yield because:

- every cash flow is discounted consistently
- coupon and maturity structure are handled naturally
- the fitted object is directly linked to valuation

### 2. Functional Form for the Curve

The chapter explicitly calls out "specifying a function for discount factors." That means the practitioner must choose a parametric or semi-parametric form, for example:

- Nelson-Siegel
- Svensson
- splines
- other smooth curve families

A generic parametric setup would be:

$$
D(t; \theta)
$$

with parameter vector $\theta$ chosen to minimize pricing errors.

In zero-rate terms, one often writes:

$$
D(t) = e^{-z(t)\,t}
$$

so a smooth zero curve $z(t)$ implies a smooth discount function.

### 3. Optimization Objective

The fitted-curve problem is an optimization problem. A standard structure is:

$$
\min_{\theta} \sum_i w_i \left(P_i^{\text{market}} - P_i^{\text{model}}(\theta)\right)^2
$$

or, if fitting yields or spread errors,

$$
\min_{\theta} \sum_i w_i \left(y_i^{\text{market}} - y_i^{\text{model}}(\theta)\right)^2
$$

The important issue is not just optimization itself, but what error metric is being minimized:

- price errors
- yield errors
- basis-point errors
- relative price errors

Different objectives change the residuals and therefore the inferred cheap/rich ranking.

### 4. Weighting Matters

The chapter has a dedicated "weights" section, which implies the authors take weighting seriously. Candidate weighting schemes may reflect:

- liquidity
- maturity importance
- duration or DV01
- issue size
- relative confidence in quotes

For example:

$$
\min_{\theta} \sum_i w_i \, \varepsilon_i^2
$$

with residual $\varepsilon_i$ defined in price or yield terms.

This matters because an unweighted fit can produce a curve that is mathematically acceptable but economically unhelpful if it overfits noisy or illiquid bonds.

### 5. Residuals as RV Signals

Once the curve is fitted, residuals become the raw material for relative-value analysis:

$$
\varepsilon_i^{P} = P_i^{\text{market}} - P_i^{\text{model}}
$$

or

$$
\varepsilon_i^{y} = y_i^{\text{market}} - y_i^{\text{model}}
$$

Interpreting residuals:

- positive price residual may suggest richness
- negative price residual may suggest cheapness

with sign conventions depending on the exact setup.

The chapter's figure references to residuals in EUR and basis points suggest the authors want the practitioner to think carefully about unit choice:

- money terms are intuitive for PnL
- basis-point terms are easier to compare across maturities

### 6. Smoothness vs Fit Quality

Fitted curves involve a trade-off:

- too rigid: the model misses meaningful structure
- too flexible: the model overfits noise and destroys the usefulness of residuals

This is a recurring fixed-income RV issue. A good fitted curve is not just the one with the smallest in-sample error. It is the one whose residuals are economically interpretable and stable enough to trade against.

### 7. Why This Chapter Matters for the Rest of the Book

Chapter 8 is a foundation chapter because later workflows use fitted curves for:

- bond selection
- maturity selection
- global bond comparison
- asset-swap and spread interpretation

Without a curve-consistent valuation framework, many later RV ideas reduce back to crude yield comparisons, which Chapter 5 warned against.

## Framework Summary

The chapter's practical workflow can be summarized as:

1. select a bond universe
2. choose a discount-factor functional form
3. define weights and residual metric
4. optimize the fitted curve
5. compute residuals in meaningful units
6. use those residuals for cheap/rich screening

This chapter is where fixed-income RV becomes concrete for bond-level work.

## How It Connects to Our Practical Notebooks

Primary notebook:

- [03_fitted_curves.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/03_fitted_curves.ipynb)

Secondary connections:

- [02_pca_yield_curve.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/02_pca_yield_curve.ipynb)
  because Chapter 9 later combines fitted curves with PCA
- [04_asset_swaps.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/04_asset_swaps.ipynb)
  because fitted curves and swap-spread logic interact in bond RV

Current notebook scope:

- placeholder curve parameterization
- simple Nelson-Siegel-style fit scaffold
- observed-vs-fitted curve comparison
- explicit TODOs for bond-level pricing inputs

What remains to implement:

- actual optimization choices with controlled weighting
- bond-level cashflow schedule generation
- residual ranking in price and basis-point terms
- richer comparison across dates or subperiods

## Open Questions and Things to Verify Empirically

### Functional Form

- Which curve family is most useful for our playground scope: Nelson-Siegel, Svensson, splines, or something simpler?
- How sensitive are residual rankings to the choice of parameterization?

### Objective and Weights

- Should we minimize price error, yield error, or DV01-scaled error?
- Which weighting scheme gives the most stable and economically sensible residuals?

### Data Fidelity

- Are constant-maturity Treasury series enough for a pedagogical scaffold, or do we need actual bond-level cashflows and prices to make Chapter 8 meaningful?
- Which missing bond-level datasets are the highest-value ingestion targets?

### Trade Usefulness

- Are fitted-curve residuals more stable and informative than simple yield or spread comparisons?
- How persistent are cheap/rich rankings across days and weeks?

### Integration with Later Chapters

- How should fitted-curve residuals feed into PCA maturity selection from Chapter 9?
- How should fitted-curve richness/cheapness interact with asset-swap spread analysis?

## Immediate Next Steps

1. Extend [03_fitted_curves.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/03_fitted_curves.ipynb) with a more explicit optimization and residual table.
2. Add a bond-level data-gap checklist for coupon schedules, prices, and conventions.
3. Compare residuals in both price units and basis-point units.
