# ER Chapter 15 Notes: Volatility Selling and Variance Risk Premium

## Core Concept

The briefing frames this topic as a broad variance risk premium chapter, but the source 2011 PDF is more specific: actual Chapter 15 focuses on selling volatility on equity indices. Ilmanen treats this strategy as the cleanest example of selling financial insurance. The core trade is straightforward: collect option premium most of the time, then absorb large losses when volatility and correlations spike during equity crashes.

## Author Intent

Ilmanen uses this chapter to show why volatility selling looks better in historical Sharpe-ratio tables than it really is. He wants the reader to separate:

- pure volatility or variance exposure from directional equity exposure
- genuine long-run premia from sample luck and peso-problem effects
- variance risk from correlation and skewness risk

The chapter also functions as a warning that many apparently unrelated premia, especially carry-like strategies, share the same bad-times insurance-selling economics.

## Key Technicalities

- Buying options is not the same as buying volatility. A long call or long put usually has strong directional exposure. A long straddle removes direction but is still an imperfect volatility bet unless it is dynamically hedged.
- A cleaner variance-risk position is a delta-hedged straddle or, even better, a variance swap. These are designed to isolate the gap between implied and realized variance.
- Under idealized option-pricing logic, implied volatility reflects expected future volatility. In practice it also embeds risk premia, so the persistent excess of implied over realized volatility is often interpreted as a volatility premium.
- Covered-call writing is not a pure volatility-selling strategy. Its return mixes:
  - long equity beta
  - short option exposure
- The index-versus-single-stock distinction is central. Index options have historically shown a larger implied-minus-realized gap than single-stock options, which suggests that correlation risk may be more consistently priced than standalone variance risk.
- The key index-variance decomposition is:

$$
\sigma_{\text{index}}^2 \approx \sum_i w_i^2 \sigma_i^2 + \sum_{i \ne j} w_i w_j \rho_{ij}\sigma_i\sigma_j
$$

so rising average correlation can make index volatility selling much more dangerous than single-name option selling.
- Skewness pricing matters as well. Out-of-the-money index puts and out-of-the-money single-stock calls are both rich, consistent with demand for crash protection and lottery-like upside.

## Historical Evidence, Theories, and Forward-Looking Indicators

- The chapter argues that selling index volatility was highly profitable between the 1987 and 2008 crashes, but measured success is overstated by peso-problem logic because the sample excluded a repeat of the largest left-tail event until the end.
- A proximate empirical reason for long-run profitability is that index implied volatility often exceeded realized volatility by roughly `2%` to `4%`.
- Covered-call-writing strategies also looked attractive historically, but Ilmanen stresses that part of their return simply came from being long equities.
- The single-stock evidence is much weaker. That weakens the pure variance-premium story and strengthens the case for a correlation premium.
- Correlation-selling trades, such as short index volatility against long single-stock volatility, were historically profitable but lost badly when correlations surged in crises.
- Rational and behavioral explanations both remain viable:
  - rational: investors demand insurance against bad-times volatility, skew, and correlation shocks
  - behavioral: crash fears and lottery demand can make option prices systematically rich
- Forward-looking signals in the chapter are limited, but the main state variables are:
  - the implied-realized volatility gap
  - skew richness across strikes
  - correlation stress
  - crisis and deleveraging conditions

## Chapter Connections

- This chapter is the nonlinear-risk counterpart to the carry and momentum chapters: all three monetize persistent patterns, but volatility selling is the most explicit insurance-selling strategy.
- It feeds directly into the later tail-risk discussion, where Ilmanen broadens the lens from volatility to correlation and skewness.
- In the local study folder, it connects directly to [05_volatility_risk_premium.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-29_expected_returns_ilmanen/05_volatility_risk_premium.ipynb).

## What Seems Immediately Testable with Available Data

- Decompose realized strategy returns in `05_volatility_risk_premium.ipynb` into directional equity exposure versus implied-minus-realized variance capture.
- Test whether the local index VRP is better explained by variance risk alone or by a dispersion/correlation component.
- Compare simple covered-call proxies with purer volatility-selling proxies to measure how much historical performance depends on equity beta.
- Condition VRP performance on crisis windows, `VIX` level, and realized correlation spikes to test the chapter's bad-times-loss logic.

## What Likely Requires External or Harder-to-Source Data

- Clean option-surface histories for both index and single-stock options.
- Tradable or reliably reconstructed variance-swap and correlation-swap series.
- Better strike-level skew data and execution-cost estimates for realistic implementation.

## Material Score

- Credibility: 5/5. The chapter is careful, technically informed, and explicit about where historical performance can mislead.
- Relevance: 5/5. VRP and related short-insurance trades are central to modern cross-asset premia and to understanding hidden tail exposure elsewhere.
- Actionability: 4/5. Basic proxies are testable locally, but the cleanest decomposition between variance, correlation, and skew premia needs richer option data.

## Open Questions and Things to Verify Empirically

- How much of observed index VRP is really correlation premium rather than pure variance premium?
- Does the local notebook's VRP signal survive after stripping out equity beta and crisis-sample luck?
- Are skew-rich option segments persistently overpriced enough to justify targeted implementations, or do trading frictions absorb the edge?
- When volatility premia look widest after crises, are they compensation for true bad-times risk or mostly temporary dislocation?
