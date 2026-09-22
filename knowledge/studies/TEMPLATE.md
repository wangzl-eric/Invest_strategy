# Study Template

The single template for a study under `knowledge/studies/<YYYY-MM-DD>_<topic>/`.
Copy it to that folder's `README.md` and fill it in as you go.

This is exploratory work — no rigor gates, no PSR/DSR, no PM review. Those belong to
`alpha_research/`. A study earns its way there via `reports/IDEAS.md`; see
"Next Steps" below.

---

## Study Information

- **Date**: YYYY-MM-DD
- **Topic**: Brief description
- **Hypothesis**: The one claim this study is trying to support or kill
- **Status**: In Progress | Complete | Archived
- **Notebook**: Path to notebook file (if applicable)

---

## Motivation

Why is this worth a day? What made you curious — a paper, a report, a market move,
a contradiction between two things you believe? Link the source if there is one.

---

## Question

What specific question are you investigating?

Example: "How does SPY-TLT correlation change during high VIX periods?"

---

## Data

- **Assets**: SPY, TLT, GLD, etc.
- **Macro indicators**: VIX (VIXCLS), 10Y yield (DGS10), etc.
- **Period**: Start date to end date
- **Source**: `quant_data.api.get_data` (local Parquet first), FRED, yfinance
- **PIT**: macro series are publication-lag shifted by default — say so if you overrode it

---

## Methodology

1. Load price/macro data
2. Calculate returns/volatility/correlation
3. Split by regime (if applicable)
4. Visualize patterns
5. Compute statistics

---

## Observations

1. **Finding 1**: Description with supporting data
   - Example: "Correlation becomes more negative during VIX > 25 (-0.6 vs -0.3 in low vol)"
2. **Finding 2**: Description with supporting data
3. **Finding 3**: Description with supporting data

Surprises count double — write down what you did *not* expect.

---

## Visualizations

- `correlation_chart.html` — Rolling correlation over time
- `regime_comparison.html` — Statistics by regime
- `drawdown_chart.html` — Drawdown analysis

---

## Caveats

- Data quality issues
- Sample size limitations
- Regime definition choices
- Survivorship bias
- Look-ahead bias (if applicable)

---

## Files

```
<YYYY-MM-DD>_<topic>/
├── README.md          # this file
├── FINDINGS_LOG.md    # one line per session
├── notebooks/         # analysis notebooks
├── data/              # study-specific cached data
└── charts/            # exported visualizations
```

A reusable data module (e.g. `vol_data.py`) at the study root is fine and encouraged
once the same pulls repeat — see `2026-06-24_volatility_workstation/` for the shape.

---

## Next Steps

- [ ] Extend analysis to other equity indices
- [ ] Test stability across longer history (pre-2020)
- [ ] Compare to international markets
- [ ] Promote to `reports/IDEAS.md` if the claim survived
- [ ] Capture a durable claim into `brain/` (`/capture-finding`) or a domain KB

---

## References

- Related studies under `knowledge/studies/` or `knowledge/books/`
- Paper notes in `knowledge/papers/`, report digests in `knowledge/reports/`
- Concepts in `knowledge/brain/concepts/`
- External articles or papers

---

## Notes

- Interesting patterns noticed
- Questions raised
- Ideas for future studies
- Connections to other work
