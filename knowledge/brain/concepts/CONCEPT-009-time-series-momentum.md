---
type: concept
id: CONCEPT-009
slug: time-series-momentum
domain: cross-asset
status: contested
sources: 5
---

# CONCEPT-009 · time-series momentum (trend)

**Definition.** Take the sign of each market's trailing 12-month excess return as a directional signal,
size every position to a constant ex-ante volatility target, rebalance monthly, aggregate across asset
classes. Refinements to the signal add little; **breadth and risk-equalised sizing do the work.**

## The rule

$$w_{i,t} = \operatorname{sign}\!\left(r_{i,t-12 \to t}\right) \cdot \frac{\sigma_{\text{target}}}{\hat{\sigma}_{i,t}}$$

Vol scaling is what makes ~67 weakly-related versions of the same bet combinable into one portfolio.
Reported: Sharpe ≈ 0.7 over 1880–2012, ≈ 0.9 post-1985, net of estimated costs — and $R^2 > 0.9$
regressing a CTA index on this single synthetic rule.

## The latency is the mechanism, and also the limit

A deliberately slow signal only flips **after** a move has already persisted for months. The same
latency that bleeds money in choppy markets is what converts protracted repricings into profit. Two
consequences follow directly from the estimator's own arithmetic, and both are usually stated as
empirical discoveries when they are actually design parameters:

1. **Trend hedges only drawdowns longer than its lookback.** All three canonical crisis wins (1929–32,
   2000–02, 2008) are multi-month-to-multi-year declines. A 12-month lookback *cannot* flip short inside
   a one-month crash — 1987, Feb-2018 and Mar-2020 are absent from the usual discussion.
   The right question is not "does it have crisis alpha" but "does its lookback match the duration of
   the crisis I am hedging". → [IDEA-009](../../reports/IDEAS.md#idea-009)
2. **Its crisis alpha and its statistical independence are in direct tension** — the correlated
   cross-market positioning that produces the hedge is what collapses effective breadth.
   → [[CONCEPT-005-effective-sample-size]]

## Who pays

The source does **not** name a payer; its entire defence is sample breadth plus crisis behaviour. That
is worth stating plainly, because breadth is not a mechanism. Candidate payers imported from surrounding
literature — commodity producers and intervening central banks transacting on mandate rather than price,
plus investors who under-react to slow news then herd late — are real but unverified here.

The honest compensated-risk story: **trend is short reversals.** It pays an insurance-like premium in
whipsaw markets and collects in persistent ones, which is why the payoff is convex rather than smooth.

## How to measure it here

| Route | Status |
|---|---|
| `SPY` `QQQ` `TLT` `IEF` `SHY` `GLD` `USO` + seven G10 crosses | **resolve** — a four-sleeve proxy is buildable today |
| `DBC` `UUP` `EFA` `EEM` `TIP` | do **not** resolve — registry lines |
| `fx` / `commodities` / `rates_yf` bundles | start **2024-02** — history must come from the yfinance fallback |
| `DFF` | resolves — needed to convert to excess returns |
| Listed trend proxies `DBMF` `KMLM` | raise `ValueError`, free via yfinance behind one registry line |
| 67 markets × 135 years | needs Norgate / CSI / GFD / Bloomberg continuous futures — **out of reach** |

## Where it fails

- **The sample ends at publication (2013)** and the following decade of weaker trend returns is
  uncovered — the one genuinely out-of-sample decade is the one missing.
  → [[CONCEPT-006-point-in-time-information]]
- **Tested here and rejected**: [VERDICT-001](../VERDICTS.md#verdict-001) — vol-scaled momentum,
  long-only equity, −3.32% alpha vs equal-weight, IS/OOS 0.35, max DD −32%. Note *what* failed: applying
  the vol-sizing half to a single long-only sleeve discards the cross-asset breadth that the concept says
  does the work. **It was not a fair test of the concept, and it was still the right rejection of the
  strategy.**
- Momentum crashes cluster in sharp post-crisis rebounds (Daniel & Moskowitz 2016) — the reversal risk
  being sold.
- The rule is public, cheap and heavily traded; the source's own transaction-cost and capacity
  assumptions are the flagged vulnerability.

## What it underpins

[IDEA-037](../../reports/IDEAS.md#idea-037) · [IDEA-009](../../reports/IDEAS.md#idea-009) ·
[IDEA-013](../../reports/IDEAS.md#idea-013) — the fee audit: ~90% of the managed-futures industry is
this one regression in a 2-and-20 wrapper · [IDEA-018](../../reports/IDEAS.md#idea-018) ·
[IDEA-034](../../reports/IDEAS.md#idea-034) · [VERDICT-001](../VERDICTS.md#verdict-001) ·
[VERDICT-004](../VERDICTS.md#verdict-004) · [VERDICT-006](../VERDICTS.md#verdict-006)

## Related

[[CONCEPT-005-effective-sample-size]] · [[CONCEPT-007-carry-crash-asymmetry]] ·
[[CONCEPT-002-volatility-risk-premium]]

## Sources

[moskowitz_tsmom_2012](../../papers/paper_notes_moskowitz_tsmom_2012.md) ·
[hurst2013](../../papers/paper_notes_hurst2013.md) ·
[geczy2017](../../papers/paper_notes_geczy2017.md) ·
[asness_momentum_fact_fiction_2014](../../papers/paper_notes_asness_momentum_fact_fiction_2014.md) ·
[daniel_moskowitz_crashes_2016](../../papers/paper_notes_daniel_moskowitz_crashes_2016.md) ·
[baltussen2021](../../papers/paper_notes_baltussen2021.md)
