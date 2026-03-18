# Review Lenses

The agent must ask itself what other angle would be useful before trusting a strategy. These lenses are mandatory and must be answered or explicitly marked not applicable.

## Core Lenses

- Hypothesis lens:
  What is the economic mechanism, and who is on the other side of the trade?

- Baseline lens:
  Does this beat a naive baseline such as equal-weight, buy-and-hold, or a simpler rule?

- Data timing lens:
  What exact data was known at decision time? Are releases lagged and revisions handled?

- Execution lens:
  What fill convention, rebalance convention, and slippage model are assumed?

- Cost and turnover lens:
  Does the strategy survive realistic costs, and is turnover consistent with the edge being claimed?

- Stability lens:
  Does the result survive parameter changes, window changes, and engine changes?

- Benchmark dependence lens:
  Is the result just expensive beta, benchmark timing, or a broad market effect?

- Capacity and tradability lens:
  Would the edge survive the liquidity and implementation burden implied by the portfolio?

## Archetype-Specific Priority

## `cross_sectional`

Prioritize:
- baseline lens
- benchmark dependence lens
- turnover lens
- survivorship and universe-definition checks
- factor crowding or concentration checks

## `optimizer_heavy`

Prioritize:
- optimizer dependence lens
- concentration and constraint-binding lens
- frontier sensitivity lens
- local vs `pypfopt` comparison
- turnover caused by optimizer churn

## `trend_carry`

Prioritize:
- regime robustness lens
- crash-period lens
- carry-rollover or proxy validity lens
- execution timing lens

## `overlay_risk_managed`

Prioritize:
- baseline lens
- “does the overlay add alpha or only change risk?” lens
- stressed-regime performance lens
- with-overlay vs without-overlay comparison

## `macro_lag_sensitive`

Prioritize:
- publication-lag lens
- revision-risk lens
- release-calendar alignment lens
- benchmark and regime dependence lens

## `execution_sensitive`

Prioritize:
- engine realism lens
- fill convention lens
- order-type lens
- slippage and partial-fill assumptions
- local vs validation-engine comparison

## Required Question Block

For `rigorous` and `highly-rigorous`, the report must answer these directly:

- What would a simpler strategy do here?
- What data would have been known at the decision timestamp?
- What breaks first: costs, windows, parameters, or engine assumptions?
- Is the edge coming from signal quality, optimizer behavior, or benchmark exposure?
- What evidence supports effectiveness?
- What evidence supports stability?
- What evidence directly contradicts the strategy?
