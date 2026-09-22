---
type: concept
id: CONCEPT-007
slug: carry-crash-asymmetry
domain: fx
status: stable
sources: 3
---

# CONCEPT-007 · carry and its crash

**Definition.** Carry earns the interest differential because it is **short a negatively skewed
payoff**. The crash is not a risk that happens to carry trades — the crash *is* the price of the carry.
Any carry book is therefore an insurance business, and must be evaluated as one.

## The structure

$$r_{\text{carry}} \approx \underbrace{(i_{\text{long}} - i_{\text{short}})}_{\text{collected continuously}} + \underbrace{\Delta s}_{\text{lost discontinuously}}$$

Uncovered interest parity fails on average, so the first term is not offset in expectation — but the
second arrives in rare, fast, correlated unwinds. Mean and volatility are the wrong two moments: the
distribution's third moment is where the compensation lives. See
[[CONCEPT-002-volatility-risk-premium]] for the identical shape in options.

**The cruel timing.** Implied vol is *lowest* in calm, wide-carry regimes — exactly when leveraged short
positioning is most crowded and an unwind would be most self-reinforcing. So the convexity that would
protect the book is cheapest precisely when the book most needs it and least wants to pay for it.
That is the actionable content: [IDEA-020](../../reports/IDEAS.md#idea-020).

## Who pays, and why it persists

The buyer of the insurance is the leveraged or hedging agent who must unwind during funding stress and
pays to avoid doing so at a random time. The seller is compensated for accepting that timing risk.

It persists because **a negatively-skewed payoff looks like alpha over every sample that does not
contain an unwind**, and because Sharpe-based evaluation actively rewards selling the tail.

## The funding leg is first-order

The short leg is not a residual. Switching funder changes the carry numerator *and* the volatility
denominator at once, because the dollar is the dominant common factor in EM FX variance. For an
identical MXN long, carry-to-vol was **2.07x higher funded in EUR than USD** — decomposing as 1.49x more
carry × 1.39x less vol — and EUR-funded vol was lower for 8 of 9 legible crosses.

$$\frac{\mathrm{CtV}^{\mathrm{EUR}}}{\mathrm{CtV}^{\mathrm{USD}}} = \frac{C + \Delta}{C} \times \frac{\sigma_{\mathrm{USD}}}{\sigma_{\mathrm{EUR}}}$$

with $\Delta \approx 1.46$pp pinned independently by five currencies quoted against both funders
(CZK, HUF, PLN, RON, RUB; dispersion 0.2pp). **Carry the identity, not the MXN number.**

The counterexample is instructive: TWD's EUR-funded vol was 36% *higher* — the relation fails where the
local currency is itself managed against the dollar. Strong prior, not a law.

## How to measure it here

| Route | Status |
|---|---|
| All seven G10 crosses, `DX-Y.NYB` | **resolve** or sit in `fx.parquet` |
| `USDJPY=X` | resolves, dedicated parquet, full history |
| `fx.parquet` history | starts **2024-02** — use per-pair parquets and yfinance fallback for depth |
| `USDBRL=X` | defined in `core/market_data_service.py` yet raises `ValueError` — ~15-line registry fix |
| 12m forwards / NDF points | **absent** — blocks the EM version entirely |
| FX implied vol, 25-delta risk reversals | **absent** — cannot answer "is the convexity cheap?" |

G10 runs today: rebuild each long against USD, EUR, JPY and CHF funders and compare realised Sharpe.
EM does not.

## Where it fails

- Proven at cost: [VERDICT-005](../VERDICTS.md#verdict-005) — pure carry with no momentum filter,
  Sharpe ≈ 0.3 unhedged, dominated by crash events.
- **A live defect sits in committed code**: the `fx_carry` proposal ranks on raw rate differentials
  (`carry_rank = rate_diffs.rank(axis=1, pct=True)`), a selector spanning only the observable half of
  expected return — [IDEA-019](../../reports/IDEAS.md#idea-019).
- Bid-ask eats EM carry: 2–7% of a 3–9% differential.
- Funder rotation is a *construction* improvement, not a premium — nobody pays you for it; you remove
  an uncompensated common exposure.

## What it underpins

[IDEA-020](../../reports/IDEAS.md#idea-020) · [IDEA-023](../../reports/IDEAS.md#idea-023) ·
[IDEA-003](../../reports/IDEAS.md#idea-003) · [IDEA-026](../../reports/IDEAS.md#idea-026) ·
[IDEA-011](../../reports/IDEAS.md#idea-011) · [VERDICT-005](../VERDICTS.md#verdict-005)

## Related

[[CONCEPT-002-volatility-risk-premium]] · [[CONCEPT-009-time-series-momentum]]

## Sources

[asness2013_fx](../../papers/paper_notes_asness2013_fx.md) ·
[koijen_carry_2018](../../papers/paper_notes_koijen_carry_2018.md) ·
[du_tepper_verdelhan2018](../../papers/paper_notes_du_tepper_verdelhan2018.md) ·
[fama1984](../../papers/paper_notes_fama1984.md)

*Brunnermeier–Nagel–Pedersen (2008) is the canonical carry-crash reference, cited in the `fx_carry`
proposal but with **no paper note** in `../papers/` — a gap worth closing.*
