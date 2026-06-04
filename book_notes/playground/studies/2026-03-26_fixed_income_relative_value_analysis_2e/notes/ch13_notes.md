# FIRV Chapter 13 Notes: Credit Default Swaps and Intra-Currency Basis

## Core Concept and Author Intent

This note combines the book's Chapter 13 on credit default swaps and Chapter 14 on intra-currency basis swaps, because in practice both topics sit inside the same broader question: how to read and trade relative pricing across closely related fixed-income instruments that should be linked by funding, credit, and term-structure structure.

The authorial intent appears to be:

1. explain CDS as a credit-risk transfer instrument and RV signal source
2. show how PCA can be applied to CDS curves and sovereign universes
3. explain intra-currency basis swaps as pricing wedges between reference-rate legs inside one currency
4. treat both as building blocks for more complex spread and basis relationships later in the book

This is where the book's fixed-income RV framework expands beyond government yield curves into credit and basis plumbing.

## Chapter Structure Cues

From the table of contents:

- Chapter 13:
  - structure of a CDS
  - trading CDS versus other CDS and versus bonds
  - PCA on the CDS curve
  - PCA on EUR sovereign CDS
  - PCA on risk-free bond yields
  - pitfalls
- Chapter 14:
  - definition of intra-currency basis swaps
  - pricing of ICBS
  - role as building blocks

Figure references suggest:

- CDS curve PCA
- sovereign CDS factor structure
- one-factor residuals
- EURIBOR basis spreads
- relation between basis swaps, FX, and futures-based proxies

## Key Technicalities

### 1. CDS as a Credit-Risk Pricing Instrument

A CDS is conceptually a contract in which:

- the protection buyer pays a periodic premium
- the protection seller pays compensation if a credit event occurs

Under a standard reduced-form setup with hazard rate $\lambda(t)$ and recovery $R$, the premium leg and protection leg satisfy:

$$
PV_{\text{premium}} = S \sum_i \alpha_i D(t_i) Q(\tau > t_i)
$$

$$
PV_{\text{protection}} = (1-R)\int_0^T D(t)\, dQ(\tau \le t)
$$

where:

- $S$ is the CDS spread
- $\alpha_i$ are accrual fractions
- $D(t)$ is the discount factor
- $Q(\tau > t)$ is survival probability

At par, these two legs are equal.

In a flat-intensity approximation, a rough relation is:

$$
S \approx (1-R)\lambda
$$

This is useful for intuition, but not a substitute for proper curve construction.

### 2. CDS vs Bonds and Other CDS

The chapter title implies the authors want the practitioner to compare:

- a CDS against another CDS on the same issuer but different tenor
- a CDS against a bond or asset-swapped bond

This is a classic relative-value problem because each instrument reflects:

- credit risk
- liquidity
- funding
- deliverability / contractual features

The key lesson is likely that a quoted spread is not a pure credit object. It is a package of credit plus market structure.

### 3. PCA on CDS Curves and Sovereign Universes

The book explicitly applies PCA to CDS structures. For a matrix of CDS quotes $X$ across maturities or issuers:

$$
\Sigma = \mathrm{Cov}(X)
$$

and

$$
\Sigma v_i = \lambda_i v_i
$$

The resulting factors can be used to:

- decompose systemic versus idiosyncratic credit moves
- identify residual dislocations along the CDS curve
- separate market-wide stress from issuer-specific richness / cheapness

Residuals take the usual factor-model form:

$$
R = X - \hat{X}
$$

with $\hat{X}$ the reconstruction from leading factors.

This aligns directly with the PCA logic from Chapter 3, but now applied in credit space.

### 4. Intra-Currency Basis Swaps

An intra-currency basis swap exchanges two floating-rate legs in the same currency, for example:

- 3M Euribor vs 6M Euribor
- 3M SOFR-style exposure vs another money-market reference

At inception, the basis spread $b$ is set so the package has zero net present value:

$$
PV(\text{Leg A} + b) = PV(\text{Leg B})
$$

or equivalently:

$$
PV_{\text{A}} + PV_{\text{basis}} - PV_{\text{B}} = 0
$$

This basis spread captures a wedge between two rates that should not be thought of as purely mechanical. It reflects:

- credit or bank-risk differences
- liquidity differences
- collateral and balance-sheet effects
- expectation mismatches across tenors

### 5. ICBS as a Building Block

The Chapter 14 subtitle "role as building blocks" matters. Intra-currency basis swaps are not just standalone instruments. They are components in:

- swap-spread relationships
- cross-currency construction chains
- synthetic reference-rate transformations

That means RV analysts need to understand them even if they do not trade them directly.

### 6. One-Factor and Residual Thinking in Credit / Basis Space

The figure references to one-factor residuals strongly suggest the authors use factor stripping as a screening tool:

$$
X_t = B f_t + \varepsilon_t
$$

where:

- $f_t$ captures broad credit or basis-market structure
- $\varepsilon_t$ captures candidate relative-value dislocations

This is especially useful in sovereign CDS and term-structure analysis, where common stress can dominate raw spread moves.

### 7. Pitfalls

Likely pitfalls in this chapter cluster include:

- treating CDS spread as identical to bond spread
- ignoring contract conventions and deliverability details
- over-interpreting PCA residuals without accounting for liquidity
- treating basis as purely technical instead of structurally driven

## Framework Summary

The practical framework across CDS and intra-currency basis is:

1. identify the relevant pricing legs and conventions
2. separate common-factor structure from residual mispricing
3. compare like-for-like tenors and hedged packages
4. interpret residuals as candidate RV, not as immediate truth
5. remember that basis markets are building blocks for later spread relationships

## How It Connects to Our Practical Notebooks

Closest current notebooks:

- [02_pca_yield_curve.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/02_pca_yield_curve.ipynb)
  for factor decomposition logic
- [04_asset_swaps.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/04_asset_swaps.ipynb)
  because CDS and asset swaps become directly comparable later in the book
- [05_cross_currency_basis.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/05_cross_currency_basis.ipynb)
  because intra-currency basis is a conceptual precursor to CCBS

There is no dedicated CDS or intra-currency-basis notebook yet.

Natural future notebook ideas:

- `06_cds_curve_pca.ipynb`
- `07_intra_currency_basis.ipynb`

## Open Questions and Things to Verify Empirically

### Data and Build Questions

- Do we have any local CDS or intra-currency basis histories, or do these chapters imply a future ingestion project?
- Which markets are easiest to source first: sovereign CDS, swap-curve basis, or money-market tenor basis?

### Relative-Value Questions

- How stable are CDS PCA factors through crisis and post-crisis periods?
- Are CDS residual dislocations better mean-reversion candidates than bond-spread residuals?

### Plumbing Questions

- Which share of intra-currency basis is credit, which is liquidity, and which is regulation / balance-sheet driven?
- How much of later cross-currency basis interpretation depends on first understanding intra-currency wedges?

## Immediate Next Steps

1. Decide whether CDS and basis data justify ingestion into the local lake.
2. If yes, prioritize a simple sovereign CDS panel and one intra-currency basis time series.
3. Reuse Chapter 3 PCA infrastructure once CDS curve data exists.
