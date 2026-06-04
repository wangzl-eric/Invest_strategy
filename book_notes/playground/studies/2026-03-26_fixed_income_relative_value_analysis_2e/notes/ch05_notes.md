# FIRV Chapter 5 Notes: Yield, Duration, and Convexity

## Core Concept and Author Intent

Chapter 5 appears to be a corrective chapter. The topic is not yield, duration, and convexity as textbook definitions alone, but how those concepts are routinely misused in practice when traders and researchers treat them as universal pricing truths rather than local approximations.

The authorial intent seems to be:

1. clarify what yield actually measures for a coupon-paying bond
2. restate duration as a local sensitivity, not a full valuation model
3. show where convexity is helpful and where it is commonly over-applied
4. push the reader toward curve-aware relative-value analysis rather than single-number heuristics

This chapter likely serves as a conceptual guardrail before the later fitted-curve, futures, and swap chapters. It tells the reader not to confuse summary statistics with a full pricing framework.

## Chapter Structure Cues

From the table of contents, the chapter centers on:

- practical comments on the yield of a coupon-paying bond
- a brief comment on duration
- a common misapplication of convexity

That structure suggests the chapter is less about deriving standard formulas from scratch and more about warning the reader where simple fixed-income analytics break down.

## Key Technicalities

### 1. Yield to Maturity Is an Internal-Rate Summary, Not a Complete State Variable

For a coupon-paying bond with cash flows $CF_i$ at times $t_i$, yield to maturity $y$ is defined implicitly by:

$$
P = \sum_i \frac{CF_i}{(1+y/m)^{m t_i}}
$$

or in continuous-compounding form:

$$
P = \sum_i CF_i e^{-y t_i}
$$

depending on the convention.

The practical point is that $y$ compresses the entire term structure into one scalar. That means:

- different discount curves can map to the same bond yield
- yield changes do not isolate where along the curve the repricing came from
- comparing yields across bonds with different coupons and maturities can be misleading

For relative-value work, yield is useful as a rough summary but insufficient as a pricing language when the relevant dislocation is curve-shaped.

### 2. Duration Is a First-Order Local Sensitivity

Macaulay duration can be written as the weighted average time of discounted cash flows:

$$
D_{\text{Mac}} = \frac{\sum_i t_i \, PV(CF_i)}{P}
$$

Modified duration is the price sensitivity to a parallel yield move:

$$
D_{\text{mod}} = -\frac{1}{P}\frac{\partial P}{\partial y}
$$

which yields the first-order approximation:

$$
\frac{\Delta P}{P} \approx -D_{\text{mod}} \, \Delta y
$$

The key practical message is that duration is:

- local
- model-dependent
- usually tied to a parallel-yield-move assumption

It is not a full description of bond risk if:

- the curve twists or butterflies rather than shifts in parallel
- spread and yield components move separately
- the bond has embedded options or nonlinear features

### 3. Convexity Is a Second-Order Correction, Not a Free Lunch

The second-order price approximation is:

$$
\frac{\Delta P}{P} \approx -D_{\text{mod}} \, \Delta y + \frac{1}{2} C (\Delta y)^2
$$

where convexity is:

$$
C = \frac{1}{P}\frac{\partial^2 P}{\partial y^2}
$$

In practice, convexity helps improve the duration-only approximation for larger rate moves. But the chapter title strongly suggests the authors are warning about a common misapplication:

- using convexity as if it were sufficient for general non-parallel curve shocks
- treating convexity as if it fully explains relative-value differences between bonds
- applying yield-based convexity to situations where the underlying repricing is curve-specific or model-specific

That is a serious issue in RV work, because many trades depend on:

- shape changes in the curve
- relative discounting across maturities
- carry and roll-down

not merely second-order price curvature around a single yield number.

### 4. Yield-Based Risk Can Mask Curve-Based Risk

Suppose two bonds have similar yield and duration statistics. They can still behave differently if:

- their cash-flow timing differs
- the relevant curve segment moves differently
- the repricing is driven by spread, repo, or funding conditions rather than pure risk-free discounting

That means relative-value analysis should often move from:

- yield space

to:

- discount-factor space
- zero-rate or fitted-curve space
- spread-to-fitted-curve residual space

This is precisely the direction the book later takes in Chapter 8 and Chapter 9.

### 5. Duration and Convexity Are Shock-Model Dependent

The usual duration/convexity approximations assume a scalar shock $\Delta y$. But many fixed-income RV dislocations are driven by vector shocks:

$$
\Delta P \approx \nabla P^\top \Delta \theta + \frac{1}{2} \Delta \theta^\top H_P \Delta \theta
$$

where $\theta$ may represent:

- multiple key rates
- fitted-curve parameters
- factor shocks such as level, slope, and curvature

This is a more useful frame for RV work than a single-yield approximation, because it makes explicit that "convexity" relative to what shock basis matters.

### 6. Common Misapplication of Convexity

The chapter's title implies a specific warning: people often compare bonds using convexity as if:

- higher convexity is automatically better
- duration+convexity fully captures the valuation problem

But that can fail when:

- financing and carry matter
- the shock is not parallel
- fitted-curve richness/cheapness dominates
- spread products and government bonds are compared in an inconsistent metric

So the practical lesson is not "ignore convexity." It is:

- use convexity only inside a clearly specified shock model
- do not substitute it for full curve analysis

## Framework Summary

The chapter's practical framework can be summarized as:

1. use yield as a summary, not as a complete model
2. use duration as a local first-order approximation
3. use convexity as a local second-order correction
4. avoid treating yield-based Greeks as substitutes for a proper curve model
5. move to fitted curves, key-rate views, or factor models when doing real RV analysis

This chapter is therefore foundational in a defensive sense: it reduces the chance that later RV work is built on oversimplified analytics.

## How It Connects to Our Practical Notebooks

Closest current notebook:

- [03_fitted_curves.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/03_fitted_curves.ipynb)

Secondary links:

- [02_pca_yield_curve.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/02_pca_yield_curve.ipynb)
  because factor shocks are a better language than scalar yield shocks in many RV settings
- [04_asset_swaps.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/04_asset_swaps.ipynb)
  because swap-spread and package valuation cannot be reduced to duration/convexity alone

Practical implication for our study flow:

- Chapter 5 explains why we should not stop at duration and convexity
- Chapter 8 is where the pricing framework becomes rich enough for actual bond RV work

## Open Questions and Things to Verify Empirically

### Yield Interpretation

- How misleading is yield ranking versus fitted-curve residual ranking for our local Treasury sample?
- Are bonds with similar yields but different coupon structures materially different in fitted-curve cheap/rich terms?

### Duration Approximation Quality

- For realistic daily or weekly shocks, how large is the error from a duration-only approximation?
- How often does a key-rate or factor-based approximation materially outperform scalar duration?

### Convexity Misuse

- In what ranges of rate moves does convexity materially improve approximation quality?
- When do curve-shape effects dominate convexity effects?

### RV Relevance

- For bond-selection problems, is duration/convexity ever enough, or do we almost always need fitted curves?
- Which practical Treasury or futures examples in our data are most illustrative of the chapter's warning?

## Immediate Next Steps

1. Add a small duration/convexity sanity-check section later to [03_fitted_curves.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/03_fitted_curves.ipynb).
2. Compare scalar-yield approximations versus curve-based residual analysis on a simple Treasury panel.
3. Keep Chapter 5 as a conceptual guardrail when interpreting later fitted-curve or futures analytics.
