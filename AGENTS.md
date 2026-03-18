# AGENTS.md — Codex CLI Context

This file provides context to Codex CLI when working in this repository.

## Role: Codex Runner

You are `codex-runner` — the execution assistant for the Zelin Investment Research team. You handle:
- **Backtest execution:** Run notebook cells, execute PortfolioBuilder backtests
- **Parameter sweeps:** Vary signal parameters and report comparative results
- **Data pulls:** Fetch market data via yfinance, FRED, or the Parquet data lake
- **Code review:** Independent review for look-ahead bias, off-by-one errors, API misuse

## Environment

```bash
conda activate ibkr-analytics          # Python 3.10
export PYTHONPATH=.                     # Required before running anything
```

## Key APIs

### Running a Backtest
```python
from backtests.builder import PortfolioBuilder

pb = PortfolioBuilder(prices_df, signals_df, rebalance_frequency="M")
result = pb.backtest(
    dynamic_reoptimize=True,
    cost_model=cost_model,      # from backtests.costs
    target_vol=0.12,            # optional vol scaling
)
# result.portfolio_returns, result.metrics, result.weights
```

### Walk-Forward Analysis
```python
from backtests.walkforward import WalkForwardAnalyzer

wfa = WalkForwardAnalyzer(prices_df, signals_df)
wf_result = wfa.run(train_years=2, test_months=3)
# wf_result.oos_sharpe, wf_result.hit_rate
```

### Statistical Tests
```python
from backtests.stats.sharpe_tests import probabilistic_sharpe_ratio, deflated_sharpe_ratio
from backtests.stats.minimum_backtest import minimum_backtest_length
from backtests.stats.cross_validation import combinatorial_purged_cv
```

### Cost Models
```python
from backtests.costs import ProportionalCost, CompositeCostModel, MarketImpactModel

cost_model = CompositeCostModel([
    ProportionalCost(bps=5),       # 5bps commission
    MarketImpactModel(eta=0.1),    # market impact
])
```

### Saving Runs
```python
from backtests.run_manager import RunManager

rm = RunManager()
run_id = rm.save_run(config=config, result=result, strategy_name="fx_carry")
```

## Architecture

```
backtests/
  builder.py       Vectorized backtesting (PortfolioBuilder)
  walkforward.py   Walk-forward analysis
  strategies/      Signal framework (BaseSignal subclasses)
  stats/           PSR, Deflated Sharpe, MinBTL, CPCV, bootstrap
  costs/           Transaction cost & slippage models
  run_manager.py   Run persistence (UUID, git commit tracking)
  parallel.py      Parameter sweeps (ProcessPoolExecutor)
portfolio/
  optimizer.py     CVXPY mean-variance, risk parity
  risk_analytics.py  Risk decomposition
research/
  strategies/      Strategy folders with notebooks and reviews
  STRATEGY_TRACKER.md  Master tracker
```

## Look-Ahead Bias Prevention (CRITICAL)

When reviewing or writing signal code:
- End-of-day trading (trade after close): use `[0]` for current bar
- Intraday / start-of-day: use `[-1]` for previous bar (safe, no look-ahead)
- Every `self.data.X[0]` access should have a comment explaining why `[0]` is valid
- Signals must be z-scored cross-sectionally at each date, NOT full-sample normalized
- Walk-forward windows must use only past data for training

## Data

- **Parquet files:** `data/market_data/` with `catalog.json`
- **Ticker universe:** `config/ticker_universe.py`
- **Schema:** prices = `(date, ticker, open, high, low, close, volume)`

## Tests

```bash
make test                              # All tests
pytest tests/unit/test_foo.py -v       # Single file
make lint                              # flake8 + black --check
```

Flake8 config: `--max-line-length=120 --ignore=E501,W503`

## Local Skills

- `skills/data-pulling/SKILL.md` — source-aware data pulls with validation and consistent reporting
- `skills/rigorous-backtest/SKILL.md` — tiered (`specific` / `rigorous` / `highly-rigorous`) backtest execution and review with engine validation, QuantStats reporting, and PyPortfolioOpt comparison for optimizer-heavy work

## Quantitative Gates (11 required for strategy approval)

| Gate | Threshold |
|------|-----------|
| Deflated Sharpe Ratio | > 0 |
| Walk-forward hit rate | > 55% |
| Survives 2x realistic costs | Sharpe > 0 |
| PSR | > 0.80 |
| Worst regime annual loss | > -15% |
| LLM verdict | != ABANDON |
| Strategy half-life | > 2 years |
| MinBTL | < available data length |
| Max Drawdown | > -25% |
| IS Sharpe | varies |
| OOS Sharpe | > 0 |
