# GMT Chapter 3 Notes: Back-Tests, Queries, and Analogs

## Core Concept and Author Intent

Chapter 3 argues that historical conditioning can improve macro decision-making even when it cannot forecast with certainty. Gliner is teaching a pragmatic use of history: do not treat the past as destiny, but use it to narrow the distribution of plausible outcomes around events and confusing price action. The chapter's real contribution is a workflow for event studies and analog matching that helps traders ask better questions before they place risk.

## Core Mental Models

- A query is an event-conditioned return study.
- An analog is a path-similarity exercise, not a causal model.
- The value of history is not certainty; it is better priors.
- The most important step is problem definition: which event or regime are you actually conditioning on?
- Mean outcome is not enough; direction frequency and dispersion matter.
- False positives are inevitable, so query-based trades need faster loss discipline than slower macro theses.

## Practitioner Heuristics

- Start with a clearly defined catalyst such as a central bank meeting, QE announcement, or major data release.
- Narrow the historical sample to cases that match the current regime as closely as possible.
- Evaluate multiple horizons, not just same-day response.
- Look at average return, up/down hit rate, and standard deviation together.
- Use queries to map portfolio exposure around events even when you do not take a directional trade.
- Treat small-sample event studies as suggestive, not authoritative.
- If a short-term query trade fails immediately, cut it quickly rather than rationalizing it.

## Key Frameworks

### 1. Event Query Workflow

The chapter's practical workflow is:

1. identify the event
2. define the conditioning set
3. select the assets likely to react
4. calculate horizon-by-horizon returns
5. record hit rates and volatility
6. decide whether the edge is strong enough to trade

This is essentially a lightweight event-study framework for discretionary macro.

### 2. Query Output Table

Gliner implicitly recommends three statistics for each asset and horizon:

- average return
- percent of up vs down outcomes
- standard deviation

That combination is useful because it separates expected move, directional consistency, and noise level.

### 3. False Positive Discipline

One of the best points in the chapter is that historical conditioning can still fail cleanly. When a query-based trade does not behave as expected, the failure is informative. The correct response is not to widen the story, but to reduce exposure because the setup was explicitly short horizon.

### 4. Historical Analog Framework

Analog analysis is a pattern-matching exercise:

- freeze a recent period of price action
- choose an analog window length
- search for historical windows with high correlation or similarity
- inspect what happened next in the matched periods

The point is not that the future "will" repeat, but that similar path geometry under similar macro conditions may suggest a useful roadmap.

## Chapter Connections

- Chapter 3 complements Chapter 2 by providing tools for pre-trade scenario analysis.
- The historical-pattern mindset overlaps with Chapter 5 technical analysis, but with more explicit event conditioning.
- The idea of structured backtesting connects directly to Chapter 6 systematic trading.

## What Seems Immediately Testable with Available Data

- Event studies around FOMC, ECB, BOE, CPI, payrolls, or other scheduled releases using liquid futures and ETF proxies.
- Query tables for cross-asset reactions around hikes, cuts, QE announcements, or emergency facilities.
- Analog searches on `DXY`, `SPX`, rates curves, or commodity baskets using rolling-window similarity metrics.
- Post-event horizon studies at `+1 day`, `+1 week`, and `+1 month`.

## What Likely Requires External or Harder-to-Source Data

- Clean historical expectations data, not just realized event outcomes.
- Intraday macro event data with consistent timestamps across assets.
- Institutional-quality macro regime tags to improve sample conditioning.

## Material Score

- Credibility: 4/5. The framework is sensible, though the chapter relies on small-sample examples and discretionary interpretation.
- Relevance: 5/5. Event studies and analogs are directly useful for macro research and review workflows.
- Actionability: 5/5. These methods are straightforward to implement with standard price data and event calendars.

## Open Questions and Things to Verify Empirically

- How much incremental predictive value comes from conditioning on expectations versus conditioning only on realized policy moves?
- Which analog distance metrics work best for macro assets: correlation, dynamic time warping, regime labels, or factor exposures?
- At what sample size do simple event queries become robust enough for live risk allocation?
- Does adding cross-asset confirmation materially improve the usefulness of analogs?
- How should one penalize false positives when query edges are evaluated out of sample?
