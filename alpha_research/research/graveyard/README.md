# Idea Graveyard
<!-- Created 2026-06-12 (alpha factory F-0 scaffolding). -->

Every killed hypothesis is archived here. **Rejections are training data, not
embarrassments to delete.** Rules: `docs/guides/alpha_factory_workflow.md` §4.4;
tunables (cooling period) in `../factory/factory_config.yaml`.

## Entry convention

One file per kill: `{hypothesis_id}_{YYYY-MM-DD}.md` containing:

```markdown
# {hypothesis_id} — KILLED {date}
- Killed at stage: S0 | S1 | S3 | S5
- Reason: <one line — which gate/challenge it failed>
- Ledger stats: versions tried, S5 runs used, best Sharpe/PSR/DSR observed
- Spec snapshot: link to strategy folder or inline summary
- Lesson: <novel? → L-number it in STRATEGY_TRACKER.md and run /learn-verdict>
- Resurrection condition: <what materially new evidence would justify re-queueing>
- Cooling until: <date + cooling_period_days>
```

## Protocol

- S0 intake **must** scan this directory before queueing a near-duplicate hypothesis.
- Resurrection requires the stated condition met AND the cooling period elapsed; the
  resurrected entry goes back to S0 as a **new version** (ledger trial counts carry over).
- Every kill also fires `/learn-verdict {folder}` so the lesson reaches the domain KBs
  (`memory/knowledge/`) — the graveyard is the archive; the KBs are the working memory.

## Pre-factory kills (migrated from STRATEGY_TRACKER.md, 2026-03)

| Hypothesis | Killed | Lesson |
|---|---|---|
| vol_scaled_momentum | 2026-03-13 | L1, L2, L3 |
| yield_curve_steepener | 2026-03-13 | no futures infra (now queued as cta-carry, parked) |
| commodity_momentum | 2026-03-13 | no futures infra (now folded into cta-trend, parked) |
| vix_regime_vrp | 2026-03-15 | L4, L5, L6, L7 |

## Factory-era kills (F-0+)

| Hypothesis | Killed | Stage | Lesson |
|---|---|---|---|
| vol_conditioned_reversal | 2026-06-14 | S5 (prelim) | L8 — STR is negative even gross at the liquid sector-ETF layer; VIX gate loses to a trailing-vol gate (re-confirms L4/L6/L7). Cooling until 2026-09-12. |
