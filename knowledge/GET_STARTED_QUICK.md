# Quick Start Guide

How to run your own manual / semi-systematic study. No rigor gates — that is
`alpha_research/`. Here you are forming a view, not promoting a strategy.

## Getting Started

### 1. Create the study folder

Studies are dated and topic-named. Cross-field topics are normal and expected —
do not try to file work under a single field.

```bash
conda activate ibkr-analytics
export PYTHONPATH=.

mkdir -p knowledge/studies/2026-09-04_my_study/{notebooks,data,charts}
cp knowledge/studies/TEMPLATE.md knowledge/studies/2026-09-04_my_study/README.md
```

Fill in the **Hypothesis** line in `README.md` before you pull any data. If you
cannot state it in one sentence, you are not ready to open a notebook.

### 2. Orient (optional)

The nine field primers list key questions and standard data sources per topic:

```bash
cat knowledge/fields/volatility/README.md
```

They are reference only — `knowledge/fields/` is a retired taxonomy (see
[FIELDS.md](FIELDS.md)); file the work in `studies/`.

### 3. Load data

Local Parquet first, API fallback. Macro series are point-in-time shifted by
default — leave `pit=True` unless you have a reason not to.

```python
from alpha_research.quant_data.api import get_data

# Everything comes back LONG, not wide:
#   prices -> (date, ticker, open, high, low, close, volume)
#   FRED   -> (date, series_id, value, reference_date)
raw = get_data(["SPY", "TLT", "GLD"], start="2015-01-01")

# Pivot to wide before doing anything cross-sectional:
panel = raw.pivot(index="date", columns="ticker", values="close")
returns = panel.pct_change().dropna()
```

For a macro series, take the `value` column:

```python
from alpha_research.quant_data.api import get_fred

vix = get_fred("VIXCLS", start="2015-01-01").set_index("date")["value"]
```

Natural-language tickers resolve too — see the `/get-market-data` skill.

### 4. Analyze & visualize

```python
from knowledge.shared.viz_helpers import plot_time_series

fig = plot_time_series(
    data=panel,                       # wide: one column per ticker
    columns=["SPY", "TLT", "GLD"],
    title="Cross-asset",
    normalize=True,
)
fig.savefig("knowledge/studies/2026-09-04_my_study/charts/cross_asset.png", dpi=300)
```

### 5. Document findings

Fill in `README.md` as you go — hypothesis, methodology, observations, caveats.
Write down what surprised you; that is the part you will not remember next month.
Append one line per session to `FINDINGS_LOG.md`.

### 6. Close the loop

A study that ends in a file nobody reads is wasted. Pick one:

- **A durable claim** → capture into `knowledge/brain/` (`/capture-finding`), or the
  relevant `knowledge/domains/KNOWLEDGE_*.md`
- **A testable idea** → add to `knowledge/reports/IDEAS.md`
- **Neither** → mark the study `Archived` and say why in one line. A negative
  result you can point to later is worth more than a folder you forgot about.

---

## Common Workflows

### Correlation analysis

```python
from alpha_research.quant_data.api import get_data
from knowledge.shared.viz_helpers import plot_correlation_matrix, plot_rolling_correlation

assets = (get_data(["SPY", "TLT", "GLD"], start="2015-01-01")
          .pivot(index="date", columns="ticker", values="close"))
returns = assets.pct_change().dropna()

fig = plot_correlation_matrix(returns, title="Asset Correlations")
fig = plot_rolling_correlation(
    returns["SPY"], returns["TLT"], window=60,
    title="SPY-TLT 60-Day Rolling Correlation",
)
```

### Regime detection

```python
import pandas as pd
from alpha_research.quant_data.api import get_fred, get_prices
from knowledge.shared.viz_helpers import plot_regime_overlay

vix = get_fred("VIXCLS", start="2015-01-01").set_index("date")["value"]
spy = get_prices("SPY", start="2015-01-01").set_index("date")["close"]

regime = pd.cut(vix, bins=[0, 15, 25, 100], labels=["Low", "Medium", "High"])
fig = plot_regime_overlay(spy, regime.reindex(spy.index))
```

### Momentum analysis

```python
from alpha_research.quant_data.api import get_data

prices = (get_data(["SPY", "QQQ", "IWM"], start="2015-01-01")
          .pivot(index="date", columns="ticker", values="close"))
momentum = prices.pct_change(252)          # 12-month
ranks = momentum.rank(axis=1, pct=True)
```

---

## Tips

1. **State the hypothesis first** — before the data, not after the chart
2. **Document as you go** — update `README.md` throughout, not at the end
3. **Cache data** — save to the study's `data/` folder to avoid refetching
4. **Promote a repeated pull into a module** — see `vol_data.py` in
   `studies/2026-06-24_volatility_workstation/`, the reference layout
5. **A surprise is the finding** — write down what you did not expect
6. **Close the loop** — brain, IDEAS.md, or an explicit archive

## Getting Help

- **`QUICK_REFERENCE.md`** — detailed data/plotting reference
- **`/get-market-data`** — data pulls with NL ticker resolution
- **`/read-to-learn`** — study a paper or book chapter properly
- **Field primers** — `knowledge/fields/<field>/README.md`

## Related

- [README.md](README.md) — what goes where in `knowledge/`
- [studies/TEMPLATE.md](studies/TEMPLATE.md) — the single study template
- [FIELDS.md](FIELDS.md) — retired field taxonomy, kept for reference
