---
name: read-industrial-report
description: >
  Read and digest an industrial / industry research report on any topic
  (sell-side research, sector & macro outlooks, consulting decks, central-bank
  notes, broker reports, white papers) into a compact, decision-oriented study
  digest. Use whenever the user says "digest this report", "read this industry
  report", "summarize this research note", "break down this deck", or hands over
  a report PDF/URL on a market, sector, or macro topic. Produces a fixed
  three-part output: a 3–5 sentence STAR-ordered (unlabeled, flowing-prose) executive
  summary (context · methodology · conclusion), Point-Evidence-Explanation blocks with bulleted
  arrow-linked causal chains dissecting how the report reaches its conclusion — and files
  the result: creates the year/month folder, moves and renames the source PDF to match
  the digest, and updates the library index — with
  the actual numbers and any load-bearing formula reproduced — and 5–10 study
  keywords, plus a required "what to watch" table and bulleted platform connection.
  Structured for scanability, not dense prose. Teaches how the call was built, not
  just what it is. Educational, no rigor gates.
---

# /read-industrial-report — Digest an Industrial Report into a Study Note

You are a study partner for a quantitative researcher (Zelin). An **industrial
report** is any practitioner-facing research document on a market, sector, asset
class, or macro theme — sell-side equity/strategy research, broker and bank notes,
consulting reports (McKinsey/BCG-style), central-bank and policy notes, industry
white papers, and similar. The goal is **not** a generic summary: it is to extract
*what was claimed, how it was argued, and how well the evidence supports it*, in a
form short enough to scan and durable enough to cite later.

## Why this exists — the digest is not the deliverable

The reports library is an **idea accumulator that runs before validation**. Reading a report is
stage 1 of three:

```
  STAGE 1  read reports → record the essence → harvest transferable ideas → score them
           ↓  accumulate until the pool is large enough to choose from
  STAGE 2  select the ideas that make the most economic sense
  STAGE 3  validate the selected pool (alpha_research/research/, python -m alpha_research.review)
```

So the digest is a **working paper**; the durable output is the scored entry it contributes to
`knowledge/reports/IDEAS.md`. Two rules follow, and they are the ones most easily got
wrong:

- **Testability is a score, never a gate.** An idea that cannot be tested on this platform today
  still belongs in the pool. Record the data gap in the score note and keep the idea. Never drop
  an idea for being currently unverifiable — that would defeat the stage.
- **Harvest the transferable mechanism, not the house call.** "GS is short the 10y JGB" is a
  position, worthless once it expires. "Net issuance mix plus central-bank taper identifies *which*
  curve sector underperforms, because mandated buyers sit at one tenor and the calendar is public"
  is an idea — reusable in another market, another year, by someone who never read the note. Test
  every candidate: *could this be applied to a different market next year?* If no, it is a call.
- **Do not validate.** No backtests, no gates, no verdicts on whether an idea works. Plausibility
  and mechanism only. Scoring an idea low is useful information, not a failure.

This is a **Playground** activity: educational, fast, no statistical gates, no PM
review. It is the report-shaped sibling of `/read-to-learn`:

| Tool | Job |
|------|-----|
| **`/read-industrial-report`** (this) | Digest a practitioner/industry report → fixed 3-part study note |
| `/read-to-learn` | Deep methodology-mindset study of a paper, article, or book chapter |
| `/explain-mechanism` | Explain an instrument, spread, or convention at desk level → answer in chat, no file |
| `/get-market-data` | Pull data if you choose to check a claim |
| `cerebro` agent | Discover new reports/papers, manage the reading queue |

Pick **this** skill when the source is a *report* that packages a house view for a
decision — sell-side and broker notes, consulting decks, central-bank and policy notes,
sector/macro outlooks — and you want it digested quickly and consistently. Pick
`/read-to-learn` when the source argues from evidence a reader could in principle
reproduce — academic papers, working papers, book chapters, and research-grade
practitioner white papers (AQR/Bridgewater-style) — and you want the longer
methodology-mindset treatment. When a source genuinely straddles both (a bank research
note with a real empirical study inside), the tiebreaker is the **output you want**: a
scannable digest that audits an argument and its incentives → here; a durable note that
teaches method → `/read-to-learn`.

---

## When to use

Use when the user hands over a report (a PDF, a URL, a pasted document, or a file
already in the repo) and wants it **digested** into the standard study format. Do
**not** use for: pulling data (`/get-market-data`), formal strategy research
(`skills/rigorous-backtest`), or instrument/convention mechanics Q&A with no source
document (`/explain-mechanism`).

---

## Inputs you need (ask only if missing)

1. **The source** — a file path, URL, arXiv/SSRN id, or pasted text. PDFs open
   directly with the `Read` tool (it renders pages; use the `pages` arg for long
   PDFs). If only a URL is given, fetch it with `WebFetch`.
2. **Topic / domain** (optional) — infer from the report if not stated; it only
   affects the keyword vocabulary and which platform connection to name.
3. **Output destination** (optional) — default is a digest filed under
   `knowledge/reports/<YYYY>/<MM>/` (see *Output* below). If the user just
   wants the digest in chat, write the three parts inline and skip the file — and skip
   the filing step with it.

Filing the source alongside the digest is part of the job, not a follow-up chore: the
skill **creates the year/month directory, moves the source PDF into it, and renames it**
to match the digest's stem (step 6). Don't ask the user where to put it or hand back a
digest that leaves the source under its original vendor filename.

---

## Workflow

### 1. Locate, open, and frame
- Open the source. For a long PDF, read the **executive summary / key-takeaways
  page first**, then the methodology/analysis sections, then the appendix tables.
  Don't read cover-to-cover before you know the spine.
- In one sentence, state the report's **central claim** and the **decision a reader
  would make differently** if it is true (allocate, hedge, time, size, avoid,
  reprice). Write nothing else until you can do this.

### 2. Read for the three things the output needs
Read the whole report once, tagging as you go:
- **Context** — who published it, when, for whom, and what question/decision it
  addresses. Note the house view, mandate, or potential conflict of interest
  (sell-side reports talk their book).
- **Methodology** — how the claim is argued: data sources and sample, the analytical
  approach (survey, regression, scenario/DCF, comparables, factor decomposition,
  event study, expert interviews), and what statistical or quantitative evidence is
  presented (point estimates, ranges, significance, charts, base/bull/bear cases).
- **Conclusion** — the headline finding, forecast, rating, or recommendation, and
  any explicit confidence or caveats.

### 3. Trace the logical chain (the analytical core)
This is what separates a digest from a summary. **The takeaway is the path to the
conclusion, not the conclusion.** Reconstruct the argument as a chain:
**observations → evidence → inference → conclusion.** For each link ask:
- Does the **evidence actually support** the inference, or is it suggestive/anecdotal?
- Are the **statistics** descriptive (levels, growth rates, shares) or inferential
  (significance, confidence intervals, model fit)? Is the sample period/universe
  broad enough, or cherry-picked to one regime?
- What **assumptions** carry the conclusion, and which one, if wrong, breaks it?
- Where does the report **leap** — extrapolate a trend, assume mean reversion,
  ignore costs/capacity, confuse correlation with causation, or talk its book?
Name the strongest evidence and the weakest link explicitly.

**Write the chain as arrows, not prose.** A report usually rests on 2–4 independent
pillars (e.g. a growth pillar, an inflation/policy pillar, a fiscal/valuation pillar).
For each pillar, capture one bulleted, arrow-linked chain while you're reading —
this becomes the spine of the digest's methodology section, not an afterthought:

> `<observation/data>` → `<what it implies>` → `<next inference>` → **`<conclusion>`**

A causal chain that can't be written this way — where the "logic" is really just a
sequence of assertions — is itself a finding: say so, and name the missing link.

**Be quantitative.** Reports hide their real content in the arithmetic:
- **Reproduce the load-bearing calculation.** If the call rests on a formula or an
  accounting identity, write it in LaTeX with symbols defined — a DCF's
  $V_0 = \sum_t \frac{CF_t}{(1+r)^t} + \frac{TV_N}{(1+r)^N}$, a scenario's
  probability-weighted expectation, a risk-parity vol-target $w_i \propto 1/\sigma_i$,
  a breakeven condition. Most house views collapse to two or three numbers.
- **Find the number that carries the conclusion**, and test its sensitivity yourself:
  what terminal growth, discount rate, margin, or correlation assumption is doing the
  work, and how much does the headline move if it is off by a plausible amount? A
  target price that needs 3.5 % terminal growth is a bet on that input, not on the
  company.
- **Distinguish forecast from extrapolation.** Is there a model with an error band, or
  is a trend drawn forward? Report the stated confidence, or note its absence.

### 3b. Extract "what to watch"
A report's durable value is the **short list of observables that would confirm or kill
the call** — that is what you carry forward after the house view is stale. Pull 3–5:
the indicator, its **current level**, and the **threshold/direction** that changes the
conclusion (e.g. "core CPI 3-month annualised, now 2.8 % — thesis fails above 3.5 %").
Prefer things measurable from this platform's data lake; note the FRED/ticker series
where one exists.

### 4. Connect to the platform (mandatory — every digest)
Name the specific strategy, signal, runner, manifest, dataset, or note in *this repo*
the report touches, and say whether it **validates, challenges, or could improve** it.
Flag contradictions explicitly — this mirrors the cerebro contradiction-check rule in
CLAUDE.md, and industry/sell-side reports are the *most* likely to cut against a live
signal, so this section is never optional. Candidate anchors:
`alpha_research/backtests/runners/`, `alpha_research/research/pool/<id>/manifest.yaml`,
`alpha_research/backtests/stats/`, `alpha_research/backtests/costs/`, existing
`knowledge/` notes and hypotheses. If the report genuinely touches nothing
in-scope, write one line saying so and score Relevance down accordingly — "nothing
applies" is an allowed answer, an absent section is not.

**One bullet per connection, never one paragraph.** A report with four things to say
about the platform gets four bullets, not four sentences fused into one block —
each bullet names the anchor, states validates/challenges/could-improve/gap, and
stops in 1–2 sentences.

### 5. Write the digest (FIXED three-part format — do not omit a part)
Produce exactly these three sections, in order, using
[templates/report_digest.md](templates/report_digest.md):

1. **Executive summary — 3 to 5 sentences, STAR-ordered but unlabeled.** Flowing
   prose, no bullets, no visible section labels — but ordered deliberately as
   Situation (who published it, when, for whom) + Task (the question/decision it
   addresses) → Action (the methodology/analytical approach) → Result (the
   conclusion and its stated confidence). STAR is scaffolding for the *order* of the
   sentences, not text that appears in the output — do not write "Situation:",
   "Action:", etc. into the digest. Hedge the Result sentence(s) to the report's own
   epistemic status: it is *GS's forecast* or *the report argues*, not settled fact —
   "GS expects 2026 growth to hold at 0.8%," not "2026 growth holds at 0.8%." No more
   than 5 sentences; no fewer than 3.
2. **Methodology & reasoning — PEE blocks + bulleted causal chains, not a wall of
   prose.** A report typically rests on 2–4 independent pillars (a growth pillar, a
   policy pillar, a valuation pillar, …). Give **each pillar its own block**, in this
   shape:
   - **Point:** the one-line claim this pillar establishes.
   - **Evidence:** the specific number(s)/data/quote that back it — with units,
     period, and sample.
   - **Chain:** the arrow-linked reasoning from step 3 —
     `<observation>` → `<inference>` → `<inference>` → **`<conclusion>`**.
   - **Read:** descriptive or inferential? load-bearing or corroborating? where does
     it leap?

   Close the section with one line: **Weakest link** — the single most load-bearing,
   least-tested assumption across *all* the pillars. Reproduce the load-bearing
   formula in LaTeX (once, after the blocks) when there is one. **Never collapse
   this into a single paragraph** — a paragraph that runs past ~4 sentences without
   a line break or bullet has failed the format, no matter how dense its content.
3. **Keywords — 5 to 10.** A comma- or bullet-listed set of study keywords/tags
   (topics, methods, instruments, themes) suitable for indexing a study report and
   finding this note later. Prefer specific terms ("shadow rate", "risk parity
   leverage", "crisis alpha") over generic ones ("finance", "investing").

Then close with two required sections, after the three numbered parts and without
disturbing their order:
- **What to watch** — the 3–5 observables from step 3b as a table (indicator, series,
  level now, confirms-if, breaks-if) — a table, not prose, since this is inherently
  tabular data.
- **Connection to our platform** — one bullet per connection from step 4; one bullet
  saying so if nothing applies.
- **Commentary — value to our investment learning** — a verdict on the report itself,
  on two **independent** axes, with the reasoning:
  - **Directness** — `direct` (supplies content applied straight to investment analysis:
    a mechanism, signal construction, risk rule, valuation identity, payoff geometry) vs
    `indirect` (contributes through context, background, or by sharpening how you read
    *other* reports).
  - **Value** — `useful` (genuinely moves capability; you would be worse off without it)
    vs `limited` (real but marginal — duplicated elsewhere in the library, or perishable
    house view rather than durable mechanism).

  Keep the axes independent: **`indirect` is not a polite synonym for `weak`.** A report
  that teaches you how to read other reports is indirect and can be highly useful. Then
  give: **why** (2–4 sentences grounded in what it contributed to `IDEAS.md` and at what
  scores — not a re-summary), **what to take**, **what to ignore** (every report has
  something perishable; name it), and **whether it is worth a second read or is spent**.

  The hard evidence is idea yield. A report whose best contributions arrived as
  *critiques of it* rather than as its own argument is teaching by negative example —
  genuine value, but `indirect`. **Be willing to write `limited`**; a library where every
  report is `direct + useful` has not been read critically.

Keep the digest tight — the value is density, not length. Optional header fields
(source, type, date, one-line claim, 1–5 scores) may precede the three parts.

### 6. File the artifacts (mandatory — create dirs, move and rename the source)

**Do this yourself; never leave a report or a digest sitting at the library root, and
never leave the source PDF under its original vendor filename.** A digest and its
source are one unit and must end up in the same folder under the same stem. Full rules
are in *Output location & convention* below; the mechanical steps are:

1. **Read three things off the report itself** (not off the file's mtime, and not off
   today's date): the **publication date** → `<YYYY>/<MM>/` and the trailing date in the
   stem; the **issuer**; the **topic**. Undated practitioner classics get a year folder
   with no month.
2. **Pick the `<tag>`** — exactly one from the vocabulary in `INDEX.md`
   (`macro` · `rates` · `economics` · `equities` · `crossasset` · `flows` · `factor` ·
   `event`). If nothing fits, add the new tag to the `INDEX.md` table in this same pass
   rather than inventing an unlisted one.
3. **Create the directory**, then move the source and write the digest beside it:

   ```bash
   cd knowledge/reports
   STEM="<tag>_<issuer>_<topic>_<YYYY-MM-DD>"      # e.g. macro_gs_jpy-macro-trading_2026-04-07
   DIR="<YYYY>/<MM>"                                # e.g. 2026/04
   mkdir -p "$DIR"
   mv "<original vendor filename>.pdf" "$DIR/$STEM.pdf"
   # then write the digest to $DIR/$STEM.md
   ```

   - Source **already inside the repo** (library root, another `knowledge/` folder) →
     `mv` it. Source **outside the repo** (Downloads, Desktop) → `cp` it in, so the
     user's original stays where they left it.
   - Vendor filenames are often long, non-ASCII, or contain spaces and smart quotes
     (`【GS先物】…`, `Global Markets Analyst_ A Macro User's Guide…`). Always quote paths.
   - Source is a URL with no local file → skip the PDF, note the URL in the `Source:`
     header field, and file the digest alone.
   - The report is a **PDF export of a digest** rather than a source report → suffix it
     `.digest.pdf` so it is never mistaken for the source.
4. **Check for a collision before moving.** If the destination stem already exists, you
   are either re-digesting something already in the library (update it in place instead
   of creating a near-duplicate) or you have the wrong date. Resolve it; do not append
   `_v2` or `_new`.
5. **Verify after moving** — confirm the `.md` and `.pdf` are both present under the
   same stem, and that nothing was left at the library root except `INDEX.md`.

### 7. Harvest into the idea pool (mandatory — this is the durable output)

Append this report's contribution to `knowledge/reports/IDEAS.md`. The digest is the
working paper; **this is what carries into stage 2.**

1. **Record the essence** in the essence table: one line for what the report fundamentally says
   (stripped of the house view), its core economic machinery, the market, the single load-bearing
   number, and the transferable lesson that outlives the call.
2. **Harvest 0–6 transferable ideas.** Quality over quantity — three sharp entries beat six padded
   ones, and **some reports genuinely yield none**. An economic outlook or a weekly positioning
   note may contain no reusable mechanism at all; record that in the *thin yield* section rather
   than manufacturing filler. Manufacturing an idea to fill a row is the main failure mode here.
3. **Type each idea** — exactly one of: `signal` (a rule generating a view) · `method` (a technique
   for evaluating claims or building signals) · `regime` (when a relationship holds, strengthens,
   or inverts) · `risk` (sizing, control, exit) · `structure` (instrument/payoff construction).
4. **Write the mechanism field — this is the point of the entry.** Answer: *who is on the other
   side, and why does this persist rather than being arbitraged away?* A real economic idea names a
   constrained or price-insensitive counterparty (a mandate, a regulation, a benchmark, a hedging
   need, a liquidity demand) or a genuinely compensated risk. If the only support is "it worked in
   the sample," say exactly that and score Economic rationale 1–2. Never dress a fitted pattern in
   mechanism language.
5. **Score 1–5 on three axes**, and be discriminating — if everything lands on 4 the ledger is
   useless:
   - **Economic rationale** — 5 = named constrained counterparty or clearly compensated risk;
     3 = plausible story, no identified payer; 1 = pattern with no mechanism.
   - **Durability** — 5 = structural, rooted in mandates/regulation/plumbing that changes slowly;
     3 = holds within a policy regime; 1 = likely arbitraged, or regime-bound with no way to detect
     the regime ending.
   - **Testability** — 5 = data already in the lake; 3 = reachable public source; 1 = needs
     proprietary data (swaption vols, dealer inventory, OIS strips). **Name the series or the gap.**
6. **Check for an existing entry first.** The same mechanism arriving from a second, independent
   report is *one* idea with two sources — and the independent arrival is itself evidence worth
   noting. Merge into the existing entry and strengthen its mechanism write-up; do not create a
   near-duplicate.
7. **Re-sort the summary table** by total score (sum of three), descending.
   **NEVER RENUMBER AN EXISTING IDEA.** An `IDEA-0NN` is a permanent handle: digests cite it,
   and re-scoring an idea re-sorts the pool, so renumbering on every pass silently invalidates
   every cross-reference in the library. Rank is a *display order*, not an identity. A new idea
   takes the next unused number regardless of where it sorts.
8. **Verify before finishing:** `python3 scripts/check_ideas_integrity.py` — checks IDs are unique
   and anchored, the summary table matches the entries and is sorted, each entry's three scores sum
   to its stated total, and every `IDEA-0NN` referenced anywhere in the library resolves. Fix any
   failure; do not hand back a pool that fails this.

### 8. Close the loop
- Math in markdown uses standard LaTeX delimiters: `$...$` inline, `$$...$$` display.
  Fix any malformed math before finishing.
- Score the source on the standard playground rubric (Credibility / Relevance /
  Actionability, 1–5 each) in the header — be honest; a glossy bank report can still
  be low-actionability. Only sources scoring ≥ 3 on all three warrant a follow-up.
- Add a row to `knowledge/reports/INDEX.md` (create it if missing), in the
  newest-report-first table: tag, digest link, report title, issuer/type, publication
  date, C/R/A scores. Keep the link **relative to the reports root**
  (`2026/04/macro_gs_jpy-macro-trading_2026-04-07.md`).
- **Paths inside the digest are repo-root-relative** (`knowledge/reports/…`)
  — the `Source:` field and every cross-link to a sibling digest. Before finishing,
  confirm each one resolves; if this pass moved or renamed anything that another digest
  references, update those references too.

---

## Output location & convention

Today's date is available in context — never call `date`/`Date.now()`.

Digests are filed by the **report's own publication date**, not the date it was read
(the read date lives in the `Read on:` header field). The library reads as a market
timeline:

```
knowledge/reports/
├── INDEX.md                                              # convention + one row per digest
├── <YYYY>/<MM>/<tag>_<issuer>_<topic>_<YYYY-MM-DD>.md    # digest
│              <tag>_<issuer>_<topic>_<YYYY-MM-DD>.pdf    # source report, SAME stem
└── <YYYY>/<tag>_<issuer>_<topic>_<YYYY>.md               # undated classics, year folder only
```

Rules:
- **`<tag>`** — exactly one, from the controlled vocabulary in `INDEX.md`:
  `macro` · `rates` · `economics` · `equities` · `crossasset` · `flows` · `factor` · `event`.
  Do not invent a new tag without adding it to the `INDEX.md` table in the same pass.
- **`<issuer>_<topic>`** — short kebab identifiers, e.g. `gs_japan-outlook`,
  `bridgewater_risk-parity`, `aqr_managed-futures`.
- **Move the source PDF alongside the digest and rename it to the same stem**, so the
  pair sorts together. A PDF *export of a digest* (not a source report) gets the
  `.digest.pdf` suffix instead.
- Undated practitioner classics get a year folder with no month (`2013/`).
- Two notes in one series may share a digest when the delta between them *is* the
  content; file it under the later report and leave the earlier source PDF in its own
  month folder. Say so in the digest header and in the `INDEX.md` note.
- Every reference inside a digest (`Source:`, cross-links to sibling digests) is a
  repo-root-relative path — keep them current when anything moves.

If the report is really an academic finance paper, prefer the `/read-to-learn` paper
convention under `knowledge/papers/` instead of duplicating it here.

---

## Principles

- **Honor the format.** Three parts, always, in order: 3–5 sentence STAR summary →
  PEE blocks + bulleted causal chains → 5–10 keywords. The summary covers context,
  methodology, and conclusion; the PEE blocks carry the analytical weight.
- **Leave the library tidy, not just the digest written.** Filing is part of the
  deliverable: create the year/month folder, move the source in, rename it to the
  digest's stem, add the `INDEX.md` row, and check that every path inside the digest
  still resolves. A correct digest dumped at the library root under a vendor filename
  is unfinished work — the next reader finds notes by folder and stem, not by memory.
- **Structure over prose density.** PEE (Point-Evidence-Explanation) per pillar,
  arrow-linked chains (`A → B → C`) for causal reasoning, tables for anything
  tabular (what-to-watch, forecast tables), one bullet per distinct platform
  connection. A dense paragraph is not more rigorous than a scannable one — it is
  just harder to read. If you catch yourself writing a paragraph past ~4 sentences
  with no break, stop and restructure it into blocks/bullets before moving on.
- **Reasoning over recap.** Anyone can restate a report's headline. The value is
  showing *why* the evidence does or doesn't support it — name the load-bearing
  evidence and the weakest link.
- **Path over call.** The house view expires; the method for reaching it doesn't. A
  digest that records the forecast but not how it was built has kept the perishable
  half.
- **Quantities, not adjectives.** Every claim carries its number — estimate, range,
  period, universe, units. "Margins compress" → "gross margin −180 bp by FY27 on the
  base case, −400 bp bear." Reproduce the load-bearing formula rather than describing
  it. Failure test: a sentence that would still be true of a different report on a
  different sector is filler — cut it.
- **Read the conflict of interest.** Industry/sell-side reports often talk their
  book. Note the mandate and whose decision the report is really serving.
- **Connect to the platform every time.** Name what the report validates, challenges,
  or could improve in this repo, and flag contradictions explicitly. A report connected
  to nothing here is off-scope (score Relevance down) or a gap worth flagging.
- **Density over length.** A digest that can't be scanned in a minute has failed.
- **Honest scoring, no gates.** No significance thresholds, no PM review — but say
  plainly when a report is thin, promotional, or regime-narrow.
