"""Strategy pool registry: lifecycle state machine over StrategyPoolEntry.

Lifecycle: ``candidate -> paper -> live``; ``retired`` is reachable from any
state. Transitions are validated and audited in ``state_history_json``.

The registry takes an optional SQLAlchemy session (tests inject the
in-memory ``test_db`` fixture); without one it opens sessions against the
configured application database (``core.database``).

Usage::

    from alpha_research.pool.registry import PoolRegistry

    pool = PoolRegistry()
    pool.register(manifest, manifest_path="alpha_research/research/pool/x/manifest.yaml")
    pool.attach_run("sector_rotation_v1", run_id="ab12cd34", verdict="REVISE")
    pool.set_state("sector_rotation_v1", "paper", reason="passed rigor gates")
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
from sqlalchemy.orm import Session

from core.models import StrategyPoolEntry

logger = logging.getLogger(__name__)

LIFECYCLE_STATES = ("candidate", "paper", "live", "retired")

# state -> allowed next states
_ALLOWED_TRANSITIONS: Dict[str, tuple] = {
    "candidate": ("paper", "retired"),
    "paper": ("live", "candidate", "retired"),  # can demote paper -> candidate
    "live": ("paper", "retired"),  # can demote live -> paper
    "retired": (),  # terminal
}


class TransitionError(ValueError):
    """Raised on an illegal lifecycle transition."""


class PoolRegistry:
    """CRUD + lifecycle management for the strategy pool."""

    def __init__(self, session: Optional[Session] = None):
        self._session = session

    # ------------------------------------------------------------------
    # Session plumbing
    # ------------------------------------------------------------------

    def _get_session(self) -> tuple[Session, bool]:
        """Return (session, owns_session)."""
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
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        manifest: "Any",
        *,
        manifest_path: str,
        reason: str = "initial registration",
    ) -> Dict[str, Any]:
        """Register (or refresh) a strategy from its manifest.

        Re-registering an existing strategy updates name/track/manifest_path
        but never resets its lifecycle state.
        """

        def _op(session: Session) -> Dict[str, Any]:
            entry = (
                session.query(StrategyPoolEntry)
                .filter_by(strategy_id=manifest.strategy_id)
                .one_or_none()
            )
            if entry is None:
                entry = StrategyPoolEntry(
                    strategy_id=manifest.strategy_id,
                    name=manifest.name,
                    track=manifest.track.value
                    if hasattr(manifest.track, "value")
                    else str(manifest.track),
                    state="candidate",
                    manifest_path=manifest_path,
                    state_history_json=json.dumps(
                        [_history_event("candidate", reason)]
                    ),
                )
                session.add(entry)
                logger.info(
                    "Registered strategy '%s' as candidate", manifest.strategy_id
                )
            else:
                entry.name = manifest.name
                entry.track = (
                    manifest.track.value
                    if hasattr(manifest.track, "value")
                    else str(manifest.track)
                )
                entry.manifest_path = manifest_path
                logger.info("Refreshed registration for '%s'", manifest.strategy_id)
            session.flush()
            return _to_dict(entry)

        return self._run(_op)

    def attach_run(
        self, strategy_id: str, *, run_id: str, verdict: str = ""
    ) -> Dict[str, Any]:
        """Record the latest review run for a strategy."""

        def _op(session: Session) -> Dict[str, Any]:
            entry = self._get_entry(session, strategy_id)
            entry.latest_run_id = run_id
            entry.latest_verdict = verdict
            session.flush()
            return _to_dict(entry)

        return self._run(_op)

    def update_health(self, strategy_id: str, health: Dict[str, Any]) -> Dict[str, Any]:
        """Merge health metrics (monitoring jobs, Phase 4)."""

        def _op(session: Session) -> Dict[str, Any]:
            entry = self._get_entry(session, strategy_id)
            current = json.loads(entry.health_json or "{}")
            current.update(health)
            entry.health_json = json.dumps(current)
            session.flush()
            return _to_dict(entry)

        return self._run(_op)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def set_state(
        self, strategy_id: str, new_state: str, *, reason: str
    ) -> Dict[str, Any]:
        """Transition a strategy's lifecycle state (validated + audited)."""
        if new_state not in LIFECYCLE_STATES:
            raise TransitionError(
                f"unknown state '{new_state}' (valid: {LIFECYCLE_STATES})"
            )

        def _op(session: Session) -> Dict[str, Any]:
            entry = self._get_entry(session, strategy_id)
            allowed = _ALLOWED_TRANSITIONS.get(entry.state, ())
            if new_state not in allowed:
                raise TransitionError(
                    f"illegal transition {entry.state} -> {new_state} for "
                    f"'{strategy_id}' (allowed: {allowed or 'none — terminal state'})"
                )
            history = json.loads(entry.state_history_json or "[]")
            history.append(_history_event(new_state, reason))
            entry.state = new_state
            entry.state_history_json = json.dumps(history)
            session.flush()
            logger.info("'%s' -> %s (%s)", strategy_id, new_state, reason)
            return _to_dict(entry)

        return self._run(_op)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get(self, strategy_id: str) -> Dict[str, Any]:
        def _op(session: Session) -> Dict[str, Any]:
            return _to_dict(self._get_entry(session, strategy_id))

        return self._run(_op)

    def list_entries(
        self, state: Optional[str] = None, *, active_only: bool = False
    ) -> pd.DataFrame:
        """List pool entries as a DataFrame (newest first).

        ``active_only`` filters to non-retired strategies — the set used by
        the review pipeline's correlation gate.
        """

        def _op(session: Session) -> pd.DataFrame:
            q = session.query(StrategyPoolEntry)
            if state is not None:
                q = q.filter_by(state=state)
            if active_only:
                q = q.filter(StrategyPoolEntry.state != "retired")
            rows = [_to_dict(e) for e in q.order_by(StrategyPoolEntry.id.desc()).all()]
            return pd.DataFrame(rows)

        return self._run(_op)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _get_entry(session: Session, strategy_id: str) -> StrategyPoolEntry:
        entry = (
            session.query(StrategyPoolEntry)
            .filter_by(strategy_id=strategy_id)
            .one_or_none()
        )
        if entry is None:
            raise KeyError(f"strategy '{strategy_id}' is not registered in the pool")
        return entry


def _history_event(state: str, reason: str) -> Dict[str, str]:
    return {
        "state": state,
        "at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "reason": reason,
    }


def _to_dict(entry: StrategyPoolEntry) -> Dict[str, Any]:
    return {
        "strategy_id": entry.strategy_id,
        "name": entry.name,
        "track": entry.track,
        "state": entry.state,
        "manifest_path": entry.manifest_path,
        "latest_run_id": entry.latest_run_id,
        "latest_verdict": entry.latest_verdict,
        "state_history": json.loads(entry.state_history_json or "[]"),
        "health": json.loads(entry.health_json or "{}"),
        "registered_at": entry.registered_at.isoformat()
        if entry.registered_at
        else None,
    }


__all__ = ["PoolRegistry", "TransitionError", "LIFECYCLE_STATES"]
