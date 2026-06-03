# Tiers

This skill has three explicit modes. Use the highest level that matches the claim being made.

## `specific`

Purpose:
- reproducible exploratory research
- fast but disciplined

Required:
- hypothesis and economic mechanism
- `strategy_archetype`
- declared `primary_engine`
- data source and date coverage
- execution convention
- explicit cost assumptions
- naive baseline or benchmark
- one saved run with metrics, equity curve, and daily returns

Required artifacts:
- config snapshot
- scalar metrics
- equity curve
- daily returns
- run ID
- benchmark comparison

Output sections:
- hypothesis
- engine path
- data and timing
- execution convention
- baseline and benchmark
- key review lenses
- artifact status
- caveats

Fail-fast:
- no strong verdicts
- no approval language
- no hidden tuning

## `rigorous`

Purpose:
- defensible internal strategy evaluation
- PM-review quality research

Required:
- everything in `specific`
- IS/OOS split or walk-forward design
- realistic `CostModel`
- pass/fail gate summary
- PSR, DSR, MinBTL
- regime analysis
- 2x realistic cost survival
- parameter-search accounting
- explicit bias audit
- at least one validation-engine check when the strategy is execution-sensitive or the result is fragile

Required artifacts:
- all `specific` artifacts
- gate summary table
- walk-forward summary or explicit IS/OOS results
- regime metrics
- parameter grid or search-count metadata
- report backend output, preferably QuantStats

Output sections:
- all `specific` sections
- IS/OOS design
- gate summary
- bias audit
- robustness summary
- engine confidence

Fail-fast:
- no `APPROVE`
- no paper-trading readiness
- cannot ignore OOS behavior

## `highly-rigorous`

Purpose:
- approval-grade review
- paper-trading readiness
- strongest claims only

Required:
- everything in `rigorous`
- full project gate pack
- CPCV or purged-CV evidence where relevant
- with-cost and no-cost reporting
- residual framework-risk disclosure
- contradiction checks on windows, costs, parameters, and engine behavior
- explicit trial and variant count
- validation-engine stance even if only profile-level
- optimizer comparison for `optimizer_heavy` strategies

Required artifacts:
- all `rigorous` artifacts
- complete gate table
- run comparison table when variants exist
- trade log when the engine provides it
- QuantStats tear sheet or a stated reason it could not be produced
- explicit residual-risk section

Output sections:
- all `rigorous` sections
- full approval-gate table
- multiple-testing or CV method
- optimizer comparison, if applicable
- residual framework risks
- final verdict
- escalation trigger if not approved

Fail-fast:
- no approval-grade claim without artifacts
- no approval-grade claim from the minimal event-driven engine alone
- no approval-grade claim when required review lenses remain unanswered

## Auto-Escalation

Move to `highly-rigorous` automatically when:

- the user asks for approval, verdict, or readiness
- a strategy folder is being prepared for PM review
- multiple variants or tuned parameters are compared
- the strategy is macro-lag-sensitive or execution-sensitive

Move to at least `rigorous` automatically when:

- there is any parameter sweep or optimizer study
- the result is being used to judge effectiveness or stability, not just feasibility
