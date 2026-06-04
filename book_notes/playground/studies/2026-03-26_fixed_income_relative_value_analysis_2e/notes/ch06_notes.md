# FIRV Chapter 6 Notes: Yield Curve Models

## Core Concept and Author Intent

Chapter 6 appears to be a compact orientation chapter on yield-curve model families rather than a full survey of every term-structure model. The emphasis in the TOC is on:

- mixed jump-diffusion models
- shadow rate models

That suggests the author's intent is to warn the practitioner that curve dynamics matter for RV work, especially when:

- rates are near lower bounds
- jumps and regime discontinuities matter
- simple Gaussian diffusions understate the structure of yield-curve risk

The chapter likely exists to provide model awareness rather than insist that every trader must run a full affine term-structure engine. It tells the reader which curve-model features matter for the later chapters.

## Chapter Structure Cues

From the TOC and figure list, Chapter 6 appears to be concise:

- introduction
- remarks about mixed jump-diffusion models
- remarks about shadow rate models

There is also a figure reference to:

- evolution of an overnight shadow rate implied by the EUR yield curve

So the chapter likely focuses on what qualitative model features are needed when ordinary linear-Gaussian assumptions fail.

## Key Technicalities

### 1. Term-Structure Models as State Dynamics for Discounting

At a high level, a yield-curve model specifies how discount factors or short rates evolve. A generic short-rate setup writes:

$$
d r_t = \mu(r_t, t)\,dt + \sigma(r_t, t)\,dW_t
$$

and derives bond prices from:

$$
P(t,T) = \mathbb{E}_t^{\mathbb{Q}}\left[\exp\left(-\int_t^T r_s \, ds\right)\right]
$$

The practical point for RV analysis is:

- discounting is model-based
- relative-value metrics inherit assumptions from the curve model

If the model misses important features such as lower bounds or jumps, RV signals built on that model can be distorted.

### 2. Mixed Jump-Diffusion Models

A jump-diffusion short-rate or factor process may take a form like:

$$
dX_t = \mu(X_t)\,dt + \sigma(X_t)\,dW_t + J_t\,dN_t
$$

where:

- $W_t$ is Brownian motion
- $N_t$ is a Poisson jump process
- $J_t$ is jump size

The motivation is straightforward:

- rates and curve factors do not always move continuously
- policy shocks, liquidity events, or stress episodes can cause discontinuous repricing

For fixed-income RV, jump risk matters because:

- spread convergence can be interrupted by macro jumps
- hedge effectiveness can change sharply when jump exposure is not aligned
- Gaussian backtests may understate tail risk

The author's likely practical point is not that a jump-diffusion must always be fitted, but that practitioners should remain aware when a smooth diffusion model is likely insufficient.

### 3. Shadow Rate Models

Shadow rate models are designed to handle the lower-bound problem. A common intuition is:

- there is an unconstrained latent or "shadow" rate $r_t^*$
- the observed short rate is a transformed version that respects the lower bound

A stylized form is:

$$
r_t = \max(r_t^*, \underline{r})
$$

where $\underline{r}$ is the effective lower bound.

More sophisticated formulations smooth that transformation, but the practical message is the same:

- observed rates near zero are not well described by an ordinary Gaussian model
- term-structure behavior becomes nonlinear near the bound
- curve shape can reflect lower-bound option-like effects

For RV analysis, this matters because fitted richness/cheapness may depend heavily on whether the model respects the lower bound.

### 4. Why Shadow Rate Matters for Relative Value

Near-zero-rate environments create distortions in:

- expected roll-down
- duration interpretation
- curvature of bond prices
- option-like asymmetry in short-end rates

If a standard Gaussian term-structure model is used when rates are pinned by a lower bound, then:

- implied discount factors may be unrealistic
- fitted curves may mis-rank cheap/rich securities
- scenario analysis may become directionally wrong

This is a key bridge to later chapters on fitted curves and bond RV.

### 5. Model Choice Is Context-Dependent

The chapter likely argues implicitly that the "best" curve model depends on the question:

- for quick screening, a simple fitted curve may suffice
- for lower-bound periods, shadow-rate awareness matters
- for event-risk-heavy trades, jump awareness matters

This is useful because it discourages both extremes:

- naive oversimplification
- unnecessary overengineering

### 6. Risk-Neutral vs Practical Modeling

The pricing formula above is risk-neutral, but many RV workflows sit between:

- a pure no-arbitrage pricing model
- a practical statistical dislocation model

That means Chapter 6 likely functions as a reminder:

- pricing models define structure and consistency
- statistical models define dislocation behavior
- a good RV process needs both

## Framework Summary

The chapter's practical framework can be summarized as:

1. choose a yield-curve model that matches the regime and question
2. do not ignore nonlinear lower-bound effects when rates are near zero
3. do not ignore jump risk when the market reprices discontinuously
4. understand that later fitted-curve and RV signals inherit assumptions from the curve model

This is a model-awareness chapter. It helps prevent later bond-selection and spread work from resting on unrealistic curve assumptions.

## How It Connects to Our Practical Notebooks

Closest current notebook:

- [03_fitted_curves.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/03_fitted_curves.ipynb)

Secondary connections:

- [01_mean_reversion.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/01_mean_reversion.ipynb)
  because mean-reversion assumptions should be tested against jump/nonlinear realities
- [05_cross_currency_basis.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/05_cross_currency_basis.ipynb)
  because reference-rate and discount-curve assumptions feed directly into basis work

Practical notebook implication:

- Chapter 6 does not yet have a dedicated scaffold
- the natural extension would be a notebook comparing:
  - simple fitted curves
  - lower-bound-aware transformations
  - jump-stress scenarios for yield-curve risk

## Open Questions and Things to Verify Empirically

### Lower-Bound Effects

- In our available local Treasury and policy-rate sample, do lower-bound nonlinearities matter enough to justify a shadow-rate treatment?
- Are simple fitted curves materially distorted when short-end rates are close to the floor?

### Jump Risk

- Which local fixed-income RV proxies show evidence of jump behavior rather than pure diffusion?
- Does adding jump stress materially change expected RV trade attractiveness?

### Model Usefulness

- For our current playground scope, when is a simple fitted curve enough and when do we need a richer dynamic model?
- Are shadow-rate or jump-diffusion ideas most useful as:
  - pricing models
  - stress overlays
  - filters for when not to trust simple signals

### Practical Replication

- Can we proxy shadow-rate behavior from local FRED and Treasury data without implementing a full term-structure model?
- What would be the minimum notebook needed to make Chapter 6 empirically useful in our workflow?

## Immediate Next Steps

1. Keep Chapter 6 in mind while extending [03_fitted_curves.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/03_fitted_curves.ipynb).
2. Add a future notebook section or sidecar note on lower-bound-aware curve interpretation.
3. Build a simple jump-stress sanity check for any mean-reversion or bond-selection signal.
