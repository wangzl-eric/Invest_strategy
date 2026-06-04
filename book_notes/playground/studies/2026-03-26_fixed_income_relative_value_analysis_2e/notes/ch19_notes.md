# FIRV Chapter 19 Notes: Options Relative Value

## Core Concept and Author Intent

Chapter 19 appears to generalize the book's relative-value framework into options. The central message is likely that options RV must be classified by exposure type rather than discussed as one monolithic thing.

The chapter structure suggests three broad trade families:

- single-underlying and multi-underlying structures
- directional versus non-directional or volatility-driven structures
- factor-model approaches for the vega sector

The authorial intent seems to be:

1. review the minimum option-pricing theory needed for practitioners
2. classify options RV trade types by exposure
3. distinguish underlying-level views from volatility-surface or vega-curve views
4. show how PCA can be applied to a vega sector for relative-value screening
5. note special issues such as Asian options

## Chapter Structure Cues

From the table of contents, Chapter 19 covers:

- brief review of option pricing theory
- classification of option trades
- trade types for:
  - single underlying
  - two or more underlyings
- factor model for the vega sector
- pitfalls of vega-sector trades
- summary of option trade types and exposures
- remarks about Asian options

Figure references suggest:

- delta, theta, and option-price behavior
- breakeven curves for straddles and payer/receiver swaptions
- realized vs implied volatility histories
- classification of a volatility surface into a vega sector
- PCA on the vega sector and residual analysis

## Key Technicalities

### 1. Basic Option Valuation

At the most abstract level, an option price is:

$$
V_t = e^{-r(T-t)} \mathbb{E}_t^{\mathbb{Q}}[\text{payoff}_T]
$$

For a vanilla call:

$$
\text{payoff}_T = (S_T - K)^+
$$

The practical point is not to re-derive all of Black-Scholes, but to establish which risk dimensions matter for RV:

- delta
- gamma
- theta
- vega
- cross-underlying sensitivities for multi-underlying structures

### 2. Local PnL Approximation

A standard local approximation is:

$$
\Delta V \approx \Delta \, \Delta S + \frac{1}{2}\Gamma (\Delta S)^2 + \Theta \, \Delta t + \mathcal{V}\, \Delta \sigma
$$

where:

- $\Delta$ is delta
- $\Gamma$ is gamma
- $\Theta$ is theta
- $\mathcal{V}$ is vega

This decomposition matters because option RV is often about:

- neutralizing some sensitivities
- isolating one targeted exposure

### 3. Single-Underlying vs Multi-Underlying RV

The chapter explicitly separates:

- single-underlying trades
- two-or-more-underlyings trades

That likely means:

#### Single-underlying RV

Examples:

- realized vs implied volatility
- skew or smile dislocations
- relative richness of payer vs receiver structures on the same underlying

#### Multi-underlying RV

Examples:

- spread options
- cross-market volatility relative value
- curve or sector option structures

The practical distinction is whether the trade's PnL is driven mainly by:

- one volatility surface
- or by relative movements across several underlyings or surface points

### 4. Breakeven and Realized vs Implied Logic

The figure titles on breakeven curves and realized-versus-implied histories strongly suggest the chapter emphasizes:

- compare option premium paid to expected realized movement
- compare implied volatility to expected future realized volatility

A stylized volatility-RV logic is:

$$
\text{edge} \approx \sigma_{\text{realized, expected}} - \sigma_{\text{implied}}
$$

after adjusting for:

- carry
- convexity
- strike and expiry
- hedging path dependence

### 5. Vega Sector PCA

One of the most interesting chapter themes is the factor model for the vega sector. If the vega surface sector is represented by a data matrix $X$:

$$
\Sigma = \mathrm{Cov}(X), \qquad \Sigma v_i = \lambda_i v_i
$$

then PCA can:

- identify dominant vega-surface factors
- isolate residual relative-value trades
- distinguish broad volatility repricing from local dislocations

Residuals are again:

$$
R = X - \hat{X}
$$

This is the options analogue of Chapter 3's PCA on rates or CDS curves.

### 6. Why Vega-Sector PCA Is Useful

A trader often does not want generic long- or short-vol exposure. They want:

- a relative dislocation inside the surface
- with broad vega-sector moves hedged out

That means choosing weights $w$ so that the position is neutral to leading factors:

$$
w^\top v_1 = 0,\quad w^\top v_2 = 0,\ \dots
$$

while retaining exposure to a residual or mispriced sector shape.

### 7. Pitfalls of Vega-Sector Trades

The chapter explicitly flags pitfalls. Likely candidates are:

- unstable eigenvectors across regimes
- hidden directional exposure
- poor realized-volatility estimation
- excessive sensitivity to smile dynamics or skew shifts
- path dependence when delta-hedging assumptions are unrealistic

In options RV, "vega-neutral" or "factor-neutral" can be much less stable than it appears in-sample.

### 8. Asian Options

The chapter ends with remarks about Asian options, which suggests the authors want the reader to remember that payoff definition changes the relevant RV framework.

A simple arithmetic-average Asian call payoff is:

$$
\left(\frac{1}{T}\int_0^T S_t\,dt - K\right)^+
$$

This matters because:

- path dependence changes effective Greeks
- realized-path assumptions become more important
- naive transfer of vanilla-option intuition can fail

## Framework Summary

The chapter's practical workflow can be summarized as:

1. classify the option RV trade by exposure type
2. isolate the desired risk factor
3. hedge away unwanted underlying or vega-sector factors
4. compare implied and expected realized behavior
5. watch for instability and path-dependence pitfalls

This chapter extends the book's general RV method into derivative space while preserving the same discipline:

- define factor structure
- isolate residuals
- be explicit about what is hedged and what is not

## How It Connects to Our Practical Notebooks

There is no dedicated options-RV notebook yet in the FIRV study folder.

Closest current connections:

- [02_pca_yield_curve.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/02_pca_yield_curve.ipynb)
  for PCA mechanics that can later be transferred to a vega sector
- [ch03_notes.md](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/ch03_notes.md)
  for factor-neutral residual construction

Suggested future notebook:

- `08_options_rv.ipynb`

Possible scope:

- implied vs realized volatility comparison
- vega-sector PCA on a swaption or options subset
- residual screening
- simple breakeven analysis for selected structures

## Open Questions and Things to Verify Empirically

### Data Questions

- Do we have any local options or swaption surface data worth using, or does this chapter imply a future data-ingestion effort?
- Which options market is the most practical first target for a playground notebook?

### Factor Questions

- How stable are vega-sector PCA eigenvectors over time?
- Can factor-neutral option trades remain neutral during stressed volatility regimes?

### Implementation Questions

- How should we estimate realized volatility in a way that matches the chapter's intended trade horizons?
- Which trade type classification is most relevant for our current fixed-income playground scope?

## Immediate Next Steps

1. Leave Chapter 19 as a conceptual note for now unless options surface data becomes available.
2. If options data is added later, build a vega-sector PCA notebook.
3. Reuse Chapter 3's PCA logic as the first implementation template.
