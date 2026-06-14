# Owner Decisions — Fire 2 Authorization (`vol_conditioned_reversal`)

> **Date:** 2026-06-14 · **Decided by:** Zelin (owner) · **Recorded by:** Claude before any code.
> These are PRE-COMMITMENTS made *before* the backtest exists. Per RESEARCH_PHILOSOPHY.md §2.4 and
> the anti-gaming rules, changing any of them after seeing a result requires a tracker entry and an
> `n_trials` bump. This file is the timestamped record that the Fire-2 design was fixed in advance.

## Decisions taken (from S3 `pm_review.md` R1–R13 + `implementation_plan.md` open decisions)

| ID | Decision | Choice | Consequence |
|---|---|---|---|
| **GO** | Proceed to Fire 2? | **GO — fail-fast** | Implement runner + manifest + look-ahead test, then run the baseline-config review FIRST and inspect **MinBTL (high-VIX sub-sample, K9/R12)** and **net Sharpe at 2× stressed cost (K1)**. If either fails → graveyard + `/learn-verdict` immediately; only run the declared parameter grid if both survive. |
| **D-COST** | $1 IBKR floor / vol-conditional spread not expressible in engine | **Approximate first, extend before promotion** | First pass uses a single stressed `proportional` bps (≈8) and annotates the ~50–65 bps/yr floor drag out-of-engine in the verdict (PM R2). Build the floor+regime-aware `CostModelSpec` only if it survives the modal kills, before any promotion past candidate. |
| **D-HISTORY** | Backfill SPDRs to ~1999 vs local 2012 start | **Backfill to ~1999** | Only lever on the modal MinBTL kill (necessary, not sufficient — does not change the half-duty-cycle) and the only way to run the Aug-2007 Khandani-Lo tail diagnostic (PM R10/R12). Cost: ~25yr dividend/split/splice QC (PM R8). |

## Defaults adopted (PM/plan recommendations; lower-stakes, not separately consulted)
- **D-KILL-HIERARCHY (PM R4):** K4 (must beat the 21-day trailing-vol filter) is pre-committed as a **HARD kill ABOVE K2** (beat unconditional reversal). K2 is the weaker test (unconditional ≈ 0 net); K4 is the binding "is it dressed-up vol-timing" test — the `vix_regime` kill.
- **D-VIX-SOURCE:** **VIXCLS (FRED)**, consumed PIT-shifted via `quant_data/pit.py` (1-day availability lag), supplied to the runner in the `macro` dict — *not* same-day `^VIX` (stale local cache to 2026-02-27; non-default consumption convention). Look-ahead test asserts no-future-VIX (PM R5).
- **D-CAPITAL:** **25k is the decision-grade column** (where the $1 floor binds); 100k reported for capacity (PM B3).
- **D-TRIALS:** **n_trials = 24 is the manifest FLOOR**; the ledger may raise the effective count, never lowered to pass DSR/PSR (PM R13, K10).
- **D-EMBARGO:** Per factory §4.3 (final-run-only embargo) and the fail-fast intent, the first probe uses the full backfilled sample; the ~18-month embargo (≈2025-01 → 2026-06) is reserved and applied only on the final pre-freeze run. Flagged, not yet a manifest field.

## Scope reminder for Fire 2
Build runner + `manifest.yaml` + look-ahead test; backfill data; run the review (writes the first
`experiment_ledger` row). Honour the reordered kill hierarchy. No promotion — verdict is the owner's.
