<!--
Template for /read-to-learn paper/article notes.
Save as: knowledge/papers/paper_notes_<author><year>.md
         (or paper_notes_<author>_<topic>_<year>.md)
ONE canonical note per paper — update the existing note instead of forking a second one,
and add/refresh its row in knowledge/papers/INDEX.md.
Delete this comment and any unused optional rows before saving. Math: $...$ / $$...$$.
-->

# Paper Notes: <Author(s)> (<Year>) — <Short Title>

- **Source:** <file path / URL / DOI / arXiv id>
- **Venue / type:** <journal, working paper, industry note, blog>
- **Read on:** <YYYY-MM-DD>
- **Surfaced in:** <study folder(s) that led here, or "standalone read">
- **One-line claim:** <the central result in one sentence>
- **Decision it changes:** <what a practitioner does differently if true>

## Score (1–5; follow up only if ≥3 on all three)

| Credibility | Relevance | Actionability |
|:-----------:|:---------:|:-------------:|
| <n>         | <n>       | <n>           |

_Rationale:_ <one line — why these numbers>

## Core focus & narrative
<What question, why it matters, the arc of the argument — 2–4 sentences, or a short
arrow chain if the arc is really a sequence: `<motivating fact>` → `<question>` →
`<approach>` → `<headline finding>`.>

## Methodology & assumptions
- **Data / sample:** <universe, period, frequency, source; PIT / survivorship handling>
- **Method:** <estimation / model / test>
- **Key assumptions:** <the ones that, if broken, break the result>
- **Author's choices:** <lookback, weighting, rebalancing — and whether they look fragile>
- **Alternative not taken:** <the obvious other estimator/construction, and why theirs>

## Key math (required if the paper has any)
<The 1–3 equations that carry the argument, in $$...$$, EVERY symbol defined, plus one
line per equation on what the term does economically. Reproduce — do not paraphrase.>

$$<equation>$$

where $<sym>$ is <...>, $<sym>$ is <...>. Economically: <what this is doing>.

## How the result was reached (derivation chain)
<The spine of the note. Fill each link with what was done, why that choice, and what
breaks if it is wrong.>

| Link | What the author did | Why / what breaks it |
|------|--------------------|----------------------|
| Economic question | <...> | <...> |
| Observable proxy | <...> | <...> |
| Construction / estimator | <...> | <...> |
| Test statistic & null | <...> | <...> |
| Result | <number, with units and period> | <...> |
| Interpretation | <...> | <the inferential leap, if any> |

## Evidence standard
- **In-sample vs OOS:** <...>
- **Significance / trials:** <t-stats, # of specs tried, multiple-testing exposure>
- **Robustness done / missing:** <subperiods, alt universes, alt specs — and what's absent>

## Economic mechanism
- **Type:** <risk-based / behavioral / structural>
- **Why it should persist:** <the compensated risk, the behavioral bias, or the
  structural rule/flow/friction>
- **Limits to arbitrage:** <why hasn't smart money closed it already?>

## Implementation reality
- **Costs / turnover:** <...>
- **Capacity:** <AUM before it saturates>
- **Decay / crowding:** <post-publication performance, if reported>

## What to watch (numbers, not adjectives)
- **Parameters & sensitivity:** <lookback / holding period / rebalance — and how much
  the result moves when they change>
- **Diagnostics worth remembering:** <t-stat, $R^2$, Sharpe gross vs net, turnover,
  breakeven cost, max drawdown>
- **Conditions where it weakens or flips:** <regime, rate level, liquidity, size
  segment, post-publication sample>

## Practitioner mindset captured
<2–4 reusable heuristics / priors this author reveals about how to reason in markets.>

## Connection to our platform (required)
<One bullet per connection — never a paragraph.>

- **<repo anchor>** — <validates / challenges / could improve / gap> — <why, 1–2 sentences>

## Critique / anti-patterns
<One bullet per anti-pattern that applies — overfitting, in-sample storytelling,
cost-blind alpha, regime-narrow evidence, look-ahead, capacity illusion, crowding.>

- **<anti-pattern>** — <where it shows up, tied to the relevant lens>

## Competing perspectives
<One bullet per rival view — who reads the same evidence differently, and on what
grounds. Cite them; link to their notes in this folder if they exist.>

- **<author/paper>** — <the competing read, and the grounds for it>

## How to validate or challenge
<Concrete data / replication / alternative-methodology tests one could run here.>

## What to do next (learning, not trading)
- [ ] <follow-up paper / mechanism to unpack with /explain-mechanism / claim to replicate if asked>
- [ ] <...>
