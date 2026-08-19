---
type: concept
id: CONCEPT-001
slug: term-premium
domain: rates
status: contested
sources: 5
---

# CONCEPT-001 · term premium

**Definition.** The component of a long-dated bond yield that is *not* the expected average future
short rate. It is the compensation demanded for bearing duration risk, and it is the residual after
the risk-neutral expected-policy-path component is stripped out.

## The decomposition

A nominal yield splits into two economically distinct pieces:

$$y_t^{(n)} = \underbrace{\frac{1}{n}\mathbb{E}_t\!\left[\sum_{i=0}^{n-1} r_{t+i}\right]}_{\text{risk-neutral: expected policy path}} + \underbrace{\mathrm{TP}_t^{(n)}}_{\text{term premium}}$$

**This split is the whole content of the concept.** The two halves are set by different forces, move
for different reasons, and transmit across borders differently — so a yield change means nothing until
you know which half moved. A 25bp selloff driven by term premium is a different event from the same
25bp driven by repricing the central bank.

The premium is not observable. It is *model output*, which is why the status here is `contested`:
every number depends on the estimator (affine no-arbitrage, survey-based, or a shadow-rate model at
the lower bound).

## Why it exists — who bears it

Duration risk is genuinely compensated: long-dated cash flows are exposed to inflation and real-rate
shocks that a short instrument is not. The price is set in **one global pool of duration-bearing
capacity** — net issuance, fiscal expansion, QT, and mandated buyers stepping forward or back. That
global pricing is exactly why the term-premium component transmits mechanically across markets while
the risk-neutral component does not: the latter is one country's policy path, which each local
reaction function partially offsets.

## How to measure it here

| Route | Status on this platform |
|---|---|
| FRED `THREEFYTP10` (ACM 10y term premium) | public, **unregistered** — reachable, one registry line |
| NY Fed ACM daily series | public, direct download, no connector |
| `DGS2` `DGS5` `DGS10` `DGS30` | **resolve** through `get_data` |
| `DGS1`, `DGS20` | in `treasury_yields.parquet` but raise `ValueError` — registry gap |
| Survey-based (SPF) decomposition | free, unregistered |
| Nelson–Siegel / Svensson fitting | no fitted-curve module on the platform |

Practical proxy in use: `DGS10` minus `T10YIE` for a real yield, with `DFII10` preferred but currently
unreachable.

## Where it fails

- **Not identified without a model.** Different estimators disagree in level and sometimes in sign at
  the lower bound; never quote a term premium without naming the estimator.
- **Breaks under segmentation.** The global-pool argument fails where capital controls or a domestic
  mandated-buyer backstop severs a local market — observable, but you have to look.
- **Overlapping-window inference.** Rolling multi-year regressions on weekly data produce heavily
  overlapping samples and overstated $t$-statistics. The EM evidence behind
  [IDEA-007](../../reports/IDEAS.md#idea-007) has exactly this defect.

## What it underpins

- [IDEA-007](../../reports/IDEAS.md#idea-007) — foreign and EM 10y load ~3x more on the term-premium
  component than on the risk-neutral path (median $t$ 6–8 vs ~2 across 16 EMs)
- [IDEA-042](../../reports/IDEAS.md#idea-042) — free float sets the market-specific beta from supply
  to yield
- [IDEA-005](../../reports/IDEAS.md#idea-005) — issuance mix and taper locate which sector loses its
  price-insensitive bid
- [IDEA-024](../../reports/IDEAS.md#idea-024) — cyclical regressors cannot explain the long end,
  because forecast panels end before the instrument does
- [VERDICT-003](../VERDICTS.md#verdict-003) — the rejected curve strategy predated this framing and
  reached for macro timing instead

## Related

[[CONCEPT-010-free-float-and-price-insensitive-holders]] · [[CONCEPT-006-point-in-time-information]]

## Sources

[cochrane_piazzesi_2005](../../papers/paper_notes_cochrane_piazzesi_2005.md) ·
[kimwright2005](../../papers/paper_notes_kimwright2005.md) ·
[duffee2002](../../papers/paper_notes_duffee2002.md) ·
[litterman1991](../../papers/paper_notes_litterman1991.md) ·
[wuxia2016](../../papers/paper_notes_wuxia2016.md) ·
[fama1984](../../papers/paper_notes_fama1984.md)
