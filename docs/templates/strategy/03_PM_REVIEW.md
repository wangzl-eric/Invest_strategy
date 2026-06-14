<!-- TEMPLATE — copy into research/strategies/<id>_<date>_<verdict>/03_PM_REVIEW.md.
Adversarial review. One `## ROUND N` section per round (max 2 revision rounds). The
[CEREBRO CONTRADICTION] and [DATA ASSESSMENT] must be in hand before a review is valid.
Delete these comments when filling. -->

# <Strategy name> — PM Review

> **Reviewer:** PM · **Researcher:** <…> · reads `00_BRIEFING.md`, `02_BACKTEST_REPORT.md`,
> and the run bundle (never summaries — cross-check against `stats_battery.json` /
> `sensitivity.json` / `gates.json`).

## ROUND 1

### Challenges
1. **Mechanism:** <is the edge real; who loses money; is it dressed-up beta/vol-timing?>
2. **Costs at our capital:** <net of realistic costs/turnover at 25k–100k; survives 2×/3×?>
3. **PIT / data lags:** <look-ahead, publication lags, survivorship, universe definition.>
4. **Baseline beatability:** <equal-weight (L1); the simplest credible alternative (L6).>
5. **Lessons L1–L7 / KB failure modes:** <which apply; are they answered?>
6. **MinBTL / significance:** <is the effective sample enough for the claimed Sharpe?>

### Requirements for approval (checklist → S5 gates)
- [ ] R1 …
- [ ] R2 …

### Verdict
`APPROVED` \| `CONDITIONAL` \| `REJECT` — <one-line rationale.> `revision_needed: <bool>`.

<!-- Add `## ROUND 2` if the researcher revised; track resolved/unresolved from Round 1.
After the final round, a verdict renames the strategy folder. REJECT → graveyard +
/learn-verdict (lesson to memory/knowledge/KNOWLEDGE_*.md). -->
