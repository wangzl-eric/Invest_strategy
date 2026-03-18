# Report Contracts

Use one schema across notebook, terminal summary, and future CLI outputs.

## Common Required Fields

- `hypothesis`
- `strategy_archetype`
- `rigor_mode`
- `primary_engine`
- `validation_engines`
- `report_backend`
- `optimizer_backend`
- `data_source`
- `date_coverage`
- `execution_convention`
- `cost_model`
- `benchmark`
- `naive_baseline`
- `run_id`
- `artifact_status`

## QuantStats Role

For `rigorous` and `highly-rigorous`, `quantstats` is the default serious report backend.

Required QuantStats inputs:
- daily returns
- benchmark returns
- aligned date coverage

Required serious-report artifacts:
- metrics summary
- gate summary
- daily returns
- equity curve
- run metadata
- QuantStats tear sheet or a stated reason it could not be produced

## Notebook Contract

The research notebook should follow these sections:

1. Strategy metadata and control block
2. Hypothesis and economic mechanism
3. Setup and run configuration
4. Data provenance, timing, benchmark, and baseline
5. Signal construction and timestamp validity
6. Engine selection and execution convention
7. Baseline backtest
8. Validation engine or IS/OOS design
9. Statistical tests and gate pack
10. Regime, beta, and benchmark dependence
11. Cost, turnover, and execution realism
12. Parameter, optimizer, and frontier sensitivity
13. Decay, capacity, and stability
14. Report generation and verdict inputs
15. RunManager persistence and artifact capture
16. Final summary and verdict

Mode-specific minimums:
- `specific`: sections 1-7, 15-16
- `rigorous`: sections 1-13, 15-16
- `highly-rigorous`: all 16 sections

## Terminal Summary Contract

Every final answer should include:

```text
Hypothesis:
Engine path:
Data and timing:
Execution convention:
Baseline and benchmark:
Key review lenses:
Gate summary:
Engine confidence:
Optimizer comparison:
Artifact status:
Verdict:
```

For `specific`, `gate summary`, `engine confidence`, and `optimizer comparison` can be marked `not required`.

## Future CLI Contract

Planned command family:

- `backtest specific`
- `backtest rigorous`
- `backtest highly-rigorous`

Planned required outputs:
- `run_metadata.json`
- `metrics.json`
- `gate_summary.json`
- `equity_curve.parquet`
- `daily_returns.parquet`
- `review.md`
- optional `trade_log.parquet`

Fail the run if the chosen tier cannot produce the required fields.
