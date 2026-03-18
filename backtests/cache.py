"""Signal caching layer backed by Parquet files.

Avoids recomputation of expensive signals by caching results keyed on
(signal_name, params_hash, data_hash).  Cache entries are invalidated
when the source data changes (mtime-based) or manually.

Thread-safe via ``threading.Lock``.

Usage:
    from backtests.cache import SignalCache

    cache = SignalCache()
    key = SignalCache.compute_data_hash(prices)

    cached = cache.get("momentum_60_21", {"lookback": 60}, key)
    if cached is None:
        signal = compute_signal(prices)
        cache.put("momentum_60_21", {"lookback": 60}, key, signal)
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers (pure)
# ---------------------------------------------------------------------------


def _params_hash(params: Dict[str, Any]) -> str:
    """Deterministic hash of a parameter dict."""
    canonical = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def _cache_filename(signal_name: str, params: Dict[str, Any], data_hash: str) -> str:
    """Build a safe filename for a cache entry."""
    ph = _params_hash(params)
    safe_name = signal_name.replace("/", "_").replace("\\", "_")
    return f"{safe_name}__{ph}__{data_hash}.parquet"


def _meta_filename(parquet_name: str) -> str:
    """Companion metadata JSON filename."""
    return parquet_name.replace(".parquet", ".meta.json")


def _source_file_hash(path: Path) -> str:
    """Fast hash of a file's mtime + size (proxy for content change)."""
    stat = path.stat()
    key = f"{stat.st_mtime_ns}:{stat.st_size}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# SignalCache
# ---------------------------------------------------------------------------


class SignalCache:
    """Cache computed signals to avoid recomputation.

    Keys: (signal_name, params_hash, data_hash)
    Storage: Parquet files in ``cache_dir/``
    Invalidation:
        - Manual via :meth:`invalidate`
        - Automatic when data_hash changes (new hash = cache miss)
        - Automatic when source Parquet mtime changes (via ``source_paths``)

    Thread-safe: all reads/writes are protected by a ``threading.Lock``.

    Args:
        cache_dir: Directory for Parquet cache files.
        max_entries: Soft limit on cache entries.  When exceeded, oldest
            entries are evicted on the next :meth:`put`.
        source_paths: Optional mapping of signal_name -> source Parquet Path.
            When provided, ``get`` auto-invalidates if the source file's
            mtime has changed since the cache entry was written.
    """

    def __init__(
        self,
        cache_dir: str = "data/cache/signals",
        max_entries: int = 500,
        source_paths: Optional[Dict[str, Path]] = None,
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_entries = max_entries
        self._source_paths: Dict[str, Path] = dict(source_paths or {})
        self._lock = threading.Lock()

    def get(
        self,
        signal_name: str,
        params: Dict[str, Any],
        data_hash: str,
    ) -> Optional[pd.DataFrame]:
        """Retrieve a cached signal DataFrame.

        Returns None on cache miss or stale entry.
        """
        fname = _cache_filename(signal_name, params, data_hash)
        path = self.cache_dir / fname

        with self._lock:
            if not path.exists():
                return None

            # Auto-invalidate if source Parquet mtime changed
            if self._is_stale(signal_name, fname):
                logger.info("Cache STALE (source changed): %s", fname)
                self._remove_entry_files(fname)
                return None

            try:
                df = pd.read_parquet(path)
                logger.debug("Cache HIT: %s", fname)
                return df
            except Exception as exc:
                logger.warning("Corrupt cache entry %s: %s", fname, exc)
                self._remove_entry_files(fname)
                return None

    def put(
        self,
        signal_name: str,
        params: Dict[str, Any],
        data_hash: str,
        signal_data: pd.DataFrame,
    ) -> None:
        """Store a signal DataFrame in the cache."""
        if signal_data is None or signal_data.empty:
            return

        fname = _cache_filename(signal_name, params, data_hash)
        path = self.cache_dir / fname
        meta_path = self.cache_dir / _meta_filename(fname)

        with self._lock:
            # Evict old entries if cache is too large
            self._maybe_evict()

            try:
                signal_data.to_parquet(path, engine="pyarrow")

                # Write metadata for staleness checks
                meta: Dict[str, Any] = {
                    "signal_name": signal_name,
                    "params": params,
                    "data_hash": data_hash,
                    "created_at": pd.Timestamp.now(tz="UTC").isoformat(),
                }
                source = self._source_paths.get(signal_name)
                if source and source.exists():
                    meta["source_hash"] = _source_file_hash(source)

                meta_path.write_text(json.dumps(meta, indent=2, default=str))

                logger.debug("Cache PUT: %s (%d rows)", fname, len(signal_data))
            except Exception as exc:
                logger.warning("Failed to write cache entry %s: %s", fname, exc)

    def invalidate(self, signal_name: Optional[str] = None) -> int:
        """Remove cache entries.

        Args:
            signal_name: If provided, only remove entries for this signal.
                If None, remove all entries.

        Returns:
            Number of entries removed.
        """
        with self._lock:
            count = 0
            for path in self._list_entries():
                if signal_name is not None:
                    entry_signal = path.stem.split("__")[0]
                    if entry_signal != signal_name:
                        continue
                self._remove_entry_files(path.name)
                count += 1

            logger.info("Invalidated %d cache entries", count)
            return count

    def list_entries(self) -> pd.DataFrame:
        """Return a DataFrame summarising all cached entries."""
        rows: List[Dict[str, Any]] = []

        with self._lock:
            for path in self._list_entries():
                meta = self._read_meta(path.name)
                size_kb = path.stat().st_size / 1024 if path.exists() else 0
                rows.append(
                    {
                        "signal_name": meta.get(
                            "signal_name", path.stem.split("__")[0]
                        ),
                        "params_hash": path.stem.split("__")[1]
                        if "__" in path.stem
                        else "",
                        "data_hash": meta.get("data_hash", ""),
                        "created_at": meta.get("created_at", ""),
                        "size_kb": round(size_kb, 1),
                    }
                )

        if not rows:
            return pd.DataFrame(
                columns=[
                    "signal_name",
                    "params_hash",
                    "data_hash",
                    "created_at",
                    "size_kb",
                ]
            )
        return pd.DataFrame(rows)

    def stats(self) -> Dict[str, Any]:
        """Return cache statistics."""
        with self._lock:
            entries = self._list_entries()
            total_bytes = sum(p.stat().st_size for p in entries if p.exists())
            signals = set()
            for p in entries:
                parts = p.stem.split("__")
                if parts:
                    signals.add(parts[0])

        return {
            "n_entries": len(entries),
            "total_bytes": total_bytes,
            "total_mb": round(total_bytes / (1024 * 1024), 2),
            "signals": sorted(signals),
        }

    # ------------------------------------------------------------------
    # Static helpers
    # ------------------------------------------------------------------

    @staticmethod
    def compute_data_hash(data: pd.DataFrame) -> str:
        """Compute a fast hash of a DataFrame for cache keying.

        Uses shape, column names, and first/last rows to build a
        fingerprint without hashing every cell.
        """
        parts: List[str] = []

        parts.append(f"shape={data.shape}")
        parts.append(f"cols={'|'.join(str(c) for c in data.columns)}")

        if len(data) > 0:
            parts.append(f"idx0={data.index[0]}")
            parts.append(f"idx-1={data.index[-1]}")

        if len(data) >= 2:
            parts.append(f"head={data.iloc[0].values.tobytes().hex()[:32]}")
            parts.append(f"tail={data.iloc[-1].values.tobytes().hex()[:32]}")
        elif len(data) == 1:
            parts.append(f"head={data.iloc[0].values.tobytes().hex()[:32]}")

        combined = "|".join(parts)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    # ------------------------------------------------------------------
    # Internal (caller must hold self._lock)
    # ------------------------------------------------------------------

    def _list_entries(self) -> List[Path]:
        """List all Parquet cache files."""
        if not self.cache_dir.exists():
            return []
        return sorted(self.cache_dir.glob("*.parquet"))

    def _read_meta(self, parquet_filename: str) -> Dict[str, Any]:
        """Read companion metadata JSON. Returns empty dict on failure."""
        meta_path = self.cache_dir / _meta_filename(parquet_filename)
        if not meta_path.exists():
            return {}
        try:
            return json.loads(meta_path.read_text())
        except Exception:
            return {}

    def _is_stale(self, signal_name: str, parquet_filename: str) -> bool:
        """Check whether a cache entry is stale based on source mtime."""
        source = self._source_paths.get(signal_name)
        if source is None or not source.exists():
            return False

        meta = self._read_meta(parquet_filename)
        stored_hash = meta.get("source_hash")
        if stored_hash is None:
            return False  # no baseline to compare

        current_hash = _source_file_hash(source)
        return stored_hash != current_hash

    def _remove_entry_files(self, parquet_filename: str) -> None:
        """Delete a cache entry's Parquet and metadata files."""
        parquet_path = self.cache_dir / parquet_filename
        meta_path = self.cache_dir / _meta_filename(parquet_filename)
        for p in (parquet_path, meta_path):
            try:
                p.unlink(missing_ok=True)
            except OSError as exc:
                logger.warning("Failed to remove %s: %s", p, exc)

    def _maybe_evict(self) -> None:
        """Evict oldest entries when cache exceeds max_entries."""
        entries = self._list_entries()
        if len(entries) <= self.max_entries:
            return

        entries_with_mtime = []
        for p in entries:
            try:
                entries_with_mtime.append((p.stat().st_mtime, p))
            except OSError:
                continue

        entries_with_mtime.sort(key=lambda x: x[0])

        n_to_remove = len(entries_with_mtime) - self.max_entries + 1
        for _, path in entries_with_mtime[:n_to_remove]:
            self._remove_entry_files(path.name)
            logger.debug("Evicted cache entry: %s", path.name)


__all__ = ["SignalCache"]
