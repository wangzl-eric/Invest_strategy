# Fire 2 — Implementation Status (`vol_conditioned_reversal`)

> **Date:** 2026-06-14 · **Stage:** S4 implementation complete; S5 battery pending network.
> Owner pre-commitments: `OWNER_DECISIONS_2026-06-14.md`. Spec: `proposal.md` / `pm_review.md`.

## Built and verified (offline)
| Artifact | Path | Status |
|---|---|---|
| Runner | `alpha_research/backtests/runners/vol_conditioned_reversal.py` | ✅ written, 94% line coverage |
| Manifest | `alpha_research/research/pool/vol_conditioned_reversal_v1/manifest.yaml` | ✅ loads + entrypoint resolves |
| Look-ahead test | `tests/unit/test_vol_conditioned_reversal_strategy.py` | ✅ **13/13 pass** |
| Lint | black / isort / flake8 | ✅ clean |

The unit suite proves the load-bearing properties offline (synthetic data, no network):
truncation-invariance of weights **and** of the VIX gate; no-future-VIX; warmup fully
populated (PM R6); dollar-neutral + capped + gross-1.0 on active weeks; gate-off weeks
exactly flat; no-trade band reduces turnover; dynamic 9→10→11 universe with no backfill;
constant-VIX → never active; missing-VIX → no trading.

The pipeline wiring is validated end-to-end up to the data fetch: `python -m
alpha_research.review run …` loaded the manifest, **loaded prices from the local lake**,
and reached the macro loader — failing only on a network timeout to `fred.stlouisfed.org`.
`_fetch_fred_csv` uses FRED's public CSV endpoint, so **no `FRED_API_KEY` is required** —
the only blocker is outbound network (absent in the dev sandbox).

## What remains (needs a networked env) — fail-fast order (PM R1/R12)
Run from the repo root in the `ibkr-analytics` conda env:

```bash
conda activate ibkr-analytics
export PYTHONPATH=.

# (D-HISTORY, owner-approved) backfill SPDRs to ~1999 so MinBTL has a chance and the
# Aug-2007 tail is testable; refresh VIXCLS to the latest ETF date. e.g.:
#   POST /api/data/pull  (Data Manager)  or  scripts/ backfill for: XLK XLF XLE XLV XLC
#   XLY XLP XLI XLB XLRE XLU SPY (prices) + VIXCLS (FRED). Then pin backtest_start to the
#   first fully-warmed trailing-60 VIX date (PM R6) in the manifest.

# the one-call battery (writes data/backtest_runs/<run_id>/ + an experiment_ledger row)
python -m alpha_research.review run alpha_research/research/pool/vol_conditioned_reversal_v1/manifest.yaml
```

**Read FIRST, before any parameter work (the two modal kills):**
1. **K1** — net Sharpe at 2× stressed cost: `gates.json → cost_survival` and
   `sensitivity.json → cost` (the 2.0 multiplier row must be > 0).
2. **K9** — MinBTL: `stats_battery.json → min_backtest_length_days` vs `n_days`
   (`minbtl_satisfied`). Evaluate it on the **high-VIX sub-sample**, not just the full
   series (the engine reports the full-sample MinBTL; the conditional sub-sample is the
   binding test — flat ~half the weeks).

If either fails → graveyard + `/learn-verdict` immediately (the correct, fast kill).
Only if both survive: run the `mom_neutralize=on` arm (PM R7) and the declared
sensitivity trials, letting the ledger accumulate `n_trials` honestly.

## Caveats the battery cannot self-check (carry into the verdict)
- **Cost model is a placeholder** (`bps: 8.0`, flat). The $1 IBKR order floor (~50–65
  bps/yr at 25k) is **not** charged inside the Sharpe (D-COST path b). Annotate it
  out-of-engine; build the floor+vol-conditional `CostModelSpec` before any promotion.
- **EW baseline is long-only** (carries equity premium); K3 is a portfolio-contribution
  test (|ρ| + marginal Sharpe), not raw Sharpe-vs-EW (PM R9).
- **K4 (beat the 21-day trailing-vol filter)** and **K2 (beat unconditional reversal)**
  are not in the automated gate set — run them as side comparisons (same engine, gate
  swapped) and apply K4 as the **hard** kill of the VIX-specific claim (PM R4).
- **|ρ| vs `sector_rotation_v1`** (K6) only populates once both have run bundles; the
  pipeline computes it automatically against the active pool.
