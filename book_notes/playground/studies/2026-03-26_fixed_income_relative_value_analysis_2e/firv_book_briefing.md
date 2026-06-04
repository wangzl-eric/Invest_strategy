# Book Briefing: Fixed Income Relative Value Analysis (2nd ed.)

**Authors:** Doug Huggins and Christian Schaller
**Publisher:** Wiley, 2024
**PDF:** /Users/zelin/Desktop/阅读学习/Fixed Income Relative Value Analysis + Website A Practitioner’s Guide to the Theory, Tools, and Trades 2nd.pdf

## Author's Central Argument

Relative value analysis identifies mispricings across fixed income instruments using statistical and financial models, enabling systematic trading and risk management. The book progresses from statistical foundations (mean reversion, PCA) to financial models (yield curves, futures, swaps) to specific market applications (reference rates, asset swaps, options).

## Book Structure

### Preface
- New reference rates (SOFR transition away from LIBOR)
- Increasing default risk of governments
- Regulation and capital constraints
- Computational access to complex models

### Part I: Statistical Models
- Chapter 2: Mean Reversion — OU process, nonparametric drift/diffusion estimation, conditional expectations, ex ante risk-adjusted returns
- Chapter 3: Principal Component Analysis — factor models, eigenvectors, level/slope/curvature decomposition, embedding PCA in trade ideas
- Chapter 4: Multivariate Mean Reversion — cross-market mean reversion (e.g. EUR 5Y5Y vs GBP 5Y5Y implied vols)

### Part II: Financial Models
- Chapter 5: Yield, Duration, Convexity — practical comments and common misapplications
- Chapter 6: Yield Curve Models — jump-diffusion, shadow rate models
- Chapter 7: Bond Futures Contracts — delivery options, multi-factor delivery option models
- Chapter 8: Fitted Bond Curves — discount factor functions, optimization
- Chapter 9: Analytic Process for Government Bond Markets — fitted curves + PCA + bond selection

### Part III: Markets
- Chapter 10: Overview
- Chapter 11: Reference Rates — SOFR, repo market, secured vs unsecured spreads, regulatory capital
- Chapter 12: Asset Swaps
- Chapters 13-18: Spreads, cross-currency basis, repo/haircuts
- Chapter 19: Options — single/multi-underlying, vega sector PCA, Asian options
- Chapter 20: Relative Value in a Broader Perspective — macroeconomic role of arbitrage

## Reading Protocol (Book)

- Track argument arc chapter by chapter
- Extract technicalities: formulas, models, frameworks
- Note how each chapter builds on previous ones
- Draft structured documentation per chapter to maintain context across sessions

## Material Scoring (apply to all related materials)

| Dimension | Description |
|-----------|-------------|
| Credibility (1-5) | Author reputation, publication venue, methodology soundness |
| Relevance (1-5) | Applicability to quant research and current playground scope |
| Actionability (1-5) | Can findings be implemented, tested, or studied concretely? |

Only materials scoring >= 3 on all three dimensions warrant deeper follow-up.
