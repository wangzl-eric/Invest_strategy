# FIRV Chapter 4 Notes: Multivariate Mean Reversion

## Core Concept and Author Intent

Chapter 4 extends the Chapter 2 mean-reversion framework from a single spread to a vector of jointly evolving variables. The core idea is that relative-value opportunities often live inside systems, not isolated series:

- multiple points on a curve
- multiple implied vol points
- multiple instruments exposed to shared factors

The authorial intent appears to be:

1. preserve the intuition of mean reversion from Chapter 2
2. add cross-series interaction and correlation structure
3. model expected path, spread behavior, and hedge relationships jointly
4. turn that joint structure into better relative-value trade design

This is a natural bridge between:

- Chapter 2's OU-style convergence logic
- Chapter 3's factor decomposition and residual construction

If Chapter 2 says "a spread may mean revert," Chapter 4 asks "how does mean reversion behave when several related variables move together?"

## Chapter Structure Cues

From the book TOC and figure list, Chapter 4 emphasizes:

- introduction
- examples
- a cross-market volatility example such as $EUR\ 5Y5Y$ vs $GBP\ 5Y5Y$
- expected values over time
- expected spreads over time
- dependence of those expectations on half-lives
- vector-field intuition for the transition matrix
- correlation as a function of horizon
- an Italian government bond example involving multiple BTP maturities and a butterfly spread
- fitting a multivariate OU / MVOU-style model to data

That suggests the chapter is not just a mathematical generalization. It is about:

- how multivariate reversion changes trade intuition
- how horizon-dependent correlation affects position design
- how spread opportunities depend on the joint system, not just a single residual

## Key Technicalities

### 1. Multivariate OU Setup

The natural multivariate extension of OU is:

$$
dX_t = K(\mu - X_t)\,dt + \Sigma\,dW_t
$$

where:

- $X_t \in \mathbb{R}^n$ is a vector of spreads, yields, or vol points
- $\mu \in \mathbb{R}^n$ is the long-run mean vector
- $K$ is the mean-reversion matrix
- $\Sigma$ is the diffusion loading matrix
- $W_t$ is a vector Brownian motion

Interpretation:

- diagonal terms in $K$ control own-series reversion
- off-diagonal terms capture how one variable's deviation affects another's path
- the model embeds both reversion and cross-sectional coupling

This is the crucial conceptual step beyond Chapter 2. Mean reversion is no longer a scalar property. It is a system property.

### 2. Conditional Expectation in the Multivariate Case

The conditional mean path for an MVOU process is:

$$
\mathbb{E}[X_{t+h}\mid X_t] = \mu + e^{-Kh}(X_t - \mu)
$$

This is the matrix analogue of the Chapter 2 OU expectation.

Practical reading:

- expected convergence depends on the full matrix $K$
- half-life becomes direction-dependent
- some combinations of variables may mean revert quickly even if individual components do not

This is important for fixed-income RV because butterflies, curve trades, and cross-market spreads are linear combinations of state variables.

### 3. Transition and Horizon Dependence

The figure list's references to expected values and expected spreads over time, including different half-lives, strongly suggest the chapter emphasizes:

$$
X_{t+h} = \mu + e^{-Kh}(X_t - \mu) + \text{noise}
$$

The matrix exponential $e^{-Kh}$ determines:

- speed of convergence
- direction of convergence
- how interactions between variables evolve with horizon

This matters because two trades can look similar at horizon $h=1$ day and very different at $h=1$ month.

### 4. Covariance Structure Over Horizon

For a multivariate OU process, horizon-dependent covariance has the form:

$$
\mathrm{Cov}(X_{t+h}\mid X_t)
=
\int_0^h e^{-Ks}\,\Sigma\Sigma^\top\,e^{-K^\top s}\,ds
$$

This connects directly to the chapter's correlation-as-a-function-of-horizon figures.

Practical implication:

- instantaneous correlation is not enough
- trade risk over a chosen holding period depends on horizon-dependent covariance
- hedging and expected spread behavior should be evaluated over the actual trading horizon

### 5. Spread Dynamics in a System

If a trade spread is a linear combination:

$$
S_t = w^\top X_t
$$

then its conditional expectation is:

$$
\mathbb{E}[S_{t+h}\mid X_t] = w^\top \mu + w^\top e^{-Kh}(X_t - \mu)
$$

and its conditional variance is:

$$
\mathrm{Var}(S_{t+h}\mid X_t) = w^\top \,\mathrm{Cov}(X_{t+h}\mid X_t)\, w
$$

This gives a natural chapter-level workflow:

1. fit the multivariate state model
2. define the candidate trade weights $w$
3. project expected convergence and risk into spread space
4. compare candidate structures by horizon

That is more informative than analyzing a butterfly purely as a historical scalar time series.

### 6. Half-Life Becomes Directional, Not Scalar

In one dimension, half-life is:

$$
t_{1/2} = \frac{\ln 2}{\kappa}
$$

In multiple dimensions, there may be no single half-life. Instead:

- different eigenmodes of the transition dynamics revert at different speeds
- different linear combinations of the state vector inherit different effective reversion speeds

This is likely why the chapter includes expected spread plots under different half-life assumptions.

Practical implication:

- "the trade has a 10-day half-life" may be too simplistic
- a given butterfly may decompose into fast and slow mean-reverting components

### 7. Relation to Correlation and Co-Movement

The repeated "correlation as a function of horizon" figure titles suggest a key lesson:

- static correlation can mislead
- the relevant dependence for a trade is horizon-conditional
- some variables can react with opposite signs to common shocks

That is particularly relevant in fixed income where:

- neighboring maturities share strong common structure
- curve shape trades often live in small residual relationships after big common-factor moves

### 8. Example Logic from the Book

The chapter examples appear to include:

- $EUR\ 5Y5Y$ vs $GBP\ 5Y5Y$ implied volatilities
- a BTP maturity set and a butterfly spread

This suggests two practical use cases:

#### Cross-market spread

Use MVOU to model a pair or vector across markets where:

- common macro shocks matter
- idiosyncratic relative-value dislocations may mean revert

#### Curve-structure spread

Use MVOU to model several points on a bond curve or a butterfly, where:

- neighboring maturities co-move
- the trade's expected path depends on the joint system, not just on one spread's history

## Framework Summary

The chapter's practical workflow can be summarized as:

1. define a multivariate state vector
2. fit a mean-reverting system rather than a single series
3. compute conditional expected paths over relevant horizons
4. translate those expectations into trade-spread forecasts
5. evaluate horizon-dependent risk through conditional covariance
6. compare candidate structures and hedges based on expected spread behavior

This makes multivariate mean reversion a tool for:

- trade design
- horizon selection
- hedge choice
- understanding how system structure changes the shape of convergence

## How It Connects to Our Practical Notebooks

There is no dedicated Chapter 4 notebook scaffold yet, so the immediate practical links are:

- [01_mean_reversion.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/01_mean_reversion.ipynb)
  for baseline OU logic on a single spread proxy
- [02_pca_yield_curve.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/02_pca_yield_curve.ipynb)
  for constructing candidate curve structures and residual directions

Natural chapter-to-notebook mapping:

1. use PCA or economic intuition to define a multivariate state vector
2. estimate an MVOU-style system
3. project expected spread paths for butterflies / steepeners / cross-market spreads
4. compare trade candidates by expected horizon-specific convergence and variance

Practical notebook implication:

- Chapter 4 probably deserves its own future notebook such as `06_multivariate_mean_reversion.ipynb`

Suggested scope for that future notebook:

- build a vector from Treasury or rate-curve points
- estimate a discrete multivariate transition matrix
- compute expected paths for a butterfly spread
- compare scalar-OU versus MVOU forecasts
- explore correlation as a function of horizon

## Open Questions and Things to Verify Empirically

### Model Specification

- What is the right state vector for our local data: raw yields, forward rates, fitted-curve residuals, or PCA factors?
- Is a full MVOU necessary, or is a lower-dimensional factor representation enough?

### Data Sufficiency

- Is our current local sample long enough to estimate a stable transition matrix?
- Do constant-maturity Treasury series provide enough fidelity, or do we need swap or bond-level data to make the chapter's logic useful?

### Trade Construction

- Does MVOU improve trade design for butterflies versus a scalar OU fit on the butterfly alone?
- Which structures benefit most from multivariate treatment: steepeners, flies, cross-market vol spreads, or fitted-curve residuals?

### Horizon Risk

- How different are short-horizon versus medium-horizon correlations in our local Treasury sample?
- Do horizon-dependent covariance effects materially change which trade is preferable?

### Stability

- Is the transition matrix stable across subperiods?
- Are estimated effective half-lives robust enough to use operationally?

### Integration with PCA

- Should Chapter 4 be implemented directly on raw curves, or on PCA factors / PCA residuals from Chapter 3?
- Does PCA preprocessing improve MVOU estimation by reducing noise and collinearity?

## Immediate Next Steps

1. Add a dedicated `06_multivariate_mean_reversion.ipynb` scaffold later.
2. Use local Treasury maturities or PCA factors as the initial multivariate state vector.
3. Compare scalar-OU and multivariate-OU forecasts for a butterfly spread.
4. Add horizon-dependent covariance and correlation diagnostics.
