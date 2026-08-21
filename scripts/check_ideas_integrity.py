#!/usr/bin/env python3
"""Integrity check for the reports idea pool.

Run after any pass that touches book_notes/playground/reports/IDEAS.md.

    python3 scripts/check_ideas_integrity.py

Why this exists: a re-digest re-scores ideas, which re-sorts them. An earlier
version of the skill told the agent to RENUMBER after sorting, which silently
invalidates every `IDEA-0NN` cross-reference in every digest. IDs are now
permanent and rank is display-only; this script enforces that and the other
invariants the pool depends on.
"""
import pathlib
import re
import sys

LIB = pathlib.Path(__file__).resolve().parent.parent / "book_notes/playground/reports"
IDEAS = LIB / "IDEAS.md"


def main() -> int:
    if not IDEAS.exists():
        print(f"FAIL  {IDEAS} not found")
        return 1
    text = IDEAS.read_text(encoding="utf-8")
    problems = []

    entries = re.findall(r"^### (IDEA-\d{3}) · (\S+)", text, re.M)
    ids = [i for i, _ in entries]
    slugs = [s for _, s in entries]

    dupe_ids = {i for i in ids if ids.count(i) > 1}
    if dupe_ids:
        problems.append(f"duplicate IDs: {sorted(dupe_ids)}")
    dupe_slugs = {s for s in slugs if slugs.count(s) > 1}
    if dupe_slugs:
        problems.append(f"duplicate slugs: {sorted(dupe_slugs)}")

    anchors = set(re.findall(r'<a id="(idea-\d+)">', text))
    for i in ids:
        if i.lower() not in anchors:
            problems.append(f"{i} has no anchor")

    table = set(re.findall(r"\| \[(\d{3})\]\(#idea-\d+\)", text))
    if table != {i[-3:] for i in ids}:
        problems.append(
            f"summary table ({len(table)}) does not match entries ({len(ids)})"
        )

    totals = [int(x) for x in re.findall(r"\| \*\*(\d+)\*\* \|$", text, re.M)]
    # A regex that matches nothing makes the sortedness test vacuously true. This pattern
    # is anchored to end-of-line, so adding any column AFTER Total silently disabled the
    # assertion below (verified 2026-08-18: mutating the table dropped 46 totals to 0 and
    # the sortedness check still passed). Count first, then compare.
    if not ids:
        problems.append(
            "no idea entries parsed — the '### IDEA-NNN ·' pattern matched nothing"
        )
    if len(totals) != len(ids):
        problems.append(
            f"summary table: matched {len(totals)} totals for {len(ids)} ideas — the Total "
            "column regex is end-of-line anchored; a column added after Total breaks it"
        )
    if totals != sorted(totals, reverse=True):
        problems.append("summary table is not sorted by total, descending")

    # every IDEA-NNN referenced anywhere in the library must resolve
    known = set(ids)
    for f in sorted(LIB.rglob("*.md")):
        for m in re.finditer(r"IDEA-\d{3}", f.read_text(encoding="utf-8")):
            if m.group(0) not in known:
                problems.append(f"{f.relative_to(LIB)} references unknown {m.group(0)}")

    # a cited ID must also MATCH the slug the sentence describes. Checking only
    # that an ID resolves let nine mis-pointed references survive two passes: the
    # 2026-08-11 repair claimed a clean slug-vs-ID check while IDEA-005/006 were
    # still transposed throughout the prose. Where a canonical slug appears on the
    # same line as an ID, they must agree.
    slug_of = dict(entries)
    id_of_slug = {s: i for i, s in entries}
    for f in sorted(LIB.rglob("*.md")):
        for lineno, line in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
            if line.startswith("### IDEA-"):
                continue
            for slug, sid in id_of_slug.items():
                pos = line.find(slug)
                if pos < 0:
                    continue
                before = [
                    m for m in re.finditer(r"IDEA-\d{3}", line) if m.start() < pos
                ]
                if before and before[-1].group(0) != sid:
                    problems.append(
                        f"{f.relative_to(LIB)}:{lineno} cites {before[-1].group(0)} "
                        f"but slug '{slug}' is {sid}"
                    )

    # anchor links must point at their own id: [IDEA-014](#idea-014), never #idea-015
    for cited, anchor in re.findall(r"\[IDEA-(\d{3})\]\([^)]*#idea-(\d+)\)", text):
        if cited != anchor:
            problems.append(f"link [IDEA-{cited}] points at #idea-{anchor}")

    # *related:* edges must be reciprocal, so every relation is navigable both ways
    rel = {}
    for chunk in re.split(r"^### IDEA-", text, flags=re.M)[1:]:
        nnn = chunk[:3]
        m = re.search(r"^\*related:\*(.*)$", chunk, re.M)
        rel[nnn] = set(re.findall(r"#idea-(\d{3})", m.group(1))) if m else set()
    for src, targets in rel.items():
        for tgt in targets:
            if src not in rel.get(tgt, set()):
                problems.append(f"IDEA-{src} -> IDEA-{tgt} is not reciprocated")

    # every relative link in the library must resolve (file, and anchor if given)
    anchor_ids = {f"idea-{i[-3:]}" for i in ids}
    for f in sorted(LIB.rglob("*.md")):
        for lineno, line in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
            for _label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", line):
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                path, _, frag = target.partition("#")
                if path:
                    dest = (f.parent / path).resolve()
                    if not dest.exists():
                        problems.append(
                            f"{f.relative_to(LIB)}:{lineno} dead link {target}"
                        )
                        continue
                    if frag and dest.name != "IDEAS.md":
                        continue
                if frag.startswith("idea-") and frag not in anchor_ids:
                    problems.append(
                        f"{f.relative_to(LIB)}:{lineno} dead anchor {target}"
                    )

    # The summary table must AGREE with the entries, not merely be sorted and complete.
    # Verified 2026-08-21: mutating a row's kind, slug case and component scores to
    # 1|9|4 (which do not sum to its stated 14) passed this checker with exit 0, because
    # only the ID (line 45) and the Total (line 51) were ever read. The table is what a
    # reader scans; a table that disagrees with its entries is a silent lie.
    entry_meta = {}
    for block in re.split(r"^### ", text, flags=re.M)[1:]:
        head = block.split("\n", 1)[0]
        if not head.startswith("IDEA-"):
            continue
        eid = head.split(" ")[0]
        kind = re.search(r"^`(\w+)` · \*\*status:", block, re.M)
        parts = re.findall(r"\| \*\*([1-5])/5\*\* \|", block)
        stated = re.search(r"\*\*(\d+)/15\*\*", block)
        entry_meta[eid] = {
            "kind": kind.group(1) if kind else None,
            "scores": [int(x) for x in parts] if len(parts) == 3 else None,
            "total": int(stated.group(1)) if stated else None,
        }

    row_re = re.compile(
        r"^\| \[(\d{3})\]\(#idea-\d{3}\) \| `(\w+)` \| \*\*(\S+)\*\* \| "
        r"(\d) \| (\d) \| (\d) \| \*\*(\d+)\*\* \|$",
        re.M,
    )
    seen_rows = set()
    for nnn, kind, slug, e, d, tst, tot in row_re.findall(text):
        eid = f"IDEA-{nnn}"
        seen_rows.add(eid)
        meta = entry_meta.get(eid)
        if not meta:
            problems.append(f"summary row {eid} has no matching entry")
            continue
        if slug != slug_of.get(eid):
            problems.append(
                f"summary row {eid}: slug '{slug}' != entry slug '{slug_of.get(eid)}'"
            )
        if meta["kind"] and kind != meta["kind"]:
            problems.append(
                f"summary row {eid}: kind '{kind}' != entry kind '{meta['kind']}'"
            )
        row_scores = [int(e), int(d), int(tst)]
        if meta["scores"] and row_scores != meta["scores"]:
            problems.append(
                f"summary row {eid}: scores {row_scores} != entry scores {meta['scores']}"
            )
        if sum(row_scores) != int(tot):
            problems.append(
                f"summary row {eid}: {row_scores} do not sum to stated total {tot}"
            )
        if meta["total"] is not None and int(tot) != meta["total"]:
            problems.append(
                f"summary row {eid}: total {tot} != entry total {meta['total']}"
            )
    if len(seen_rows) != len(ids):
        problems.append(
            f"summary table: {len(seen_rows)} well-formed rows parsed for {len(ids)} entries "
            "— a row that does not match the expected shape is invisible to every row check"
        )

    # each entry's three scores must sum to its stated total
    for block in re.split(r"^### ", text, flags=re.M)[1:]:
        head = block.split("\n", 1)[0]
        if not head.startswith("IDEA-"):
            continue
        stated = re.search(r"\*\*(\d+)/15\*\*", block)
        parts = re.findall(r"\| \*\*([1-5])/5\*\* \|", block)
        if (
            stated
            and len(parts) == 3
            and sum(int(p) for p in parts) != int(stated.group(1))
        ):
            problems.append(
                f"{head.split(' ')[0]}: scores {parts} do not sum to {stated.group(1)}"
            )

    if problems:
        print(f"FAIL  {len(problems)} problem(s) in the idea pool:")
        for p in problems:
            print(f"  - {p}")
        return 1
    pairs = sum(len(v) for v in rel.values()) // 2
    print(
        f"OK    {len(ids)} ideas · IDs unique and anchored · table sorted and complete · "
        f"cross-refs resolve and match their slugs · {pairs} reciprocal relations · links live"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
