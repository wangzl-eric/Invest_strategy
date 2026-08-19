# The Brain — a research second brain

*Created 2026-08-18. Purpose: hold a pool of thoughts in a form that survives the source they came
from, so that high-dimensional reading (reports, papers, books) collapses into low-dimensional,
reusable logic — without ever destroying the original.*

---

## The one rule

**Nothing here replaces its source.** Every atom in this brain is an *additional* view, never a
substitute. The source PDF stays, the source-faithful digest stays, and the atom cites both. If you
ever find yourself deleting an L1 note because "the concept captured it", stop — the compression is
lossy by design and the loss is only acceptable because the original is still there.

## The dimensional ladder

```
L0  the source                    PDF / book / paper                       immutable
L1  source-faithful digest        preserves the AUTHOR'S argument          book_notes/playground/{reports,papers,studies}/
L2  atom                          transferable, source-independent         <- this brain
L3  structure over atoms          families, hubs, threads, contradictions
L4  validated strategy            rigor gates, pool lifecycle              alpha_research/research/
```

L1 answers *what did this author claim, and how well?* L2 answers *what do I now know, and what is it
built from?* They are different questions and both are worth keeping. The ladder is not a pipeline
with a discard step — every level persists, and the links between levels are the point.

## The three atom types

An atom is the smallest unit worth a permanent ID. Three kinds, because forcing them into one schema
distorts all three:

| Type | ID | Answers | Scored on | Lives in |
|---|---|---|---|---|
| **Mechanism** | `IDEA-NNN` | *What could I trade, and who pays?* | economic rationale · durability · testability (3–15) | [`../reports/IDEAS.md`](../reports/IDEAS.md) |
| **Concept** | `CONCEPT-NNN` | *What machinery is that built from?* | status: `stable` / `contested` / `unsettled` | [`concepts/`](concepts/) — one note each |
| **Verdict** | `VERDICT-NNN` | *What did we try, and what happened?* | outcome + what it cost to learn | [`VERDICTS.md`](VERDICTS.md) |

The distinction that matters most: a **mechanism** has a counterparty who must trade, a **concept**
has a definition and a failure boundary, a **verdict** has a date and a body count. "Term premium" is
a concept; "foreign long ends load 3x more on term premium than on the risk-neutral path" is a
mechanism; "VIX Regime rejected, MinBTL 3,968 years" is a verdict.

**Concepts underpin mechanisms; verdicts kill or temper them.** That triangle is the brain's core
structure — a mechanism with no concept beneath it is usually a pattern, and a mechanism that
contradicts a verdict is a mistake you have already paid for once.

## Layout

```
brain/
├── README.md          this file — the architecture
├── INBOX.md           raw thought capture, unpolished, triaged later
├── CONCEPTS.md        generated index over concepts/
├── concepts/          CONCEPT-NNN-<slug>.md, one atom per note
└── VERDICTS.md        append-only log of tested outcomes
../reports/IDEAS.md    the mechanism pool (46 atoms) — deliberately NOT moved
```

**Why `IDEAS.md` is not in here.** It is the oldest and only battle-tested layer: permanent IDs, merge
semantics, independent-arrival evidence, and an enforced integrity checker. 105 digest back-links point
at it. Moving it would buy tidiness and cost the whole citation graph. It is a first-class member of
this brain that happens to live one directory up. The naming is historical debt — `IDEA-NNN` means
*mechanism* — and is not worth a renumbering, since IDs here are permanent by law.

**Why concepts are atomic notes but verdicts are not.** Concepts are the densely cross-linked layer —
each is cited by several mechanisms and several other concepts, so one-note-per-atom is where Obsidian's
graph and backlink pane actually earn their keep. Verdicts are log-shaped: append-only, read
chronologically, rarely cited by each other. A single file suits them and mirrors the
`memory/knowledge/KNOWLEDGE_*.md` structure they were rescued from.

## Laws

1. **IDs are permanent.** `CONCEPT-012` is a handle, not a rank. Re-scoring or re-sorting never
   renumbers. New atoms take the next unused number wherever they land. This law exists because an
   earlier pass renumbered the mechanism pool and silently invalidated every cross-reference in the
   library — see the housekeeping record in `IDEAS.md`.
2. **Every atom cites its L1 source.** No orphan knowledge. If you cannot name where it came from, it
   belongs in `INBOX.md` until you can.
3. **Independent arrival is evidence.** The same concept or mechanism reached from two unrelated
   sources is one atom with two sources, and the arrival itself is recorded. Merges are logged, and
   deliberate non-merges are logged too — a recorded distinction is worth as much as a recorded link.
4. **Testability is a score, never a gate.** An idea that cannot be tested on this platform today
   still belongs in the pool; the gap is recorded and the atom stays.
5. **A contradiction is a finding, not an error to smooth over.** When a concept contradicts a
   mechanism or a verdict, record the contradiction on both ends.
6. **The checkers run automatically.** `python3 scripts/check_brain_integrity.py` plus
   `python3 scripts/check_ideas_integrity.py`, and **both are wired into
   `.pre-commit-config.yaml` as of 2026-08-19** — a commit touching `brain/` or `reports/` is
   blocked when either fails. A green check that asserts nothing is worse than no check: two
   silent-failure bugs were found and fixed in these very scripts on 2026-08-19 (an end-of-line
   anchored regex that made the sortedness test vacuous, and a wikilink resolver that picked one
   of 27 `[[README]]` candidates). This brain lost five layers to unenforced conventions; law 6
   is now a hook, not a habit.

## How something enters

```
   a thought while reading, walking, or arguing
        │
        ▼
   INBOX.md ──── triage ────► atom (mechanism / concept / verdict)   ·or·  dropped, with a reason
        ▲                            │
        │                            ▼
   a source you read           linked to its L1 note and to related atoms
   (/read-to-learn,                  │
    /read-industrial-report)         ▼
        │                     L4 validation if it is tradable
        └────► L1 digest ─────► harvest ─► atom
```

Two intakes, deliberately. Source-derived atoms come from the reading skills, which already produce
L1 digests — and the report path is already automated in
[`scripts/digest_watcher.sh`](../../../scripts/digest_watcher.sh), which watches
`~/Dropbox/report-inbox`. **Your own thoughts come through capture** — unpolished, dated, un-scored.
That path exists because the most valuable thought is often the one you had *between* sources, and it
evaporates if the only way to record it is to first decide what type of atom it is.

**Captures land in `~/Dropbox/thought-inbox/`, outside this repo** — one immutable file each, no links,
no IDs. The repo is public, so raw thinking must not become a public commit. The format and its rules
are in [`CAPTURE.md`](CAPTURE.md); validate with
`python3 scripts/check_brain_integrity.py --captures`. [`INBOX.md`](INBOX.md) keeps the triage laws
and the Dropped ledger.

## Status of the build

| Layer | State |
|---|---|
| Mechanisms | **46 atoms**, complete for the 10 report digests · no atoms yet from papers or books |
| Concepts | **10 seeded** from the paper notes and the rescued KB · the layer is new |
| Verdicts | **13 records**, rescued from `memory/knowledge/` before further rot |
| Inbox | live, empty |

**Not yet harvested** — the two biggest untapped sources, each deserving its own pass:
- `studies/*/study_hypotheses.md` — 2,409 lines across 4 books, per-study silos, no atoms extracted
- `papers/paper_notes_*.md` — 46 notes stopping at L1; their mechanisms and concepts are not pooled

## Retired

- `memory/knowledge/KNOWLEDGE_{EQUITY,FX,MACRO,VOL}.md` — the verdict content is rescued into
  `VERDICTS.md`; the market-fact and paper content is superseded by `concepts/` and `../papers/`.
  These went stale because their documented intake (`/capture-finding`, `/learn-verdict`,
  `/learn-source`) was **never installed** — only `read-to-learn` exists. Kept read-only as an archive.
- `playground/fields/` — a 9-field taxonomy scaffold that was never populated. Topic organisation is
  handled by concept `domain:` frontmatter and the mechanism families instead.
- `alpha_research/research/external_ideas.md` — frozen 2026-03-13; its transferable content belongs in
  the atom layer.
