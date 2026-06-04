# GMT Chapter 9 Notes: Fixed Income

## Core Concept and Author Intent

Chapter 9 is a market-plumbing chapter. Gliner is trying to make the reader operationally literate in short-rate markets, rates derivatives, sovereign curves, and credit risk so that fixed income stops being a black box. The chapter's practical message is that fixed income is not just a place to express duration views; it is the funding, discounting, inflation, and sovereign-risk backbone of macro.

## Core Mental Models

- Money markets are the funding layer underneath the visible asset markets.
- Short-end rates anchor much of the global pricing system.
- The yield curve encodes policy expectations, growth, inflation, and at times default risk.
- Carry and rolldown matter as much as direction in rates trading.
- Real rates and inflation can be separated through TIPS and breakevens.
- Sovereign credit can be expressed in bonds, curves, or CDS, each with different mechanics.

## Practitioner Heuristics

- Track funding stress through benchmark spreads such as LIBOR-OIS.
- Do not trade rates futures or swaps without understanding the underlying settlement and delivery mechanics.
- When trading curve views, size on a DV01-neutral basis and explicitly account for carry and rolldown.
- Use TIPS and breakevens to distinguish inflation views from nominal-duration views.
- Treat long-end curve inversion in stressed sovereigns as credit information, not just growth information.
- Use CDS when the objective is asymmetric protection or basis hedging, not just because it looks cleaner than the cash bond.

## Key Frameworks

### 1. Short-Term Funding Architecture

The chapter opens with money-market instruments and the funding stack:

- commercial paper
- Treasury bills
- government agencies
- municipals
- banker's acceptances
- time deposits
- interbank loans
- repos

The point is not to memorize instruments; it is to recognize that the fixed-income system starts with how capital is borrowed overnight to one year out.

### 2. Benchmark Short-Rate Framework

Gliner then maps the key short-rate benchmarks and derivatives:

- LIBOR
- Eurodollar futures
- Fed funds
- OIS
- FRA
- swaps

This is the chapter's way of showing how policy expectations and funding costs move from central-bank language into tradable curves.

### 3. Real Rates and Inflation Framework

The TIPS section is more important than it first appears. It gives a clean macro decomposition:

- nominal yield
- minus breakeven inflation
- equals real yield

That is a reusable macro identity. Once you can separate nominal rates into inflation expectations and real rates, many cross-asset moves become easier to interpret.

### 4. Curve Expression Framework

The chapter's core trading framework is the curve:

- steepeners
- flatteners
- bull flatteners
- bear flatteners
- carry and rolldown

This matters because many macro rates views are relative-duration views rather than outright duration bets.

### 5. Sovereign Credit Framework

Gliner connects sovereign risk across three layers:

- the bond curve
- curve inversion
- CDS pricing and credit events

The strongest practitioner lesson is that bond and CDS markets are insurance and funding markets as much as forecasting markets.

## Chapter Connections

- Chapter 9 deepens Chapter 4's claim that fixed income is the key discount-rate market.
- The mechanics of policy implementation and reserves connect directly to Chapter 11.
- Inflation, growth, and fiscal indicators from Chapter 12 are major drivers of the rates and sovereign-credit frameworks here.
- In the current study folder, the nearest notebook links are `01_cross_asset_overview.ipynb` and `04_central_bank_policy.ipynb`. There is no dedicated fixed-income notebook yet.

## What Seems Immediately Testable with Available Data

- Curve-slope and curve-change signals versus future macro regimes.
- Breakeven inflation versus realized inflation and cross-asset reactions.
- Term-structure carry and rolldown strategies in liquid Treasury futures.
- Funding-stress indicators such as LIBOR-OIS or modern equivalents against equity and credit stress.
- Sovereign-curve inversion as a recession or credit-stress signal across countries.

## What Likely Requires External or Harder-to-Source Data

- Full OTC swap and FRA histories with realistic trading assumptions.
- Sovereign CDS histories and basis data.
- Repo-market and collateral data.
- Detailed delivery-option and cheapest-to-deliver analytics for historical futures studies.

## Material Score

- Credibility: 4/5. The market descriptions are solid and operationally useful, though some benchmarks are specific to the pre-SOFR era.
- Relevance: 5/5. This chapter is central to any real macro trading workflow.
- Actionability: 4/5. Many ideas are testable, but some require institutional data and instrument-level expertise.

## Open Questions and Things to Verify Empirically

- Which curve trades are most robust after carry and rolldown are fully accounted for?
- How much information content remains in sovereign curves when central banks dominate local bond markets?
- What modern benchmark best replaces the chapter's LIBOR-centric framing?
- When does CDS provide earlier warning than bonds, and when is it just a leveraged echo?
- How should rates signals be combined with macro data revisions to avoid trading pure noise in central-bank-heavy regimes?
