# ER Chapter 10 Notes: Credit Risk Premium

## Core Concept

The credit risk premium is the expected return advantage of bearing credit exposure instead of holding Treasuries. Ilmanen's core point is that raw credit spreads are not the same thing as ex ante excess returns, because spreads also compensate for expected default and downgrading losses, illiquidity, and embedded options.

The chapter's most important empirical conclusion is uncomfortable: long-run realized credit outperformance has been modest, and much worse than the historical level of spreads would suggest.

## Author Intent

Ilmanen wants the reader to stop equating "wide spreads" with "high realized reward." He decomposes credit spreads, explains why ex post credit premia have been so poor, and then isolates the one area he thinks has been structurally attractive: short-dated, top-rated credit carry against Treasuries.

The tone is explicitly practitioner-focused: what matters is not just default math, but how mandates, index rules, liquidity, and funding conditions shape realized outcomes.

## Key Technicalities

- The stylized spread decomposition is:

$$
\text{Raw spread} \approx \text{true ex ante return advantage} + \text{expected default/downgrading loss cushion} + \text{embedded option cushion}
$$

- Expected default loss is:

$$
\text{Expected default loss} = \text{Default probability} \times (1 - \text{Recovery rate})
$$

- Structural models such as Merton treat equity as a call option on firm assets and debt as riskless debt minus a short put. This explains why bondholders are effectively short firm volatility.
- Reduced-form models estimate default risk directly from market prices and observable indicators, but they are easier to overfit.
- The chapter's practical puzzle is why historical spreads were wide while realized excess returns were small.
- Ilmanen's answer is investor heterogeneity:
  - buy-and-hold investors keep downgraded and aging bonds
  - index investors sell fallen angels and short-dated bonds at exactly the wrong time
  - this bad mechanical selling destroys a meaningful part of the spread advantage
- The standout technical niche is front-end high-grade credit carry:
  - high spread-duration ratios
  - broad break-even cushions
  - Treasury convenience yield and financing asymmetries that prevent levered arbitrageurs from fully eliminating the opportunity

## Historical Evidence, Theories, and Forward-Looking Indicators

- Long-run investment-grade excess returns over Treasuries are only about `0.2%`-`0.5%` annually, despite much wider average spreads.
- Long-dated corporate bonds have performed especially poorly, while `BB`-rated bonds are the strongest long-run rating bucket.
- The weakest long-run performance sits in the riskiest tail, with `CCC` bonds looking particularly unattractive as strategic long-horizon holdings.
- The chapter treats front-end `AAA/AA` carry as the main exception, with unusually strong historical reward-to-risk prior to the 2007-2008 crisis.
- For top-rated bonds, spread variation is driven more by Treasury liquidity scarcity and convenience yield than by default risk.
- For `A` and `BBB` bonds, cyclical effects and equity/spread volatility dominate.
- For high yield, expected default clustering is the key driver.
- Tactical forecasting in the chapter leans on wide spreads, cyclical weakness, volatility, and supply-demand conditions, but Ilmanen stresses that not all wide spreads are alike.

## Chapter Connections

- This chapter extends the bond-premium logic in [ch09_notes.md](/Users/zelin/Desktop/PA%20Investment/Invest_strategy/workstation/playground/studies/2026-03-29_expected_returns_ilmanen/ch09_notes.md) into non-government debt.
- It also connects directly to later carry discussions because front-end credit carry is one of the book's clearest cross-market carry examples.
- Within the repo, it links naturally to the fixed-income and credit ideas already outlined in `study_hypotheses.md`.

## What Seems Immediately Testable with Available Data

- Use `BAMLH0A0HYM2`, `NFCI`, `^VIX`, and `SPY` to test the local Chapter 10 hypotheses already written in `study_hypotheses.md`, especially `CRP-1` through `CRP-5`.
- Measure whether very wide spreads plus improving liquidity predict better forward equity and credit-sensitive outcomes than wide spreads alone.
- Test whether spread-widening shocks are better thought of as tail-risk transmitters than as simple contrarian entry signals.
- Use the local `credit_spread_carry` series in `03_carry_proxy_panel.csv` as a reduced-form bridge to the chapter's carry logic, while explicitly recognizing that it is not a full bond total-return implementation.

## What Likely Requires External or Harder-to-Source Data

- Investable credit total-return series such as `LQD`, `HYG`, CDX, or iTraxx histories.
- Cleaner rating-bucket and fallen-angel datasets for directly testing Ilmanen's index-investor argument.
- Bond-level liquidity, financing-rate, and specialness data for a proper front-end credit-carry decomposition.

## Material Score

- Credibility: 5/5. The chapter is rigorous, nuanced, and unusually clear about where spread intuition fails.
- Relevance: 5/5. It is highly relevant to fixed-income and cross-asset risk work in this repo.
- Actionability: 4/5. The chapter's reduced-form stress signals are testable now, but the cleanest bond-level implementations need richer data.

## Open Questions and Things to Verify Empirically

- How much of the historical credit puzzle is really due to bad index rules versus illiquidity and convenience-yield effects?
- Does front-end high-grade carry remain attractive after the post-crisis market-structure and balance-sheet changes?
- Can we separate liquidity-driven spread widening from default-driven widening well enough to improve tactical signals?
- How often do wide spreads normalize quickly, and how often are they just the first stage of a deeper funding shock?
