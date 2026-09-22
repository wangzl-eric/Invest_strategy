# Historical Dataset Store — Deployment Plan

> Created 2026-09-04. Status: **DRAFT — awaiting approval.** No code changed yet.
> Scope: deploy a single queryable database for historical market/macro datasets,
> replacing the current scattered-Parquet read path.

## 1. Why now — what the audit found

I inventoried the existing data layer before drafting. Five findings drive the design.

### 1.1 There are two storage schemes, and the sophisticated one is dead

| | Designed layout | Live layout |
|---|---|---|
| Path | `data_lake/{layer}/{provider}/{kind}/{universe}/{freq}/date=YYYY-MM-DD/` | `data/market_data/{prices,fred}/*.parquet` |
| Code | `quant_data/{paths,registry,meta_db,duckdb_store,io/parquet_writer,pipelines/ingest_bars}.py` | `core/market_data_store.py`, `quant_data/api.py` |
| On disk | **Does not exist.** `data_lake/` holds only `brain.sqlite` | 46 files, 3.4 MB prices + 60 KB fred |
| Consumers | **Zero** outside its own package | Everything |

`research.duckdb` and `quant_data_meta.db` have never been created. Yet `README.md:501-517`,
`docs/PROJECT_DOCUMENTATION.md:389-441` and `.claude/agents/data.md:56-63` document this
scaffolding as live infrastructure — so agents are being told to query a database that
does not exist. This plan either lights it up or deletes it; the current half-state is the
worst of both.

### 1.2 The read path is a full-lake scan per ticker

`quant_data/api.py::_read_parquet_prices` globs every file in `prices/` and calls
`pd.read_parquet()` on each until a ticker matches. That is O(entire lake) per single-series
lookup, with a bare `except: continue` swallowing every failure. At 46 files it is merely
wasteful; it does not survive growth to intraday or a wide universe.

### 1.3 Three incompatible schemas — and the deepest history is unreachable

| Schema | Files | Example row counts |
|---|---|---|
| `(date, ticker, open, high, low, close, volume)` — the documented contract | 28 | EURUSD_X 45, HYG 43, IEF 151, NZDUSD_X 10 |
| `(date, series_id, value)` — FRED long format | 14 | DGS10 394, CPIAUCSL 172 |
| `(open, high, low, close, volume)` — date in index, **no ticker column** | 1 | `spy_ohlc.parquet` **5,070** |
| `(open, high, low, close)` — date in index, **no ticker column** | 2 | `vix_daily.parquet` **5,070**, `vix3m_daily.parquet` **4,936** |

The last two groups have no `ticker`/`symbol` column, so `_read_parquet_prices` hits
`if col_ticker is None: continue` and skips them **silently**. The result: ~15,000 rows of the
longest daily history in the repo — 20 years of SPY and VIX — are invisible to `get_data`,
while the per-ticker caches it *can* read hold as few as 10 rows. A researcher asking for SPY
gets the 43-row cache, not the 5,070-row file sitting next to it.

### 1.4 No single source of truth per series

FRED series exist in both `prices/DGS10.parquet` and the `fred/treasury_yields.parquet`
bundle. `_read_parquet_macro` acknowledges this in a comment and resolves it with a
"freshest `end` date wins" heuristic across duplicates. That is a tiebreak, not a contract —
two files can disagree on the *value* at a shared date and nothing detects it.

### 1.5 The catalog is not usable as a coverage index

`catalog.json` is keyed by **asset-class bundle** — `equities`, `fx`, `commodities`,
`rates_yf`, `treasury_yields`, `macro_indicators`, `fed_liquidity`, `ibkr_equities`,
`ibkr_fx` — and each entry writes `start_date` / `end_date`.

`_catalog_coverage(ticker)` does `catalog.get(ticker)` and then reads `entry.get("start")`
/ `entry.get("end")`. Both the key and the field names are wrong, so the function always
returns `None`. Coverage checking is currently dead code.

Secondary: **31 Parquet files are tracked in git** (`data_lake/` is gitignored, `data/market_data/`
is not). `SPY.parquet` and `XLE.parquet` show as modified in the working tree right now —
binary data drift is landing in commits.

---

## 2. Design decision: embedded DuckDB, not a server

**Recommendation: DuckDB, single file at `data_lake/market.duckdb`, with a strict
single-writer rule.**

Sizing the decision honestly:

- Today: 3.4 MB. Daily bars, 5,000 tickers × 20y ≈ 25M rows ≈ 400 MB — trivial for DuckDB.
- The only volume that would change this is minute bars at scale (100 tickers × 10y ≈ 100M rows,
  low single-digit GB). DuckDB still handles that; it is what it is built for.
- Postgres/TimescaleDB buys concurrent writes and network access. This is a single-user local
  platform that already runs SQLite for account data. A server is operational overhead against
  a problem we do not have.

**The real constraint is concurrency, not size.** DuckDB permits one read-write process.
This repo runs a FastAPI backend, an APScheduler job, a Dash frontend, and multiple agent
worktrees simultaneously — naive adoption would deadlock. So the architecture is explicit:

- **Exactly one writer**: the ingestion process, holding the DB read-write, serialized by a
  file lock. Nothing else ever opens it writable.
- **All readers open `read_only=True`** — backend, dashboard, notebooks, backtests, agents.
  DuckDB permits unlimited concurrent read-only processes.
- Ingestion writes to a staging table and swaps, so readers never observe a partial load.

Escape hatch: keep the existing SQLAlchemy metadata registry (`meta_db_url`) pointing at
SQLite/Postgres. If the store ever needs to go multi-writer, only the fact tables migrate;
the registry contract is already portable.

**Parquet is retained** as the interchange/export format and as the raw landing zone, not as
the query path. DuckDB tables become the query surface.

---

## 3. Target schema

Bitemporal where it matters — this is the substantive upgrade over the current layer.

```sql
-- Dimension: one row per instrument, fed from quant_data/ticker_map.py
CREATE TABLE symbol (
    ticker        VARCHAR PRIMARY KEY,
    asset_class   VARCHAR NOT NULL,   -- equity|fx|commodity|rate|crypto
    venue         VARCHAR,
    currency      VARCHAR,
    description   VARCHAR
);

-- Fact: daily bars. One row per (ticker, date, source).
CREATE TABLE bar_daily (
    ticker        VARCHAR NOT NULL,
    date          DATE    NOT NULL,
    open          DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE,
    adj_close     DOUBLE,
    volume        BIGINT,
    source        VARCHAR NOT NULL,   -- yfinance|ibkr|stooq|akshare|polygon
    ingested_at   TIMESTAMP NOT NULL,
    PRIMARY KEY (ticker, date, source)
);

-- Fact: macro observations, vintage-aware.
CREATE TABLE macro_obs (
    series_id       VARCHAR NOT NULL,
    reference_date  DATE    NOT NULL,  -- period the value describes
    vintage_date    DATE    NOT NULL,  -- when this value became public
    value           DOUBLE,
    source          VARCHAR NOT NULL,
    ingested_at     TIMESTAMP NOT NULL,
    PRIMARY KEY (series_id, reference_date, vintage_date)
);
```

`vintage_date` is the point of the exercise. Today `quant_data/pit.py` approximates
availability with a static `PUBLICATION_LAG_DAYS` table (CPI = 45 days, and a 45-day default
for anything unlisted). That is a defensible conservative estimate, but it is an estimate,
and it cannot represent **revisions** — GDP and PAYEMS get restated, and a backtest that sees
the final print instead of the first print is look-ahead biased in a way the lag table cannot fix.

Storing vintages makes the PIT read a real query:

```sql
SELECT series_id, reference_date, value
FROM macro_obs
WHERE vintage_date <= $as_of
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY series_id, reference_date ORDER BY vintage_date DESC
) = 1;
```

FRED exposes vintages via ALFRED. Where a vintage is unavailable, we synthesize
`vintage_date = reference_date + PUBLICATION_LAG_DAYS` and flag `source='synthetic_lag'` —
so `pit.py` stays the documented fallback, not the only mechanism, and every series states
which regime it is under.

**Source precedence**: `bar_daily` keyed by `(ticker, date, source)` keeps overlapping
providers rather than silently picking one. A `v_bar_daily` view resolves to a single row per
`(ticker, date)` by declared precedence (e.g. ibkr > yfinance > stooq). This replaces the
"freshest end date wins" heuristic in §1.4 with an explicit, inspectable rule — and makes
cross-source disagreement a query, not an invisible coin flip.

---

## 4. Phased rollout

Each phase is independently revertible. **No phase deletes Parquet** — the files remain the
rollback path until Phase 5.

### Phase 0 — Inventory & reconciliation (no writes)
- `scripts/audit_data_lake.py`: enumerate every Parquet file, its schema group, ticker/series
  coverage, row count, date range, and **which files `get_data` can and cannot currently reach**.
- Reconcile duplicated series (§1.4): report every `(series_id, date)` where two files disagree
  on the value. This is a data-quality finding to resolve before migrating, not after.
- Decide the canonical identity for the headerless files (`spy_ohlc`, `vix_daily`, `vix3m_daily`)
  and their `source` attribution.
- **Exit criterion**: a written inventory whose row counts we can assert against post-migration.

### Phase 1 — Schema + backfill (additive)
- `alpha_research/quant_data/store/schema.sql` + a `migrate.py` that is idempotent and re-runnable.
- Backfill all four schema groups into `bar_daily` / `macro_obs`, normalizing the headerless
  files by promoting the index to `date` and assigning `ticker`. **This alone recovers the
  ~15,000 unreachable rows from §1.3.**
- Bootstrap `symbol` from `ticker_map.py`.
- **Exit criterion**: per-series row counts and date ranges match the Phase 0 inventory exactly,
  modulo the deduplication explicitly authorized in Phase 0.

### Phase 2 — Read cutover
- `quant_data/store/reader.py`: read-only DuckDB connections, indexed lookup by ticker + date range.
- Repoint `quant_data/api.py::get_data` at the store; delete `_read_parquet_prices` /
  `_read_parquet_macro` full-scans. Fix or remove the dead `_catalog_coverage` (§1.5) —
  coverage now comes from a real `SELECT min(date), max(date)`.
- **Dual-read verification**: for every ticker in the inventory, assert old path and new path
  return identical frames *where the old path returned anything*. Differences are expected only
  where the old path was silently returning a truncated cache — each such case gets logged
  and eyeballed, not auto-accepted.
- Preserve the API contract exactly: same signature, same column names, same `pit=True` default.

### Phase 3 — Single-writer ingestion
- `quant_data/store/writer.py`: file-lock guarded, staging-table + atomic swap, upsert on the
  declared primary keys.
- Route `core/market_data_store.py` writes and the connectors through it; log each load into the
  **existing** `Dataset` / `DatasetVersion` / `IngestionRun` registry models — this is where the
  §1.1 scaffolding finally earns its place instead of being deleted.
- Wire `quant_data/qc.py` as a pre-commit gate on ingestion: missing bars, stale prices, extreme
  returns block the swap.
- Continue writing Parquet as the raw landing zone, so the DB stays rebuildable from files.

### Phase 4 — PIT vintages
- ALFRED vintage pull for the FRED series in `PUBLICATION_LAG_DAYS`; synthesize the rest from
  the lag table, flagged as `synthetic_lag`.
- `pit.py::as_of_series` reads real vintages when present, falls back to the lag shift otherwise.
- **This changes backtest inputs.** It ships behind a flag, and §5 gates it.

### Phase 5 — Retire the old surface
- Delete or fold in the unused scaffolding (`paths.py`, `duckdb_store.py`,
  `io/parquet_writer.py`, `pipelines/ingest_bars.py`) depending on what Phase 3 absorbed.
- Correct `README.md`, `docs/PROJECT_DOCUMENTATION.md`, `docs/QUANT_DATA_SPEC.md`,
  `CLAUDE.md`, and `.claude/agents/data.md` — they currently describe infrastructure that
  does not exist (§1.1).
- **Git hygiene**: stop tracking the 31 Parquet blobs; gitignore `data/market_data/`, add a
  `make data-bootstrap` that rebuilds from connectors, and keep `catalog.json` (small, text,
  useful in diffs) tracked.

---

## 5. The gate that matters: reproducibility

Changing the data layer changes backtest inputs. The strategy pool records `run_id` artifacts
under `data/backtest_runs/`, and pool entries were promoted on those numbers. If a migration
silently shifts a Sharpe, every prior verdict becomes unauditable.

**Hard gate, before Phase 2 merges:** re-run an existing pool strategy (`sector_rotation_v1`)
against the new store and assert the results are **bit-identical** to its recorded artifacts.

- Phases 1–3 are a storage refactor and **must** produce identical numbers. A diff here is a
  migration bug, not an improvement.
- Phase 4 is the exception: real vintages *should* change macro-dependent results, because the
  old numbers were computed against an approximation. That phase requires a deliberate re-run
  and re-review of affected pool entries, with the before/after recorded — it is not a silent upgrade.

Per `CLAUDE.md`, this work is logged in `alpha_research/research/STRATEGY_TRACKER.md`, one
entry per session.

---

## 6. Open decisions for you

1. **Vintages in scope now, or defer Phase 4?** It is the strongest correctness win and the only
   phase that invalidates existing backtest numbers. Clean to defer.
2. **Source precedence order** for `v_bar_daily` — I assumed ibkr > yfinance > stooq.
3. **The headerless files** (`spy_ohlc`, `vix_daily`, `vix3m_daily`, ~15k rows): confirm ticker
   identity and provenance, or we migrate 20 years of history under a guessed source.
4. **Untrack the Parquet blobs?** It means the repo no longer clones with data — bootstrap
   becomes a network fetch.
5. **Sequencing**: Phase 0 is read-only and answers several of the above. I'd recommend running
   it first regardless of how you decide the rest.
