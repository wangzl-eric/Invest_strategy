---
type: concept
id: CONCEPT-003
slug: risk-contribution-vs-capital-weight
domain: portfolio
status: stable
sources: 1
---

# CONCEPT-003 · risk contribution vs capital weight

**Definition.** The share of a portfolio's *risk* carried by a sleeve is not its share of *capital*.
Capital weights systematically understate the high-volatility sleeve, and the distortion scales with
the square of the volatility ratio. This is an accounting identity, not an empirical claim.

## The math

For two sleeves with weights $w_i$, volatilities $\sigma_i$ and correlation $\rho$, sleeve $i$'s
marginal contribution to risk is

$$\mathrm{MCR}_i = w_i\,\frac{\partial \sigma_p}{\partial w_i} = \frac{w_i\left(w_i\sigma_i^2 + w_j\rho\,\sigma_i\sigma_j\right)}{\sigma_p}$$

Ignoring correlation, variance shares go as $w_i^2\sigma_i^2$. So if $\sigma_1 = k\,\sigma_2$, the
high-vol sleeve's variance share is understated by roughly $k^2$. At $k = 3$ — equity vol ≈ 3x bond
vol — a **60/40 portfolio is ≈ 90% equity risk**. The "balanced" label describes the capital, not the
exposure.

**The derivation is the transferable part.** It applies unchanged one level down: sector, country and
factor weights lie in exactly the same way, and that within-sleeve extension is the half the platform
does not currently compute.

## Why the mis-labelling persists

Nobody is on the other side of an identity — what persists is the *naming*. Institutional policy
portfolios, IPS documents and peer-group benchmarks are written in capital terms, so a
benchmark-relative allocator is mandated to a number that does not describe the risk held and has **no
permission to restate it**. The constraint is documentary and moves on decade timescales, which is why
an arithmetic point that has been public for decades still describes how most money is allocated.

## The unstated collateral

Any risk-balanced construction is **economically short the stock-bond correlation**. The identity
above is exact; the *usefulness* of equalising risk contribution depends entirely on the correlation
staying where it was. Naming that assumption converts a framework argument into a stress-testable one —
and the source note never named it. See [IDEA-001](../../reports/IDEAS.md#idea-001).

## How to measure it here

| Route | Status |
|---|---|
| `risk_parity_optimize`, `risk_contribution` in [`advanced_analytics.py`](../../../../alpha_research/portfolio/advanced_analytics.py) | **present and verified** (lines ~227 and ~250) |
| `SPY` `TLT` `IEF` `GLD` | **resolve** |
| `TIP`, `DBC` | do **not** resolve — registry lines |
| Rolling 60d / 252d covariance | trivially computable from the lake |

Nothing blocks this. It is a report-and-render gap rather than a research gap: our own backtest reports
emit **no per-sleeve contribution table at all**, which is the same omission
[IDEA-028](../../reports/IDEAS.md#idea-028) says makes a claim un-auditable.

## Where it fails

- **It is a measurement correction, not an edge.** Restating weights earns nothing; the premium for
  *exploiting* the imbalance is a separate claim — [[CONCEPT-004-leverage-aversion]].
- Risk contribution is only as stable as the covariance matrix, and covariance is least stable exactly
  when it matters.
- Equalising *variance* contribution is not equalising *drawdown* contribution; higher moments are
  outside the identity entirely ([[CONCEPT-002-volatility-risk-premium]]).

## What it underpins

[IDEA-004](../../reports/IDEAS.md#idea-004) · [IDEA-001](../../reports/IDEAS.md#idea-001) ·
[IDEA-025](../../reports/IDEAS.md#idea-025) · [IDEA-008](../../reports/IDEAS.md#idea-008) ·
[VERDICT-007](../VERDICTS.md#verdict-007)

## Related

[[CONCEPT-004-leverage-aversion]] — the premium that makes the correction actionable ·
[[CONCEPT-005-effective-sample-size]] — the same "the label overstates what you have" move, applied to
sample size

## Sources

[bridgewater2012](../../papers/paper_notes_bridgewater2012.md)

*Provenance caution: single-source, and the source is the originator of the product it advertises. It
presents only descriptive statistics — vol ratios, taxonomies, quadrant maps — and no inferential ones,
which tells you where its author declined to look.*
