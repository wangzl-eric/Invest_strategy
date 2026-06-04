# GMT Chapter 4 Notes: The Building Blocks of Global Macro Trading

## Core Concept and Author Intent

Chapter 4 establishes the four basic product groups of macro trading: currencies, equities, fixed income, and commodities. Gliner's main point is that a macro trader should not treat these as separate silos. They are linked through growth, inflation, policy, trade flows, and risk appetite. The chapter is therefore less about asset definitions and more about cross-asset translation: if one market moves, what else should move, and why?

## Core Mental Models

- Global macro starts with four product groups, but edge comes from understanding the links between them.
- Fixed income is the discount-rate and policy anchor for the rest of the system.
- Certain currencies are shadow expressions of commodities or risk appetite.
- Risk-on / risk-off is a cross-asset regime switch, not an equities-only concept.
- Correlation is state-dependent and becomes more dangerous in stress.
- A portfolio can look diversified by line item while still being one macro bet.

## Practitioner Heuristics

- Start each day by checking representative anchors in each product group rather than staring at one market in isolation.
- Use commodity-linked currencies as fast readouts on commodity regimes.
- Treat sovereign fixed income as the central policy transmission channel, not just another asset bucket.
- Expect correlations to spike when markets are stressed; calm-period diversification is fragile.
- Do not assume central-bank-distorted fixed income markets are reliable "fundamental value" signals.
- When expressing a macro theme, ask which asset offers the cleanest and highest-beta implementation.

## Key Frameworks

### 1. Four Product Group Map

- Currencies: liquid expression of cross-country growth, policy, and terms-of-trade views.
- Equities: primary risk-asset barometer.
- Fixed income: valuation anchor, carry engine, and policy signal.
- Commodities: growth, scarcity, inflation, and geopolitical stress gauges.

This is the book's core ontology for macro.

### 2. Cross-Asset Linkage Framework

The chapter gives intuitive examples:

- `CAD` tracks oil because Canada exports energy.
- `CLP` tracks copper because Chile exports copper.
- Strong U.S. growth can lift equities, industrial commodities, and commodity currencies together.

The practical lesson is to think in terms of transmission chains rather than single-market stories.

### 3. Risk-On / Risk-Off Diagnostic

Risk-on is a regime in which pro-growth assets move together:

- equities up
- oil and copper up
- commodity currencies stronger

Risk-off is the reverse. This is a useful trader shorthand, but Gliner is clear that it is a tendency, not a law. Policy surprises can break the pattern.

### 4. Correlation as a Portfolio Risk Tool

Correlation is not just a descriptive statistic; it tells the trader whether separate positions are really the same exposure. The important twist is that downside correlations tend to be stronger than upside correlations, so stress testing matters more than average-period estimation.

## Chapter Connections

- Chapter 4 supplies the asset map that Chapters 7 through 12 unpack in detail.
- The risk-on / risk-off language supports Chapter 3 event studies and analogs.
- The correlation discussion ties directly back to Chapter 2 portfolio risk management.

## What Seems Immediately Testable with Available Data

- Rolling correlations between `CAD` and `WTI`, `CLP` and copper, `AUD` and industrial metals, `SPX` and high-beta EM equities.
- Stress versus calm correlation regimes across the four product groups.
- Simple risk-on baskets that combine equities, commodities, and FX to detect broad regime shifts.
- Event studies showing how central bank surprises propagate through multiple asset classes.

## What Likely Requires External or Harder-to-Source Data

- Institutional flow data to separate causal trade channels from coincident price movement.
- Higher-frequency cross-asset data around macro releases and policy events.
- Clean country-level trade and capital-flow datasets for deeper transmission modeling.

## Material Score

- Credibility: 4/5. The cross-asset relationships are standard macro practice, though many are presented heuristically rather than formally.
- Relevance: 5/5. This chapter provides the base map for all later macro work.
- Actionability: 5/5. Most of the chapter's claims can be tested with public prices and rolling correlation work.

## Open Questions and Things to Verify Empirically

- Which cross-asset linkages are stable and which are regime-dependent?
- How much has central-bank intervention weakened the information content of sovereign yields?
- Can a robust risk-on / risk-off factor be built that outperforms simple equity-beta proxies?
- Which market tends to lead in each linkage pair: the commodity, the currency, or the equity index?
- How should correlation estimates be shrunk or stress-adjusted when building macro books?
