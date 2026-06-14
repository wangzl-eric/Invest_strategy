"""Global trial ledger — the factory's multiple-testing control.

Wraps the ``experiment_ledger`` table (``core.models.ExperimentLedger``).
The review pipeline calls this on every run so the effective ``n_trials``
fed to DSR is computed from the *accumulated* history of an idea, not trusted
from the manifest (alpha_factory_workflow.md §4.1). The manifest value is a
floor; the ledger is the truth.

Session plumbing mirrors ``alpha_research.pool.registry.PoolRegistry``: pass a
session (tests inject the in-memory ``test_db`` fixture) or let it open one
against the configured application database.

Two facts make the counting honest:

* **Trial identity excludes the entrypoint.** ``manifest_spec_hash`` hashes the
  economic spec only, so N independent implementations of one idea (the
  multi-impl robustness cross-check) are ONE trial, not N. Reporting the best
  of N implementations would itself be the multiple testing this guards.
* **Re-running an identical spec is not a new trial.** Distinct
  ``manifest_hash`` values under a ``hypothesis_id`` are the trial count;
  re-runs of the same hash reuse their version and do not inflate it.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from typing import Any, Dict, Optional

import pandas as pd
from sqlalchemy.orm import Session

from core.models import ExperimentLedger

logger = logging.getLogger(__name__)

# Trailing spec-version / implementation markers stripped to recover the
# idea-level grouping key, e.g. sector_rotation_v2_implb -> sector_rotation.  gitleaks:allow
_VERSION_SUFFIX_RE = re.compile(r"_(?:v\d+|impl[a-z0-9]+)$", re.IGNORECASE)


def derive_hypothesis_id(strategy_id: str) -> str:
    """Strip trailing ``_vN`` / ``_implX`` markers to the idea-level key.

    ``sector_rotation_v1`` and ``sector_rotation_v2`` share the hypothesis
    ``sector_rotation`` so their trials accumulate; ``momentum`` (no marker)
    is returned unchanged.
    """
    hid = strategy_id
    while True:
        stripped = _VERSION_SUFFIX_RE.sub("", hid)
        if stripped == hid:
            return hid
        hid = stripped


def manifest_spec_hash(manifest: "Any") -> str:
    """sha256 of the *economic* spec — entrypoint and metadata excluded.

    Two implementations of the same idea (identical params/universe/costs but
    different runner code) hash equal, so the multi-impl cross-check counts as
    a single trial. Author, name, description, created date, and the entrypoint
    string are intentionally omitted; changing the runner is not a new trial,
    changing the economics is.
    """
    spec = {
        "hypothesis_id": derive_hypothesis_id(manifest.strategy_id),
        "universe": sorted(manifest.universe),
        "params": manifest.params,
        "rebalance": manifest.rebalance.model_dump(mode="json"),
        "cost_model": manifest.cost_model.model_dump(mode="json"),
        "data_requirements": sorted(
            (dr.model_dump(mode="json") for dr in manifest.data_requirements),
            key=lambda d: (d.get("id", ""), d.get("kind", "")),
        ),
        "promotion_rules": manifest.promotion_rules.model_dump(mode="json"),
    }
    blob = json.dumps(spec, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class TrialLedger:
    """Read/write access to the global trial ledger."""

    def __init__(self, session: Optional[Session] = None):
        self._session = session

    # ------------------------------------------------------------------
    # Session plumbing (mirrors PoolRegistry)
    # ------------------------------------------------------------------

    def _get_session(self) -> tuple[Session, bool]:
        if self._session is not None:
            return self._session, False
        from core.database import SessionLocal, init_db

        init_db()
        return SessionLocal(), True

    def _run(self, fn):
        session, owns = self._get_session()
        try:
            result = fn(session)
            session.commit()
            return result
        except Exception:
            session.rollback()
            raise
        finally:
            if owns:
                session.close()

    # ------------------------------------------------------------------
    # Planning (read-only) — called before the battery
    # ------------------------------------------------------------------

    def plan_trial(
        self, hypothesis_id: str, manifest_hash: str, n_trials_floor: int
    ) -> Dict[str, Any]:
        """Resolve the trial context for a run *before* it executes.

        Returns the version this spec maps to, how many runs the version has
        already had (for the iteration cap), and the effective ``n_trials`` —
        ``max(floor, #distinct specs ever tried for this hypothesis incl. this
        one)``. Read-only: no row is written until :meth:`record`.
        """

        def _op(session: Session) -> Dict[str, Any]:
            rows = (
                session.query(ExperimentLedger)
                .filter_by(hypothesis_id=hypothesis_id)
                .all()
            )
            hashes = [r.manifest_hash for r in rows]
            distinct = list(dict.fromkeys(hashes))  # preserve first-seen order
            is_new_spec = manifest_hash not in distinct

            if is_new_spec:
                version = len(distinct) + 1
                prior_runs_this_version = 0
            else:
                version = distinct.index(manifest_hash) + 1
                prior_runs_this_version = sum(1 for h in hashes if h == manifest_hash)

            n_specs_incl_this = len(distinct) + (1 if is_new_spec else 0)
            effective = max(int(n_trials_floor), n_specs_incl_this)
            return {
                "available": True,
                "hypothesis_id": hypothesis_id,
                "manifest_hash": manifest_hash,
                "version": version,
                "is_new_spec": is_new_spec,
                "prior_runs_this_version": prior_runs_this_version,
                "n_trials_declared": int(n_trials_floor),
                "n_trials_effective": effective,
            }

        return self._run(_op)

    # ------------------------------------------------------------------
    # Recording (write) — called after artifacts are saved
    # ------------------------------------------------------------------

    def record(
        self,
        *,
        hypothesis_id: str,
        strategy_id: str,
        family: str,
        version: int,
        manifest_hash: str,
        run_id: str,
        verdict: str,
        sharpe: Optional[float],
        psr: Optional[float],
        dsr: Optional[float],
        n_trials_declared: int,
        n_trials_effective: int,
    ) -> Dict[str, Any]:
        """Append one immutable trial row for a completed review run."""

        def _op(session: Session) -> Dict[str, Any]:
            row = ExperimentLedger(
                hypothesis_id=hypothesis_id,
                strategy_id=strategy_id,
                family=family,
                version=int(version),
                manifest_hash=manifest_hash,
                run_id=run_id,
                verdict=verdict,
                sharpe=_nan_to_none(sharpe),
                psr=_nan_to_none(psr),
                dsr=_nan_to_none(dsr),
                n_trials_declared=int(n_trials_declared),
                n_trials_effective=int(n_trials_effective),
            )
            session.add(row)
            session.flush()
            logger.info(
                "Trial logged: %s v%d run=%s verdict=%s (n_trials eff=%d, decl=%d)",
                hypothesis_id,
                version,
                run_id,
                verdict,
                n_trials_effective,
                n_trials_declared,
            )
            return _to_dict(row)

        return self._run(_op)

    # ------------------------------------------------------------------
    # Queries (FDR pass, iteration-cap enforcement, reporting)
    # ------------------------------------------------------------------

    def list_rows(
        self,
        *,
        hypothesis_id: Optional[str] = None,
        family: Optional[str] = None,
    ) -> pd.DataFrame:
        """Ledger rows (newest first), optionally scoped to a hypothesis/family."""

        def _op(session: Session) -> pd.DataFrame:
            q = session.query(ExperimentLedger)
            if hypothesis_id is not None:
                q = q.filter_by(hypothesis_id=hypothesis_id)
            if family is not None:
                q = q.filter_by(family=family)
            rows = [_to_dict(r) for r in q.order_by(ExperimentLedger.id.desc()).all()]
            return pd.DataFrame(rows)

        return self._run(_op)


def _nan_to_none(v: Optional[float]) -> Optional[float]:
    if v is None:
        return None
    f = float(v)
    return None if f != f else f  # NaN -> None (SQLite stores NULL)


def _to_dict(row: ExperimentLedger) -> Dict[str, Any]:
    return {
        "id": row.id,
        "hypothesis_id": row.hypothesis_id,
        "strategy_id": row.strategy_id,
        "family": row.family,
        "version": row.version,
        "manifest_hash": row.manifest_hash,
        "run_id": row.run_id,
        "verdict": row.verdict,
        "sharpe": row.sharpe,
        "psr": row.psr,
        "dsr": row.dsr,
        "n_trials_declared": row.n_trials_declared,
        "n_trials_effective": row.n_trials_effective,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


__all__ = [
    "TrialLedger",
    "derive_hypothesis_id",
    "manifest_spec_hash",
]
