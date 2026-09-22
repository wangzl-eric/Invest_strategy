---
name: read-to-learn
description: >
  Read and study a quant/finance paper, article, or book to learn the
  industrial-standard mindset and methodology of market analysis — not just
  summarize it. Use whenever the user says "read this paper", "study this
  chapter", "help me understand <book>", "take notes on", "extract the
  methodology from", or "what can I learn from <source>". Produces structured,
  methodology-first notes — paper notes in knowledge/papers/, book
  chapter notes in knowledge/books/ — and scores each source on
  credibility / relevance / actionability. Educational, no rigor gates. For
  practitioner/industry reports (sell-side, broker, consulting, central-bank notes)
  use /read-industrial-report instead.
---

# /read-to-learn — Study a Source for Mindset & Methodology

You are a study partner for a **junior quantitative researcher** (Zelin). The goal
of every read is not a summary — it is to **transfer the practitioner's mindset and
methodology** of market analysis: how a serious quant frames a problem, what
evidence they trust, where they are skeptical, and how the idea would survive
contact with real data and real costs.

This is a **Playground** activity: educational, fast, no statistical gates, no PM
review. It complements the existing tools — it does not replace them:

| Tool | Job |
|------|-----|
| **`/read-to-learn`** (this) | Read a source → methodology-first notes + scoring |
| `/read-industrial-report` | Digest a practitioner/industry report → fixed 3-part study note |
| `/get-market-data` | Pull data if you choose to replicate a claim |
| `market-study` skill | Exploratory data study (correlation/regime/event) |
| `/explain-mechanism` | Explain an instrument, spread, or convention at desk level → answer in chat, no file |
| `cerebro` agent | Discover *new* papers, manage the reading queue |

**Routing between the two read skills.** Pick **this** one when the source argues from
evidence a reader could in principle reproduce — academic papers, working papers, book
chapters, and research-grade practitioner white papers (AQR/Bridgewater-style) — and you
want the longer methodology-mindset treatment. Pick `/read-industrial-report` when the
source is a *report* that packages a house view for a decision — sell-side and broker
notes, consulting decks, central-bank and policy notes, sector/macro outlooks — and you
want it digested quickly into the fixed three-part format. When a source genuinely
straddles both (a bank research note with a real empirical study inside), the tiebreaker
is the **output you want**: a durable note that teaches method → here; a scannable digest
that audits an argument and its incentives → `/read-industrial-report`.

The line you must hold: **read for understanding and methodology, not to ship a
strategy.** If a source looks tradable, that is a *graduation* signal (see below),
not a license to backtest here.

---

## When to use

Use when the user wants to **learn from a specific piece of material**: a PDF in
`knowledge/sources/`, a URL, an arXiv/SSRN id, or a chapter of a book
already being studied. Do **not** use for: pulling data (`/get-market-data`),
formal strategy research (`skills/rigorous-backtest`), or instrument/convention
mechanics Q&A with no source document (`/explain-mechanism`).

---

## Inputs you need (ask only if missing)

1. **The source** — a file path, URL, or the title of a book/chapter already in a
   study folder. PDFs in `knowledge/sources/` and study folders open
   directly with the `Read` tool (it renders PDF pages).
2. **Material type** — *paper/article* or *book chapter*. If unsure, infer from the
   source; a single self-contained PDF with an abstract is a paper, a numbered
   chapter of a larger work is a book chapter.
3. **Depth** — default is **notes + methodology extraction** (no code). Only
   replicate a claim on data when the user explicitly asks ("test this", "replicate
   the result", "does this hold on our data?").

---

## Workflow

### 1. Locate & frame (before reading deeply)
- Open the source. For a long book, read only the **target chapter(s)** plus enough
  front matter to know the author's overall argument arc.
- In one sentence, state the **central claim** and the **decision a practitioner
  would make differently** if it is true. Write nothing else until you can do this.

### 2. Read through the right protocol
Pick the branch by material type. The full lens catalog is in
[references/methodology-lenses.md](references/methodology-lenses.md) — read it once;
it is the core of this skill.

**Papers / articles** → claim-validation protocol:
- Core focus, narrative, central claim.
- Data sources, sample, frequency; methodology choices and *why* each was made.
- The **construction**: how the abstract idea was turned into a number a computer can
  compute — the sort/portfolio/regression/estimator, written out.
- Evidence standard: in-sample vs out-of-sample, significance, multiple-testing,
  robustness checks the author did (and the ones they skipped).
- Concrete ways to **validate or challenge** the result (data, replication,
  alternative methodology).

**Books** → progression protocol (across sessions):
- Track the chapter's place in the author's overall argument arc — what was
  established before, what this chapter adds.
- Extract technicalities (formulas, methods, frameworks) into durable notes so
  context survives across sessions.
- Capture: concepts encountered, how they build on each other, and what the author
  is ultimately trying to convey.

### 3. Reconstruct the derivation chain (the spine of the note)
**The takeaway is not the result — it is the path to the result.** Before writing
anything else, reconstruct how the author got from a question to a number, as an
explicit chain. Every link gets *what was done*, *why that choice*, and *what would
break if it were wrong*:

> economic question → observable proxy → **construction / estimator** → **test statistic
> & null** → result → interpretation

Write out the **load-bearing math** — normally 1–3 equations, no more. Use display math
with every symbol defined, and say in one line what each term *does economically*:

$$\text{HML}_t \;=\; \tfrac12\!\left(R^{SV}_t + R^{BV}_t\right) - \tfrac12\!\left(R^{SG}_t + R^{BG}_t\right)$$

where $R^{SV}$ is the small-value portfolio return, … — i.e. the long leg is cheap
stocks, the short leg expensive ones, size-neutralised by averaging across both caps.

Then answer, concretely:
- **Why this estimator and not the obvious alternative?** (OLS vs Fama–MacBeth vs GMM;
  sorts vs regression; equal- vs value-weighted; Newey–West lags and why that many.)
- **What is the null, and what would rejecting it actually prove?** Distinguish
  "different from zero" from "different from the benchmark" from "economically large".
- **Where is the inferential leap** — the step where a correlation becomes a mechanism,
  or an in-sample fit becomes a forecast.

If you cannot reproduce the chain from your own note, the note is not finished.

### 4. Note what to watch
Extract the **handful of quantities that govern whether the result holds** — this is
what converts reading into judgment. Typically: the parameters that were chosen and
their sensitivity (lookback, holding period, rebalance frequency), the diagnostic
numbers worth remembering (t-stat, $R^2$, Sharpe gross vs net, turnover, breakeven
cost), and the conditions under which the effect weakens or flips (regime, rate level,
liquidity, post-publication sample). State them with **numbers and units**, not
adjectives.

### 5. Extract the mindset (the part that matters most)
For **every** source, fill the methodology-and-mindset lenses from
[references/methodology-lenses.md](references/methodology-lenses.md):
problem framing · data & sample · methodology & assumptions · evidence standard ·
economic mechanism (risk vs behavioral) · implementation reality (costs, capacity,
turnover, decay, crowding) · practitioner heuristics (what they trust / distrust) ·
connection to our platform.

The **connection-to-our-platform** lens is mandatory and specific: name the
strategy, signal, runner, or doc in this repo that the source **validates,
challenges, or could improve** (e.g. `alpha_research/backtests/runners/...`,
a `research/pool/<id>/manifest.yaml`, a playground study). If it contradicts or
exposes an issue in existing code or notes, **flag it explicitly** — this mirrors
the cerebro contradiction-check rule in CLAUDE.md.

### 6. Score the source
Score on the standard playground rubric (1–5 each). Only sources scoring **≥ 3 on
all three** warrant deeper follow-up or a queue entry.

| Dimension | Question |
|-----------|----------|
| Credibility | Author reputation, venue, methodology soundness |
| Relevance | Direct applicability to quant research & current scope |
| Actionability | Can the findings be implemented, tested, or studied concretely? |

### 7. Write the note
Write to the **specificity contract** below — read it before drafting, not after.
Use the matching template — note that papers and book chapters land in **different
places** (see *Output location & convention* below):
- Paper / article → [templates/paper_note.md](templates/paper_note.md), saved to the
  central papers library `knowledge/papers/` as
  `paper_notes_<author><year>.md` (or `paper_notes_<author>_<topic>_<year>.md`), then
  add a row to that folder's `INDEX.md`.
- Book chapter → [templates/book_chapter_note.md](templates/book_chapter_note.md),
  saved inside the book's study folder as `notes/ch<NN>_notes.md`.

**One canonical note per paper.** If the paper already has a note in `papers/`, *update
it* rather than writing a second one — merge the new perspective in and record which
book/study surfaced it again. Never fork a paper note per study folder.

Then append a one-line entry to the relevant study folder's `FINDINGS_LOG.md`, and add
any follow-up materials surfaced (that scored ≥ 3/3/3) to that study's
`reading_queue.md` — linking to the canonical note in `papers/`. For a standalone paper
read with no parent study, the note plus its `INDEX.md` row is the whole deliverable.

### 8. Close the loop
- Math in markdown uses standard LaTeX delimiters: `$...$` inline, `$$...$$`
  display. Fix any malformed math before finishing.
- Re-read the note against the **specificity contract** below and cut or sharpen every
  sentence that fails it.
- End with **2–4 concrete "what to do next"** items framed as learning, not
  trading: a follow-up paper, a mechanism to unpack with `/explain-mechanism`, or — if the user
  asked — a claim to replicate via `/get-market-data` + `market-study`.

---

## Output location & convention

Today's date is available in context — never call `date`/`Date.now()`.

Paper notes live in one **central, flat library**; book artifacts live in
timestamped book folders; cross-field topic work lives in study folders:

```
knowledge/papers/                 # canonical paper/article notes
├── INDEX.md                                  # one row per note, grouped by source study
└── paper_notes_<author><year>.md             # or paper_notes_<author>_<topic>_<year>.md

knowledge/books/<YYYY-MM-DD>_<book_slug>/     # one folder per book
├── notes/                        # ch<NN>_notes.md
├── reading_queue.md              # scored follow-ups (≥3/3/3), linking to ../../papers/
├── FINDINGS_LOG.md               # one line per session
└── study_hypotheses.md           # optional: testable ideas the reading raised

knowledge/studies/<YYYY-MM-DD>_<topic_slug>/  # cross-field topic investigations
└── (same shape, plus notebooks/ and data/ when the topic needs them)
```

Paper notes are **not** written into study folders — a paper surfaced by three different
books still gets exactly one note in `papers/`, with each book's connection preserved
inside it. Read `knowledge/papers/INDEX.md` before writing; it states the
naming and merge convention and shows which papers already have notes.

Reuse the **existing** folder when continuing a book already in `knowledge/books/`
or a topic already in `knowledge/studies/`; create a new one only for genuinely new
material. Match the structure of existing folders (e.g.
`knowledge/books/2026-03-29_expected_returns_ilmanen`) — that is the proven convention. Industrial
report digests go to `knowledge/reports/` via `/read-industrial-report`.

---

## Optional: replicate a claim (only when asked)

If the user wants to test whether a result holds on our data, stay lightweight:
1. Pull data via the **`/get-market-data`** skill (`quant_data.api.get_data`,
   local-Parquet-first). There is no legacy `data_helpers.py` shim — do not
   reference one; shared plotting helpers live in `knowledge.shared.viz_helpers`.
2. Reproduce *one* central claim, save a notebook + figures into the study folder's
   `notebooks/`, and note where your result agrees or diverges from the source.
3. This is illustration, not validation — no PSR/DSR, no walk-forward. Divergence is
   a finding, not a failure.

---

## Graduating to formal research

If a source produces a genuinely tradable, well-formed hypothesis, **do not**
backtest it here. Follow the migration path in `knowledge/README.md`:
check lessons learned → message `cerebro` for a literature briefing → create a
strategy folder → use the formal template → enter the manifest → review → pool
workflow (`docs/guides/strategy_pool_workflow.md`). Note the candidate in
`study_hypotheses.md` and stop.

---

## The specificity contract (applies to every note)

The reader is a working quant. Vague notes are worse than no notes — they *feel* like
understanding without transferring any. Hold every sentence to these:

1. **Reproduce the math, don't describe it.** If a formula carries the argument, write
   it in LaTeX and define every symbol. "They regress returns on a value signal" is
   not a note; $r_{i,t+1} = \alpha + \beta\,z_{i,t} + \varepsilon_{i,t+1}$ with $z$
   defined as the cross-sectionally standardised book-to-market rank *is*.
2. **Every claim carries its number.** Coefficient, t-stat, $R^2$, Sharpe, turnover,
   sample period, universe, frequency, units. "Costs matter" → "gross Sharpe 0.9 falls
   to 0.31 net at 210% annual turnover and 10 bp one-way; breakeven ≈ 29 bp."
3. **Name the alternative that was not taken.** A methodology choice is only
   informative next to the choice rejected — and *why*.
4. **The failure test:** if a sentence would still be true of a different paper on a
   different asset class, it is filler. Delete or sharpen it.
5. **Be scientific about uncertainty.** Separate what the evidence establishes, what
   the author asserts, and what you infer. Label the third as yours.
6. **Structure over prose density.** The derivation chain and key-math sections are
   already tabular/display-math by template — keep it that way. For the remaining
   free-text sections (economic mechanism, critique, competing perspectives,
   connection to platform), use **PEE** (Point → Evidence → Explanation) per idea and
   **one bullet per distinct claim**, not a fused paragraph: a section with three
   things to say gets three bullets. Write any multi-step reasoning as an explicit
   arrow chain — `<observation>` → `<inference>` → **`<conclusion>`** — instead of
   narrating it in prose. A paragraph running past ~4 sentences with no break has
   failed the format regardless of how correct its content is.

## Principles

- **Path over result.** The takeaway is *how the result was reached* — question →
  proxy → estimator → test → interpretation. A note that records the finding but not
  the derivation has failed, even if the finding is correct.
- **Methodology over summary.** A good note teaches *how to think*, not *what the
  paper said*. If your note could have been written from the abstract alone, go
  deeper.
- **Skeptical, not cynical.** Name what the author got right and what they hand-waved.
- **Connect to the platform every time.** A source that touches nothing in this repo
  is either off-scope (score it down) or a gap worth flagging.
- **Honest scoring.** A famous paper can still be low-actionability for us. Say so.
- **No gates.** No significance thresholds, no PM review. Fast iteration, durable notes.
