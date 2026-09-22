---
type: concept
id: CONCEPT-005
slug: effective-sample-size
domain: method
status: stable
sources: 2
---

# CONCEPT-005 · effective sample size (effective breadth)

**Definition.** The number of *independent* observations a strategy actually has, which is strictly less
than the number of observations it reports whenever those observations are correlated. Breadth offered
in place of a mechanism must be discounted by the strategy's own cross-market position correlation.

## The math

For $N$ markets with average pairwise correlation $\bar\rho$ among the *positions* (not the assets):

$$N_{\text{eff}} = \frac{N}{1 + (N-1)\bar\rho}$$

At $\bar\rho = 0.3$ and $N = 67$, $N_{\text{eff}} \approx 3.3$. **Sixty-seven markets can be three
independent bets.** The same collapse applies along the time axis when a signal is slow: a 12-month
lookback rebalanced monthly does not deliver 12 independent decisions a year.

Everything downstream inherits the error. A $t$-statistic scales as $\sqrt{N}$, so overstating $N$ by
20x overstates $t$ by ~4.5x — and deflated Sharpe, PSR and MinBTL all consume the sample size as an
input.

## The sharp version

**A strategy's hedge value and its statistical independence are in direct tension.** Crisis alpha
exists *because* all sleeves go short together — which is precisely the property that collapses
effective breadth. You cannot claim both at full strength. "67 markets × 135 years" is not 9,000
independent observations for a strategy that holds the same directional bet everywhere at once.

## Why the error persists

Breadth is rhetorically persuasive, and computing $N_{\text{eff}}$ requires the **position matrix**,
which a reader of a published note never receives. So the discount can be demanded but rarely applied
from outside. Inside our own work there is no such excuse — the positions are ours.

## How to measure it here

| Route | Status |
|---|---|
| [`cross_validation.py`](../../../alpha_research/backtests/stats/cross_validation.py) | **present** |
| `minimum_backtest.py`, `multiple_testing.py` in `backtests/stats/` | **present** |
| Position matrices from `backtests/runners/*` | **present** — `sector_rotation.py`, `vol_conditioned_reversal.py` |
| The adjustment itself | **not wired** — the stats consume nominal, not effective, sample size |

Fully implementable against existing code. This is a gate to add, not a dataset to acquire — the
concrete change is feeding $N_{\text{eff}}$ into the deflated-Sharpe / MinBTL inputs.

**Caution on our own review pipeline:** what it calls "walk-forward" is `np.array_split` segment Sharpe,
not purged k-fold CV. Purged CV lives only in the ML-signal path. Segment Sharpe on adjacent splits is
exactly where correlated-sample optimism hides.

## Where it fails

- It **corrects** a claim rather than generating one — no counterparty, no premium.
- $\bar\rho$ is itself estimated, and it is unstable in the regimes where it matters.
- Not verifiable against an external note whose position data is unpublished — you can demand the
  discount without being able to compute it.

## What it underpins

[IDEA-018](../../reports/IDEAS.md#idea-018) — the implementable version, with a code path ·
[IDEA-041](../../reports/IDEAS.md#idea-041) — count independent *estimates*, not outputs ·
[IDEA-037](../../reports/IDEAS.md#idea-037) — the breadth claim being discounted ·
[IDEA-010](../../reports/IDEAS.md#idea-010) · [VERDICT-002](../VERDICTS.md#verdict-002) —
MinBTL 3,968 years, the statistic doing its job

*The pool keeps [IDEA-018](../../reports/IDEAS.md#idea-018) and
[IDEA-041](../../reports/IDEAS.md#idea-041) deliberately unmerged: one asks how many models produced
these numbers (dependency structure), the other converts the intuition into a specific statistical
adjustment on our own strategies.*

## Related

[[CONCEPT-006-point-in-time-information]] · [[CONCEPT-009-time-series-momentum]] ·
[[CONCEPT-003-risk-contribution-vs-capital-weight]]

## Sources

[baltussen2021](../../papers/paper_notes_baltussen2021.md) ·
[asness_momentum_fact_fiction_2014](../../papers/paper_notes_asness_momentum_fact_fiction_2014.md)

*Study lane: `studies/2026-06-17_advances_financial_ml/` is the natural home for the formal treatment
(purged CV, deflated Sharpe, MinBTL) and has not yet been harvested into atoms.*
