# GMT Chapter 2 Notes: Trading Process, Sizing Trades, and Monitoring Performance

## Core Concept and Author Intent

Chapter 2 is the operational heart of the book. Gliner's main message is that a macro trader's process matters more than any single thesis, and that risk control is the true source of survival. The chapter is less about generating ideas than about turning ideas into positions with predetermined downside, explicit conviction, and disciplined review. It is also a behavioral chapter: the process exists to defend the trader from the trader.

## Core Mental Models

- Think about loss first, not profit first.
- A good process is an anti-bias machine.
- Position sizing is more important than security selection once an idea is on the table.
- Volatility-adjusted risk is the common language across assets.
- Risk should be scaled nonlinearly with conviction and performance.
- Monitoring should be granular enough to reveal where edge actually lives.

## Practitioner Heuristics

- Journal every trade with thesis, conviction, outcome, and postmortem.
- Predefine stops and targets before entry so the trade is not managed emotionally.
- Use volatility-adjusted sizing instead of equal notional sizing.
- Prefer at least 1:3 risk/reward before putting on a trade.
- Know correlated exposures at the portfolio level; separate positions can still be the same bet.
- Run smaller size in long-horizon thematic trades because they can stay wrong for a long time.
- Cut risk after losses and only scale risk up through predefined rules.
- Treat gap risk as real, especially across weekends and policy events.

## Key Frameworks

### 1. Bias Management Checklist

Gliner focuses on three judgment failures:

- confirmation bias
- availability bias
- anchoring bias

The practical lesson is not "be rational," but "build routines that force contact with opposing evidence." A trade journal, scenario map, and deliberate devil's-advocate review are the actual tools.

### 2. Turtle-Style Volatility Sizing

The chapter borrows heavily from Turtle-style thinking:

- estimate recent volatility with a range-based measure (`N`)
- define a unit of portfolio risk
- size contracts so each trade risks a comparable amount
- consider wider stops such as `2N` rather than `1N` to reduce noise stop-outs

This is a portable framework because it translates macro views into consistent risk budgets across very different instruments.

### 3. Risk/Reward Gate

The chapter's core rule is to avoid trades whose upside is too small relative to predefined downside. The mechanical implication is simple:

- expected payoff must compensate for being wrong often
- winners must be allowed to run
- losers must be cut without negotiation

This is less a pricing model than a discipline filter.

### 4. Portfolio-Level Risk Stack

Single-trade sizing is not enough. Gliner layers:

- correlation awareness
- gap risk
- drawdown limits
- VaR usage
- stress testing

The important mental model is that the trader does not own trades one by one; the trader owns an aggregate distribution of outcomes.

### 5. Performance Attribution Framework

The chapter recommends monitoring P&L by:

- asset class
- strategy type
- duration bucket
- conviction bucket
- trend alignment

This is a strong practitioner idea because it converts vague intuition about "what I am good at" into analyzable slices.

## Chapter Connections

- Chapter 2 provides the operating discipline that Chapters 3 through 6 assume.
- The bias and stop-loss logic connects naturally to Chapter 5 technical analysis.
- The sizing and monitoring framework is a discretionary analog to the rule-based construction in Chapter 6.

## What Seems Immediately Testable with Available Data

- Backtest `N`-based or ATR-based sizing versus equal-notional sizing on futures or ETF proxies.
- Compare stop distance choices such as `1N` versus `2N` on trend and event-driven trades.
- Build a trade blotter schema that attributes returns by asset class, duration, conviction proxy, and trend regime.
- Stress-test historical portfolios against known shock dates listed in the chapter.
- Evaluate whether reducing risk after drawdowns improves long-run drawdown control.

## What Likely Requires External or Harder-to-Source Data

- Real discretionary trade journals from professional macro books.
- Intraday execution quality and slippage data for fast discretionary trading.
- Fund-level VaR utilization policies and drawdown governance.

## Material Score

- Credibility: 4/5. The risk-management principles are standard and defensible even if some specific parameter choices are heuristic.
- Relevance: 5/5. This chapter is directly applicable to both discretionary and systematic research workflows.
- Actionability: 5/5. Nearly every framework here can be implemented or audited immediately.

## Open Questions and Things to Verify Empirically

- Does `2N` materially improve realized Sharpe after accounting for larger average loss size?
- Which attribution buckets actually explain the most variance in discretionary macro P&L?
- Are conviction scores useful, or do they mainly expose bias and overconfidence?
- How should VaR-based throttles be adapted in modern regimes where cross-asset correlations jump discontinuously?
- What is the best way to encode thematic-trade half-life so those positions do not dominate risk capital for too long?
