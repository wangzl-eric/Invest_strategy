---
name: research-pipeline
description: Run the repository's end-to-end quant research pipeline from data selection and refresh through backtest execution, run persistence, and review artifact generation. Use when a task spans data ingestion, backtests, walk-forward checks, run saving, and report delivery.
---

# Research Pipeline

Use this skill when the task is not just "pull data" or "run a backtest", but to drive the whole research workflow from input data to review output.

## Environment

Run from the repo root with:

```bash
conda activate ibkr-analytics
export PYTHONPATH=.
```

If shell activation is awkward, prefer:

```bash
conda run -n ibkr-analytics env PYTHONPATH=. python ...
```

## Canonical Flow

1. Pick the data path deliberately.
   - Dashboard-compatible market data lives in `data/market_data/`.
   - New partitioned research datasets live in `data_lake/` through `workstation/quant_data/`.
   - Do not describe these as interchangeable unless you verified the consuming code reads the chosen store.

2. Use the right skill for the first mile.
   - For source selection, freshness, and gap checks, use `skills/data-pulling/SKILL.md`.
   - For strategy evaluation and approval-grade review, use `skills/rigorous-backtest/SKILL.md`.

3. Keep the pipeline boundary clear.
   - `workstation/quant_data/` is ingestion and dataset metadata code.
   - `workstation/backtests/` is research and validation code.
   - `backend.data_pipeline` is the canonical local-first interface for reading cached research data and launching refresh jobs.
   - `apps/dashboard/backend/reporting.py` is for operational account/trade PDFs, not research backtest verdicts.

4. Persist serious runs.
   - Save research runs with `backtests.run_manager.RunManager`.
   - Save `metrics`, `equity_curve`, and `daily_returns` whenever available.
   - Treat `data/backtest_runs/<run_id>/` as the reproducibility root for research artifacts.

5. Generate review artifacts from saved runs.
   - Use `backtests.reporting.review.build_review_bundle_from_run(...)`.
   - Prefer `report_backend="quantstats"` when daily returns are available.
   - Save markdown/json review artifacts before presenting a final verdict.

6. Route the output to the right destination.
   - Notebook and PM review material belongs under `workstation/research/strategies/...`.
   - Run artifacts belong under `data/backtest_runs/...`.
   - Dashboard PDF exports stay in the app/reporting lane and should not replace research review bundles.

## Minimal Output Contract

Every final answer for an end-to-end pipeline task should state:

```text
Data path:
Backtest path:
Run artifact:
Review artifact:
Open risks:
Next step:
```
