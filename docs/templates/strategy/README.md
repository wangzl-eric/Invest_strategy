# Strategy deliverable structure (canonical)

> Created 2026-06-14. Every strategy folder
> `alpha_research/research/strategies/<id>_<YYYY-MM-DD>_<verdict>/` holds **exactly these
> four markdown documents** (numeric-prefixed so the folder reads top-to-bottom), plus the
> executable spec and the machine bundle which live in their own canonical locations.
> Fewer, templated, predictable — move fast *and* stay rigorous. Copy the templates here
> to start a new strategy.

```
<id>_<date>_<verdict>/
  00_BRIEFING.md        # what it is, the trade expression, why, and the pre-committed gates
  01_RESEARCH_LOG.md    # dated per-stage notes: the audit trail (S0→S3 + decisions)
  02_BACKTEST_REPORT.md # AUTO-GENERATED — never hand-written (see below)
  charts/               # PNGs embedded by 02
  03_PM_REVIEW.md       # adversarial challenges, requirements checklist, verdict
```

Plus (not markdown — canonical homes, linked from `00`):
- **Runner** (the node's logic): `alpha_research/backtests/runners/<id>.py` (`build_weights`).
- **Manifest** (the node's registration): `alpha_research/research/pool/<id>/manifest.yaml`.
- **Machine bundle**: `data/backtest_runs/<run_id>/` (`performance.json`, `gates.json`,
  `stats_battery.json`, `engine_reconciliation.json`, …).

## The four documents

| File | Owner / stage | Purpose |
|---|---|---|
| `00_BRIEFING.md` | Researcher (S0/S2) | The single front page. Status header → description → **trade expression (maps 1:1 to manifest params)** → economic rationale (incl. key supporting *and* contradicting evidence) → **pre-committed kill thresholds** (the pre-registration; timestamped — changing them later bumps `n_trials`). |
| `01_RESEARCH_LOG.md` | Researcher + Cerebro (S0–S3) | The audit trail. One dated section per stage: framing, the full literature survey (contradictions/decay/crowding/prior-art), proposal drafting + conflicts resolved, revision rounds, and every owner decision. This is what makes `n_trials` honest. |
| `02_BACKTEST_REPORT.md` | **Generated** (S5) | Results with embedded charts + metric/gate/significance/sensitivity tables + engine reconciliation. **Do not hand-edit.** Produced by `python -m alpha_research.review run …` (into the run bundle) and rendered into the strategy folder with `python -m alpha_research.review report <run_id> --out <this folder>`. |
| `03_PM_REVIEW.md` | PM (S3/S6) | Adversarial review: challenges (mechanism, costs, PIT, baselines, lessons), an explicit "requirements for approval" checklist, and the verdict. One `## ROUND N` section per round (≤2). |

## The flow (idea → results, no extra files)

1. Copy `00_BRIEFING.md` / `01_RESEARCH_LOG.md` / `03_PM_REVIEW.md` into the new strategy folder.
2. Fill `00` (expression + rationale + gates) and log the journey in `01` as you go.
3. Write the node: `runners/<id>.py:build_weights` + `pool/<id>/manifest.yaml` (+ the
   `test_no_lookahead_truncation_invariance` test).
4. `python -m alpha_research.review run <manifest>` → bundle + `report.md`/`charts/`.
5. `python -m alpha_research.review report <run_id> --out <strategy folder>` → `02_BACKTEST_REPORT.md`.
6. PM writes `03_PM_REVIEW.md`. Verdict renames the folder (`…_PENDING` → `…_rejected`/`…_paper`/…).

Full reference: `docs/guides/backtest_output_reference.md`.
