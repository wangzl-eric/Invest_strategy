# ER Chapter 11 Notes: Alternative Asset Premia

## Core Concept

Alternative assets can improve diversification and sometimes enhance returns, but Ilmanen's treatment is deliberately skeptical. The common alternative-asset sales pitch is weakened by three recurring facts:

- alternatives are often illiquid and opaque
- historical performance is heavily shaped by reporting and smoothing biases
- broad alternative portfolios often fail exactly in bad times

The chapter therefore treats "alternative premia" as a heterogeneous set of exposures rather than a single magic return source.

## Author Intent

Ilmanen closes the asset-premia case-study block by asking which alternative return sources are genuine, which are mostly compensation for illiquidity or hidden beta, and which are overstated by bad data. He wants the reader to distinguish between:

- real assets such as real estate and commodities
- delegated-strategy vehicles such as hedge funds and private equity

and to judge them on diversification quality, inflation sensitivity, fees, and behavior in stress regimes rather than on headline Sharpe ratios alone.

## Key Technicalities

- Real estate:
  - key valuation measures are rental yield, cap rate, income return, and cash-flow yield
  - private-market data are smoothed and stale, which understates volatility and correlation
  - listed REITs are cleaner but contain more equity-market contamination
- Commodity futures:

$$
R_{\text{fut}} \approx \Delta S + R_{\text{collateral}} + R_{\text{roll}}
$$

  - roll return depends on curve shape
  - backwardation supports positive roll
  - contango imposes negative carry
- Hedge funds:
  - historical returns are contaminated by survivorship, backfill, and illiquidity smoothing
  - apparent alpha often includes traditional and alternative beta plus tail and liquidity risk
- Private equity:
  - performance should be judged net of fees, stale marks, leverage, and selection effects
  - top-quartile manager selection matters far more than average industry exposure
- A recurring technical theme is that alternatives are strongly procyclical: they do best when liquidity is abundant and risk appetite is high.

## Historical Evidence, Theories, and Forward-Looking Indicators

- Real estate long-run return sits broadly between bonds and equities, with most of the long-run real return coming from income rather than real price appreciation. Starting valuations matter.
- Commodity futures have historically offered low correlation and good inflation-hedging properties, but their long-run average return depends heavily on collateral and roll rather than on spot appreciation alone.
- The commodity sleeve is heterogeneous: energy and industrial metals have been much stronger than agriculture or livestock over many windows.
- Hedge funds appear to have added value in index data, but Ilmanen repeatedly warns that those data likely overstate true industry returns and understate downside risk.
- Private equity looks much less impressive after adjusting for reporting bias and risk; average funds may underperform listed equities despite their liquidity disadvantage.
- The chapter is unusually candid that alternatives largely failed as broad diversification tools in `2008`, which is exactly the stress test that matters most.
- Forward-looking indicators are scarce for alternatives. Ilmanen leans more on historical evidence, valuation signals where available, and flow/crowding logic than on any one universal ex ante metric.

## Chapter Connections

- This chapter completes the Part II asset-premia survey after equities, bonds, and credit.
- It also connects to later carry, momentum, volatility, and illiquidity chapters because many alternatives are bundles of those more primitive premia.
- Within this repo, it links naturally to the commodity and macro-regime work already built in the GMT study and to the alternative-premia hypotheses in this study folder.

## What Seems Immediately Testable with Available Data

- Reuse the commodity-proxy work referenced in `study_hypotheses.md`, especially `COM-1` to `COM-3` and `ALT-1` to `ALT-3`, to test Chapter 11 ideas in reduced form using `GC=F`, `CL=F`, breakevens, the dollar index, and Fed-liquidity proxies.
- Use the GMT commodity basket and `05_commodities_macro.ipynb` as the cleanest current implementation of the chapter's commodity-premium discussion.
- Test gold as a real-yield hedge versus a generic risk-off asset using `DFII5`, `DFII10`, and macro-regime splits.
- Compare inflation-beta versus equity-beta behavior of the local commodity proxies during inflation-shock and funding-stress windows.

## What Likely Requires External or Harder-to-Source Data

- Private real-estate datasets with de-smoothed returns and consistent cap-rate histories.
- Hedge-fund databases with explicit survivorship and backfill controls.
- Private-equity cash-flow and PME-style benchmarking datasets.
- Full commodity-futures curve data for proper roll and term-structure analysis.

## Material Score

- Credibility: 4/5. The chapter is careful and nuanced, but some asset classes suffer from weak or biased historical data.
- Relevance: 4/5. The commodity and gold sleeves are directly relevant now; real estate, hedge funds, and private equity are more data-constrained locally.
- Actionability: 4/5. Several reduced-form commodity and gold tests are immediately feasible, but much of the true alternative-premia space needs better data.

## Open Questions and Things to Verify Empirically

- Which alternative exposures in practice are mostly hidden equity beta, and which provide genuinely distinct premia?
- How much of the historical commodity premium is roll versus inflation sensitivity versus spot trend?
- Are gold and broad commodities better modeled as inflation hedges, real-yield hedges, or funding-stress assets?
- How much diversification benefit survives once illiquidity smoothing and reporting bias are stripped out of real estate, hedge fund, and private-equity data?
