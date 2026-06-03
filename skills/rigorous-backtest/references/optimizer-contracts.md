# Optimizer Contracts

Use this file when portfolio optimization is central to the strategy.

## Default Policy

- `local` remains the default optimizer backend
- `pypfopt` is a required comparison lens for `optimizer_heavy` strategies in `rigorous` and `highly-rigorous`
- `optimizer_backend=both` is the preferred setting for serious optimizer-heavy reviews

## When `pypfopt` Comparison Is Required

Require it when any of these are true:

- optimizer choice is a large part of the claimed edge
- constraints appear to bind heavily
- turnover looks extreme
- concentration is high
- PM or reviewer questions whether the optimizer is adding value

## Required Comparison Outputs

- same universe and date range
- same expected-return inputs where possible
- same or comparable covariance assumptions
- local weights
- `pypfopt` weights
- concentration summary
- turnover implication
- frontier or objective-family comparison
- explanation of material divergence

## Verdict Rules

- if the local optimizer and `pypfopt` tell the same story, confidence increases
- if they diverge materially, downgrade the verdict until the reason is explained
- if the strategy only works under one optimizer family, say so explicitly

## Questions The Agent Must Ask

- Is the strategy edge really alpha, or optimizer leverage on weak alpha?
- Are constraints doing most of the work?
- Would a simpler allocation beat this optimizer-driven result?
- Is turnover caused by signal quality or optimizer churn?
