# Fixed Income Relative Value Analysis (2nd ed.) Study

- **Date**: 2026-03-26
- **Book**: *Fixed Income Relative Value Analysis (2nd ed.)* by Doug Huggins and Christian Schaller
- **PDF**: `/Users/zelin/Desktop/阅读学习/Fixed Income Relative Value Analysis + Website A Practitioner’s Guide to the Theory, Tools, and Trades 2nd.pdf`
- **Purpose**: Scaffold a reproducible playground study flow for the book's fixed-income relative-value techniques

## Structured Book Context

- `BOOK_MAP.md`
  Briefing-aligned chapter map covering the argument arc, technicalities, chapter dependencies, material scoring, and notebook mapping.

## Notebook Plan

- `01_mean_reversion.ipynb`
  Chapter 2 scaffold with a real 2s5s10s yield butterfly proxy and Ornstein-Uhlenbeck fitting workflow.
- `02_pca_yield_curve.ipynb`
  Chapter 3 scaffold for PCA on the Treasury curve, factor interpretation, residual construction, and PCA-neutral trades.
- `03_fitted_curves.ipynb`
  Chapter 8 scaffold for fitted curves, discount-factor parameterizations, and curve residual analysis.
- `04_asset_swaps.ipynb`
  Chapter 12 scaffold for asset-swap intuition, pricing inputs, and spread-driver decomposition.
- `05_cross_currency_basis.ipynb`
  Chapter 15 scaffold for cross-currency basis workflows, CIP-style decomposition, and data gap inventory.

## Relevant Local Data Already Available

### FRED Treasury and Rate Series

From [data/market_data/catalog.json](/Users/zelin/Desktop/PA Investment/Invest_strategy/data/market_data/catalog.json:70):

- `DGS1MO`, `DGS3MO`, `DGS6MO`
- `DGS1`, `DGS2`, `DGS3`, `DGS5`, `DGS7`, `DGS10`, `DGS20`, `DGS30`
- `DFII5`, `DFII10`, `DFII30`
- `SOFR`, `DFEDTARU`
- `T10Y2Y`, `T10Y3M`, `T10YIE`, `T5YIE`, `T5YIFR`

Coverage in the current local lake is approximately `2024-02-26` through `2026-02-27`.

### Yahoo Rates Proxies

From [data/market_data/catalog.json](/Users/zelin/Desktop/PA Investment/Invest_strategy/data/market_data/catalog.json:56):

- `^IRX` (13-week)
- `^FVX` (5-year proxy)
- `^TNX` (10-year proxy)
- `^TYX` (30-year proxy)

### FX Spot Proxies

From [data/market_data/catalog.json](/Users/zelin/Desktop/PA Investment/Invest_strategy/data/market_data/catalog.json:19):

- `EURUSD=X`, `GBPUSD=X`, `USDJPY=X`, `USDCAD=X`, `USDCHF=X`
- `AUDUSD=X`, `NZDUSD=X`, `USDNOK=X`, `USDSEK=X`
- `DX-Y.NYB`

These are useful for cross-currency-basis placeholders and FX-hedged bond intuition, but they are not actual basis swap quotes.

## Important Gaps For Fixed-Income RV

Not currently visible in the local `quant_data` / market-data lake:

- USD swap curve tenors
- OIS curves by currency
- Swaption vol surfaces
- Cash-bond term structures with coupon schedules and dirty prices
- Asset swap spread history
- Cross-currency basis swap quotes
- Repo specialness / collateral schedules
- Bond futures CTD data
- CDS curves and sovereign/corporate credit term structures

The notebooks therefore use:

- locally available Treasury and rate proxies where possible
- explicit placeholders where the book requires market data that is not yet in the data lake

## Environment

Use the repo's standard notebook environment:

```bash
conda activate ibkr-analytics
export PYTHONPATH=.
jupyter lab
```

## Notes

- The mean-reversion notebook uses the Treasury `2s5s10s` butterfly as a practical local proxy for the book's swap-curve examples.
- The other notebooks prioritize structure, reusable helper code, and clearly marked TODO cells for later implementation.
