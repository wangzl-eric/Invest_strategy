# The capture contract

*The file format is the deliverable. It outlives any client — a Shortcut, a bot, a web page,
or a native app all just write this. Adopt it by hand today; automate the writing later.*

---

## Where captures live: NOT in this repo

```
~/Dropbox/thought-inbox/            <- captures land here (transport)
~/Dropbox/thought-inbox-archive/    <- promoted/ and dropped/ move here after triage
knowledge/brain/        <- only PROMOTED atoms enter the vault
```

**Raw captures are deliberately outside the git repo.** `github.com/wangzl-eric/Invest_strategy`
is **public** — the same reason `.gitignore` excludes the licensed sell-side PDFs. A half-formed
thought about a position you are considering should not become a public commit, and a push is
irreversible in a way a local file is not. Dropbox supplies the version history instead.

This also mirrors what [`scripts/digest_watcher.sh`](../../scripts/digest_watcher.sh) already
does for reports (`INBOX="$HOME/Dropbox/report-inbox"`), so both intakes share one shape.

## The two laws

1. **One immutable file per capture.** Never edit an existing capture from any device. Two
   writers can then never collide — there is nothing to merge, only files to add. This is the
   entire sync design; everything else follows from it.
2. **A capture may not contain a link.** No `[[wikilink]]`, no `](`, no heading. Relating an
   idea to the pool means writing *both* sides of a reciprocal edge inside a 1,485-line file
   that only [`check_ideas_integrity.py`](../../scripts/check_ideas_integrity.py) can
   validate. A phone cannot do that safely, so it is not permitted to try.

## The format

Filename — `YYYY-MM-DD-HHMM-short-slug.md`:

```markdown
---
type: capture
captured: 2026-08-19T22:41:00+09:00   # ISO 8601, local time with offset
status: open                          # open | triaged | dropped
source: shortcut                      # shortcut | voice | share | manual
lens: vol                             # OPTIONAL — must be a domain already in concepts/
refs: [IDEA-003, CONCEPT-002]         # OPTIONAL — bare IDs, a HINT for triage, never links
---

The thought, as thought. Fragments are fine. Write it wrong rather than not at all.

?? the open question, if you have one
```

Only `type`, `captured` and `status` are required. **`refs` is a hint, not an edge** — triage
decides whether it becomes a real relation, and triage writes both sides.

## Fields

| Field | Required | Rule |
|---|---|---|
| `type` | yes | always `capture` |
| `captured` | yes | ISO 8601 with offset. The *thinking* time, not the filing time — see [[CONCEPT-006-point-in-time-information]] |
| `status` | yes | `open` → `triaged` or `dropped`; set by triage on the Mac, not by the phone |
| `source` | no | `shortcut` · `voice` · `share` · `manual` |
| `lens` | no | must already exist as a `domain:` in `brain/concepts/` — no new vocabulary from a phone |
| `refs` | no | bare IDs only (`IDEA-NNN`, `CONCEPT-NNN`, `VERDICT-NNN`), each must resolve |

## Validate

```bash
python3 scripts/check_brain_integrity.py --captures
```

Checks filename shape, required frontmatter, `status`/`source` enums, that `lens` matches a real
concept domain, that every `refs` ID resolves, and that the body contains no links. Exits 0 when
the transport directory is absent, so it is safe in any hook.

## Triage

Captures leave by one of four doors, exactly as [`INBOX.md`](INBOX.md) specifies — and the fourth
door is real. A dropped thought moves to `thought-inbox-archive/dropped/` **with its reason
recorded**; a thought that silently vanishes will be re-had at full cost in six months.

Triage happens where the checkers run. **Nothing mints an ID except the Mac.**
