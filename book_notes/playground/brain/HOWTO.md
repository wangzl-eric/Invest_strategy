# How to actually use this

*Two intakes, one triage, one rule. Everything else is optional.*

**The rule:** capture is not classification. Never decide what a thought *is* while having it.

---

## Daily — 30 seconds, no thinking

A thought arrives. Write one file into `~/Dropbox/thought-inbox/`:

```
~/Dropbox/thought-inbox/2026-08-20-1412-vol-carry-is-fx-carry.md
```

```markdown
---
type: capture
captured: 2026-08-20T14:12:00+09:00
status: open
source: manual
---

Vol carry and FX carry may be the same short-convexity trade wearing two labels.
If so, sizing them independently double-counts one exposure.

?? does our review battery treat them as independent sleeves
```

Only `type`, `captured`, `status` are required. No links, no IDs, no tags — those come later, on purpose. Fragments are fine. **Write it wrong rather than not at all.**

Optional if it costs you nothing: `lens: vol` (must be a domain already in `concepts/`) and `refs: [IDEA-003]` (a *hint* for triage, never an edge).

Check anything sitting there is well-formed:

```bash
python3 scripts/check_brain_integrity.py --captures
```

## When you read a report — drop and sweep

```bash
cp ~/Downloads/gs_note.pdf ~/Dropbox/report-inbox/
bash scripts/digest_watcher.sh          # no flags = process the inbox
```

Produces a full digest under `../reports/<year>/<month>/`, files the source PDF beside it, harvests ideas into the pool, and runs the integrity checker afterwards. `--status` shows queue and health. (`--install` for launchd is currently blocked by macOS TCC because the repo sits under `~/Desktop` — running it by hand is the workaround, and it loses nothing but automatic triggering.)

## When you read a paper or a book chapter

Use the reading skills — they produce the **L1 source-faithful layer**, not atoms:

```
/read-to-learn <paper or chapter>        → papers/ or studies/
/read-industrial-report <report>          → reports/ (same as the watcher path)
```

Atoms come later, from harvest. L1 is never replaced.

---

## Weekly — the triage sweep, ~20 minutes

This is the only ritual that matters. Without it the inbox becomes the sixth dead layer.

```bash
python3 scripts/triage_inbox.py list           # oldest first, with age
python3 scripts/triage_inbox.py show <file>
```

Then every capture leaves by one of four doors:

| It is… | Door |
|---|---|
| a definition, identity, or measurement discipline | **concept** |
| something with a counterparty who must trade, and a position you'd put on | **mechanism** |
| something tried, with an outcome | **verdict** |
| not surviving contact | **drop — with the reason** |

```bash
# concept
python3 scripts/triage_inbox.py promote <file> --to concept \
    --slug carry-is-short-convexity --domain vol --status contested

# verdict
python3 scripts/triage_inbox.py promote <file> --to verdict \
    --slug some-test --domain equity --outcome REJECTED

# mechanism — you supply judgement, the tool guarantees invariants
python3 scripts/triage_inbox.py promote <file> --to mechanism \
    --slug issuance-mix-locates-the-loser --kind signal \
    --econ 5 --dur 5 --test 3 --source "2026/04 · macro_gs_jpy-macro-trading_2026-04-07" \
    --related "IDEA-003=the moment mismatch it inherits|the carry expression of the same convexity"

# drop — the fourth door is real
python3 scripts/triage_inbox.py drop <file> --reason "already covered by CONCEPT-002"
```

**Record the drop.** A thought you rejected and can explain is knowledge; one that silently vanished will be re-had, at full cost, in six months.

**Not sure?** Leave it in the inbox. A permanent resident is allowed if you say why. Unsure is not a reason to force an atom — a wrong atom costs more than a late one.

### What promotion guarantees

`triage_inbox.py` is the **only** place an ID is minted. On a mechanism it also inserts the summary-table row in correct descending-total position and writes **both sides** of every reciprocal edge. Every write is transactional: snapshot → apply → reindex → run both checkers → **roll back completely on red**. It will not leave the pool broken.

---

## Before you build anything — read the pool

The system's weakest link is not capture, it is that nothing forces the pool to be *read*. Before writing a proposal or running a manifest:

```bash
grep -n "<your topic>" book_notes/playground/brain/VERDICTS.md
```

Two things it will tell you that are easy to forget:

- **Check the data first.** 5 of 13 recorded verdicts died on data reach, not on economics — a missing series, a sector classification, an account permission. Cost the data before costing the research.
- **An overlay must add alpha, not subtract risk.** Both properly-tested strategies died that way. Benchmark against equal-weight *and* a trailing-vol baseline from round one.

Then read [`CONCEPTS.md`](CONCEPTS.md) for the machinery, and the six families in
[`IDEAS.md`](../reports/IDEAS.md#how-the-pool-interconnects) for mechanisms.

---

## Safety rails you don't have to think about

- Both checkers are **pre-commit hooks** — a commit touching `brain/` or `reports/` is blocked if either fails.
- Captures live **outside the repo** (`~/Dropbox/`), because this repo is public.
- A capture **cannot contain a link or an ID**, so no capture device can corrupt the pool.
- Run them by hand any time:

```bash
python3 scripts/check_ideas_integrity.py
python3 scripts/check_brain_integrity.py --captures
```

---

## Honest status

Working: report intake, triage, promotion, enforcement.
Manual for now: writing the capture file (a Shortcut would make it one tap — not built).
The real gap: **the pool is ~3.5% populated.** 46 paper notes and 2,409 lines of book hypotheses have produced zero atoms. Until they are harvested, "read the pool before you build" pays less than it should.
