# vol_conditioned_reversal — KILLED 2026-06-14

- **Killed at stage:** S5 (mechanical validation). Vetted S0–S3 (verdict CONDITIONAL),
  implemented S4 (runner + manifest + tests), then a **preliminary S5 backtest on local
  data** failed decisively. The canonical FRED-VIXCLS / ~1999-backfill run is still
  pending (sandbox had no network), but every modal kill fired and the outcome is
  near-certain — the canonical run would be worse (adds the $1 IBKR floor; more history
  cannot rescue a negative *gross* edge).
- **Reason (one line):** A dollar-neutral 5-day sector-ETF reversal is **negative even
  GROSS** in 2012–2026 (5-day sector returns *continue*, they don't reverse), so it fails
  K1 (net Sharpe < 0 at every cost level), K9 (MinBTL — Sharpe negative on both the full
  and high-VIX sub-samples), and the **hard K4** (the simpler 21-day trailing-vol gate
  *beats* the VIX gate → "dressed-up vol timing", the `vix_regime` kill).
- **Ledger stats:** versions tried = 1 (`vol_conditioned_reversal_v1`); S5 runs used = 1
  (preliminary, local ^VIX / 2012–2026-02 / flat 8bps; **no `experiment_ledger` row** —
  the diagnostic bypassed `register`). Best observed: net Sharpe **−0.84** (1×), **−1.46**
  (2×), **−2.04** (3×); PSR **0.1%**; DSR **0.00**; ann. turnover **3045%/yr**; vs EW
  long-only **+0.84**. Active high-VIX sub-sample Sharpe **−1.09**. Baselines: unconditional
  reversal −0.97, trailing-vol-gated reversal −0.62 (beats ours).
- **Spec snapshot:** `research/strategies/vol_conditioned_reversal_2026-06-13_rejected/`
  (hypothesis.md, cerebro_briefing.md, proposal.md, pm_review.md, implementation_plan.md,
  OWNER_DECISIONS_2026-06-14.md, PRELIMINARY_BACKTEST_RESULTS.md, preliminary_backtest.py).
  Code retained for reference / resurrection: runner
  `alpha_research/backtests/runners/vol_conditioned_reversal.py` + manifest
  `alpha_research/research/pool/vol_conditioned_reversal_v1/manifest.yaml` + tests
  `tests/unit/test_vol_conditioned_reversal_strategy.py` (13/13 green).
- **Lesson (novel → L8 in STRATEGY_TRACKER.md, captured in KNOWLEDGE_EQUITY.md):**
  Short-term reversal does not survive — does not even exist *gross* — at the liquid
  sector-ETF layer; the reversal premium lives in illiquid single names (Avramov-Chordia-
  Goyal) and the liquid sector cross-section instead exhibits short-horizon *continuation*
  (Blitz 2024; Da-Liu-Schaumburg). A VIX regime gate adds no value over a cheaper 21-day
  trailing-vol gate (re-confirms L4/L6 and the `vix_regime` kill). Turnover for a 5-day
  reversal is brutal (~3000%/yr) even weekly with a no-trade band (re-confirms L7).
- **Resurrection condition:** materially new evidence that a reversal premium clears costs
  at an ETF layer — e.g. intraday/overnight reversal on a less-arbitraged ETF universe
  (Della Corte et al.), OR a construction where the VIX gate demonstrably beats a
  trailing-vol gate (spanning t ≥ 1.96). Re-enters at S0 as a new version; ledger trial
  counts carry over.
- **Cooling until:** 2026-09-12 (90 days, `cooling_period_days` in factory_config.yaml).
