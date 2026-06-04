# Macro Regime Overlay Design

Design note for applying a macro regime gate across FIRV signal families using locally available FRED data.

## Objective

Build a simple, reusable overlay that classifies each day into one of four macro regimes:

1. inflation shock
2. growth scare
3. stable carry
4. funding stress

Then apply that regime layer to all existing FIRV signal families so we can test whether hit rate and mean-reversion half-life improve when trades are filtered by the backdrop.

## Local Inputs

All of the following are already present in the local FRED lake:

- `SOFR`
- `DFEDTARU`
- `T10Y2Y`
- `T10Y3M`
- `T5YIE`
- `T10YIE`

Observed local coverage:

- approximately `2024-02-26` through `2026-02-27`
- `SOFR` and the spread/inflation series are aligned enough to build a usable daily overlay after forward-fill and conservative missing-data handling

## Design Principles

- Keep the regime layer interpretable
- Use only variables already available locally
- Avoid overfitting by using coarse, rule-based thresholds first
- Let the overlay be testable against each signal family rather than hard-coding trade beliefs

## Regime Variables and Intuition

### 1. Policy / funding stance

- `SOFR`
- `DFEDTARU`

Why:
- captures realized short-rate conditions
- captures policy-target anchor
- gap between the two can indicate funding dislocation or short-term stress

### 2. Growth / curve shape

- `T10Y2Y`
- `T10Y3M`

Why:
- curve inversion or aggressive flattening is a natural growth / policy stress signal
- also helps distinguish benign carry environments from late-cycle or recessionary ones

### 3. Inflation expectations

- `T5YIE`
- `T10YIE`

Why:
- rising breakevens flag inflation repricing
- falling breakevens often align with disinflationary growth scares
- front-end versus long-end inflation expectations also help gauge whether the inflation move is broad or short-lived

## Proposed Preprocessing

Before classification:

1. align all series to business-day index
2. forward-fill short missing gaps
3. compute 20-day z-scores for each raw series
4. compute 20-day or 60-day changes where relevant

Suggested derived features:

- `policy_gap = SOFR - DFEDTARU`
- `curve_signal = mean(zscore(T10Y2Y), zscore(T10Y3M))`
- `inflation_signal = mean(zscore(T5YIE), zscore(T10YIE))`
- `policy_signal = zscore(SOFR)`

## Four Regime Definitions

These should be treated as the first-pass rule set, not the final answer.

### Regime 1: Inflation Shock

**Interpretation**
- inflation expectations are rising
- policy/funding is tight or tightening
- the curve is not giving a clean recession signal yet, or is bear-flattening from rate pressure

**Rule sketch**
- `inflation_signal >= +0.75`
- `policy_signal >= +0.50`
- and `curve_signal > -1.00`

**What it means for RV**
- long-duration “reversion” trades can stay wrong longer
- level shocks contaminate local curve dislocations
- funding-adjusted signals matter more than pure curve richness

### Regime 2: Growth Scare

**Interpretation**
- curve is inverted or strongly flattening
- inflation expectations are stable to falling
- policy is not necessarily dislocated, but macro growth fear is dominant

**Rule sketch**
- `curve_signal <= -0.75`
- `inflation_signal <= +0.25`
- and `policy_gap <= +0.50 z-score equivalent`

**What it means for RV**
- classical duration and quality trades often work better
- local curve dislocations may mean revert faster if they are not funding-driven
- long-end richness may persist if flight-to-quality dominates

### Regime 3: Stable Carry

**Interpretation**
- short rates are not under stress
- inflation expectations are range-bound
- curve is not aggressively inverting or steepening

**Rule sketch**
- `abs(inflation_signal) < 0.75`
- `abs(curve_signal) < 0.75`
- `abs(zscore(policy_gap)) < 0.75`

**What it means for RV**
- mean reversion studies should be most reliable here
- PCA-neutral structures should have cleaner entry/exit behavior
- fitted-curve richness/cheapness should be less contaminated by macro regime shifts

### Regime 4: Funding Stress

**Interpretation**
- short-term funding conditions are strained relative to target
- policy gap matters more than the level of rates alone
- this is the regime where basis and ASW signals should be treated differently

**Rule sketch**
- `zscore(policy_gap) >= +1.0`
- optionally reinforced by:
  - `SOFR` elevated
  - curve strongly distorted

**What it means for RV**
- cross-currency basis and asset-swap signals should be segmented here first
- convergence may slow because arbitrage capital is balance-sheet constrained
- “cheap” on curve metrics may not mean “cheap” on funding-adjusted metrics

## Suggested Classification Procedure

For each date:

1. compute `policy_gap`, `curve_signal`, `inflation_signal`, `policy_signal`
2. assign regimes in this order:
   1. funding stress
   2. inflation shock
   3. growth scare
   4. stable carry

The ordering matters because funding stress should override broad macro labels if the short-rate plumbing is distorted.

## Existing Signal Families and Regime Gates

## Signal Family A: Chapter 2 Mean-Reversion Spreads

Examples:
- `2s5s10s` butterfly
- `DGS2 - SOFR`
- `DGS2 - DFEDTARU`
- `30s10s` or long-end curvature spreads

### Gate rule

- **Allow full-size entries in:** stable carry
- **Allow selective entries in:** growth scare
- **Reduce size or raise entry threshold in:** inflation shock
- **Usually block or heavily discount in:** funding stress

### Why

- stable carry is the cleanest environment for OU-style decay
- growth scare can still support local curve reversion, but long-duration richness can persist
- inflation shock creates trend contamination
- funding stress breaks the assumption that dislocations close quickly

### Expected improvement

- **Hit rate:** +5 to +10 percentage points versus unconditional signals
- **Estimated half-life:** 10% to 20% shorter for accepted trades in stable carry

### Best first test

- compare `MR-1` and `MR-2` signal hit rate across the four regimes

## Signal Family B: Chapter 3 PCA Residual and PCA-Neutral Trades

Examples:
- single-tenor PCA residual snapback
- PCA-neutral `2Y/5Y/10Y` butterfly
- factor-instability filtered structures

### Gate rule

- **Allow in:** stable carry
- **Allow with tighter stability filter in:** growth scare
- **Require stronger residual z-score threshold in:** inflation shock
- **Block if factor geometry is unstable or policy gap is extreme in:** funding stress

### Why

- PCA assumes factor structure is informative and reasonably stable
- inflation and funding shocks can rotate the factor structure abruptly
- growth-scare periods can still preserve usable factor structure if eigenvectors remain stable

### Expected improvement

- **Hit rate:** +7 to +12 percentage points for residual trades after filtering
- **Estimated half-life:** 15% to 25% shorter when signals are taken only in stable carry / stable-factor windows

### Best first test

- split the `PCA-2` trade by regime and compare z-score reversion speed

## Signal Family C: Fitted-Curve Richness / Cheapness

Examples:
- daily fitted residuals by tenor
- Chapter 9 combined PCA + fitted-curve screen

### Gate rule

- **Prefer in:** stable carry
- **Allow in:** growth scare, but separate long-end from belly signals
- **Discount in:** inflation shock
- **Interpret very cautiously in:** funding stress

### Why

- fitted-curve residuals are strongest when broad macro repricing is not dominating the entire curve
- in funding stress, a tenor can look cheap for structural reasons unrelated to expected quick convergence

### Expected improvement

- **Hit rate:** +6 to +10 percentage points
- **Estimated half-life:** 10% to 20% shorter in stable carry, especially for belly-tenor residuals

### Best first test

- once fitted residuals exist, compare fitted-only versus regime-gated fitted residuals

## Signal Family D: Asset Swap and Funding-Linked Signals

Examples:
- ASW mean reversion
- SOFR-adjusted bond cheapness
- fitted-versus-funding-adjusted disagreement

### Gate rule

- **Do not treat stable carry as the only “good” regime**
- **Segment first by:** funding stress versus non-funding stress
- **Then refine by:** inflation shock and growth scare

### Why

- these signals are fundamentally about funding and balance-sheet conditions
- ignoring the regime is likely to mix together two different processes:
  - fair-value convergence
  - balance-sheet / funding repricing

### Expected improvement

- **Hit rate:** +10 to +15 percentage points once ASW data exists
- **Estimated half-life:** highly regime-dependent; can improve materially in non-stress windows, but more importantly should prevent false expectations of fast convergence in stress

### Best first test

- once ASW data is ingested, compare half-life estimates by funding regime before any trade filtering

## Signal Family E: Cross-Currency Basis

Examples:
- basis-widening / basis-closing trades
- FX-hedged foreign bond carry screens

### Gate rule

- **Primary split:** funding stress versus non-stress
- **Secondary split:** inflation shock versus growth scare

### Why

- cross-currency basis is most directly linked to funding conditions
- macro regime matters, but funding stress is the first-order gate

### Expected improvement

- **Hit rate:** +10 to +20 percentage points by avoiding trades that assume fast convergence during dollar funding stress
- **Estimated half-life:** better interpreted rather than universally reduced; the main gain is avoiding wrong convergence assumptions

## Signal Family F: Options Surface / Vega-Sector RV

Examples:
- implied-vol surface residual trades
- vega-bucket mean reversion

### Gate rule

- **Allow in:** stable carry
- **Selective in:** growth scare
- **Discount in:** inflation shock
- **Block or widen thresholds in:** funding stress

### Why

- vol-surface dislocations can mean revert, but shock regimes often reshape the entire surface rather than producing local anomalies
- stable carry should give the cleanest factor-residual framework

### Expected improvement

- **Hit rate:** +8 to +12 percentage points once surface data exists
- **Estimated half-life:** 10% to 20% shorter for accepted trades in quiet regimes

## Implementation Plan

### Step 1: Build the regime panel

Create a panel with:
- raw levels
- 20d z-scores
- 20d or 60d changes
- assigned regime label

### Step 2: Attach regime labels to signal histories

For each existing notebook signal:
- join by date
- compute hit rate and half-life by regime

### Step 3: Compare unconditional versus gated results

For each signal family, report:
- baseline hit rate
- gated hit rate
- baseline half-life
- gated half-life
- signal count reduction

## Success Criteria

This overlay is useful if it does one or more of the following:

- raises hit rate by at least 5 percentage points for local curve signals
- shortens realized half-life materially in accepted regimes
- identifies funding stress as a regime where convergence assumptions should be relaxed
- provides one common macro language across Chapters 2, 3, 8, 12, 15, 17, and 19

## Recommended Next Build Order

1. implement the regime panel as a reusable helper notebook or study utility
2. test it first on:
   - `MR-1` 2s5s10s OU signal
   - `PCA-2` PCA-neutral butterfly
3. then attach it to:
   - fitted-curve residuals
   - future ASW and CCBS studies once data is added
