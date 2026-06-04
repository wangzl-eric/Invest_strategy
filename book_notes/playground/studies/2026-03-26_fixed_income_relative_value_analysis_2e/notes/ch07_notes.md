# FIRV Chapter 7 Notes: Bond Futures Contracts

## Core Concept and Author Intent

Chapter 7 appears to explain why government bond futures are not simple forwards on a single bond. The key issue is the delivery option: the short can choose among deliverable securities, which creates option value and makes futures pricing depend on the joint dynamics of the deliverable basket.

The authorial intent seems to be:

1. explain futures pricing and CTD logic
2. show why one-factor delivery-option models are limited
3. motivate multi-factor modeling for realistic RV work
4. connect delivery-option structure to basis and relative-value opportunities

This chapter is likely foundational for any work involving:

- futures vs cash bonds
- CTD switching
- futures-basket richness/cheapness

## Chapter Structure Cues

From the TOC and figure list, Chapter 7 focuses on:

- futures price and delivery option
- one-factor delivery option models
- the need for multi-factor delivery option models
- a flexible multi-factor delivery option model

Figure titles suggest practical emphasis on:

- CTD region as a function of yield level
- fair futures price as a function of yield level
- Monte Carlo simulation of CTD at delivery
- volatility of yield spreads between CTD candidates

That means the chapter is explicitly about state-dependent CTD behavior and why the deliverable basket cannot be reduced to a single scalar factor in realistic settings.

## Key Technicalities

### 1. Conversion Factors and Invoice Price

For a bond futures contract, the invoice price at delivery is typically:

$$
\text{Invoice Price} = F \times CF_i + AI_i
$$

where:

- $F$ is the futures price
- $CF_i$ is the conversion factor of deliverable bond $i$
- $AI_i$ is accrued interest

The short chooses which bond to deliver. This embedded choice is the delivery option.

### 2. Cheapest-to-Deliver Logic

The short's optimization is usually expressed through net basis or implied repo-style comparisons. A stylized choice criterion is:

$$
\text{CTD} = \arg\min_i \left(\text{Cash Price}_i - F \times CF_i\right)
$$

up to carry, financing, and convention adjustments.

The key point is that CTD depends on market state. As yields and curve shape move, the identity of the CTD can change.

### 3. Futures as an Option on the Deliverable Basket

Because the short can choose among deliverables, the futures price is not just one discounted expectation. It includes the value of that choice:

$$
F \approx \min_i \left(\frac{\text{Expected delivery-adjusted bond value}_i}{CF_i}\right)
$$

conceptually, with proper modeling under the relevant measure and conventions.

The practical lesson is:

- the futures contract contains optionality
- simple carry or duration calculations can miss that option value

### 4. One-Factor Delivery Models

One-factor models may treat the basket as driven mainly by a single yield level factor. They can be useful when:

- candidate deliverables are close in maturity
- curve shape changes are small
- CTD switching is rare

But they become fragile when:

- relative slope/curvature moves matter
- several candidate bonds are close in value
- CTD regions change materially with non-parallel shifts

This is likely why the chapter quickly moves to the need for multi-factor models.

### 5. Need for Multi-Factor Modeling

If candidate bond values depend on several curve dimensions, a one-factor model is too restrictive. A more realistic setup might use a factor vector $X_t$:

$$
dX_t = \mu(X_t)\,dt + \Sigma(X_t)\,dW_t
$$

with each deliverable bond priced as a function:

$$
P_i = P_i(X_t)
$$

Then the CTD region and futures value depend on:

- level
- slope
- curvature
- potentially volatility and basis effects

This makes the futures delivery option inherently a multi-factor object.

### 6. Monte Carlo and CTD Region Analysis

The figure list mentions Monte Carlo simulation of CTD at delivery. That implies a practical workflow:

1. simulate factor paths for the relevant horizon
2. compute all deliverable bond prices under each path
3. identify CTD bond by path
4. estimate expected futures value and CTD switching probabilities

This is useful because CTD switching is not just a pricing curiosity. It changes:

- hedge ratios
- basis behavior
- trade PnL attribution

### 7. Basis and Relative-Value Implications

For RV work, the delivery option matters because:

- futures richness/cheapness can be misread if CTD dynamics are ignored
- cash-vs-futures trades depend on which bond is effectively being delivered
- curve-relative moves between candidate bonds can create or remove apparent basis opportunities

So Chapter 7 likely teaches that a futures trade is partly a view on:

- the deliverable basket
- CTD switching risk
- factor structure of the underlying bond universe

## Framework Summary

The chapter's practical workflow can be summarized as:

1. identify the deliverable basket
2. understand conversion factors and invoice pricing
3. compute or approximate the CTD choice
4. recognize that CTD is state-dependent
5. move from one-factor to multi-factor logic when curve shape matters
6. use simulation or factor scenarios when delivery-option behavior is material

This chapter helps prevent a common error: treating a futures contract as if it were a single bond.

## How It Connects to Our Practical Notebooks

There is no dedicated bond-futures notebook scaffold yet.

Closest current connections:

- [03_fitted_curves.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/03_fitted_curves.ipynb)
  because pricing and residuals of deliverable bonds depend on curve fitting
- [02_pca_yield_curve.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/02_pca_yield_curve.ipynb)
  because level/slope/curvature factors are natural drivers of CTD switching

Suggested future notebook:

- `06_bond_futures_delivery_option.ipynb`

Potential scope for that notebook:

- define a mock or real deliverable basket
- compute duration/BPV and conversion-factor-adjusted comparisons
- simulate CTD switching under factor moves
- compare one-factor vs multi-factor approximations

## Open Questions and Things to Verify Empirically

### Data Availability

- Do we have enough local data to build even a simplified CTD study, or do we need futures-basket data ingestion first?
- Can Treasury constant-maturity proxies support a pedagogical CTD notebook, or do we need actual bond-level deliverables?

### Model Choice

- How wrong is a one-factor approximation for plausible Treasury deliverable baskets?
- In which contracts or maturity sectors does multi-factor modeling matter most?

### RV Relevance

- Which basis trades are most sensitive to CTD switching?
- How much of apparent richness/cheapness in a futures contract is actually a delivery-option effect?

### Practical Implementation

- Can we build a useful playground approximation using stylized deliverables and fitted-curve scenarios before sourcing full futures-basket data?
- Should CTD region analysis be linked to PCA factors from Chapter 3?

## Immediate Next Steps

1. Add a future notebook scaffold for bond futures delivery options.
2. Inventory what actual deliverable-basket data is missing from the local lake.
3. Use Chapter 3 factor ideas to build simple level/slope/curvature CTD scenarios.
