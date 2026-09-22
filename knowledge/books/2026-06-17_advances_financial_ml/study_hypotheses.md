# Study Hypotheses — Advances in Financial Machine Learning

Testable ideas raised while reading. These are *learning* probes for the playground,
not strategy proposals. Promote to formal research only via the migration path in
`knowledge/README.md`.

## H1 — The "$k \to T$" leakage detector reproduces on our own CV code
**From:** Ch. 7. De Prado claims that under leakage, CV performance rises monotonically
as folds $k \to T$, and that a clean (purged+embargoed) setup stops improving past some
$k^*$.
**Probe:** Generate synthetic features (some pure noise) with deliberately *overlapping*
labels. Run `alpha_research.backtests.stats.cross_validation.purged_kfold_split` with
(a) no purge / no embargo and (b) purge + 1% embargo, sweeping $k$. Expect monotone
improvement in (a), flattening in (b).
**Value:** Demonstrates the leakage mechanism *on our own code*, and would make a clean
regression test for the CV module. Educational, low cost.

## H2 — Embargo sensitivity as a thin-edge detector
**From:** Ch. 7 implementation-reality lens.
**Probe:** For a couple of pooled strategies, recompute reported CV/backtest metrics at
`embargo_pct` ∈ {0, 0.01, 0.05}. Large degradation as embargo grows ⇒ the edge may be
leakage-dependent.
**Value:** A cheap robustness lens to add to intuition before trusting a pooled metric.

## Resolved verification (was a code question)
*Does `alpha_research/review` pass real `label_end_times` (t1) into `purged_kfold_split`?*
**Resolved 2026-06-17:** review never calls `purged_kfold_split` — it imports only
scalar rigor stats and does "walk-forward" via `np.array_split(returns, 4)`
(contiguous-segment Sharpe). Purged CV is correctly fed a real `t1` only in the
ML-signal path (`signals.py` + `labeling.py`). So "purged CV" is *not* a leakage
guarantee for weights-contract runners — and doesn't need to be: that path controls
look-ahead via the execution-convention shift + PIT macro instead. Not a bug; a
design boundary. (Detail in `notes/ch07_notes.md` → Connection to our platform.)
