# VERDICTS — what we tried and what happened

*Append-only record of tested outcomes. Rescued 2026-08-18 from
`memory/knowledge/KNOWLEDGE_{EQUITY,FX,MACRO,VOL}.md` (41 failure-mode lines, 22 verdict lines,
heavily duplicated) and reconciled against `alpha_research/research/STRATEGY_TRACKER.md` and the live
pool (`python -m alpha_research.pool list`), which are the authorities where they disagree.*

> **Why this file is the most valuable layer in the brain.** A mechanism is a hypothesis; a verdict is
> a receipt. These 13 records cost multi-round PM reviews to obtain and were sitting in a knowledge base
> whose intake had never been installed. `VERDICT-NNN` IDs are permanent.

---

## The two patterns

Compressing 13 verdicts loses almost nothing, because they fail in only two ways:

**1. Five of thirteen never got tested at all — they died on data access, not on economics.**
[VERDICT-003](#verdict-003), [VERDICT-004](#verdict-004), [VERDICT-008](#verdict-008),
[VERDICT-009](#verdict-009), [VERDICT-010](#verdict-010). Not one was rejected because its idea was
bad; each was rejected because a series, a sector classification, a fundamentals pipeline or an account
permission was missing. **The binding constraint on this platform's research has been data reach, not
idea quality** — which is the same conclusion the mechanism pool's calibration record reaches from the
other direction (no idea scored testability 1; the modal 3 is registry wiring, not proprietary data).
The operational read: *cost the data before costing the research*, and treat a registry gap as a
one-line fix rather than a rejection.

**2. Of the two that were properly tested, both died the same death — a risk-reduction mechanism
mistaken for an alpha source.** [VERDICT-001](#verdict-001) and [VERDICT-002](#verdict-002). Vol
targeting and a VIX regime overlay both reduced drawdown, and in both cases the reduction was
mechanical from lower average exposure — reproducible with a cash allocation and worth no fee. The rule
extracted: **an overlay must be shown to add alpha, not to subtract risk**, benchmarked from round one
against both equal-weight and a trailing-vol baseline. See [[CONCEPT-002-volatility-risk-premium]] and
[[CONCEPT-009-time-series-momentum]] for the machinery each was built on.

---

## The record

<a id="verdict-001"></a>
### VERDICT-001 · vol_scaled_momentum — REJECTED

`equity` · 2026-03-15 · rejected after **3 rounds** · [`vol_scaled_momentum_2026-03-13_rejected`](../../../alpha_research/research/strategies/vol_scaled_momentum_2026-03-13_rejected/proposal.md)

**Numbers.** −3.32% alpha vs equal-weight · IS/OOS ratio 0.35 · max drawdown −32%.

**Why it failed.** Vol scaling did not fix crash risk for a long-only equity book, because a
backward-looking vol estimate cannot react to a sudden shock — it begins cutting exposure only after
the drawdown is underway. The drawdown reduction it did deliver was mechanical from lower average
exposure. Separately, mean-variance optimisation under tight constraints added noise rather than alpha;
ranking-based allocation dominated it.

**Transferable lesson.** Benchmark against equal-weight from round one — this was missed until round
three, and it was decisive. Drawdown reduction is not alpha: if a cash allocation reproduces the
effect, there is no edge to pay for.

**Bears on.** [[CONCEPT-009-time-series-momentum]] · [IDEA-009](../reports/IDEAS.md#idea-009)
(hedge efficacy scales with crash duration — the same latency argument, reached from a book)
· [IDEA-037](../reports/IDEAS.md#idea-037)

<a id="verdict-002"></a>
### VERDICT-002 · vix_regime (VRP + term structure) — REJECTED

`vol` · 2026-03-15 · rejected after **2 rounds** · [`vix_regime_2026-03-15_rejected`](../../../alpha_research/research/strategies/vix_regime_2026-03-15_rejected/pm_review.md)

**Numbers.** MinBTL = **3,968 years** — statistically indistinguishable from chance · spanning alpha
t = −0.18 after controlling for market beta and momentum · VIX overlay cut Sharpe 0.503 → 0.206
(−59%) · signal *did* have predictive content (Q5 t = 9.45; crisis interaction t = −3.77).

**Why it failed.** The strongest single lesson in the file: **predictive signal content did not
translate into tradeable alpha.** The signal genuinely forecast crisis, and the strategy still had no
incremental alpha, because beta reduction is not alpha generation. It was also dominated on *every*
metric by a simple trailing-volatility baseline, so even the risk-management case did not survive.

**Transferable lesson.** Always run the regime signal against a trailing-vol baseline before believing
it. Require a minimum improvement (+0.15 Sharpe was the standard set) from any overlay. Position-sizing
overlays carry a structural headwind in a secular bull market — being out of the market has a cost that
is invisible in drawdown statistics.

**Do not confuse this with the cross-sectional sort.** A VIX-*level* regime overlay (rejected here) and
a VIX-*beta* cross-sectional sort ([[CONCEPT-008-idiosyncratic-volatility-puzzle]]) are different
constructs; the KB flagged this explicitly and it remains the live confusion risk.

**Bears on.** [[CONCEPT-002-volatility-risk-premium]] · [IDEA-003](../reports/IDEAS.md#idea-003) ·
[IDEA-031](../reports/IDEAS.md#idea-031) · [IDEA-045](../reports/IDEAS.md#idea-045)

<a id="verdict-003"></a>
### VERDICT-003 · yield_curve steepener/flattener — REJECTED

`rates` · 2026-03-13 · [`yield_curve_2026-03-13_rejected`](../../../alpha_research/research/strategies/yield_curve_2026-03-13_rejected/proposal.md)

**Why it failed.** Insufficient data depth, and no alpha source identifiable beyond macro timing.
A data-reach rejection, not an economic one.

**Standing note.** The mechanism pool has since produced curve ideas with named counterparties that
this verdict did not consider — [IDEA-005](../reports/IDEAS.md#idea-005) (issuance mix plus taper
locates the squeezed sector from public calendars) and [IDEA-007](../reports/IDEAS.md#idea-007) (term
premium vs risk-neutral transmission). **Neither is testable on JGBs here, but the US transposition
is reachable.** If curve work is revisited, it should start from those rather than from macro timing.

**Bears on.** [[CONCEPT-001-term-premium]] · [[CONCEPT-010-free-float-and-price-insensitive-holders]]

<a id="verdict-004"></a>
### VERDICT-004 · commodity_momentum + inflation — REJECTED

`commodities` · 2026-03-13 · [`commodity_momentum_2026-03-13_rejected`](../../../alpha_research/research/strategies/commodity_momentum_2026-03-13_rejected/proposal.md)

**Why it failed.** Insufficient data and implementation complexity. Again data reach, not economics.

**Standing note.** `DBC`, `UUP`, `EFA`, `EEM` and `TIP` are confirmed *physically present or definable*
yet raising `ValueError` through `get_data` — a registry gap of roughly one line each in
[`ticker_map.py`](../../../alpha_research/quant_data/ticker_map.py), not a data gap. The commodity
literature is also unusually strong ([[CONCEPT-009-time-series-momentum]]).

**Bears on.** [IDEA-037](../reports/IDEAS.md#idea-037) · [IDEA-013](../reports/IDEAS.md#idea-013)

<a id="verdict-005"></a>
### VERDICT-005 · fx_carry + momentum — CONDITIONAL

`fx` · 2026-03-13 · conditional after **1 round** · [`fx_carry_2026-03-13_conditional`](../../../alpha_research/research/strategies/fx_carry_2026-03-13_conditional/proposal.md)

**Numbers.** Pure carry, unhedged: Sharpe ≈ 0.3, dominated by crash events.

**Condition.** Pure carry with no momentum filter is exposed to crash risk and was not approvable
standalone.

**Live defect found later, from the reports lane.** The proposal ranks on raw rate differentials —
`carry_rank = rate_diffs.rank(axis=1, pct=True)` — which is exactly the construction
[IDEA-019](../reports/IDEAS.md#idea-019) identifies as a selector that fails to span total expected
return, and [IDEA-023](../reports/IDEAS.md#idea-023) shows the funding leg is a first-order choice the
signal does not expose at all. **This verdict is the clearest case in the brain of a report idea
landing directly on committed code.**

**Bears on.** [[CONCEPT-007-carry-crash-asymmetry]] · [IDEA-003](../reports/IDEAS.md#idea-003) ·
[IDEA-019](../reports/IDEAS.md#idea-019) · [IDEA-023](../reports/IDEAS.md#idea-023) ·
[IDEA-026](../reports/IDEAS.md#idea-026)

<a id="verdict-006"></a>
### VERDICT-006 · equity_momentum (cross-sectional) — CONDITIONAL

`equity` · 2026-03-13 · conditional after **3 rounds** · [`equity_momentum_2026-03-13_conditional`](../../../alpha_research/research/strategies/equity_momentum_2026-03-13_conditional/proposal.md)

**Status.** Conditional, awaiting a full round-one with proper factor analysis (alphalens-reloaded was
installed for this). Cross-sectional 12−1 momentum is among the most replicated factors, so the open
question was never existence but implementation in a highly efficient large-cap universe.

**Standing caution.** US large-cap is efficient enough that any claimed Sharpe above 1.0 requires
extraordinary evidence.

**Bears on.** [[CONCEPT-009-time-series-momentum]] · [[CONCEPT-005-effective-sample-size]] ·
[IDEA-018](../reports/IDEAS.md#idea-018)

<a id="verdict-007"></a>
### VERDICT-007 · sector_rotation (macro-linked) — CONDITIONAL

`equity/macro` · 2026-03-13 · conditional after **4 rounds** — the most-reviewed strategy on record ·
[`sector_rotation_2026-03-13_conditional`](../../../alpha_research/research/strategies/sector_rotation_2026-03-13_conditional/proposal.md)

**Status.** Four rounds without resolution. Its successor is registered in the pool as
[VERDICT-012](#verdict-012).

**Bears on.** [IDEA-036](../reports/IDEAS.md#idea-036) · [IDEA-019](../reports/IDEAS.md#idea-019) ·
[[CONCEPT-003-risk-contribution-vs-capital-weight]]

<a id="verdict-008"></a>
### VERDICT-008 · GS Defensive Sector Rotation — REJECTED (data)

`equity` · 2026-03-17 · from [`goldman_sachs_strategy_assessment_2026-03-17.md`](../../../alpha_research/research/goldman_sachs_strategy_assessment_2026-03-17.md)

**Why it failed.** No sector-classification data pipeline. The alternatives priced at the time were a
Norgate subscription at \$5K+/yr or a ~6-month valuation-pipeline build. Rejected on cost, never on
merit.

<a id="verdict-009"></a>
### VERDICT-009 · GS HALO factor (High Asset, Low Obsolescence) — REJECTED

`equity` · 2026-03-17

**Why it failed.** Two independent reasons: no fundamental-data pipeline, **and** the factor definition
itself was too vague to implement. The only verdict in the file rejected partly for
under-specification — worth remembering as its own failure mode, since a vague factor cannot be
falsified and will absorb unlimited research time.

<a id="verdict-010"></a>
### VERDICT-010 · GS Geographic Rotation — REJECTED (access)

`equity` · 2026-03-17

**Why it failed.** No international equity data, and the IBKR account lacks international permissions.
An account-permission constraint, which is the cheapest of all constraints to check first and was
checked last.

<a id="verdict-011"></a>
### VERDICT-011 · GS Quality + Safe-Haven overlay — APPROVED for research

`equity` · 2026-03-17 · priority 2

**Why it passed.** The only one of the four GS ideas that was implementable with instruments already
reachable: `QUAL`/`USMV` for the quality sleeve, `GLD`/`USO` and `JPY`/`CHF` for the safe-haven leg.
Approved *for research*, not for capital — the distinction matters and this is not a pool entry.

**Open.** Whether it was ever taken up is not recorded anywhere I can find; there is no
`quality_safe_haven` strategy folder. **Treat as an unclosed loop.**

<a id="verdict-012"></a>
### VERDICT-012 · sector_rotation_v1 — REVISE (pool)

`etf_rotation` · 2026-06-12 · pool state **candidate** · run `0f63c0e1`

**Status.** The only strategy registered in the live pool. Latest verdict REVISE, so it is a candidate
that has not earned paper trading. This is the one record here produced by the current
manifest → review → pool path rather than by the older PM-review process.

**Bears on.** [VERDICT-007](#verdict-007) (its predecessor) · [IDEA-036](../reports/IDEAS.md#idea-036)

<a id="verdict-013"></a>
### VERDICT-013 · vol_conditioned_reversal — REJECTED, with a state discrepancy

`vol` · 2026-06-13 · [`vol_conditioned_reversal_2026-06-13_rejected`](../../../alpha_research/research/strategies/vol_conditioned_reversal_2026-06-13_rejected/proposal.md)

**Status.** The strategy folder is marked `_rejected`, and it is the most heavily documented strategy
in the repo (hypothesis, three proposal drafts, PM review, preliminary results, owner decisions, a
sample professional report).

**Discrepancy to reconcile — flagged, not resolved.** A manifest exists at
`alpha_research/research/pool/vol_conditioned_reversal_v1/manifest.yaml`, but the strategy does **not
appear in the pool database** (`python -m alpha_research.pool list` returns only `sector_rotation_v1`).
So a rejected strategy carries a pool manifest while not being registered. Either the manifest is a
leftover from an intended registration, or a registration was lost. **Recorded here rather than
guessed at.**

**Bears on.** [[CONCEPT-002-volatility-risk-premium]] · [IDEA-003](../reports/IDEAS.md#idea-003) ·
[IDEA-044](../reports/IDEAS.md#idea-044)

---

## Open loops

| Loop | Why it is open |
|---|---|
| `quality_safe_haven` | [VERDICT-011](#verdict-011) approved it for research 2026-03-17; no strategy folder exists |
| `vol_conditioned_reversal_v1` | pool manifest present, not registered in the pool DB — see [VERDICT-013](#verdict-013) |
| `fx_carry` selector defect | [VERDICT-005](#verdict-005) — the raw-rate-differential ranking is still in committed code |
| Registry gaps | ~15 series physically present yet unreachable through `get_data`; blocked [VERDICT-004](#verdict-004) and constrains most of the mechanism pool |
