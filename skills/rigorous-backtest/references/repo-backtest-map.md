# Repo Backtest Map

This repository has mixed research and validation paths. Always state which one produced each result.

## Primary Paths

## `local`

Main modules:
- `backtests/builder.py`
- `backtests/portfolio_backtest.py`
- `backtests/stats/__init__.py`
- `backtests/run_manager.py`

Use for:
- portfolio-level vectorized research
- most current notebook workflows
- optimizer-heavy strategies

Important truths:
- official runs should use `dynamic_reoptimize=True`
- official daily-data runs should use `align_calendar=True`
- official cost claims should use an explicit `CostModel`
- `PortfolioBuilder` Sharpe is raw unless you compute excess-return Sharpe separately
- returned `weights` are not the full rebalance history
- `equity_curve` and `daily_returns` exist, but turnover series and cost series may need extra work

## `backtrader`

Main modules:
- `backtests/walkforward.py`
- `backend/backtest_engine.py`

Use for:
- walk-forward validation
- execution-timing cross-checks
- trade-log-producing paths

Important truths:
- this is the repo’s main validation engine
- walk-forward, grid search, and cost-sensitivity utilities route here
- serious reports must disclose train/test windows, metric, and strategy factory assumptions

## `event-driven`

Main module:
- `backtests/event_driven/engine.py`

Use for:
- supplemental diagnostics only

Important truths:
- realism is limited
- do not use as sole evidence for approval-grade claims

## Rigor Tooling

Canonical stats package:
- `backtests/stats/__init__.py`

Persistence:
- `backtests/run_manager.py`

Known truth sets:
- `tests/unit/test_bugfixes.py`
- `tests/unit/test_phase1_gates.py`
- `research/framework_audit/`

## Residual Repo Risks The Skill Must Surface

- mixed-engine comparability is not automatic
- macro publication lag is not globally enforced
- parameter-search accounting is procedural, not automatic
- vectorized outputs do not always expose the full audit trail needed for execution-grade claims
