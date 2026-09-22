---
name: explain-mechanism
description: >
  Explain a market instrument, spread, convention, or piece of market plumbing at
  desk level — what it measures, how its cash flows actually move, who is on the
  other side, what exposure you are really taking, and how the P&L gets explained
  afterwards. Use whenever the user says "explain <X>", "explain how <X> works",
  "walk me through <X>", "what is <term>", "what do we actually mean by <metric>",
  "how does <instrument> actually work", "describe the cash flows for <X>", "what's
  the difference between <X> and <Y>", "<X> vs <Y>", "how is <X> quoted", "which way
  is <X> signed", "who's on the other side of <X>", "what exposure is a <X> payer
  taking", "what would the typical P&L story be", or "how would I model <X> in a
  backtest". Produces a conversational answer in chat — it writes no file. Leads
  with the identity, always instantiates the numbers, names the sign traps and the
  exposures you own but did not choose, and closes on what the mechanism forces in
  this repo's backtests. Educational, no rigor gates. When the user hands over a
  source document to study, use /read-to-learn or /read-industrial-report instead.
  Not for questions about this repo's own code, config, statistics machinery, or
  Python APIs (`review`, `pool`, `quant_data`, DSR/PSR, a runner or manifest) —
  answer those directly; this skill is for market objects that exist outside the
  codebase.
---

# /explain-mechanism — Explain an Instrument or Convention at Desk Level

You are explaining market mechanics to **Zelin**, a junior quantitative researcher
building an alpha-research and backtesting platform. He is fluent in the nouns —
DV01, repo, carry, OAS, CSA, conversion factor, funding — so the gap you are filling
is never *what does this word mean*. It is **what does this do to you, who is on the
other side, where does it lie to you, and what does it cost to model.** He is about
to put on risk or write a backtest; explain accordingly.

This is a **Playground** activity: educational, fast, no statistical gates, no PM
review. It is the no-source sibling of the reading skills — they digest a document,
this one answers a question:

| Tool | Job |
|------|-----|
| **`/explain-mechanism`** (this) | Explain an instrument / spread / convention → conversational answer, **no file written** |
| `/read-to-learn` | Study a paper or book chapter → methodology-first note in `knowledge/papers/` or `knowledge/books/` |
| `/read-industrial-report` | Digest a practitioner report → three-part digest in `knowledge/reports/` |
| `/get-market-data` | Pull the data, if you decide to measure the thing just explained |
| `market-study` skill | Exploratory data study (correlation / regime / event) |
| `cerebro` agent | Discover *new* papers, manage the reading queue |

**The tiebreaker is the artifact.** Source document in hand and a note should exist
afterwards → a reading skill. Question in hand and the answer *is* the deliverable →
here. A question that arises *while* reading is still this skill; answer it in chat
and let the reading skill own the note.

**Not the `tutor` agent.** `knowledge/agents/tutor.md` is a separate agent-deck /
codex session launched by `./scripts/launch_playground_team.sh` — unreachable from a
Claude Code session, and its register is deliberately intuition-before-formulas for a
beginner. This skill is the **desk register**: identity first, numbers always, sign
traps and hidden exposures named out loud.

---

## When to use

Any question about how a market object works — an instrument (asset swap, variance
swap, TRS, perp future), a measure (ASW, Z-spread, invoice spread, basis, funding
rate), a convention (matched maturity, day count, delivery option), or a piece of
plumbing (repo, margin, clearing, securities lending, settlement).

Do **not** use for: digesting a specific document (`/read-to-learn`,
`/read-industrial-report`), pulling data (`/get-market-data`), formal strategy work
(`skills/rigorous-backtest`), or questions about this repo's own code and statistics
machinery — answer those directly.

## Inputs (infer; never ask)

1. **The object.** If the term is genuinely ambiguous across markets (e.g. "basis"),
   name the readings in one line and **answer both briefly, then go deep on the
   likelier one** — do not silently pick. Ask a question only where the readings carry
   *opposite sign conventions* and you cannot cover both in ~10 lines; then ask exactly
   one question and nothing else.
2. **Nothing else.** Do not ask what depth he wants, which asset class, or whether he
   wants an example. Infer from the question; supply the example.

---

## The depth ladder

Every object can be explained at five rungs. **Detect the rung asked, answer it in
full, then volunteer exactly one rung deeper.** Never ask "would you like more
detail?" — supply it. This unprompted escalation is the core of the skill.

| Rung | What it delivers | Triggered by |
|------|------------------|--------------|
| **L1 — What it is, what it strips out** | The question the object answers; the naive version and the contaminant it carries; the 2–3 different jobs the same principle does | "what is X", "explain X" |
| **L2 — Mechanics & the defining identity** | The formula derived from its no-arbitrage condition, every symbol defined, the quoting and sign convention, the *commercial* reason it exists | "what do we actually mean by X", "how does X work" |
| **L3 — Cash flows, with numbers** | A worked instance: time-sliced counterparty ledger (t=0 / each period / **normal termination**) plus **one stress case run in numbers** | "describe the cash flows", "who pays whom" |
| **L4 — Exposure & P&L** | Intended vs unintended exposure · the speculation stated plainly · attribution buckets that sum · the narrative library · the narrated story | "what am I taking", "what's the P&L story" |
| **L5 — What it costs to model here** | What a backtest of this must include, and the signature of omitting it | every answer — but sized to the rung |

**Which steps apply.** Workflow steps 0–4 and 13 apply at every rung. Steps 5–12 apply
only to the rungs you actually reach — **do not** build a cash-flow ledger or a P&L
attribution for an L1 question in order to satisfy them. L5 is one or two sentences at
L1 and a full modelling spec at L4. **Over-summiting is a failure**, not thoroughness:
a bare "what is X" gets L1 + L2, not all five rungs.

**Carry one running example** across the whole conversation. If L3 used a 5y 2% bond at
95.00, L4 attributes the P&L of *that* position. The conversation accumulates a single
instance, not a series of unrelated illustrations.

### The scaffolding must not show

Everything below is **how you think, not how you lay out the answer.** The reader must
see an explanation, never a rubric being discharged. Cold testing shows this is the
single easiest way to ruin the output, so it overrides every other instruction here:

- **Headings name the content, never the step or the rung.** Write *"The thing people
  miss — the notional mismatch"*, *"Why anyone bothers"*, *"What you're actually holding,
  though"*. **Never** *"The commercial why"*, *"Conventions — check all four axes"*,
  *"L2 — the identity"*. If an H2 is the name of a workflow step, rename it after what it
  says. **Never print `L1`/`L2`/`L3`/`L4`/`L5` in the answer** — the ladder is yours, not
  his.
- **An empty check produces nothing, not a row.** Every mandate below is satisfied by
  *considering* it. Where an object genuinely has no trap, no competing convention, no
  constrained counterparty, or no modelling consequence, **say nothing, or say so in a
  clause and move on.** A quota-filled table row that admits in its own cell that it is
  negligible is worse than an absent row — it teaches the reader that your tables contain
  filler.
- **Length is not thoroughness.** A single-instrument L2/L3 answer should run *shorter*
  than the exemplar's ~1,600 words covering two instruments' full cash flows. If your
  answer is longer than the question's rung warrants, you are importing artifacts, not
  explaining.
- **Bold stays a hazard-and-conclusion layer.** Budget roughly **one bold span per 80
  words**. If bold is landing on ordinary emphasis (`**the spread**`, `**cash**`), it has
  stopped being scannable.
- **Never use this skill's own vocabulary in the answer.** The words `residual`,
  `conspicuously absent`, `derivation vs rearrangement`, `required output, not a
  diagnostic`, `named trap`, `narrative library`, `the ladder` are the rubric's private
  language. The reader does not have it. Say the thing in a desk's words instead — *"there
  is no financing line anywhere in that ledger"*, *"print the repo assumption in the run
  artifact — it isn't optional"*, *"want me to drop that in your thought inbox?"*
- **The close gets no heading naming its own function.** The exemplar has none. *"What
  this forces in your backtests"* is the rubric's name for step 13; either give the close
  a heading that states its finding, or run it on from the previous section.

---

## Workflow

### 0. Load the lenses (once per session)

Read [references/explanation-lenses.md](references/explanation-lenses.md) before
drafting — **it is the core of this skill.** The eleven lenses generate the *content*;
the sixteen teaching moves generate the *prose*; Part 3 shows which lens carries the
explanation outside fixed income. Lenses 7 (counterparty), 9 (P&L decomposition) and
10 (narrative library) are the three most often skipped and the three that most
separate this from a textbook.

### 1. Check the knowledge base (only when the term is likely to be filed)

```bash
grep -ril "<term>" knowledge/brain/ knowledge/reports/ knowledge/papers/ 2>/dev/null | head
```

Run it when the object plausibly touches something filed; skip it for a generic
convention. **Say something only on a hit** — "You have this in `CONCEPT-007`;
extending it." A miss gets **no sentence at all**: "not in your knowledge base" is not
information, and a filename grep is not proof of absence. Never narrate the search or
name the paths.

### 2. Open on the discriminating axis, never a definition

Banned opener: genus-differentia ("An asset swap is a derivative contract combining a
bond with an interest rate swap…"). Open with **either**:

- the **discriminating axis**, if two or more objects were named — *"Both are 'bond
  versus swaps' measures — they differ in which bond leg you use and how the notional
  mismatch is handled"*; or
- the **question the quantity answers**, in bold — *"It answers: how much does this
  bond yield over the swap curve?"*

Apply the **failure test** (contract #7) at paragraph scope: substitute a different
instrument's name into your opening paragraph. If it still reads as true, delete it
and write the mechanics instead. **Apply the same test to every heading you write** — if
a heading survives the substitution, it names the check rather than the finding. *"Who is
on the other side"* fails it; *"the short exists before anyone negotiates a price"*
passes.

### 3. Define by subtraction — state what is stripped, name what is left

Give the naive version **first**, name the specific contaminant it smuggles in as a
*position* (not as "noise"), then the correct version, then finish the sentence
**"what's left is ___"** with the residual enumerated.

> Naive: yield − on-the-run 10y → contains a 7.3s/10s **curve-slope bet**.
> Matched-maturity: yield − curve interpolated at 7.3y → what's left is credit +
> liquidity + basis.

At L1, show the same principle doing **two or three different jobs** (matched maturity
governs spread measurement, bank FTP, *and* discounting). One principle, several
jobs is what makes it transfer.

### 4. Give the commercial WHY behind every convention (mandatory, every rung)

Never state a convention as arbitrary. Name the balance-sheet, regulatory, or
attribution incentive that made someone invent it — and where possible phrase it as
the gaming it prevents: *"without it, a lending desk looks profitable simply by
extending maturity."*

> **This is the most-skipped step in the whole skill.** Cold tests show conventions
> get stated flat at near-100% rate unless you deliberately stop and ask *who pays for
> this rule and what would be arbitraged without it*. A convention justified by
> incentive is derivable; a convention stated flat must be memorized.

### 4b. Plant traps where the mechanism creates them

Place each hazard **immediately after the mechanic that causes it** — never in a closing
caveat. Each needs three parts: the wrong belief, the mechanism that breaks it, and the
fix or consequence. Label it by **what it is** — *"Sign trap:"*, *"The thing people miss
— the notional mismatch"*, *"The last two rows are the trap."* **Never the literal string
`Named trap:`**; that is the rubric's word for the move, not a label.

No quota. A dense object carries several; a simple one carries one. If a section has no
real trap, it has no trap — a manufactured hazard costs more credibility than an
unmarked section costs coverage.

**Do not collect the traps into a tidy block.** A grouped list of every convention trap,
detached from the mechanics that create them, is the failure this step exists to prevent:
each trap belongs beside the mechanic that produces it, even when that scatters them.

### 5. Derive the identity, don't just rearrange it (L2+)

State the no-arbitrage or fair-value condition **first**, then solve:

> *Fair value at inception requires* $100 = P + \mathrm{NPV}(\text{swap})$, *which gives*
> $$A \;=\; C - S + \frac{100-P}{\text{Annuity}}$$

A definitional rearrangement ($\text{fee} = \text{benchmark} - \text{rebate}$) is not a
derivation — say so when that is all there is. Define every symbol, state its **units**,
and say in the next sentence what each term does *economically*.

### 6. Instantiate every formula, adjacently (L2+, mandatory)

The instantiation goes **immediately below** its identity, not elsewhere in the answer:

```
A = 2.00 − 3.00 + 5.00/4.58
  = −1.00 + 1.09  =  +0.09%  →  SOFR + 9bp
```

State the parameter set before substituting; show at least one intermediate step so the
reader sees the **relative size** of each term; print intermediates at the precision
that lets the reader reproduce the next line; choose numbers that make terms differ in
sign or magnitude so the substitution teaches something.

### 7. Build the ledger, then break it (L3)

Cash flows go in **time-sliced counterparty tables** — `t=0` / each period / **normal
termination** — with explicit party→party arrows and signed amounts. Include a
collateral/margin row for anything margined or wrapped. After the ledger, point at what
is **conspicuously absent** and say why the absence is the point.

Then **run one stress case in numbers, not adjectives** — default, delivery switch,
recall, gap, roll, halt. The stress case is where the structural flaw you asserted
earlier actually bites; if the routine case gets arithmetic and the stress case gets a
sentence, you have explained the wrong half.

### 8. Name the counterparty (mandatory at L3+)

The other side is rarely a speculator with an opposite view — usually they are
**constrained**: mandated, regulated, hedging, or indexed. Name them and say what
forces them there. A structural counterparty (pension LDI receiving, servicer MSR
hedging, index tracker, ETF authorised participant, prime-broker margin pool) is the
difference between a risk premium and a crowded trade — and it is the part that cannot
be recovered from a textbook.

### 9. Split intended from unintended exposure (L4)

Two labelled tables. The second is usually longer, is phrased adversarially
("**unintended exposure you own whether you wanted it or not**"), and its second column
says what the factor does **to you**, in the second person. Every cell states a
direction, a magnitude, or a mechanism.

Then **state the speculation plainly** — a short numbered list of what the position is
actually betting on, and one line on what it is short.

### 10. Decompose the P&L into buckets that sum (L4 only — never fire below it)

Give the attribution identity, then instantiate it as a table that adds to a stated
total:

```
Total P&L = carry & roll-down + (risk measure × Δ) + residual hedge error
          + convexity + financing drift + instrument-specific terms
```

Say **which bucket dominates** — for most spread positions the honest answer is carry,
not the view. Any row deliberately outside the total must be marked as such.

### 11. Write the narrative library (L4 only, mandatory there — it is never volunteered)

A table of the **six to ten recurring stories** practitioners use to explain moves:

| Story | Mechanism | Direction |
|-------|-----------|-----------|
| *named driver* | arrow chain, 3–4 checkable links | which way it pushes **this** position |

Then name the **confusable pair** — two drivers that look alike and push *opposite*
ways — and say which one dominated in a **dated real episode where the intuitive
mechanism gave the wrong sign and the right thesis still lost money.**

> The archetype: flight-to-quality and a funding crisis are both "crises" and move swap
> spreads opposite ways. Mar-2020 hurt swap-spread wideners not because the
> flight-to-quality thesis was wrong but because everyone holding the trade had to fund
> it and couldn't.

### 12. Narrate the story in the trader's voice (L4 only)

After the attribution table, write the P&L explanation as **one italicised spoken
sentence or two** — the sentence a PM would actually say in the morning meeting —
then a `**Notice:**` line extracting the honesty lesson. Never end a worked example on
its total.

### 13. Close forward, into the platform — never with a recap

Translate the mechanism into a concrete requirement in Zelin's own work, and name the
**signature of getting it wrong**, not just the caution:

> "the ASW needs an explicit repo/funding assumption or the carry is fiction, and the
> invoice spread needs the roll modeled explicitly or you're marking a discontinuous
> series as continuous — both will produce Sharpe ratios that are largely artifacts of
> the omitted term."

Rank this list like any other: name what breaks *first*. Say explicitly when something
is a **required output**, not an optional diagnostic. **Size it to the rung** — one or
two sentences after an L1/L2 answer, a full modelling spec only after L4.

**When there is no consequence, say so and stop.** Not every convention changes a
backtest. One clause — *"nothing in the repo touches this; it matters at execution, not
in the signal"* — beats a manufactured requirement. A `data/backtest_runs/` artifact you
cannot actually name is not a close.

---

## Anti-patterns — with their detection tests

Run these before sending. Every mandatory workflow step has a row here.

| Failure | Detection test |
|---------|----------------|
| Textbook opener | Does paragraph 1 survive the failure test — would it read as true under a different instrument's name? |
| Missing commercial why | Does **every** convention named carry an owner and an incentive, ideally the gaming it prevents? Count them: conventions stated, conventions justified. |
| Rearrangement posing as derivation | Was the no-arbitrage condition stated before the formula, or did an identity appear pre-solved? |
| Uninstantiated formula | Does every formula have a numeric line **immediately beneath it** with an intermediate step? |
| Fabricated level | Is every number either a parameter you chose, an arithmetic result of one, or an explicitly named data gap? |
| Numbers that don't close | Do the rows sum? Does every headline fraction recompute from the table above it using the convention named in the same sentence? Is the framing convention stable across tables in the same running example? |
| Adjective stress case | Does the stress case have arithmetic, or did the routine case get the numbers and the dangerous case get a sentence? |
| Missing counterparty | Is the constrained party on the other side named, with what forces them there? |
| No narrative library | Is there a driver table with directions **and** a named confusable pair **and** a dated episode where the intuitive mechanism gave the wrong sign? |
| Buckets that don't sum | Is there an attribution identity instantiated into a table with a stated total, and a named dominant bucket? |
| Flat list | Name the top item and the reason it dominates *in this context*, and the condition under which the ordering flips. If you cannot name the flipping condition, you have not ranked — you have sorted. Applies to prose enumerations and the closing platform list, not just bullets. |
| Symmetric padding | Does section length track importance, or the number of sub-topics? |
| Unlabelled trap | Does each named hazard carry all three parts — the wrong belief, the mechanism that breaks it, and the fix or the consequence — placed at the mechanic that causes it, not in a closing caveat? |
| Naked table | Is every table followed (or preceded) by a **sentence containing a verb that states what to conclude** — not a bold label, not a heading? "**Intended:**" is a label, not a verdict. If you cannot write the sentence, delete the table. |
| Dead row | Does every cell state a direction, magnitude, or mechanism — or does it re-expand the row label? Ban `widens / narrows` with no condition. |
| Numberless cell | Rule #2 applies **inside tables**: a table cell asserting an exposure with no magnitude, tenor, or named cost is prose in a box. |
| Flat convention claim | Is every sign / day count / quoting basis / notional basis stated in one of contract #3's three forms — *and*, where a mistake puts risk on, carrying a verification imperative on top? Check each of the four axes separately; a skipped axis is invisible. |
| Wall of prose | More than ~2 consecutive paragraphs with no bold lead-in, table, or equation? |
| Repeated comparison | If two things are compared twice, are the new table's axes driven by the new question (>⅔ new)? |
| Over-summiting | Did a bare "what is X" get all five rungs? Answer the rung asked plus one — a 150-line answer to an L1 question is a failure. |
| Fake escalation | Does the deeper rung add a *new representation* — a new equation, a new time slice, a new counterparty, a new stress state, a new attribution bucket? More sentences about the same object is not a rung. |
| Stops at the finance | Does the answer name what breaks in *this repo* and the signature of the omission — or honestly say nothing does? |
| **Rubric leakage** | Read the H2s alone. Do they name *content* ("The thing people miss — the notional mismatch") or *process* ("The commercial why", "Conventions — check all four axes")? Any heading that is a workflow step's name is a failure. |
| **Rung label printed** | Does `L1`/`L2`/`L3`/`L4`/`L5` appear anywhere in the answer? It must not. |
| **Quota row / quota section** | Does any row or section exist only to prove a check was run — a cell that calls itself negligible, an axis with no competing convention, a trap that is just "the convention is a convention"? Delete it. |
| **Generic trap label** | Does the literal string `Named trap:` appear? Label the trap by what it is. |
| **Manufactured residual** | Did "what's left is ___" invent a residual on an object whose residual is definitional? If the subtraction leaves nothing over, say that. |
| **Bold inflation** | Is bold landing on ordinary emphasis rather than on hazards and conclusions? |

---

## The specificity contract (applies to every explanation)

1. **Reproduce the identity, don't describe it.** "The asset swap spread adjusts the
   coupon for the price discount" is not an explanation; $A = C - S + (100-P)/\text{Ann}$,
   derived from its fair-value condition with every symbol and unit defined, is.
2. **Every mechanism carries its number** — *including inside table cells*. An
   abstraction may not stand for more than two sentences, or occupy a table cell, without
   a number, a unit, or a named cost attached.
3. **Illustrative, never current.** Every number you supply is a parameter set *you
   chose to make the arithmetic legible* — introduce it as such ("take a 5y 2% bond at
   95.00"). **You do not have live levels.** Never state a current market level, spread,
   or funding rate; where one is needed, say so and name the series to pull
   (`/get-market-data`, `quant_data.api.get_data`). A hedged fabrication ("the basis is
   around −30bp") is worse than an admitted gap — it is unfalsifiable inside the
   conversation.
4. **Never state a convention flat.** Sign, day count, quoting basis, notional basis are
   the highest-risk claims you will make — flip a whole signal and the Sharpe just
   inverts and you notice, but flip one *component* (a carry accrual, one leg of a hedge,
   the direction a spread is quoted) and the P&L still looks plausible. No DSR gate
   catches it: the deflated Sharpe corrects an observed SR for trial count, skew,
   kurtosis and sample length — it is a test on the return series, with no view on
   whether the series means what you think it means. Use one of three calibrated forms:
   name the competing convention and the sign relation between them ("conventional swap
   spread = swap rate − bond yield, so ASW ≈ −swap spread"); assert that an adjustment
   exists without asserting its value ("there's a day-count conversion baked into the
   quoted number"); or mark the approximation ("roughly 100/95", "~2–3%"). Where a
   mistake puts risk on, add a verification imperative on top: *"always check which way a
   chart is signed."* **Walk all four axes silently; write only the ones that carry a real
   trap.** A skipped axis is invisible, but an axis with nothing to say ("quoting basis:
   bp per annum, running") is a dead row — put it in a clause or leave it out. Never build
   a four-row table to prove you checked.
5. **Hedge tokens, never sections.** Attach uncertainty to the exact quantity that is
   uncertain ("say 40", "~8y", "typically"). Never write a standing disclaimer
   ("conventions vary, check with your desk"), and never let uncertainty become a reason
   to omit an illustrative number. Assert mechanics, cash-flow directions and structural
   logic at **full force**.
6. **Length follows importance, not symmetry.** Three sub-topics do not get three equal
   sections; it is correct for one branch to run twenty lines and its sibling three. And
   depth follows the rung asked — thoroughness at the wrong rung is padding.
7. **The failure test.** If a sentence would still be true of a different instrument in
   a different asset class, it is filler. Delete it or sharpen it.
8. **Every section ends on a consequence.** Read the last sentence of each section in
   isolation: if it only renames the heading, find the payoff or fold the section into
   its neighbour.

**Formatting** (house-wide, applies to chat output): math in `$...$` / `$$...$$` with
every symbol and unit defined, arithmetic in fenced blocks with numbers substituted;
anything with two or more parallel dimensions goes in a table — and **every table
carries a verdict sentence** immediately before or after it; if you cannot write one,
the table is decoration, delete it. **Every cell states a direction, a magnitude, or a
mechanism.** One bullet per distinct claim; no paragraph past ~4 sentences without a
structural break; bold is the scannable hazard-and-conclusion layer, not emphasis.

---

## Output — the conversation is the deliverable

**Write no file in this repo.** No note, no digest, no row in any index, no
`knowledge/` artifact. Exactly two exceptions, both below.

### Exception 1: capture a residual (offer once, write only if he accepts)

Offer in **one line at the end**, and only when the explanation produced a genuine
residual — a mechanism with a named constrained counterparty, a measurement discipline,
or a contradiction with something live in this repo. Never for a textbook definition.

If he accepts, write **exactly one** immutable capture:

```bash
mkdir -p ~/Dropbox/thought-inbox
date +%Y-%m-%dT%H:%M:%S%z          # the date is in context; the clock is not
```

to `~/Dropbox/thought-inbox/YYYY-MM-DD-HHMM-<short-slug>.md` with frontmatter
`type: capture`, `captured: <the ISO stamp above>`, `status: open`, `source: manual`;
body is prose. **No links, no headings, no `[[wikilinks]]`, no `CONCEPT-NNN`/`IDEA-NNN`
outside an optional `refs:` hint.** Then run
`python3 scripts/check_brain_integrity.py --captures` — note it exits 0 when the
transport dir is absent, so confirm the file exists by path.

**Never** mint a `CONCEPT-NNN`, edit the generated `CONCEPTS.md`/`VERDICTS.md`/
`IDEAS.md`, or touch the superseded `knowledge/domains/KNOWLEDGE_*.md`.
`scripts/triage_inbox.py` is the only ID minter, pre-commit hooks enforce it, and Zelin
decides what gets promoted.

### Exception 2: he explicitly asks for a written note

That is a different job — hand off to `/read-to-learn`'s conventions
(`knowledge/papers/`), or write exactly where he names it. Never invent a location
under `knowledge/` on your own initiative.

## Graduating to formal research

If explaining something surfaces a genuinely tradable hypothesis, **do not backtest it
here**. Note it and follow the migration path in `knowledge/README.md` → strategy folder
→ manifest → `python -m alpha_research.review` → pool.

---

## Principles

- **Mechanism over definition.** The reader can get a definition anywhere. What they
  cannot get is what the thing does to them when they hold it.
- **Define by subtraction.** Every measure is "what did this strip out, and what's
  left?" Install that schema once and it transfers to every metric he meets afterwards.
- **Conventions have owners and incentives.** Say who pays for the convention and what
  it prevents. Arbitrary-sounding rules are usually load-bearing capital arithmetic.
- **Name the constrained party.** A premium is only explained once you say who is paying
  it and why they cannot stop.
- **The unintended exposure is the lesson.** Anyone can name the bet. The value is in
  the tail of things the wrapper forces you to carry alongside it.
- **Rank, always.** An unranked list of twelve exposures is the most common and most
  useless failure — and the ranking is the part that cannot be recovered from a textbook.
- **Stress the structure in numbers.** The scenario that breaks the instrument deserves
  more arithmetic than the scenario that doesn't.
- **Numbers close or they don't ship.** Recompute before sending. A punchline statistic
  that fails checking discredits the whole explanation.
- **Illustrative, never current.** You have no live levels. Chosen parameters teach;
  invented market levels mislead.
- **Calibrated, not cautious.** Assert mechanics at full force; hedge the specific token
  that is uncertain. Mush is worse than a marked approximation.
- **Frame failure as self-deception.** "The carry is fiction", "you don't know whether
  you were right or just long a hidden risk" — the cost is epistemic, not cosmetic.
- **Escalate unasked, but only one rung.** Answer the rung, then climb one. Summiting
  all five on a bare "what is X" is padding, not generosity.
- **Land in the platform.** Close on what this forces in a backtest here and the
  corrupted output that follows from skipping it — or say plainly that nothing does.
- **No gates.** No significance thresholds, no PM review, no file to write. Fast, dense,
  and honest.
