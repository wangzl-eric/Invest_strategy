# FIRV Chapter 15 Notes: Cross-Currency Basis Swaps

## Core Concept and Author Intent

Chapter 15 appears to treat cross-currency basis swaps as a central expression of modern fixed-income market segmentation. The chapter likely starts from the textbook covered-interest-parity intuition, then explains why real markets require a persistent basis spread to reconcile funding, collateral, and balance-sheet constraints.

The authorial intent seems to be:

1. define the CCBS cleanly
2. show its applications in funding, issuance, and hedged investment
3. explain how any reference rate can be transformed into another through basis chains
4. connect basis to structural drivers rather than treating it as an anomaly that should instantly vanish

## Chapter Structure Cues

From the table of contents, Chapter 15 covers:

- definition
- applications of CCBS
- constructing any reference rate from any other
- issuing foreign bonds without FX exposure
- investing in foreign bonds without FX exposure
- pricing of the CCBS
- impact of the transition to new reference rates

Figure references point to:

- JPY/USD and EUR/USD basis levels
- a PCA factor on JPY CCBS
- relation between CCBS and FX spot
- relation between CCBS and asset-swap differentials

That suggests the chapter mixes:

- valuation mechanics
- structural interpretation
- RV signal generation

## Key Technicalities

### 1. Covered Interest Parity Baseline

In textbook CIP, spot and forward FX are linked by interest rates:

$$
\frac{F_{t,T}}{S_t} = \frac{1+r_d(T)}{1+r_f(T)}
$$

or, in discount-factor form,

$$
F_{t,T} = S_t \frac{D_f(t,T)}{D_d(t,T)}
$$

where:

- $S_t$ is spot FX
- $F_{t,T}$ is forward FX
- $D_d$ and $D_f$ are domestic and foreign discount factors

In frictionless markets, no additional basis should be needed.

### 2. Cross-Currency Basis as a Pricing Wedge

In practice, CCBS pricing requires an additional spread $b$ on one leg so the package prices to zero:

$$
PV(\text{domestic leg}) = PV(\text{foreign leg converted via FX and basis})
$$

Conceptually, one can think of the forward relation being modified by a basis term:

$$
\frac{F_{t,T}}{S_t} \approx \frac{D_f(t,T)}{D_d(t,T)} e^{-b(T-t)}
$$

under a simplified continuous-compounding approximation.

The exact implementation depends on conventions, reset structures, and discounting, but the practical point is:

- $b \neq 0$ measures a persistent wedge between idealized CIP and actual funding markets

### 3. CCBS Applications

The chapter structure suggests three practical applications:

#### Constructing one reference rate from another

CCBS lets practitioners move from:

- domestic funding
- into foreign funding
- and back into desired reference-rate exposure

#### Issuing foreign bonds without FX exposure

A borrower can:

1. issue in foreign currency
2. swap proceeds back into domestic funding
3. compare all-in funding after basis adjustment

#### Investing in foreign bonds without FX exposure

An investor can:

1. buy foreign bonds
2. hedge FX risk via forwards / basis swaps
3. compare hedged yield versus domestic alternatives

That is why CCBS is so important for RV: it turns international bond comparison into a curve-and-basis problem, not just a yield comparison.

### 4. Structural Drivers of CIP Deviations

The user specifically asked for structural drivers, and the chapter framing strongly supports that emphasis. Persistent basis can reflect:

- balance-sheet scarcity
- regulatory capital constraints
- collateral asymmetry
- hedging demand from issuers or investors
- safe-asset scarcity in one currency
- segmentation across money-market and derivatives funding channels

This is the key practical lesson: CCBS is not just a temporary "mispricing." It is often equilibrium pricing under constrained arbitrage.

### 5. Factor Structure and PCA

The figure list includes a PCA factor on JPY CCBS, suggesting the chapter uses factor decomposition to understand basis dynamics.

For a matrix of basis quotes $X$ by tenor or currency pair:

$$
\Sigma = \mathrm{Cov}(X), \qquad \Sigma v_i = \lambda_i v_i
$$

This allows the analyst to separate:

- broad basis-market regime shifts
- pair-specific or tenor-specific residual dislocations

That is valuable for screening relative-value opportunities within basis markets.

### 6. Relationship to Asset Swaps and Bond Markets

The later chapters in the book connect CCBS to asset swaps and global bond RV. Conceptually, hedged foreign-bond value depends on:

$$
\text{hedged yield} \approx \text{local bond yield} + \text{asset swap adjustment} + \text{basis adjustment}
$$

up to convention and package specifics.

So CCBS belongs inside a larger equilibrium system:

- local bond pricing
- swap spreads
- basis swaps
- credit risk

### 7. Transition to New Reference Rates

The TOC explicitly mentions the transition to new reference rates. That matters because:

- old LIBOR-linked basis and new SOFR-linked basis are not identical objects
- discounting and floating-leg conventions changed
- pre- and post-transition histories are not always directly comparable

So any empirical work on basis must be explicit about:

- which reference rates are on each leg
- what discounting convention is assumed
- where structural breaks enter the data

## Framework Summary

The chapter's practical workflow can be summarized as:

1. start from CIP as the clean benchmark
2. introduce basis as the market-clearing wedge
3. use CCBS to compare funding and investment opportunities across currencies
4. interpret the basis structurally, not just statistically
5. combine basis analysis with swap and bond RV analysis

## How It Connects to Our Practical Notebooks

Primary notebook:

- [05_cross_currency_basis.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/05_cross_currency_basis.ipynb)

Secondary links:

- [04_asset_swaps.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/04_asset_swaps.ipynb)
  because later equilibrium logic combines asset swaps and basis
- [02_pca_yield_curve.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/02_pca_yield_curve.ipynb)
  for factor-analysis methods that may carry over to basis surfaces

Current notebook reality:

- we only have FX spot and USD funding proxies locally
- we do not yet have FX forwards, foreign OIS curves, or actual CCBS quotes

That means the current notebook is a structural placeholder, not a proper empirical replication yet.

## Open Questions and Things to Verify Empirically

### Data Questions

- Which CCBS series can realistically be sourced next for EUR/USD and JPY/USD?
- Do we also need foreign OIS curves and FX forwards before the notebook becomes useful?

### Structural Questions

- Which part of observed basis is best understood as balance-sheet cost rather than arbitrage opportunity?
- How stable are basis factors across reference-rate transitions?

### RV Questions

- Once data exists, can PCA isolate pair-specific basis dislocations cleanly?
- How tightly do CCBS moves co-move with asset-swap differentials and FX spot changes?

## Immediate Next Steps

1. Keep [05_cross_currency_basis.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/05_cross_currency_basis.ipynb) as the implementation anchor for this chapter.
2. Build a data-ingestion wish list for FX forwards, foreign OIS curves, and CCBS quotes.
3. Later, connect Chapter 15 directly to Chapters 12 and 16 in a joint note or notebook.
