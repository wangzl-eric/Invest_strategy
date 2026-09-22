---
type: concept
id: CONCEPT-008
slug: idiosyncratic-volatility-puzzle
domain: equity
status: contested
sources: 5
---

# CONCEPT-008 · the two cross-sectional volatility effects

**Definition.** Two *empirically distinct* equity effects, routinely conflated. **VIX-beta:** stocks
whose returns load positively on VIX innovations earn ~**−1%** per month — they are priced as volatility
insurance and are structurally expensive. **IVOL:** stocks with high idiosyncratic volatility (residual
from a factor model) earn ~**−1.06%** per month — the puzzle, because it is the *opposite* of what
Merton (1987) predicts.

Both survive horse-race regressions against each other, so they are two mechanisms, not one.

## The math

VIX-beta from a two-factor time-series regression per stock:

$$r_{i,t} = \alpha_i + \beta_i^{\mathrm{MKT}} r_{m,t} + \beta_i^{\Delta \mathrm{VIX}} \Delta \mathrm{VIX}_t + \varepsilon_{i,t}$$

IVOL as the residual dispersion from a factor model within each month:

$$\mathrm{IVOL}_{i} = \operatorname{sd}\!\left(\varepsilon_{i,t}\right), \qquad \varepsilon_{i,t} = r_{i,t} - \left[\beta_i^{\mathrm{MKT}}\mathrm{MKT}_t + \beta_i^{\mathrm{SMB}}\mathrm{SMB}_t + \beta_i^{\mathrm{HML}}\mathrm{HML}_t\right]$$

**The price of aggregate volatility risk is negative**: bearing vol risk earns a positive premium,
hedging against it costs one. The IVOL side has no such clean account, which is why it is a *puzzle* and
why this concept's status is `contested`.

## The confusion to avoid

**A VIX-*level* regime overlay and a VIX-*beta* cross-sectional sort are different constructs.** The
former was tested here and rejected outright — [VERDICT-002](../VERDICTS.md#verdict-002), MinBTL 3,968
years. The latter is untested on this platform. The rejection of one says nothing about the other, and
the knowledge base flagged this explicitly as the live confusion risk. Keep them apart.

## How to measure it here

| Route | Status |
|---|---|
| IVOL: regress daily returns on FF3 within each month, take residual sd | **infrastructure ready** — `equities.parquet` |
| VIX-beta: rolling 60-month regression on market + $\Delta$VIX | **ready** — `vix_daily.parquet` + `equities.parquet` (2005+) |
| `VIXCLS` | **resolves** |
| `IVOLSignal` / `VIXBetaSignal` | **not implemented** in `backtests/strategies/signals.py` |
| Existing `VolatilitySignal` (signals.py ~line 116) | **total realised vol, not factor-adjusted IVOL** — directionally similar, theoretically imprecise |

The data is ready and the signals are not built. That last row is the trap: using the existing
`VolatilitySignal` as if it were IVOL conflates systematic and idiosyncratic variance.

## Where it fails

- **Concentrated in small-cap, illiquid names.** A large-cap-only universe attenuates the effect
  significantly (Bali & Cakici 2008; value-weighting weakens it).
- **The short leg drives most of the spread** (Stambaugh, Yu & Yuan 2015) — a long-only implementation
  loses most of the alpha, and this platform is long-only by default.
- **Net of realistic costs and short-borrow, alpha is substantially smaller** than the gross spread.
- **VIX-beta estimates are noisy** from rolling 5-year single-stock regressions — high month-to-month
  classification error.
- Lottery demand explains perhaps ~50% of IVOL (Hou & Loh 2016), so part of the "puzzle" is a preference,
  not a premium.

Taken together these are the reason to treat this as a study, not a candidate strategy: every mechanism
that makes it real also makes it hard to capture here.

## What it underpins

[IDEA-027](../../reports/IDEAS.md#idea-027) — risk attribution selects the hedge instrument ·
[IDEA-003](../../reports/IDEAS.md#idea-003) · [VERDICT-002](../VERDICTS.md#verdict-002) ·
[VERDICT-006](../VERDICTS.md#verdict-006)

## Related

[[CONCEPT-002-volatility-risk-premium]] — the time-series premium; this is its cross-sectional cousin ·
[[CONCEPT-004-leverage-aversion]] — the low-beta relative

## Sources

[ang_hodrick_xing_zhang_2006](../../papers/paper_notes_ang_hodrick_xing_zhang_2006.md) — the two-effect
paper, credibility 5/5

*Rescued from `knowledge/domains/KNOWLEDGE_VOL.md` (topic `vol-cross-section`, entries dated 2026-03-30 —
note these postdate that file's own "last updated 2026-03-19" header). Four supporting papers are cited
there with **no notes in `../papers/`**: Ang et al. 2009 (G7 international), Bali & Cakici 2008
(robustness), Stambaugh–Yu–Yuan 2015 (short-leg mechanism), Hou & Loh 2016 (lottery demand). Closing
those would move this concept from `contested` toward settled.*
