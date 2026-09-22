# Tutorials

Numbered, progressive walkthroughs of the platform. Run them in order the first
time; after that they work standalone.

| # | Notebook | Teaches |
|---|---|---|
| 00 | `00_getting_started.ipynb` | Data access — `alpha_research.quant_data.api`, long vs. wide, plotting |
| 01 | `01_beginner_research.ipynb` | Backtrader basics, first signal |
| 02 | `02_intermediate_research.ipynb` | Research workflow, walk-forward |
| 03 | `03_advanced_research.ipynb` | Advanced signal and portfolio construction |
| 04 | `04_signal_research.ipynb` | Signal development (`alpha_research.backtests.strategies.signals`) |
| 05 | `05_backtest_robustness.ipynb` | PSR, deflated Sharpe, CPCV, bootstrap |
| 06 | `06_portfolio_builder.ipynb` | Mean-variance, risk parity, rebalancing |
| 07 | `07_pnl_query.ipynb` | Querying PnL history with filters and charts |
| 08 | `08_verdict_example.ipynb` | A worked LLM verdict |

## Before you start

```bash
conda activate ibkr-analytics
export PYTHONPATH=.
jupyter lab
```

All data pulls return **long** format — `(date, ticker, …)` for prices,
`(date, series_id, value, …)` for FRED. Pivot to wide for anything
cross-sectional. Tutorial 00 covers this.

## Related

- [`../GET_STARTED_QUICK.md`](../GET_STARTED_QUICK.md) — how to run your own study
- [`../QUICK_REFERENCE.md`](../QUICK_REFERENCE.md) — data/plotting cheat sheet
- [`../studies/TEMPLATE.md`](../studies/TEMPLATE.md) — the study template
- `alpha_research/notebooks/templates/` — scaffolds for a new research notebook
