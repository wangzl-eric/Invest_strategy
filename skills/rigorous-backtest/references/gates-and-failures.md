# Gates And Failures

Use this file for the threshold set and the hard stop conditions.

## Required Quantitative Gates

Project thresholds from `AGENTS.md` and `research/STRATEGY_TRACKER.md`:

- Deflated Sharpe Ratio `> 0`
- Walk-forward hit rate `> 55%`
- Survives `2x` realistic costs with Sharpe `> 0`
- Probabilistic Sharpe Ratio `> 0.80`
- Worst regime annual loss `> -15%`
- LLM verdict `!= ABANDON`
- Strategy half-life `> 2 years`
- Minimum backtest length `< available data length`
- Max drawdown `> -25%`
- OOS Sharpe `> 0`

## Canonical Repository Functions

Use these, not notebook-local substitutes:

- `probabilistic_sharpe_ratio`
- `deflated_sharpe_ratio`
- `minimum_backtest_length`
- `cpcv_split`
- `purged_kfold_split`
- `walk_forward_split`
- `rolling_sharpe`
- `strategy_half_life`
- `regime_conditional_sharpe`

Core execution and persistence:

- `PortfolioBuilder.backtest(...)`
- `WalkForwardAnalyzer.run(...)`
- `RunManager.save_run(...)`

## Hard Fail Conditions

Do not issue a strong positive verdict if any of these are true:

- execution convention is missing
- source data and date coverage are unclear
- cost assumptions are missing
- daily returns are missing for a serious report
- OOS treatment is missing in `rigorous` or `highly-rigorous`
- parameter-search count is hidden after tuning
- the strategy fails a required review lens for its archetype

## Escalation Conditions

Escalate the review or downgrade the verdict if any of these occur:

- Sharpe is unusually high for the asset class and horizon without a credible explanation
- OOS Sharpe materially exceeds IS Sharpe in a suspicious way
- Small parameter changes collapse the result
- Performance disappears after realistic costs
- A macro-driven signal uses unlagged releases or revised data
- Local and validation-engine results diverge without explanation
- Local and `pypfopt` optimizer conclusions materially diverge for an optimizer-heavy strategy
