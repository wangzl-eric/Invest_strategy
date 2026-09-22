# Methodology & Mindset Lenses

The reason `/read-to-learn` exists. A junior researcher who only summarizes a paper
learns *facts*; a researcher who runs every source through these lenses learns the
**industrial-standard mindset** — how a professional quant frames, tests, doubts,
and implements an idea. Apply every lens to every source. When a lens does not
apply, say *why* (that absence is itself information).

For each lens: capture **what the author did**, then **what a skeptical practitioner
would ask**. The second column is where the learning lives.

---

## Lens 0 — The derivation chain (the spine every other lens hangs off)

**The result is the least transferable part of a paper.** Next year the number will be
stale; the *route* from question to number is what you keep. Reconstruct it explicitly:

$$\text{economic question} \to \text{observable proxy} \to \text{construction/estimator}
\to \text{test statistic \& null} \to \text{result} \to \text{interpretation}$$

- **What:** For each arrow, what the author did and what they *chose* to do it that way.
  Write out the load-bearing math (1–3 equations), every symbol defined, with one line
  on what each term does economically.
- **Ask:**
  - **Proxy step** — how much of the economic concept survives the proxy? (book-to-market
    *is not* value; VIX *is not* expected volatility; realised vol *is not* risk.) Most
    silent failures enter here.
  - **Estimator step** — why this and not the obvious alternative (OLS vs Fama–MacBeth
    vs GMM; portfolio sorts vs cross-sectional regression; equal- vs value-weighted;
    Newey–West with how many lags, and justified how)? Sorts are non-parametric and
    robust but throw away information; regressions use all of it but impose functional
    form. Which trade did the author make, and does it favour their conclusion?
  - **Test step** — what exactly is the null, and what does rejecting it prove? Separate
    *statistically ≠ 0*, *better than the benchmark*, and *economically large enough to
    trade*. A $t = 2.5$ on a 0.2 % annual spread rejects a null nobody cared about.
  - **Interpretation step** — locate the **inferential leap**: where a correlation is
    narrated as a mechanism, or an in-sample fit is asserted as a forecast. There is
    almost always exactly one. Name it.

**Standard of done:** you could re-run the study from your note alone. If you could not,
you recorded a conclusion, not a method.

---

## 1. Problem framing
- **What:** What economic question is really being answered? What decision changes if
  the claim is true (allocate, hedge, time, size, avoid)?
- **Ask:** Is this a *return* question, a *risk* question, or a *cost* question? Whose
  problem is it — an allocator's, a PM's, a market-maker's? A well-framed problem
  names the decision and the counterfactual.

## 2. Data & sample
- **What:** Universe, period, frequency, source. Point-in-time or restated?
  Survivorship-, look-ahead-, and selection-bias handling.
- **Ask:** Does the sample contain enough independent regimes (not just one bull
  market)? Would the result survive on a different universe or a held-out decade?
  Is the data the author *had* the data a trader would have had *in real time*?
  (Cf. this repo's PIT/FRED rule in CLAUDE.md and `alpha_research/quant_data/pit.py`.)

## 3. Methodology & assumptions
- **What:** Estimation method, model, controls, and every assumption (linearity,
  stationarity, normality, no-arbitrage, frictionless markets).
- **Ask:** Which assumption, if broken, breaks the result? What did the author
  *choose* (lookback, rebalancing, weighting) and would a different reasonable choice
  flip the sign? Distinguish identifying assumptions from convenience assumptions.

## 4. Evidence standard
- **What:** In-sample vs out-of-sample, t-stats / significance, number of trials,
  robustness checks performed (subperiods, alt specs, alt universes).
- **Ask:** How many strategies were *implicitly* tried before this one was reported?
  (Multiple-testing / data-snooping — the deflated-Sharpe mindset.) Is significance
  economic or just statistical? What robustness check is conspicuously *missing*?
- **Quantify it, don't eyeball it.** Two arithmetic checks worth doing on every
  empirical claim, because they turn a vibe into a number:
  - **Multiple testing.** Under $N$ independent trials the expected maximum t-stat
    is roughly $\sqrt{2\ln N}$ — $N=100$ specs gives $\approx 3.0$ *by luck alone*.
    A reported $t=2.8$ from a paper that admits to a "grid search" is not evidence.
    (This is the intuition behind Harvey–Liu–Zhu's raised hurdle and the deflated
    Sharpe ratio in `alpha_research/backtests/stats/`.)
  - **Sharpe standard error.** With $T$ years, $\mathrm{se}(\widehat{SR}) \approx
    \sqrt{(1 + \tfrac12 SR^2)/T}$. A Sharpe of 0.5 over 10 years carries
    $\mathrm{se}\approx 0.33$ — the 95 % CI spans roughly $[-0.15, 1.15]$. Ask how
    many years of data would be needed to distinguish this from zero, then check
    whether the sample has them.

## 5. Economic mechanism
- **What:** *Why* should this work and persist? Risk-based (compensation for bearing
  something) vs behavioral (a bias + limits to arbitrage) vs structural (rules,
  flows, frictions).
- **Ask:** If it is a risk premium, what is the bad-times payoff? If behavioral, why
  hasn't arbitrage closed it — what are the limits to arbitrage? A pattern with no
  mechanism is an overfit until proven otherwise.

## 6. Implementation reality
- **What:** Transaction costs, turnover, capacity, shorting/borrow, liquidity,
  signal decay, crowding, and post-publication performance.
- **Ask:** Does the edge survive realistic costs (cf. the 1×/2×/3× cost sensitivity
  in `alpha_research/review`)? How fast does the signal decay? Has publication itself
  arbitraged it away? Gross alpha is a hypothesis; net alpha is the claim.

## 7. Practitioner heuristics (the mindset)
- **What:** Read between the lines for *how the author reasons*. What do they treat as
  obvious, what do they stress-test, what makes them skeptical, what rules of thumb do
  they invoke?
- **Ask:** What would this author *not* believe without seeing? What is their default
  prior? Collect these — they compound into judgment. Examples worth noting: "prefer
  simple, economically-motivated signals", "out-of-sample or it didn't happen",
  "respect costs and capacity", "beware the single lucky backtest".

## 8. Connection to our platform (mandatory)
- **What:** Name the specific strategy / signal / runner / manifest / doc / study in
  *this repo* the source touches.
- **Ask:** Does it **validate**, **challenge**, or **could improve** that artifact? If
  it contradicts existing code or notes, flag it explicitly (the cerebro
  contradiction-check rule). Candidate anchors:
  - `alpha_research/backtests/runners/` — weights-contract entrypoints
  - `alpha_research/research/pool/<id>/manifest.yaml` — pooled strategies
  - `alpha_research/backtests/stats/` — PSR, deflated Sharpe, CPCV, bootstrap
  - `alpha_research/backtests/costs/` — cost & slippage models
  - existing `knowledge/{books,studies}/` notes & hypotheses
  A source connected to nothing here is off-scope (score Relevance down) or a gap.

---

## Mindset anti-patterns to flag when you see them

A note becomes a *teaching* note when it catches the source (or the reader) slipping:

- **Backtest overfitting** — many specs tried, best one reported, no penalty.
- **In-sample storytelling** — mechanism invented to fit a pattern after the fact.
- **Cost-blind alpha** — headline Sharpe on gross, paper-thin net.
- **Regime-narrow evidence** — one bull market dressed as a universal law.
- **Look-ahead leakage** — restated data, or signals using information not yet public.
- **Capacity illusion** — works on $10M, vanishes at $1B.
- **Crowding / publication decay** — edge real once, arbitraged after print.

When you spot one, name it in the note's *Critique* section and tie it to the
relevant lens above — that is the transfer of mindset the user is after.
