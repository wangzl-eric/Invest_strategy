# ER Chapter 7 Notes: Equity Risk Premium

## Core Concept

The study briefing numbers this topic as Chapter 7, but in the source 2011 PDF the underlying material is actual Chapter 8, `Equity risk premium`. The core concept is the expected excess return of broad equities over a non-equity alternative, with Ilmanen distinguishing carefully between premium over cash and premium over long bonds.

He treats the equity risk premium as the most important traditional long-run reward source, but also as one of the most contested. Historical averages are informative, yet they are not enough, because ex ante ERP varies sharply with valuations, inflation conditions, and investor sentiment.

## Author Intent

Ilmanen's goal is to reconcile four lenses on ERP:

- historical excess returns
- normative theory and the equity-premium puzzle
- forward-looking valuation models
- tactical forecasting indicators

The chapter is written to move the reader away from the lazy "future equals past" ERP assumption and toward a framework where expected equity returns are conditional on starting yields, growth assumptions, macro regime, and investor expectations.

## Key Technicalities

- ERP terminology matters:
  - `ERPC` is the premium over short-dated cash or bills
  - `ERPB` is the premium over long-dated Treasuries
  - both ex post and ex ante versions matter
- The chapter distinguishes realized ERP from objective forward-looking ERP and from subjective survey expectations.
- The main forward-looking valuation identity is the Gordon/DDM expression:

$$
ERP \approx D/P + G - Y
$$

  where $D/P$ is cash-flow yield, $G$ is long-run growth, and $Y$ is long-bond yield.
- Ilmanen emphasizes that $G$ is the most weakly anchored DDM input. Long-run growth in earnings per share and dividends has generally lagged GDP growth, so plugging GDP growth directly into DDMs overstates feasible equity returns.
- Yield-ratio style indicators such as the Fed Model are useful shorthand for the equity-bond premium, but they are regime-sensitive because the relative risk of bonds and stocks changes over time.
- Tactical ERP indicators in the chapter include:
  - valuation ratios such as dividend yield and smoothed earnings yield
  - relative valuation measures versus Treasury yields
  - business-cycle indicators such as unemployment, ISM, and output-gap style measures
  - leverage and credit conditions
  - sentiment and intra-equity correlation measures

## Historical Evidence, Theories, and Forward-Looking Indicators

- Long-run U.S. equity excess returns over government bonds are roughly in the `3%`-`5%` range, somewhat higher over bills and somewhat lower outside the U.S.
- Standard consumption-based models struggle to explain the historical magnitude of ERP, which is the classic equity-premium puzzle.
- Forward-looking ERP measures vary enormously through time. Ilmanen treats near-zero or even negative implied premia during extreme booms and much higher premia after severe drawdowns as economically plausible.
- High equity valuations tend to cluster in periods of stable, mild inflation and low macro volatility, which is not a favorable setup for future multiple expansion.
- Survey evidence is mixed:
  - retail expectations look extrapolative and procyclical
  - professional estimates tend to cluster around a more modest long-run ERP
  - academic estimates often remain too high because they lean on benign historical averages
- Tactical market-timing evidence exists, but Ilmanen explicitly treats it as fragile. Valuation, cyclical, leverage, and sentiment indicators can work in sample, yet their stability is uncertain.

## Chapter Connections

- This chapter is the equity-side anchor for the rest of Part II and links directly to the bond-side material in [ch08_notes.md](/Users/zelin/Desktop/PA%20Investment/Invest_strategy/workstation/playground/studies/2026-03-29_expected_returns_ilmanen/ch08_notes.md) and [ch09_notes.md](/Users/zelin/Desktop/PA%20Investment/Invest_strategy/workstation/playground/studies/2026-03-29_expected_returns_ilmanen/ch09_notes.md).
- The valuation logic here feeds directly into later strategy chapters on value, carry, and tactical timing.
- The disagreement between rational, behavioral, and survey-based ERP estimates also extends the Part I debates from Chapters 5 and 6.

## What Seems Immediately Testable with Available Data

- Reuse `01_equity_risk_premium.ipynb` together with `01_erp_proxy_panel.csv` and `01_erp_regime_summary.csv` to test reduced-form ERP timing signals already scaffolded in this study folder.
- Test whether real-yield shocks, credit spreads, and `^VIX` jointly explain short-horizon forward `SPY` excess returns better than any one signal alone.
- Compare the predictive content of yield-curve steepness, unemployment, and business-confidence proxies for forward equity returns over `5d`, `20d`, and `60d` windows.
- Stress-test the tactical signals by separating anchored-inflation windows from inflation-repricing windows, since the chapter repeatedly warns that regime changes matter.

## What Likely Requires External or Harder-to-Source Data

- Clean long-history earnings-yield, buyback-yield, and payout-ratio datasets for a proper DDM implementation.
- Survey-based ERP expectations for households, institutions, and academics.
- Better leverage and dealer-balance-sheet datasets for the risk-appetite and intermediary-capital channel.

## Material Score

- Credibility: 5/5. This is a canonical Ilmanen chapter, with strong historical, theoretical, and forward-looking framing.
- Relevance: 5/5. ERP remains the central long-run benchmark premium and is directly connected to the existing notebook work in this study.
- Actionability: 4/5. Reduced-form timing signals are immediately testable, but the full DDM and survey exercises need richer datasets.

## Open Questions and Things to Verify Empirically

- Which reduced-form local proxy best captures Ilmanen's ex ante ERP in practice: real yields, yield ratios, leverage, or cyclical stress?
- Do equity timing signals work only because they proxy for broad discount-rate variation, or do they contain independent information?
- How often do valuation-based ERP signals fail specifically because bond risk itself has changed regime?
- Are professional survey expectations genuinely more useful than market-based ERP proxies, or just less extrapolative?
