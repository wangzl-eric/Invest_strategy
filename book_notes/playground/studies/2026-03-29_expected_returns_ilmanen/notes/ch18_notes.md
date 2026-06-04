# ER Chapter 18 Notes: Tail Risks and Crisis Alpha

## Core Concept

The study briefing labels this topic as tail risks and crisis alpha, while the closest 2011 PDF source is actual Chapter 19, `Tail risks (volatility, correlation, skewness)`, with useful support from Chapter 20 on feedback effects and crowding. The chapter is not a literal crisis-alpha manual. Its core point is that volatility, correlation, and skewness exposures shape expected returns because they bite hardest in bad times and are often mispriced or misunderstood.

Ilmanen's main claim is that correlation risk is more consistently priced than pure volatility risk, while lottery preference and leverage constraints help explain why the riskiest-looking securities inside asset classes often earn disappointing returns.

## Author Intent

Ilmanen uses this chapter to broaden the volatility-selling discussion into a more general tail-risk framework. He wants the reader to stop treating tail risk as just high volatility and instead distinguish among:

- variance or volatility risk
- correlation risk
- skewness and lottery-ticket demand
- time variation in premia after adverse events

The crisis-alpha angle in the briefing is best interpreted as a regime lens: after tail events, some hedging or insurance-like exposures become especially valuable, while premia for bearing tail risk can become exceptionally wide.

## Key Technicalities

- Tail risk here means higher-moment risk, especially volatility, correlation, and skewness.
- Ilmanen emphasizes that not all volatility is equal. Standalone or idiosyncratic volatility should not automatically be rewarded, while systematic bad-times volatility exposure can be.
- The chapter's most important technical distinction is between volatility risk and correlation risk:
  - index option selling has historically been profitable
  - single-stock option selling much less so
  - this points to a correlation premium rather than a generic variance premium
- High correlation across stocks is treated as a more informative timing variable than high market volatility alone. Rising correlation damages diversification and therefore commands a more robust premium.
- Skewness pricing is linked to lottery preference:
  - investors overpay for positively skewed, lottery-ticket-like payoffs
  - they also pay heavily for crash protection through index puts
- Ilmanen's preferred explanations for low returns on high-volatility or high-beta securities are:
  - investor preference for asymmetric, lottery-like payoff profiles
  - leverage constraints that push return-seeking investors into the highest bang-for-the-buck assets
- Tail-risk premia are time varying. The chapter argues that premia can be especially high just after adverse events, when capital has been damaged and insurance sellers are scarce.

## Historical Evidence, Theories, and Forward-Looking Indicators

- The empirical relation between volatility and future returns is ambiguous. Across asset classes, higher-volatility assets can have higher average returns, but within asset classes the most volatile securities often underperform.
- High-volatility stocks underperform low-volatility stocks, and the longest-duration or most volatile bonds and credit instruments are not reliably rewarded.
- Index implied volatility tends to exceed realized volatility, but the same is not true in the same way for single-stock options, which strengthens the correlation-premium story.
- Correlation-selling trades were historically profitable before costs, but they lose precisely when correlations spike in crises.
- Market prices appear consistent with investors liking positive skewness:
  - out-of-the-money index puts are rich because crash insurance is valuable
  - out-of-the-money single-stock calls are rich because lottery-like upside is attractive
- The chapter also links tail-risk pricing to other styles. Volatility selling, carry, and illiquidity harvesting all share the same bad-times feature: high long-run returns paired with ill-timed losses.
- The clearest forward-looking implication is regime dependence. After volatility or correlation spikes, implied premia can stay elevated for months or years, though timing them remains difficult.

## Chapter Connections

- This chapter extends Chapter 15's volatility-selling discussion from option markets into a broader cross-asset higher-moment framework.
- It also connects directly to carry, illiquidity, and feedback-effect chapters because many popular premia fail through the same bad-times and crowding channels.
- The chapter helps explain why trend following and long-volatility style hedges can look like crisis diversifiers even when most insurance-selling strategies blow up during stress.

## What Seems Immediately Testable with Available Data

- Compare low-volatility and high-volatility cross-sectional portfolios in equities and bonds to test the chapter's within-asset-class anomaly claims.
- Test whether realized correlation adds more predictive power for future equity returns or VRP than realized market volatility alone.
- Extend the local volatility-risk-premium work by adding simple dispersion or correlation proxies around crisis windows.
- Study post-shock regimes to see whether tail-risk premia are systematically wider after crises than in long benign periods.

## What Likely Requires External or Harder-to-Source Data

- Long histories of index and single-stock option surfaces.
- Tradable correlation-swap or robust synthetic-dispersion datasets.
- Better skewness-sensitive cross-sectional datasets for equities and credit.
- Cleaner data on constrained leverage and crowded positioning to separate lottery demand from institutional frictions.

## Material Score

- Credibility: 5/5. The chapter is conceptually rich and tightly linked to both option evidence and broader cross-sectional anomalies.
- Relevance: 5/5. Tail-risk pricing is central for interpreting carry, VRP, low-volatility effects, and crisis behavior across the study set.
- Actionability: 4/5. Several reduced-form tests are feasible locally, but the cleanest decomposition between volatility, correlation, and skewness premia needs richer derivatives data.

## Open Questions and Things to Verify Empirically

- Is correlation risk consistently more priced than volatility risk in current local samples, or was that mostly a pre-2009 option-market feature?
- How much of low-volatility outperformance is lottery preference versus leverage-constraint effects?
- After a crisis, how long do elevated tail-risk premia actually remain harvestable before competition compresses them?
- Which local sleeves truly provide crisis diversification rather than just looking defensive in backtests?
- Can crowding indicators improve the timing of tail-risk-bearing strategies enough to avoid the worst bad-times losses?
