"""Derived SQLite index over the brain's markdown.

THE RULE: markdown is the source of truth; this database is disposable. Delete it
and rebuild in under a second, losing nothing. That is what makes drift structurally
impossible, and it follows the precedent in alpha_research/pool/registry.py, where
git-versioned YAML manifests are canonical and SQLite is derived, gitignored state.

    python3 -m alpha_research.brain.index --build     rebuild from markdown
    python3 -m alpha_research.brain.index --check     assert index matches markdown
    python3 -m alpha_research.brain.index --stats     what is in the pool
"""
from __future__ import annotations

import argparse
import hashlib
import sqlite3
import sys

from alpha_research.brain import parser

DB = parser.ROOT / "data_lake/brain.sqlite"  # data_lake/ is gitignored

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS atoms (
    id      TEXT PRIMARY KEY,
    type    TEXT NOT NULL CHECK (type IN ('mechanism','concept','verdict','capture')),
    slug    TEXT NOT NULL,
    path    TEXT NOT NULL,
    kind    TEXT,
    domain  TEXT,
    status  TEXT,
    econ    INTEGER, dur INTEGER, test INTEGER, total INTEGER,
    body    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS atoms_type   ON atoms(type);
CREATE INDEX IF NOT EXISTS atoms_domain ON atoms(domain);
CREATE INDEX IF NOT EXISTS atoms_total  ON atoms(total DESC);

-- Directed. Reciprocity is an INVARIANT OF THE MARKDOWN enforced by
-- check_ideas_integrity.py, not a constraint here: this table must be able to
-- REPRESENT a one-way edge so the UI can show that the pool is broken.
CREATE TABLE IF NOT EXISTS edges (
    src    TEXT NOT NULL,
    dst    TEXT NOT NULL,
    reason TEXT,
    PRIMARY KEY (src, dst)
);
CREATE INDEX IF NOT EXISTS edges_dst ON edges(dst);

CREATE TABLE IF NOT EXISTS sources (
    atom_id TEXT NOT NULL,
    path    TEXT NOT NULL,
    PRIMARY KEY (atom_id, path)
);

CREATE VIRTUAL TABLE IF NOT EXISTS atoms_fts
    USING fts5(id UNINDEXED, slug, body, tokenize='porter unicode61');

CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""

WATCHED = (
    "book_notes/playground/reports/IDEAS.md",
    "book_notes/playground/brain/VERDICTS.md",
)


def fingerprint() -> str:
    """Hash of every markdown file the index is derived from."""
    h = hashlib.sha256()
    for rel in WATCHED:
        p = parser.ROOT / rel
        if p.exists():
            h.update(p.read_bytes())
    for f in sorted(parser.CONCEPTS_DIR.glob("*.md")):
        h.update(f.read_bytes())
    if parser.CAPTURES.exists():
        for f in sorted(parser.CAPTURES.glob("*.md")):
            h.update(f.read_bytes())
    return h.hexdigest()


def connect() -> sqlite3.Connection:
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def build() -> dict:
    con = connect()
    with con:
        con.execute("DELETE FROM atoms")
        con.execute("DELETE FROM edges")
        con.execute("DELETE FROM sources")
        con.execute("DELETE FROM atoms_fts")
        atoms = parser.all_atoms()
        for a in atoms:
            con.execute(
                "INSERT INTO atoms (id,type,slug,path,kind,domain,status,econ,dur,test,total,body)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    a.id,
                    a.type,
                    a.slug,
                    a.path,
                    a.kind,
                    a.domain,
                    a.status,
                    a.econ,
                    a.dur,
                    a.test,
                    a.total,
                    a.body,
                ),
            )
            con.execute(
                "INSERT INTO atoms_fts (id,slug,body) VALUES (?,?,?)",
                (a.id, a.slug.replace("-", " "), a.body),
            )
            for s in a.sources:
                con.execute("INSERT OR IGNORE INTO sources VALUES (?,?)", (a.id, s))
            for e in a.edges:
                con.execute(
                    "INSERT OR REPLACE INTO edges VALUES (?,?,?)",
                    (e.src, e.dst, e.reason),
                )
        con.execute(
            "INSERT OR REPLACE INTO meta VALUES ('fingerprint',?)", (fingerprint(),)
        )
    return stats(con)


def check(con: sqlite3.Connection | None = None) -> tuple[bool, str]:
    """Does the index still match the markdown? The whole safety story."""
    con = con or connect()
    row = con.execute("SELECT value FROM meta WHERE key='fingerprint'").fetchone()
    if not row:
        return False, "index has never been built — run --build"
    if row["value"] != fingerprint():
        return False, "STALE: markdown changed since the index was built — run --build"
    # one-way edges are a markdown defect the UI must be able to surface
    oneway = con.execute(
        "SELECT e.src, e.dst FROM edges e"
        " WHERE e.src LIKE 'IDEA-%' AND e.dst LIKE 'IDEA-%'"
        "   AND NOT EXISTS (SELECT 1 FROM edges r WHERE r.src=e.dst AND r.dst=e.src)"
    ).fetchall()
    if oneway:
        return False, f"{len(oneway)} non-reciprocal edge(s): " + ", ".join(
            f"{r['src']}->{r['dst']}" for r in oneway[:5]
        )
    return True, "index matches markdown"


def stats(con: sqlite3.Connection | None = None) -> dict:
    con = con or connect()
    q = lambda s, *a: con.execute(s, a).fetchone()[0]  # noqa: E731
    return {
        "mechanisms": q("SELECT COUNT(*) FROM atoms WHERE type='mechanism'"),
        "concepts": q("SELECT COUNT(*) FROM atoms WHERE type='concept'"),
        "verdicts": q("SELECT COUNT(*) FROM atoms WHERE type='verdict'"),
        "captures": q("SELECT COUNT(*) FROM atoms WHERE type='capture'"),
        "edges_directed": q("SELECT COUNT(*) FROM edges"),
        "orphans": q(
            "SELECT COUNT(*) FROM atoms a WHERE a.type='mechanism'"
            " AND NOT EXISTS (SELECT 1 FROM edges e WHERE e.src=a.id)"
        ),
    }


def search(term: str, limit: int = 20, type_: str | None = None) -> list[sqlite3.Row]:
    con = connect()
    sql = (
        "SELECT a.id,a.type,a.slug,a.domain,a.total,"
        " snippet(atoms_fts,2,'[',']','…',12) AS snip, bm25(atoms_fts) AS rank"
        " FROM atoms_fts JOIN atoms a ON a.id = atoms_fts.id"
        " WHERE atoms_fts MATCH ?"
    )
    args = [term]
    if type_:
        sql += " AND a.type = ?"
        args.append(type_)
    return con.execute(sql + " ORDER BY rank LIMIT ?", (*args, limit)).fetchall()


def neighbours(atom_id: str) -> list[sqlite3.Row]:
    con = connect()
    return con.execute(
        "SELECT e.dst AS id, e.reason, a.slug, a.type FROM edges e"
        " LEFT JOIN atoms a ON a.id = e.dst WHERE e.src = ?"
        " UNION SELECT e.src, e.reason, a.slug, a.type FROM edges e"
        " LEFT JOIN atoms a ON a.id = e.src WHERE e.dst = ?",
        (atom_id, atom_id),
    ).fetchall()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--search")
    a = ap.parse_args()
    if a.build:
        s = build()
        print("rebuilt " + str(DB.relative_to(parser.ROOT)))
        print("  " + " · ".join(f"{k}: {v}" for k, v in s.items()))
    if a.check or a.build:
        ok, msg = check()
        print(("OK    " if ok else "FAIL  ") + msg)
        if not ok:
            return 1
    if a.stats:
        print("  " + " · ".join(f"{k}: {v}" for k, v in stats().items()))
    if a.search:
        for r in search(a.search):
            print(f"  {r['id']:12} {r['type']:10} {r['slug'][:42]:44} {r['snip'][:60]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
