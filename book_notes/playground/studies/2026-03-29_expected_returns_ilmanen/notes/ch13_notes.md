# ER Chapter 13 Notes: Carry Strategies Across Assets

## Core Concept

The study briefing labels this topic as carry strategies across assets, but in the 2011 PDF the closest source chapter is actual Chapter 13, `Currency carry`, especially the section `Carry here, carry there, carry everywhere`. The core concept is simple: buy assets with high current yield or positive carry and fund them by shorting lower-yielding counterparts. In FX, this means going long high-yield currencies and short low-yield currencies.

Ilmanen treats carry as one of the most portable premia in finance. It appears in currencies most clearly, but related yield-seeking strategies also show up in rates, credit, commodities, and adjacent relative-value trades.

## Author Intent

Ilmanen uses the carry chapter to make three connected points:

- naive yield seeking has worked far better historically than standard parity conditions would predict
- the premium is not a free lunch, because carry crashes are violent and badly timed
- carry is not just an FX curiosity but a broader cross-asset style with common economic logic

The chapter is meant to move the reader beyond the narrow `UIP failed` observation and toward a broader framework where carry is understood as a rewarded but crash-prone style exposure.

## Key Technicalities

- In FX, carry is the return from holding a higher-yield currency funded by a lower-yield currency.
- Under uncovered interest parity, expected FX depreciation should offset the initial yield gap:

$$
E[\Delta s_{t+1}] \approx i_t^{H} - i_t^{L}
$$

where $i_t^{H}$ and $i_t^{L}$ are high- and low-yield interest rates and $\Delta s_{t+1}$ is the expected exchange-rate move.
- Empirically, that offset has not occurred on average. This is the forward-rate-bias or forward-premium-puzzle result.
- Ilmanen's baseline G10 carry strategy ranks currencies by short-rate level each week, buys the top three and shorts the bottom three with `50/30/20` weights.
- Refinements discussed in the chapter include:
  - expanding the universe to emerging markets
  - volatility-scaling carry signals
  - combining carry with valuation or vulnerability indicators
  - timing exposure with regime indicators related to risk aversion, volatility, and liquidity
- Ilmanen's preferred interpretation is that carry resembles selling catastrophe insurance:
  - small, frequent gains
  - rare, severe losses
  - especially poor performance in bad times
- Section `13.5` generalizes the style: carry often decomposes into a current yield advantage plus market expectations of adverse future price moves, and in many markets the expected offset proves too small.

## Historical Evidence, Theories, and Forward-Looking Indicators

- The chapter reports that G10 carry was highly profitable over `1983-2009`, with about `6.1%` annual excess return, `10.5%` volatility, and a Sharpe ratio around `0.61`.
- Performance was fairly consistent across decades, and even the earlier `1953-1982` evidence still shows a strong Sharpe ratio near `0.5`.
- Emerging-market carry did even better in Ilmanen's sample, though the window was unusually favorable and trading costs were higher.
- High-yield currencies did not systematically depreciate enough to offset their carry advantage. On average, dynamic carry portfolios earned their carry.
- The chapter reviews three explanation families:
  - rational risk premia
  - irrational expectations or systematic forecast errors
  - peso-problem or rare-disaster logic
- Ilmanen lands closest to a risk-premium story, but one informed by skewness and crash timing: carry loses during flights to quality, liquidity droughts, and systemic unwinds.
- Timing signals are useful but fragile. The chapter emphasizes:
  - overcrowded positions and overvalued high-yielders as slow warning signs
  - rising implied volatility, recent carry losses, and tighter liquidity as nearer-term warning signals
  - stop-loss discipline can help because carry losses often persist for a short period after the break starts
- Cross-asset carry evidence is strong but uneven. FX carry, emerging-market FX carry, and cross-country fixed-income carry outperformed within-country credit carry in Ilmanen's samples.
- Diversifying across carry sleeves improves Sharpe most of the time, but it does not diversify away the generic bad-times exposure. In systemic stress, carry sleeves can fail together.

## Chapter Connections

- This chapter sits naturally beside value and momentum as one of the book's core dynamic style premia.
- It connects directly to the tail-risk and illiquidity chapters because carry crashes are tied to skewness, crowding, and liquidity deterioration.
- The cross-asset generalization in section `13.5` links carry to rates, credit, commodities, and volatility-selling themes elsewhere in the book.
- In the local study folder, it connects directly to [03_carry_strategies.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-29_expected_returns_ilmanen/03_carry_strategies.ipynb).

## What Seems Immediately Testable with Available Data

- Rebuild simple G10 and broader carry portfolios from short-rate differentials and compare static versus dynamically reranked implementations.
- Test volatility-scaled carry against plain carry using the local `03_carry_proxy_panel.csv` and `03_carry_forward_summary.csv` artifacts.
- Evaluate crash-timing indicators such as recent carry losses, implied-volatility spikes, and equity drawdowns for short-horizon carry-risk management.
- Compare FX carry with other local carry proxies in rates and commodities to test Ilmanen's claim that cross-country carry has historically dominated within-country carry.

## What Likely Requires External or Harder-to-Source Data

- Longer and cleaner emerging-market rate and FX histories with realistic trading-cost assumptions.
- Survey-based exchange-rate expectations to separate risk premia from forecast errors more cleanly.
- Better positioning, funding, and dealer-balance-sheet data to measure crowding and unwind risk directly.

## Material Score

- Credibility: 5/5. The chapter is one of the book's strongest style-premium case studies and combines empirical evidence with careful skepticism about why the effect exists.
- Relevance: 5/5. Carry is a core cross-asset style and directly relevant to both macro and relative-value research.
- Actionability: 5/5. The baseline strategy, refinements, and crash-timing questions are all implementable with standard market data.

## Open Questions and Things to Verify Empirically

- How much of carry's long-run reward survives once modern crowding and realistic post-2008 trading frictions are imposed?
- Are survey-based forecast errors really the dominant explanation, or do they just coexist with a genuine bad-times risk premium?
- Which timing indicators are actually useful in real time rather than merely descriptive after a crash?
- Does cross-asset diversification among carry sleeves still help materially, or has systemic synchronization made generic carry too singular a risk factor?
