#!/usr/bin/env python3
"""Triage captured thoughts into the brain's atom layers.

    python3 scripts/triage_inbox.py list
    python3 scripts/triage_inbox.py show   <file>
    python3 scripts/triage_inbox.py drop   <file> --reason "..."
    python3 scripts/triage_inbox.py promote <file> --to concept  --slug <slug> --domain <d> --status <s>
    python3 scripts/triage_inbox.py promote <file> --to verdict  --slug <slug> --domain <d> --outcome <o>
    python3 scripts/triage_inbox.py promote <file> --to mechanism --slug <slug> --kind <k> \
        --econ N --dur N --test N --source "<digest path>" \
        --related "IDEA-003=why it relates|how it relates back" ...

Why this exists: promotion is the ONLY place an ID is minted, and it is the one operation
that must write BOTH sides of a reciprocal edge, insert the summary-table row in sorted
position, and regenerate the concept index. A phone cannot do that (see brain/CAPTURE.md);
this runs where the checkers run.

Every write is transactional: the files it touches are snapshotted, the edit is applied,
BOTH checkers run, and on any failure everything is rolled back. It refuses to leave the
pool red.
"""
import argparse
import datetime as dt
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
BRAIN = ROOT / "book_notes/playground/brain"
CONCEPTS = BRAIN / "concepts"
VERDICTS = BRAIN / "VERDICTS.md"
IDEAS = ROOT / "book_notes/playground/reports/IDEAS.md"
CAPTURES = pathlib.Path.home() / "Dropbox/thought-inbox"
ARCHIVE = pathlib.Path.home() / "Dropbox/thought-inbox-archive"

CHECKERS = (
    [sys.executable, str(ROOT / "scripts/check_ideas_integrity.py")],
    [sys.executable, str(ROOT / "scripts/check_brain_integrity.py")],
)


# ---------------------------------------------------------------- helpers
def frontmatter(text):
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    out = {}
    for line in text[4:end].split("\n"):
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


def body_of(text):
    if text.startswith("---"):
        end = text.find("\n---", 4)
        if end >= 0:
            return text[end + 4 :].strip()
    return text.strip()


def captures():
    if not CAPTURES.exists():
        return []
    out = []
    for f in sorted(CAPTURES.glob("*.md")):
        if f.name == "README.md":
            continue
        fm = frontmatter(f.read_text(encoding="utf-8"))
        out.append((f, fm))
    return out


def next_id(kind):
    if kind == "concept":
        used = [int(p.name[8:11]) for p in CONCEPTS.glob("CONCEPT-*.md")]
        return f"CONCEPT-{max(used, default=0) + 1:03d}"
    if kind == "verdict":
        used = [
            int(x)
            for x in re.findall(
                r"^### VERDICT-(\d{3}) · ", VERDICTS.read_text(encoding="utf-8"), re.M
            )
        ]
        return f"VERDICT-{max(used, default=0) + 1:03d}"
    used = [
        int(x)
        for x in re.findall(
            r"^### IDEA-(\d{3}) · ", IDEAS.read_text(encoding="utf-8"), re.M
        )
    ]
    return f"IDEA-{max(used, default=0) + 1:03d}"


class Transaction:
    """Snapshot -> apply -> verify -> rollback on red."""

    def __init__(self, paths):
        self.paths = [pathlib.Path(p) for p in paths]
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="triage-"))
        self.saved = {}

    def __enter__(self):
        for p in self.paths:
            if p.exists():
                dest = self.tmp / p.name
                shutil.copy2(p, dest)
                self.saved[p] = dest
        return self

    def rollback(self):
        for p, saved in self.saved.items():
            shutil.copy2(saved, p)
        for p in self.paths:
            if p not in self.saved and p.exists():
                p.unlink()

    def verify(self):
        # regenerate the concept index first so it can never be stale at check time
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/check_brain_integrity.py"),
                "--reindex",
            ],
            capture_output=True,
        )
        for cmd in CHECKERS:
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                return False, r.stdout + r.stderr
        return True, ""

    def __exit__(self, *exc):
        shutil.rmtree(self.tmp, ignore_errors=True)
        return False


def finish(tx, cap, status):
    ok, out = tx.verify()
    if not ok:
        tx.rollback()
        print("REFUSING TO WRITE — checkers went red, everything rolled back:\n")
        print(out)
        return 1
    dest = ARCHIVE / ("promoted" if status == "triaged" else "dropped")
    dest.mkdir(parents=True, exist_ok=True)
    if cap and cap.exists():
        shutil.move(str(cap), str(dest / cap.name))
    print(out.strip() or "checkers green")
    return 0


# ---------------------------------------------------------------- commands
def cmd_list(_a):
    rows = captures()
    if not rows:
        print(f"no captures in {CAPTURES}")
        return 0
    today = dt.date.today()
    print(f"{len(rows)} capture(s) in {CAPTURES}\n")
    for f, fm in rows:
        age = ""
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", f.name)
        if m:
            age = f"{(today - dt.date(*map(int, m.groups()))).days}d"
        first = next(
            (
                ln
                for ln in body_of(f.read_text(encoding="utf-8")).split("\n")
                if ln.strip()
            ),
            "",
        )
        print(f"  [{fm.get('status','?'):7}] {age:>5}  {f.name}")
        print(f"            {first[:96]}")
        if fm.get("refs"):
            print(f"            refs: {fm['refs']}")
    return 0


def cmd_show(a):
    f = CAPTURES / a.file
    if not f.exists():
        print(f"no such capture: {f}")
        return 1
    print(f.read_text(encoding="utf-8"))
    return 0


def cmd_drop(a):
    f = CAPTURES / a.file
    if not f.exists():
        print(f"no such capture: {f}")
        return 1
    inbox = BRAIN / "INBOX.md"
    with Transaction([inbox]) as tx:
        text = inbox.read_text(encoding="utf-8")
        first = next(
            (
                ln
                for ln in body_of(f.read_text(encoding="utf-8")).split("\n")
                if ln.strip()
            ),
            f.name,
        )
        row = f"| {dt.date.today().isoformat()} | {first[:70]} | {a.reason} |\n"
        text = (
            text.replace("| — | — | — |\n", "| — | — | — |\n" + row, 1)
            if "| — | — | — |" in text
            else text + row
        )
        inbox.write_text(text, encoding="utf-8")
        return finish(tx, f, "dropped")


def cmd_promote(a):
    f = CAPTURES / a.file
    if not f.exists():
        print(f"no such capture: {f}")
        return 1
    text = f.read_text(encoding="utf-8")
    body = body_of(text)
    fm = frontmatter(text)

    if a.to == "concept":
        cid = next_id("concept")
        note = CONCEPTS / f"{cid}-{a.slug}.md"
        with Transaction([note, BRAIN / "CONCEPTS.md"]) as tx:
            note.write_text(
                f"---\ntype: concept\nid: {cid}\nslug: {a.slug}\ndomain: {a.domain}\n"
                f"status: {a.status}\nsources: 0\n---\n\n"
                f"# {cid} · {a.slug.replace('-', ' ')}\n\n"
                f"**Definition.** TODO — one precise paragraph.\n\n"
                f"## From the capture\n\n> {body}\n\n"
                f"*Captured {fm.get('captured','?')}, promoted {dt.date.today().isoformat()}.*\n\n"
                f"## The math\n\nTODO\n\n## Where it fails\n\nTODO\n\n"
                f"## What it underpins\n\nTODO\n\n## Sources\n\nTODO\n",
                encoding="utf-8",
            )
            print(f"created {note.relative_to(ROOT)}")
            return finish(tx, f, "triaged")

    if a.to == "verdict":
        vid = next_id("verdict")
        with Transaction([VERDICTS]) as tx:
            t = VERDICTS.read_text(encoding="utf-8")
            block = (
                f'\n<a id="{vid.lower()}"></a>\n### {vid} · {a.slug}\n\n'
                f"`{a.domain}` · {dt.date.today().isoformat()} · **{a.outcome}**\n\n"
                f"**What happened.** {body}\n\n"
                f"**Transferable lesson.** TODO\n\n**Bears on.** TODO\n"
            )
            marker = "\n---\n\n## Open loops"
            t = t.replace(marker, block + marker, 1) if marker in t else t + block
            VERDICTS.write_text(t, encoding="utf-8")
            print(f"appended {vid} to VERDICTS.md")
            return finish(tx, f, "triaged")

    # ---- mechanism: the dangerous one
    mid = next_id("mechanism")
    nnn = mid[-3:]
    total = a.econ + a.dur + a.test
    fwd, rev = [], []
    for spec in a.related or []:
        tgt, _, why = spec.partition("=")
        f_why, _, r_why = why.partition("|")
        tgt = tgt.strip()
        if not re.fullmatch(r"IDEA-\d{3}", tgt):
            print(f"--related target must be IDEA-NNN, got {tgt!r}")
            return 1
        fwd.append(f"[{tgt}](#idea-{tgt[-3:]}) {f_why.strip()}")
        rev.append((tgt[-3:], f"[{mid}](#idea-{nnn}) {(r_why or f_why).strip()}"))

    with Transaction([IDEAS]) as tx:
        t = IDEAS.read_text(encoding="utf-8")

        # 1. summary-table row, inserted in sorted (descending total) position
        row = (
            f"| [{nnn}](#idea-{nnn}) | `{a.kind}` | **{a.slug}** | "
            f"{a.econ} | {a.dur} | {a.test} | **{total}** |"
        )
        lines = t.split("\n")
        placed = False
        for i, ln in enumerate(lines):
            m = re.match(r"\| \[\d{3}\]\(#idea-\d{3}\) \|.*\| \*\*(\d+)\*\* \|$", ln)
            if m and int(m.group(1)) < total:
                lines.insert(i, row)
                placed = True
                break
        if not placed:
            for i in range(len(lines) - 1, -1, -1):
                if re.match(r"\| \[\d{3}\]\(#idea-\d{3}\) \|", lines[i]):
                    lines.insert(i + 1, row)
                    placed = True
                    break
        if not placed:
            print("could not locate the summary table")
            return 1
        t = "\n".join(lines)

        # 2. the entry itself, appended to the end of the entries section
        entry = (
            f'\n<a id="idea-{nnn}"></a>\n### {mid} · {a.slug}\n\n'
            f"`{a.kind}` · **status: unvalidated** · **{total}/15**\n"
            f"*source:* {a.source}\n"
            f"*applies to:* TODO\n<!-- edges -->\n"
            + (f"*related:* {' · '.join(fwd)}\n" if fwd else "")
            + f"\n**Statement.** {body}\n\n"
            f"**Mechanism — who pays, why it persists.** TODO\n\n"
            f"| | | |\n|---|:--:|---|\n"
            f"| Economic rationale | **{a.econ}/5** | TODO |\n"
            f"| Durability | **{a.dur}/5** | TODO |\n"
            f"| Testability | **{a.test}/5** | TODO |\n\n"
            f"**Evidence so far.** TODO\n\n**To test later.** TODO\n"
        )
        marker = "\n---\n\n## Merges and independent arrivals"
        t = t.replace(marker, entry + marker, 1) if marker in t else t + entry

        # 3. BOTH sides of every reciprocal edge
        for tgt_nnn, back in rev:
            # Line-based on purpose: a DOTALL regex here swallowed the rest of the file
            # and appended the back-edge to EOF instead of the target's *related:* line.
            lines = t.split("\n")
            try:
                start = next(
                    i for i, ln in enumerate(lines) if f'<a id="idea-{tgt_nnn}">' in ln
                )
            except StopIteration:
                print(f"IDEA-{tgt_nnn} not found — cannot reciprocate")
                return 1
            rel_at = next(
                (
                    i
                    for i in range(start, min(start + 12, len(lines)))
                    if lines[i].startswith("*related:*")
                ),
                None,
            )
            if rel_at is None:
                print(f"IDEA-{tgt_nnn} has no *related:* line — cannot reciprocate")
                return 1
            lines[rel_at] = lines[rel_at].rstrip() + f" · {back}"
            t = "\n".join(lines)

        IDEAS.write_text(t, encoding="utf-8")
        print(f"inserted {mid} ({total}/15) with {len(rev)} reciprocal edge(s)")
        return finish(tx, f, "triaged")


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    s = sub.add_parser("show")
    s.add_argument("file")
    s.set_defaults(fn=cmd_show)
    s = sub.add_parser("drop")
    s.add_argument("file")
    s.add_argument("--reason", required=True)
    s.set_defaults(fn=cmd_drop)
    s = sub.add_parser("promote")
    s.add_argument("file")
    s.add_argument("--to", required=True, choices=["concept", "verdict", "mechanism"])
    s.add_argument("--slug", required=True)
    s.add_argument("--domain", default="method")
    s.add_argument(
        "--status", default="unsettled", choices=["stable", "contested", "unsettled"]
    )
    s.add_argument("--outcome", default="REJECTED")
    s.add_argument(
        "--kind",
        default="method",
        choices=["signal", "method", "regime", "risk", "structure"],
    )
    s.add_argument("--econ", type=int, default=3)
    s.add_argument("--dur", type=int, default=3)
    s.add_argument("--test", type=int, default=3)
    s.add_argument("--source", default="TODO")
    s.add_argument("--related", action="append")
    s.set_defaults(fn=cmd_promote)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
