---
name: rigorous-backtest
description: Run or review strategy backtests in this repository with one of three explicit modes: `specific`, `rigorous`, or `highly-rigorous`. Use when evaluating a strategy, building a research notebook, comparing engines, generating a serious report, or issuing a verdict that must be defensible.
---

# Rigorous Backtest

Use this skill for any backtest that could influence research direction, PM judgment, or paper-trading readiness. The default stance is adversarial: try to break the strategy before accepting it.

## Defaults

- Default `rigor_mode`: `highly-rigorous`
- Default `primary_engine`: `local`
- Default `report_backend` for serious work: `quantstats`
- Default `optimizer_backend`: `local`
- Required override for optimizer-heavy work: compare against `pypfopt`

## First Step

Before running or reviewing anything, declare this control block:

```text
rigor_mode:
strategy_archetype:
primary_engine:
validation_engines:
report_backend:
optimizer_backend:
```

Allowed values:

- `rigor_mode`: `specific` | `rigorous` | `highly-rigorous`
- `strategy_archetype`: `cross_sectional` | `optimizer_heavy` | `trend_carry` | `overlay_risk_managed` | `macro_lag_sensitive` | `execution_sensitive`
- `primary_engine`: `local` | `backtrader` | `qlib` | `vnpy`
- `report_backend`: `quantstats` | `native`
- `optimizer_backend`: `local` | `pypfopt` | `both`

If the user does not specify a mode, use `highly-rigorous`. If the task asks for approval, verdict, or final readiness, do not downgrade the mode.

## Environment

Run from the repo root with:

```bash
conda activate ibkr-analytics
export PYTHONPATH=.
```

## Core Rules

- Do not accept a strong result from one attractive equity curve.
- Always declare which engine path produced each result.
- For official `PortfolioBuilder.backtest(...)` claims, use `dynamic_reoptimize=True`.
- For official cost claims, use an explicit `CostModel`.
- For daily data, use `align_calendar=True`.
- Label `PortfolioBuilder` Sharpe as raw unless you compute excess-return Sharpe separately.
- Save serious runs through `RunManager`.
- If parameters were tuned, disclose how many combinations or iterations were tried.
- If a required review lens is unanswered, the result cannot be stronger than `REVISE`.

## Repo Reality

This repository has mixed backtest paths:

- `local`: `PortfolioBuilder` and related vectorized research flows
- `backtrader`: `WalkForwardAnalyzer` and `backend.backtest_engine`
- `event-driven`: minimal supplemental engine only, not approval-grade by itself

Read the repo map before making claims about realism or comparability.

## Load These References

- Mode rules: [tiers.md](references/tiers.md)
- Strategy self-question matrix: [review-lenses.md](references/review-lenses.md)
- Local engine map and caveats: [repo-backtest-map.md](references/repo-backtest-map.md)
- Engine validation policy: [engine-validation.md](references/engine-validation.md)
- Report and notebook contracts: [report-contracts.md](references/report-contracts.md)
- Optimizer comparison policy: [optimizer-contracts.md](references/optimizer-contracts.md)
- Quantitative thresholds and fail conditions: [gates-and-failures.md](references/gates-and-failures.md)
- Parallel review workflow: [subagents.md](references/subagents.md)

## Escalation

Escalate to `highly-rigorous` if any of these are true:

- the task asks for approval, final verdict, or paper-trading readiness
- multiple variants, sweeps, or optimizer comparisons are involved
- the strategy is macro-lag-sensitive or execution-sensitive
- the result is unusually strong, unstable, or hard to explain economically

## Output Contract

Every final answer must include:

```text
Hypothesis:
Engine path:
Data and timing:
Execution convention:
Baseline and benchmark:
Key review lenses:
Artifact status:
Verdict:
```

For `rigorous` and `highly-rigorous`, add the required gate, robustness, engine-confidence, and optimizer-comparison sections from the references.
