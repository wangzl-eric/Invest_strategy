# Study Template

Use this template when documenting playground studies.

## Study Information

- **Date**: YYYY-MM-DD
- **Topic**: Brief description
- **Notebook**: Path to notebook file (if applicable)

---

## Question

What specific question are you investigating?

Example: "How does SPY-TLT correlation change during high VIX periods?"

---

## Data

List the data sources used:

- **Assets**: SPY, TLT, GLD, etc.
- **Macro indicators**: VIX (VIXCLS), 10Y yield (DGS10), etc.
- **Period**: Start date to end date
- **Source**: yfinance, FRED, Parquet lake, etc.

---

## Methodology

Brief description of your approach:

1. Load price/macro data
2. Calculate returns/volatility/correlation
3. Split by regime (if applicable)
4. Visualize patterns
5. Compute statistics

---

## Observations

Key findings from your analysis:

1. **Finding 1**: Description with supporting data
   - Example: "Correlation becomes more negative during VIX > 25 (-0.6 vs -0.3 in low vol)"

2. **Finding 2**: Description with supporting data
   - Example: "Relationship stable across multiple high vol episodes"

3. **Finding 3**: Description with supporting data
   - Example: "Breakdown during March 2020 when both assets fell together"

---

## Visualizations

List key charts created (save to study folder):

- `correlation_chart.html` - Rolling correlation over time
- `regime_comparison.html` - Statistics by regime
- `drawdown_chart.html` - Drawdown analysis

---

## Caveats

Note any limitations or concerns:

- Data quality issues
- Sample size limitations
- Regime definition choices
- Survivorship bias
- Look-ahead bias (if applicable)

---

## Next Steps

What should be explored next?

- [ ] Extend analysis to other equity indices
- [ ] Test stability across longer history (pre-2020)
- [ ] Compare to international markets
- [ ] Consider for risk overlay strategy (graduate to research)

---

## References

Links to related work:

- Related playground studies
- Existing research notebooks
- External articles or papers
- Cerebro briefings (if applicable)

---

## Notes

Any additional context or thoughts:

- Interesting patterns noticed
- Questions raised
- Ideas for future studies
- Connections to other work
