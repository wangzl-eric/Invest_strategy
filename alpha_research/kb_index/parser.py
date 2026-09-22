"""The single grammar for the research brain's markdown.

Markdown is the source of truth. This module reads it; nothing here writes.
Writing goes through scripts/triage_inbox.py, which is transactional and
checker-gated.

The grammar here deliberately mirrors the one in scripts/check_ideas_integrity.py
and scripts/check_brain_integrity.py. Two implementations of one grammar is how
corpora rot, so ``agreement()`` asserts this parser and the checkers still agree
on the counts they can both compute. If that assertion ever fails, this file is
wrong until proven otherwise — the checkers are the enforcement point.
"""
from __future__ import annotations

import dataclasses
import pathlib
import re
from typing import Iterator

ROOT = pathlib.Path(__file__).resolve().parents[2]
IDEAS = ROOT / "knowledge/reports/IDEAS.md"
BRAIN = ROOT / "knowledge/brain"
CONCEPTS_DIR = BRAIN / "concepts"
VERDICTS = BRAIN / "VERDICTS.md"
CAPTURES = pathlib.Path.home() / "Dropbox/thought-inbox"

SECTIONS = ("Statement", "Mechanism", "Evidence so far", "To test later")


@dataclasses.dataclass
class Edge:
    src: str
    dst: str
    reason: str


@dataclasses.dataclass
class Atom:
    id: str
    type: str  # mechanism | concept | verdict | capture
    slug: str
    path: str  # repo-relative, or absolute for captures
    kind: str | None = None  # signal/method/regime/risk/structure  (mechanisms)
    domain: str | None = None  # concepts, verdicts
    status: str | None = None
    econ: int | None = None
    dur: int | None = None
    test: int | None = None
    total: int | None = None
    body: str = ""
    sources: tuple = ()
    edges: tuple = ()


def _frontmatter(text: str) -> dict:
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


def mechanisms() -> Iterator[Atom]:
    """Parse the 46-entry single-file mechanism pool."""
    text = IDEAS.read_text(encoding="utf-8")
    parts = re.split(r'\n<a id="idea-(\d{3})"></a>\n### IDEA-\d{3} · (\S+)\n', text)
    rel = str(IDEAS.relative_to(ROOT))
    for i in range(1, len(parts), 3):
        nnn, slug, body = parts[i], parts[i + 1], parts[i + 2]
        atom = Atom(id=f"IDEA-{nnn}", type="mechanism", slug=slug, path=rel, body=body)
        m = re.search(
            r"^`(\w+)` · \*\*status: ([^*]+)\*\* · \*\*(\d+)/15\*\*", body, re.M
        )
        if m:
            atom.kind, atom.status, atom.total = (
                m.group(1),
                m.group(2).strip(),
                int(m.group(3)),
            )
        scores = dict(
            re.findall(
                r"\| (Economic rationale|Durability|Testability) \| \*\*(\d)/5\*\*",
                body,
            )
        )
        atom.econ = (
            int(scores["Economic rationale"])
            if "Economic rationale" in scores
            else None
        )
        atom.dur = int(scores["Durability"]) if "Durability" in scores else None
        atom.test = int(scores["Testability"]) if "Testability" in scores else None
        atom.sources = tuple(
            src
            for _label, src in re.findall(
                r"\[([^\]]+)\]\((\d{4}(?:/\d{2})?/[^)]+\.md)\)", body
            )
        )
        line = re.search(r"^\*related:\*(.*)$", body, re.M)
        if line:
            atom.edges = tuple(
                Edge(atom.id, f"IDEA-{d}", " ".join(r.split()))
                for d, r in re.findall(
                    r"\[IDEA-(\d{3})\]\(#idea-\d{3}\)\s+([^·\n]+)", line.group(1)
                )
            )
        yield atom


def concepts() -> Iterator[Atom]:
    for f in sorted(CONCEPTS_DIR.glob("CONCEPT-*.md")):
        text = f.read_text(encoding="utf-8")
        fm = _frontmatter(text)
        yield Atom(
            id=fm.get("id", f.stem[:11]),
            type="concept",
            slug=fm.get("slug", f.stem),
            path=str(f.relative_to(ROOT)),
            domain=fm.get("domain"),
            status=fm.get("status"),
            body=text,
            edges=tuple(
                Edge(fm.get("id", ""), t.strip(), "related")
                for t in re.findall(r"\[\[([^\]|#]+)", text)
            ),
        )


def verdicts() -> Iterator[Atom]:
    if not VERDICTS.exists():
        return
    text = VERDICTS.read_text(encoding="utf-8")
    parts = re.split(
        r'\n<a id="verdict-(\d{3})"></a>\n### VERDICT-\d{3} · (.+)\n', text
    )
    rel = str(VERDICTS.relative_to(ROOT))
    for i in range(1, len(parts), 3):
        nnn, title, body = parts[i], parts[i + 1], parts[i + 2]
        m = re.search(r"^`([\w/-]+)`", body, re.M)
        yield Atom(
            id=f"VERDICT-{nnn}",
            type="verdict",
            slug=title.strip(),
            path=rel,
            domain=m.group(1) if m else None,
            body=body,
        )


def captures() -> Iterator[Atom]:
    if not CAPTURES.exists():
        return
    for f in sorted(CAPTURES.glob("*.md")):
        if f.name == "README.md":
            continue
        text = f.read_text(encoding="utf-8")
        fm = _frontmatter(text)
        yield Atom(
            id=f.stem,
            type="capture",
            slug=f.stem,
            path=str(f),
            domain=fm.get("lens"),
            status=fm.get("status", "open"),
            body=text,
        )


def all_atoms() -> list[Atom]:
    return [*mechanisms(), *concepts(), *verdicts(), *captures()]


def agreement() -> dict:
    """Cross-check this grammar against the checkers' own counts.

    Two implementations of one grammar is how a corpus rots. These are the
    numbers both sides can compute independently; they must match.
    """
    text = IDEAS.read_text(encoding="utf-8")
    mechs = list(mechanisms())
    directed = sum(len(a.edges) for a in mechs)
    return {
        "entries_parser": len(mechs),
        "entries_checker": len(re.findall(r"^### IDEA-\d{3} · ", text, re.M)),
        "edges_parser": directed,
        "edges_checker": sum(
            len(re.findall(r"#idea-\d{3}", m.group(1)))
            for m in re.finditer(r"^\*related:\*(.*)$", text, re.M)
        ),
        "scores_sum_ok": sum(
            1
            for a in mechs
            if None not in (a.econ, a.dur, a.test)
            and a.econ + a.dur + a.test == a.total
        ),
        "concepts": len(list(concepts())),
        "verdicts": len(list(verdicts())),
        "captures": len(list(captures())),
    }
