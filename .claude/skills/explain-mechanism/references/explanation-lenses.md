# Explanation lenses — the core of `/explain-mechanism`

*Read this once. The SKILL.md gives the procedure; this gives the questions that
generate the content. They are asset-class agnostic on purpose — the same eleven
questions work on an asset swap, a perp funding rate, and a variance swap.*

---

## Part 1 — The eleven lenses

Run these against any instrument, spread, or convention. Most objects light up six
or seven; the ones that stay dark are themselves informative (an instrument with no
funding leg is a different animal from one with three).

### 1. The two legs
**What:** almost every market object is a difference between two claims. Name both, and
say what each is a claim *on*.
**Ask:** what is leg A a claim on, what is leg B, and why were these two chosen as the
pair? What third thing would have been the more natural comparison, and why isn't it?

### 2. The residual
**What:** every measure is a subtraction. Its value is what remains after the
subtraction, and its danger is what *fails* to be subtracted.
**Ask:** what does this strip out? What's left? Does the residual still contain
something the user doesn't want — a curve bet, a funding cost, a term premium?

### 3. The mismatch
**What:** the defect that makes the clean story wrong. Notional, timing, maturity,
currency, day count, settlement, or frequency.
**Ask:** are the two legs matched in size, in date, in basis? Where they aren't, what
happens in the state of the world where the mismatch bites? Name the variant of the
instrument that repairs it.

### 4. The funding leg
**What:** who finances the position, at what rate, on whose balance sheet. The most
under-explained and most P&L-relevant lens for anything involving a cash asset.
**Ask:** is this funded or unfunded? Repo, margin, or outright? What happens to the
funding cost at quarter-end, in a squeeze, or under a capital rule? **A position whose
funding you cannot name is a position whose carry you cannot compute.**

### 5. The embedded optionality
**What:** somebody in the structure has a choice. Whoever holds the choice is long an
option, and the price already reflects it.
**Ask:** who gets to decide something — what to deliver, when to prepay, whether to
exercise, when to call? Which side sold it? Does the quoted spread look artificially
wide or tight *because* of the option value?

### 6. Sign and quoting convention
**What:** the highest-risk claim in any markets answer, and the one that silently
corrupts backtests.
**Ask:** which way is up? What is the competing convention, and what is the sign
relation between them? Is the quote clean or dirty, annualized or periodic, per unit
or per notional, bp of what? **Walk the four axes separately — sign, day count, quoting
basis, notional basis — because a skipped axis is invisible in the output.** Watch units
in particular: an annuity in *years* and a PV01 in *currency* differ by notional × 1bp,
and substituting one for the other silently rescales the answer.

### 7. The counterparty
**What:** the other side is rarely a speculator with an opposite view. Usually they are
*constrained* — mandated, regulated, hedging, or indexed.
**Ask:** who is naturally on the other side, and what forces them there? A structural
counterparty (pension LDI, servicer hedging, index tracker, exchange market-maker) is
the difference between a risk premium and a crowded trade.

### 8. The stress case
**What:** the scenario that proves the structural flaw asserted in lens 3 or 5.
**Ask:** what happens on default, on a delivery switch, on a gap move, on the roll, on
a halt, on a funding squeeze? Run it in numbers, not in adjectives.

### 9. The P&L decomposition
**What:** the buckets that sum to the total. If you cannot decompose it, you cannot
tell a correct call from a lucky funding move.
**Ask:** carry and roll-down · the directional term (risk measure × Δ) · residual
hedge error · convexity · financing drift · instrument-specific terms (option decay,
roll, prepayment). **Which bucket usually dominates?** For most spread positions the
honest answer is carry, not the view.

### 10. The narrative library
**What:** the recurring stories practitioners use to explain moves — and, critically,
the pairs that look alike but push in opposite directions.
**Ask:** what are the six-to-ten standard drivers, and which way does each push? Which
two are commonly confused? (Flight-to-quality and funding crisis are both "crises" and
move swap spreads opposite ways — that pair is the archetype.)

### 11. The modelling cost
**What:** what a backtest of this in *this repo* must include, and the signature of
omitting it.
**Ask:** which `alpha_research/quant_data/` series exists or is missing? Does it need a
`alpha_research/backtests/costs/` model, a roll convention, a funding assumption, a PIT
lag? **What does the Sharpe look like if you skip it?** Name the artifact, not the
caution.

---

## Part 2 — Teaching moves

The lenses generate content; these generate the *prose*. Use them liberally.

| Move | Form |
|------|------|
| **Naive-vs-correct** | Wrong-but-obvious version first, name the contaminant as a *position*, then the correct version |
| **Residual sentence** | "…what's left is credit + liquidity + basis" — always enumerate the remainder |
| **Named trap** | Bolded label at the mechanic that causes it: wrong belief → mechanism → fix |
| **Commercial why** | The incentive that made someone invent the convention; ideally the gaming it prevents |
| **Arrow chain** | 3–4 checkable links to an observable consequence, terminal state bolded |
| **Conversion identity** | The operation that turns instrument A into instrument B — then spend the identity on a third object |
| **Time-sliced ledger** | Cash flows as tables by t=0 / each period / termination / stress, with party arrows and signed amounts |
| **What's absent** | After the ledger, point at what is conspicuously *missing* and say why the absence is the point |
| **Intended vs unintended** | Two tables; the second is longer and phrased adversarially, in the second person |
| **Notice:** | One sentence after a worked number extracting the honesty lesson — never end an example on its total |
| **Domain of validity** | Where the metric is clean, where it lies, the named variant that repairs it |
| **Job assignment** | When two metrics compete, don't rank — give each a job ("ASW is the tradeable package, Z-spread is the honest valuation metric") |
| **Slogan compression** | Close an extended comparison with one parallel-structure line |
| **Dated falsifier** | A real episode where the intuitive mechanism gave the wrong sign, and the right thesis still lost money |
| **Second person** | "you sold that optionality", not "the position is short the option" |
| **Forward close** | Portable diagnostic questions, re-pointed at a different instrument to show they generalize |

**Register notes.** No preamble, no flattery, no glossary — the nouns are assumed. Bold
is a hazard-and-conclusion layer, not emphasis. Take the exception at the same time as
the rule; never stage-simplify or say "we'll come back to this." Reuse earlier concepts
by name and flag the reuse ("the par/par asymmetry from before").

---

## Part 3 — The lenses outside fixed income

The lens set is only worth anything if it survives contact with other asset classes.
Worked applications, showing which lens carries the explanation:

### Crypto perpetual funding rate
- **Two legs:** perp price vs spot index. The funding payment is the tether between them.
- **Residual:** funding strips the perp's drift back to spot; what's left is a pure
  leveraged spot exposure plus a carry stream.
- **Funding leg (dominant):** longs pay shorts when the perp trades above index (sign
  flips when below). Paid on a periodic stamp — commonly 8-hourly, but the interval and
  the clamp are *venue-specific*; check the venue's spec rather than assuming.
- **Counterparty:** basis traders and market-makers harvesting the premium against a
  spot or dated-future hedge. Crowded in exactly the regimes where funding is richest.
- **Stress case:** liquidation cascade and auto-deleveraging — your hedge gets torn off
  at the worst moment. Exchange credit is a real, non-diversifiable leg.
- **Modelling cost:** funding must be accrued at the venue's actual stamps with the
  actual sign. Daily resampling is not neutral, but the bias is not automatic —
  *summing* signed stamps preserves the net, *averaging* them and applying the average
  once understates it threefold, and *last-value-of-day* discards two stamps. The real
  overstatement is conditional: any entry rule triggered on the sign of funding looks
  better than it was, because the daily figure hides the stamps on which you paid.

### Variance swap
- **Two legs:** realized variance vs the strike, on a variance (not vol) basis.
- **Embedded optionality (dominant):** the log contract is replicated by a strip of OTM
  options weighted $1/K^2$. The replication is exact only for a *continuum* of strikes
  and a diffusive path — so the **replicating dealer** is short the truncation and the
  jump term, and prices that gap into the strike you pay.
- **Mismatch:** var swap vs vol swap differ by a convexity adjustment; quoting one and
  hedging the other is a classic error.
- **Stress case:** a gap. Payoff is linear in variance, hence convex in vol — a short
  loses far more than the linear intuition suggests.
- **Narrative library:** VRP harvest, hedging demand, index-vs-single-name dispersion,
  crash gap.
- **Modelling cost:** without the strike-truncation and jump assumption stated, a VRP
  backtest overstates the premium — you have modelled a variance exposure that the
  available strikes cannot actually replicate, and booked the un-hedgeable tail as edge.

### Cross-currency basis
- **Two legs:** direct USD borrowing vs synthetic USD via an FX swap. The basis is the
  deviation from covered interest parity.
- **Funding leg (dominant):** it *is* the funding lens — the basis is the price of
  balance sheet for dollar funding.
- **Counterparty:** non-US banks and insurers with structural dollar needs, against
  dealers whose capacity is capital-constrained.
- **Sign convention:** quoted as the spread added to the *non-USD* leg — EUR Euribor +
  basis against USD SOFR flat. Negative basis = synthetic dollars via the FX swap cost
  more than borrowing them directly = dollars are expensive. EUR and JPY have been
  persistently negative since 2008. Some charts plot it inverted as a positive "dollar
  premium" — always check which leg the chart signs.
- **Narrative library:** quarter-end and year-end turn, dollar stress, central-bank swap
  lines, hedging-ratio shifts by Japanese/European lifers.
- **Modelling cost:** the turn is large, recurring and *calendar-predictable* — but it
  lives in **short-dated FX swaps** (O/N to 1m), printing as the reporting date rolls
  into the tenor window; the 3m-vs-3m and 5y basis swaps barely twitch. A backtest that
  averages through the turn, or that proxies short-dated dollar funding with the 3m
  basis, misprices both the carry and the tail.

### MBS negative convexity
- **Embedded optionality (dominant):** the homeowner holds a prepayment option; you sold
  it. Duration extends when rates rise, shortens when they fall — precisely the wrong way.
- **Counterparty:** MSR holders/servicers, money managers, banks and mortgage REITs
  hedging their own convexity, which *amplifies* the move that caused it — rates rise →
  MBS duration extends → holders sell duration (pay fixed) → rates rise further. The GSE
  retained portfolios that dominated this flow pre-2008 were wound down under
  conservatorship, so naming GSEs dates the story to the 2003 archetype; the modern bid
  is mostly servicer MSR hedging plus real-money extension flow.
- **Sign convention:** OAS is spread net of the option cost — so it is only as good as the
  prepayment model and the vol surface used to strip it.
- **Modelling cost:** a static-cash-flow backtest of MBS is fiction. It needs a prepay
  model and a rate-vol assumption, and the OAS is an output of those choices, not a
  market observable.

### CDS–bond basis
- **Two legs:** CDS spread vs the bond's cash spread (Z-spread or ASW) on matched
  maturity. **Basis = CDS − cash spread.** Negative basis = the bond is cheap to CDS;
  the trade is buy bond + buy protection and bank the carry.
- **Mismatch + funding:** the bond leg must be financed in repo; the CDS leg is unfunded.
  That asymmetry pushes the basis *negative* — the bond has to be cheap enough to pay for
  its own repo and haircut. Much of the basis is the price of that, not a view on credit.
- **Embedded optionality:** CDS has its own cheapest-to-deliver among the deliverable
  obligations — the protection buyer holds it, and it pushes the basis the *other* way,
  positive. **The observed basis is the net of two forces with opposite signs**, so a
  basis level tells you nothing until you say which one is dominating.
- **Stress case:** the 2008 negative-basis unwind — right on credit, destroyed by funding
  and haircut widening. The archetype for lens 4 dominating lens 1.

**The pattern across all five:** in every case the *unintended* lens — funding,
optionality, or mismatch — carries more P&L than the intended view, at least some of the
time. That is why the intended/unintended split in the SKILL.md is mandatory rather
than stylistic.
