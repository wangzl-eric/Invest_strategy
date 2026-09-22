---
type: concept
id: CONCEPT-002
slug: volatility-risk-premium
domain: vol
status: stable
sources: 4
---

# CONCEPT-002 · volatility risk premium (VRP)

**Definition.** The systematic excess of implied over subsequently-realized volatility. Selling
options earns it; buying them pays it. Empirically robust across markets and regimes — roughly
**10–20%** in rates swaptions, and persistently positive in equity index options.

## The math that decides everything

For a delta-hedged short straddle, P&L over $dt$ is quadratic in the state variable:

$$\mathrm{P\&L} \approx \tfrac{1}{2}\,\Gamma\,S^2\left(\sigma_{IV}^2 - \sigma_{RV}^2\right)dt$$

**Read the consequence, not the formula.** The payoff is *quadratic*, so it is mechanically
asymmetric — small gains most of the time, large losses rarely. A mean-variance statistic (Sharpe,
return-to-vol) is structurally blind to precisely the risk that defines the strategy. This is why
[IDEA-003](../../reports/IDEAS.md#idea-003) insists skew, kurtosis and max drawdown are mandatory
rather than supplementary columns for anything short-convexity.

## Why it exists — who pays

End users structurally **overpay for crash protection**: mandate-driven and accounting-driven hedgers
must buy protection where their reporting windows sit, and they are price-insensitive within that
constraint. The seller is the insurer and is compensated for bearing the crash. The premium is
therefore *not an anomaly to be arbitraged* — it is a risk transfer, and the tail is the price.

Persistence has a second, uncomfortable cause: performance is evaluated on Sharpe, and Sharpe rewards
selling the tail. **The metric creates the incentive.**

## The level trap

The *level* of implied vol is 70–85% explained by observable macro fundamentals (consensus forecast
dispersion for growth, inflation, policy; distance from the neutral rate). Therefore a z-score of the
level against its own history is **mostly measuring fundamentals, not the premium** — it silently
assumes fair value is constant. The harvestable signal is the residual from a fundamentals fair value:
see [[CONCEPT-001-term-premium]] for the same "residual, not level" move in rates, and
[IDEA-033](../../reports/IDEAS.md#idea-033).

Conditioning matters more than the average: return-to-vol ≈ **1.9** in the richest-and-falling quintile
vs ≈ **0.2** in the cheapest — a ~9x spread, though fitted full-sample on a proprietary model.

## How to measure it here

| Route | Status |
|---|---|
| `VIXCLS` | **resolves** |
| `vix_daily.parquet`, `vix3m_daily.parquet` | in the lake — term structure available |
| Realized vol from `SPY` / `equities.parquet` (2005+) | **resolves** |
| MOVE or swaption ATM grid | **absent** — no rates-vol series anywhere |
| Options pricing / delta-hedge P&L engine | **absent from `alpha_research/backtests`** — only `knowledge/studies/_legacy/vix_futures_options_research.ipynb` |

The equity analogue is fully testable today; the rates version is not. The missing P&L engine is one of
only two genuine *infrastructure* walls in the mechanism pool (the other being repo/OIS instruments).

## Where it fails

- **Crisis detection is not investable alpha.** Proven here at cost — see
  [VERDICT-002](../VERDICTS.md#verdict-002): the signal forecast crisis ($t = 9.45$ on Q5, crisis
  interaction $t = -3.77$) and the strategy still had spanning alpha $t = -0.18$.
- **Beta reduction is not alpha generation.** The same verdict.
- **A trailing-vol baseline is the benchmark to beat**, and VRP lost to it on every metric.
- Premium may thin toward zero when the forward curve prices little path uncertainty — though that
  reading is contested and partly circular ([IDEA-045](../../reports/IDEAS.md#idea-045), durability 1,
  the pool's low anchor).

## What it underpins

[IDEA-003](../../reports/IDEAS.md#idea-003) · [IDEA-020](../../reports/IDEAS.md#idea-020) ·
[IDEA-033](../../reports/IDEAS.md#idea-033) · [IDEA-034](../../reports/IDEAS.md#idea-034) ·
[IDEA-045](../../reports/IDEAS.md#idea-045) · [VERDICT-002](../VERDICTS.md#verdict-002) ·
[VERDICT-013](../VERDICTS.md#verdict-013)

## Related

[[CONCEPT-007-carry-crash-asymmetry]] — the FX expression of the same short-convexity shape ·
[[CONCEPT-008-idiosyncratic-volatility-puzzle]] — the cross-sectional vol effect, a *different*
construct · [[CONCEPT-009-time-series-momentum]]

## Sources

[carr_wu_vrp_2009](../../papers/paper_notes_carr_wu_vrp_2009.md) ·
[cremers_halling_weinbaum_2015](../../papers/paper_notes_cremers_halling_weinbaum_2015.md) ·
[rates_vrp](../../papers/paper_notes_rates_vrp.md) ·
[ang_hodrick_xing_zhang_2006](../../papers/paper_notes_ang_hodrick_xing_zhang_2006.md)
