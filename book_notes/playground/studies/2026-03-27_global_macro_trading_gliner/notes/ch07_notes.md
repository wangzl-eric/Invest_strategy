# GMT Chapter 7 Notes: Foreign Exchange in Global Macro

## Core Concept and Author Intent

Chapter 7 frames FX as the most liquid and systemically important product group in macro, but also one of the hardest to value. Gliner's main point is that currencies cannot be analyzed in isolation: they are relative prices shaped by reserve status, policy regime, growth expectations, trade flows, credit conditions, and carry. The chapter is trying to give the reader a practical valuation stack rather than a single grand model.

## Core Mental Models

- FX is always relative. A currency never has an absolute price; it only has value against another currency.
- The U.S. dollar is the system numeraire because it dominates settlement, reserves, and funding.
- Regime comes before valuation. A pegged or heavily managed currency cannot be treated like a free float.
- Cross-asset signals matter. Equities, CDS, commodities, and rates can all act as FX inputs.
- Carry is powerful, but unadjusted carry is just compensated risk-taking.
- PPP is a slow anchor, not a short-term timing tool.

## Practitioner Heuristics

- Start by classifying the currency regime before building a directional view.
- Use the dollar index and reserve trends to understand the global backdrop, not just the local story.
- In EM, track equity performance and sovereign credit alongside the currency.
- Use current account and terms of trade as medium-term structural anchors.
- Treat risk reversals as sentiment and hedging demand indicators rather than standalone forecasts.
- Compare carry on a risk-adjusted basis; raw yield differentials can be misleading.
- Be skeptical of debt-to-GDP as a short-horizon FX predictor unless funding and policy conditions are also deteriorating.

## Key Frameworks

### 1. USD-Centric FX System

The chapter starts with a simple but important reality:

- the U.S. dollar dominates FX turnover
- central banks overwhelmingly hold reserves in dollars
- the dollar index is a convenient proxy for global dollar strength

That framing matters because many local currency stories are really dollar stories in disguise. In practice, the dollar is not just another currency; it is the reserve and funding asset around which much of the system is organized.

### 2. FX Market Structure by Instrument

Gliner walks through the main FX instruments:

- spot
- forwards
- non-deliverable forwards
- futures
- options

The practical distinction is that different instruments reveal different constraints. NDFs, for example, are not just another derivative; they are evidence that the local currency regime itself is restricted.

### 3. Currency Regime Framework

The chapter's regime taxonomy is one of its most useful ideas:

- fixed
- floating with frequent intervention
- floating with little intervention

The Hong Kong dollar and Brazilian real case studies make the lesson concrete. Before estimating fair value, the trader must know whether policy makers are willing to override it.

### 4. FX Valuation Stack

Rather than rely on one formula, Gliner builds a stack of practical inputs:

- relative equity performance
- earnings revisions and equity flows
- sovereign CDS and credit spreads
- risk reversals for sentiment
- current account and trade-weighted indices
- GDP and macro forecast revisions
- export-partner growth
- direct export exposures such as oil for `CAD`
- debt-to-GDP
- absolute and relative PPP
- GDP per capita and productivity
- carry via OIS, LIBOR differentials, and carry-to-risk ratios

The chapter's real contribution is this layered methodology. The working assumption is that no single FX model is robust enough on its own, so the trader should compare multiple partial signals.

### 5. Carry as Both Return and Risk

Carry is presented as one of the strongest recurring FX forces. But the important subtlety is that Gliner does not stop at rate differentials. He pushes toward risk-adjusted carry, which is closer to how a macro desk would actually compare crosses across funding and volatility conditions.

## Chapter Connections

- Chapter 7 is the direct asset-level extension of Chapter 4's cross-asset map.
- The emphasis on intervention and policy transmission ties closely to Chapter 11.
- The heavy use of current account, growth, and inflation inputs connects directly to Chapter 12.
- The natural notebook link in this study folder is `02_fx_valuation.ipynb`, with `03_macro_regime_indicators.ipynb` as a useful companion for macro inputs.

## What Seems Immediately Testable with Available Data

- PPP, terms-of-trade, and carry signals for major and liquid EM crosses.
- Predictive value of relative equity performance for currencies such as `BRL`, `MXN`, and `AUD`.
- Commodity-linked FX relationships such as `CAD`-oil and `CLP`-copper.
- Current-account and growth-revision signals for medium-horizon FX moves.
- Simple carry-to-volatility ranking strategies across liquid crosses.

## What Likely Requires External or Harder-to-Source Data

- Clean options data for three-month risk reversals.
- Reliable equity flow data by country.
- Timely export-partner forecast datasets with historical vintages.
- Institutional EM credit and basis data beyond public proxies.

## Material Score

- Credibility: 4/5. The chapter's signals are standard macro tools, though some are presented more heuristically than formally.
- Relevance: 5/5. This is directly useful for discretionary and systematic FX research.
- Actionability: 5/5. Most of the signals can be prototyped immediately with market and macro data.

## Open Questions and Things to Verify Empirically

- Which parts of the valuation stack are most stable across different FX regimes?
- How much predictive power survives once carry, dollar regime, and commodity beta are controlled for simultaneously?
- When does PPP become useful in practice: one year, three years, or longer?
- Does sovereign CDS add incremental value beyond rates differentials and equity performance in EM FX?
- Which currencies are best modeled as policy-regime trades and which as macro-factor trades?
