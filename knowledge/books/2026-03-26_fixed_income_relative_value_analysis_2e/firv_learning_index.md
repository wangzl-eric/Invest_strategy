# FIRV Learning Index

This file is the working map for the *Fixed Income Relative Value Analysis (2nd ed.)* playground study.

## Book-Level Context

- [Book briefing](firv_book_briefing.md)
- [Book map](00_book_map.md)
- [Study README](README.md)

## Chapter Notes

- [Chapter 2: Mean Reversion](notes/ch02_notes.md)
- [Chapter 3: Principal Component Analysis](notes/ch03_notes.md)
- [Chapter 4: Multivariate Mean Reversion](notes/ch04_notes.md)
- [Chapter 5: Yield, Duration, and Convexity](notes/ch05_notes.md)
- [Chapter 6: Yield Curve Models](notes/ch06_notes.md)
- [Chapter 7: Bond Futures Contracts](notes/ch07_notes.md)
- [Chapter 8: Fitted Bond Curves](notes/ch08_notes.md)
- [Chapter 9: Analytic Process for Government Bond Markets](notes/ch09_notes.md)
- [Chapter 10: Overview — Swap Block Bridge](notes/ch10_notes.md)
- [Chapter 11: Reference Rates and SOFR](notes/ch11_notes.md)
- [Chapter 12: Asset Swaps](notes/ch12_notes.md)
- [Chapter 13 / 14: CDS and Intra-Currency Basis](notes/ch13_notes.md)
- [Chapter 15: Cross-Currency Basis](notes/ch15_notes.md)
- [Chapter 16: Cross-Market Bond RV](notes/ch16_notes.md)
- [Chapter 17: Global Bond RV via Fitted Curves and SOFR ASW](notes/ch17_notes.md)
- [Chapter 18: Repo, Haircuts, and Collateral](notes/ch18_notes.md)
- [Chapter 19: Options Relative Value](notes/ch19_notes.md)
- [Chapter 20: Macro Perspective on Arbitrage](notes/ch20_notes.md)

## Practical Notebooks

- [01 Mean Reversion](notebooks/01_mean_reversion.ipynb)
- [02 PCA Yield Curve](notebooks/02_pca_yield_curve.ipynb)
- [03 Fitted Curves](notebooks/03_fitted_curves.ipynb)
- [04 Asset Swaps](notebooks/04_asset_swaps.ipynb)
- [05 Cross-Currency Basis](notebooks/05_cross_currency_basis.ipynb)

## Concept-to-Notebook Map

| Concept | Primary note | Primary notebook | Next practical step |
|---|---|---|---|
| Scalar mean reversion / OU | [ch02_notes.md](notes/ch02_notes.md) | [01_mean_reversion.ipynb](notebooks/01_mean_reversion.ipynb) | add nonparametric drift and first-passage diagnostics |
| Curve PCA / factor residuals | [ch03_notes.md](notes/ch03_notes.md) | [02_pca_yield_curve.ipynb](notebooks/02_pca_yield_curve.ipynb) | add PCA-neutral weight solving and rolling stability |
| Multivariate OU / system-level spreads | [ch04_notes.md](notes/ch04_notes.md) | currently bridges [01_mean_reversion.ipynb](notebooks/01_mean_reversion.ipynb) and [02_pca_yield_curve.ipynb](notebooks/02_pca_yield_curve.ipynb) | create a dedicated multivariate mean reversion notebook |
| Yield / duration / convexity guardrails | [ch05_notes.md](notes/ch05_notes.md) | currently conceptual support for [03_fitted_curves.ipynb](notebooks/03_fitted_curves.ipynb) | add a small duration-vs-curve residual sanity check |
| Yield-curve model awareness | [ch06_notes.md](notes/ch06_notes.md) | currently conceptual support for [03_fitted_curves.ipynb](notebooks/03_fitted_curves.ipynb) | add shadow-rate / jump-stress notes to future curve work |
| Bond futures delivery option | [ch07_notes.md](notes/ch07_notes.md) | no dedicated notebook yet | scaffold a futures delivery-option notebook |
| Fitted discount / yield curves | [00_book_map.md](00_book_map.md) | [03_fitted_curves.ipynb](notebooks/03_fitted_curves.ipynb) | add actual calibration and residual ranking |
| Fitted-curve methodology | [ch08_notes.md](notes/ch08_notes.md) | [03_fitted_curves.ipynb](notebooks/03_fitted_curves.ipynb) | extend optimization and residual diagnostics |
| Asset swaps / swap-spread drivers | [00_book_map.md](00_book_map.md) | [04_asset_swaps.ipynb](notebooks/04_asset_swaps.ipynb) | ingest or source asset-swap spread histories |
| CDS curves and intra-currency basis | [ch13_notes.md](notes/ch13_notes.md) | currently conceptual support for [04_asset_swaps.ipynb](notebooks/04_asset_swaps.ipynb) and [05_cross_currency_basis.ipynb](notebooks/05_cross_currency_basis.ipynb) | source a CDS panel and one intra-currency basis time series |
| Cross-currency basis | [00_book_map.md](00_book_map.md) | [05_cross_currency_basis.ipynb](notebooks/05_cross_currency_basis.ipynb) | source FX forwards, OIS curves, and CCBS quotes |
| Cross-currency basis mechanics and structural drivers | [ch15_notes.md](notes/ch15_notes.md) | [05_cross_currency_basis.ipynb](notebooks/05_cross_currency_basis.ipynb) | turn placeholder structure into a proper CIP / basis notebook once data exists |
| Options RV and vega-sector PCA | [ch19_notes.md](notes/ch19_notes.md) | no dedicated notebook yet | add an options-RV notebook only if usable options surface data is available |
| Macro perspective on arbitrage | [ch20_notes.md](notes/ch20_notes.md) | conceptual lens across all notebooks | use it to distinguish transient dislocations from structural wedges |

## Current Data Status

Already available locally:

- Treasury FRED curve and policy/funding proxies
- inflation expectation and real-yield proxies
- Yahoo rate proxies
- major FX spot pairs

Still missing for deeper fixed-income RV implementation:

- swap curves
- OIS curves across currencies
- cross-currency basis quotes
- asset swap spread time series
- bond-level price and cashflow histories
- repo/collateral specialness data

## Suggested Reading / Implementation Order

1. Read [ch02_notes.md](notes/ch02_notes.md) and run [01_mean_reversion.ipynb](notebooks/01_mean_reversion.ipynb)
2. Read [ch03_notes.md](notes/ch03_notes.md) and run [02_pca_yield_curve.ipynb](notebooks/02_pca_yield_curve.ipynb)
3. Read [ch04_notes.md](notes/ch04_notes.md) and design the next multivariate notebook
4. Read [ch05_notes.md](notes/ch05_notes.md), [ch06_notes.md](notes/ch06_notes.md), and [ch07_notes.md](notes/ch07_notes.md) as conceptual guardrails before deeper instrument work
5. Read [ch08_notes.md](notes/ch08_notes.md) and extend [03_fitted_curves.ipynb](notebooks/03_fitted_curves.ipynb)
6. Read [ch13_notes.md](notes/ch13_notes.md) and [ch15_notes.md](notes/ch15_notes.md) before deeper spread/basis work
7. Read [ch19_notes.md](notes/ch19_notes.md) if the study extends into options or vega-sector RV
8. Use [ch20_notes.md](notes/ch20_notes.md) as the macro lens when interpreting persistent dislocations

## Open Follow-Ups

- ~~add notes for Chapters 16-18 to complete the market-structure arc~~ **DONE** — ch16, ch17, ch18 notes complete as of 2026-03-26
- decide whether to ingest swap, OIS, CDS, and basis data before deeper replication work
- consider scaffolding a dedicated bond futures notebook and a multivariate mean reversion notebook
- reading queue: 11 papers still unread (#3, #4, #6, #9, #13, #14, #15, #16, #18, #19, #20) — next priority: #3 Nelson-Siegel (Ch8) and #15 Kim-Wright (Ch9)
