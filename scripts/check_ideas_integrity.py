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
    if totals != sorted(totals, reverse=True):
        problems.append("summary table is not sorted by total, descending")

    # every IDEA-NNN referenced anywhere in the library must resolve
    known = set(ids)
    for f in sorted(LIB.rglob("*.md")):
        for m in re.finditer(r"IDEA-\d{3}", f.read_text(encoding="utf-8")):
            if m.group(0) not in known:
                problems.append(f"{f.relative_to(LIB)} references unknown {m.group(0)}")

    # each entry's three scores must sum to its stated total
    for block in re.split(r"^### ", text, flags=re.M)[1:]:
        head = block.split("\n", 1)[0]
        if not head.startswith("IDEA-"):
            continue
        stated = re.search(r"\*\*(\d+)/15\*\*", block)
        parts = re.findall(r"\| \*\*(\d)/5\*\* \|", block)
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
    print(
        f"OK    {len(ids)} ideas · IDs unique and anchored · table sorted and complete · all cross-refs resolve"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
