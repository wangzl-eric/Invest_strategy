# FIRV Chapter 2 Notes: Mean Reversion

## Core Concept and Author Intent

Chapter 2 introduces mean reversion as a practical relative-value framework for identifying dislocations, forecasting expected convergence, and structuring trades with explicit horizon and execution logic.

The authorial intent is not just "fit an OU process and trade z-scores." The chapter appears to build a full workflow:

1. distinguish mean reversion from random-walk behavior
2. choose an appropriate model form using diagnostics
3. estimate the process
4. convert the fitted model into conditional expectations and densities
5. evaluate ex ante, risk-adjusted opportunity
6. optimize execution rather than entering mechanically

This is the book's first serious statistical chapter, so it sets the tone for the rest of the text: relative value should be model-based, state-aware, and operationally explicit.

## Chapter Structure Cues

From the book TOC and illustration list, the chapter emphasizes:

- what mean reversion is and why it matters
- diagnostics for model selection
- model estimation
- conditional expectations and densities
- ex ante risk-adjusted returns
- execution optimization
- one integrated practical example

Examples and figures suggest the chapter works across:

- simulated random-walk vs mean-reverting processes
- a `2/5/10` USD swaps butterfly
- a volatility spread example such as `EUR 5Y5Y - GBP 5Y5Y`
- drift and diffusion diagnostics
- first-passage-time style analysis

## Key Technicalities

### 1. Mean Reversion vs Random Walk

The basic conceptual distinction is:

- random walk:
  $$
  dX_t = \sigma dW_t
  $$

- mean-reverting process:
  $$
  dX_t = \kappa(\mu - X_t)\,dt + \sigma dW_t
  $$

where:

- $X_t$ is the spread or dislocation measure
- $\mu$ is the long-run mean
- $\kappa$ is mean-reversion speed
- $\sigma$ is diffusion volatility

Interpretation:

- larger $\kappa$ means faster pull back to equilibrium
- the half-life is:
  $$
  t_{1/2} = \frac{\ln 2}{\kappa}
  $$

This matters because relative-value trades are only attractive if convergence is fast enough relative to carry, volatility, and transaction costs.

### 2. Discrete-Time Estimation

A practical implementation often starts from:

$$
X_{t+\Delta} = a + b X_t + \varepsilon_{t+\Delta}
$$

and maps it back to the OU parameters through:

$$
\kappa = -\frac{\ln b}{\Delta}, \qquad
\mu = \frac{a}{1-b}
$$

subject to the usual caveat that $b$ must be in a sensible range for the mapping to be stable.

This is the discrete scaffold we already use in the playground notebook.

### 3. Conditional Expectations and Variance

For a standard OU process, the conditional mean over horizon $h$ is:

$$
\mathbb{E}[X_{t+h}\mid X_t] = \mu + (X_t - \mu)e^{-\kappa h}
$$

and the conditional variance is:

$$
\mathrm{Var}(X_{t+h}\mid X_t) =
\frac{\sigma^2}{2\kappa}\left(1 - e^{-2\kappa h}\right)
$$

This is central to the chapter's practical use:

- expected convergence gives direction and magnitude
- conditional variance gives horizon-dependent risk
- together they produce expected risk-adjusted trade attractiveness

### 4. State-Dependent Drift and Diffusion

The chapter outline and figure titles strongly suggest the authors go beyond a constant-parameter OU and look at nonparametric drift/diffusion estimation:

$$
dX_t = \mu(X_t)\,dt + \sigma(X_t)\,dW_t
$$

This is important because many fixed-income spreads:

- mean revert only outside certain bands
- revert faster when dislocations are large
- exhibit state-dependent volatility

Practical implication:

- fitting a constant-parameter OU may be a useful baseline
- but diagnostics should test whether $\mu(x)$ and $\sigma(x)$ vary materially with state

### 5. Distribution Forecasting and First-Passage Logic

The chapter appears to connect conditional densities and first-passage-time reasoning to execution. That means the question is not just:

- "Will this spread revert?"

but:

- "What is the distribution of future spread levels over my holding horizon?"
- "What is the probability of hitting my target before my stop or horizon cutoff?"

This moves the framework from a pure signal model toward an execution model.

### 6. Ex Ante Risk-Adjusted Return

The chapter explicitly references "conditional, ex ante risk-adjusted returns." The practical structure is likely:

- expected convergence PnL over horizon $h$
- divided by some horizon-appropriate risk measure
- with execution timing and position sizing layered on top

In our language, that suggests a model-based screening metric like:

$$
\text{score}(h) =
\frac{\mathbb{E}[\Delta X_{t,h} \mid X_t]}{\sqrt{\mathrm{Var}(\Delta X_{t,h} \mid X_t)}}
$$

or a trade-level Sharpe-style proxy after carry and costs.

## Framework Summary

The chapter's practical workflow can be summarized as:

1. define a spread or dislocation series
2. test whether mean reversion is plausible
3. choose a model class
4. estimate drift and diffusion
5. compute conditional mean/variance over trade horizons
6. translate that into expected risk-adjusted return
7. optimize entry, target, stop, and holding period

This is more useful than a simple "z-score > 2" heuristic because it makes the time dimension explicit.

## How It Connects to Our Practical Notebooks

Primary notebook:

- [01_mean_reversion.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/01_mean_reversion.ipynb)

Current implementation choice:

- we use a locally available Treasury `2s5s10s` butterfly proxy
- the book example appears to emphasize a USD swap butterfly
- our current notebook is therefore structurally aligned but not yet market-identical

What the notebook currently supports:

- local data load from FRED-backed Treasury series
- spread construction
- baseline OU fit
- z-score visualization
- placeholders for drift, diffusion, and first-passage diagnostics

What Chapter 2 says we still need:

- nonparametric drift estimation
- state-dependent diffusion diagnostics
- horizon-dependent expected-value and risk calculations
- explicit execution-rule optimization

## Open Questions and Things to Verify Empirically

### Model Validity

- Does the Treasury `2s5s10s` butterfly actually exhibit stable mean reversion over the local sample?
- Is the local sample long enough to estimate a meaningful half-life?
- Are there structural breaks around policy regime changes?

### Proxy Quality

- How different is the Treasury butterfly from the book's preferred USD swap butterfly in behavior, half-life, and volatility?
- Do Treasury and swap butterflies deliver similar signals, or does swap-specific funding/credit plumbing materially change the process?

### Drift and Diffusion

- Is constant-parameter OU adequate, or is drift clearly nonlinear in the tails?
- Does volatility rise in stressed dislocation regimes, making entry thresholds nonlinear?

### Execution

- If expected convergence is positive, is it fast enough to overcome transaction costs and carry?
- Is first-passage-time analysis materially better than fixed-horizon exits?
- Does waiting for more extreme dislocations improve expected value enough to offset lower trade frequency?

### Cross-Market Extension

- Does the chapter's framework port cleanly from yield-curve butterflies to vol spreads or basis spreads?
- Which fixed-income RV structures in our data universe are plausible next candidates after the Treasury butterfly proxy?

## Immediate Next Steps

1. Extend `01_mean_reversion.ipynb` with local linear or kernel drift estimation.
2. Add horizon-dependent conditional expectation / variance tables.
3. Add a first-passage or threshold-hitting approximation.
4. Decide whether USD swap-curve ingestion is worth prioritizing for a book-faithful replication.
