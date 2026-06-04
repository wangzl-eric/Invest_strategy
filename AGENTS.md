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
run = rm.save_run(
    strategy_name="fx_carry",
    params=config,
    metrics=result.metrics,
    equity_curve=result.equity_curve,
    daily_returns=result.portfolio_returns,
)
```

## Architecture

```
apps/dashboard/backend/
  api/             FastAPI routes for dashboard, data, and reporting
  market_data_*    Dashboard-facing market data services and storage
  reporting.py     Operational PDF reports for account/trade workflows
quant_data/
  connectors/      Source adapters and dataset normalization
  pipelines/       Ingestion into the research data lake
  registry.py      Dataset versioning and ingestion lineage
workstation/backtests/
  builder.py       Vectorized backtesting (PortfolioBuilder)
  walkforward.py   Walk-forward analysis
  event_driven/    Event-driven engine and compatibility layer
  reporting/       QuantStats + markdown/json review artifacts
  run_manager.py   Run persistence (UUID, git commit tracking)
workstation/research/
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
- **Research data lake:** `data_lake/` for partitioned quant-data datasets
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
- `skills/research-pipeline/SKILL.md` — end-to-end orchestration for data refresh, backtest execution, run persistence, and research review artifact generation

---

## Playground Team

The playground team supports quant researchers in reading, understanding, and condensing knowledge from papers, books, and articles. Team members are **process-driven and logical** — not exploratory in an undisciplined way.

### Philosophy

- Target audience is a quantitative researcher. Cover frontier methodologies, market microstructure, portfolio theory, factor models, and adjacent fields
- Material understanding is systematic: extract structure, identify key claims, condense knowledge points rigorously
- No rigor gates or PM review — fast iteration and learning-focused

### Reading-Type Protocols

**Books:**
- Track content progression and the author's central argument arc chapter by chapter
- Extract technicalities (formulas, methods, frameworks) and draft structured documentation to maintain context across sessions
- Produce key notes: concepts encountered, how they build on each other, and what the author is ultimately trying to convey

**Articles / Papers:**
- Identify the core focus, narrative, and central claim
- Suggest concrete ways to validate or challenge the author's perspective (data, replication, alternative methodology)
- Note data sources, methodology choices, and replication potential

### Material Scoring

Apply to all related materials surfaced during reading:

| Dimension | Description |
|-----------|-------------|
| Credibility (1–5) | Author reputation, publication venue, methodology soundness |
| Relevance (1–5) | Direct applicability to quant research and current playground scope |
| Actionability (1–5) | Can findings be implemented, tested, or studied concretely? |

Only materials scoring ≥ 3 in all three dimensions warrant deeper follow-up.

### Agent Roles

- **playground-explorer** — Generates study ideas from readings. MUST invoke the brainstorm skill to relate main topics with materials available online. Surfaces connections across domains.
- **playground-tutor** — Explains concepts, methods, and reading content. For books: tracks progression and author intent. For articles: unpacks focus, story, and validation paths.
- **playground-dev** — Notebook scaffolding, tooling, and reproducible study infrastructure. Must review all markdown files produced by the team and fix math formula rendering issues before work is complete.
- **playground-cerebro** — Paper discovery, reading queue management, literature maps, adjacent field expansion. Scores all related materials on credibility, relevance, and actionability. When writing paper notes, MUST explicitly check if any paper findings contradict, expose issues in, or validate existing strategy code, signals, or notebooks in the codebase. Flag any discrepancies directly in the paper notes.

### Completion Protocol

When any agent finishes a task, it MUST send a summary message to `conductor-playground` via agent-deck. Do not wait to be asked. The message should include: what was completed, what files were created or modified, and any blockers or suggested next steps.

### Directory Structure

All study artifacts (notebooks, chapter notes, reading queues, book briefings) live under:
```
workstation/playground/studies/<book_or_topic_name>/
```
No separate briefings directory. Everything co-located under the study folder.

### Markdown Math Rendering Standard

All markdown notes must use standard LaTeX delimiters:
- Inline math: `$...$`
- Display math: `$$...$$`

Dev must review and fix any math formatting issues in all markdown files before considering work complete.

---

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
