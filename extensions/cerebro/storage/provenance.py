"""Provenance tracking for the paper-to-strategy pipeline.

Tracks the full lifecycle: paper DOI -> extracted signal -> validated
backtest -> PM verdict -> strategy tracker. Each transition is recorded
as an IdeaProvenance entry with stage-specific details.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from cerebro.storage.models import IdeaProvenance, ResearchPaper

logger = logging.getLogger(__name__)

# Valid pipeline stages in order
PIPELINE_STAGES = (
    "discovered",
    "summarized",
    "scored",
    "proposed",
    "backtested",
    "reviewed",
    "approved",
    "rejected",
)


class ProvenanceTracker:
    """Tracks the provenance chain of research ideas through the pipeline.

    Records each stage transition with metadata, enabling full audit
    trails from paper discovery to strategy deployment (or rejection).
    """

    def __init__(self, db_session_factory: Any = None) -> None:
        """Initialize the provenance tracker.

        Args:
            db_session_factory: SQLAlchemy session factory. If None,
                attempts to import from backend.database.
        """
        self._session_factory = db_session_factory
        if self._session_factory is None:
            try:
                from backend.database import SessionLocal

                self._session_factory = SessionLocal
            except ImportError:
                logger.warning(
                    "backend.database not available. "
                    "ProvenanceTracker requires a session factory."
                )

    def _get_session(self) -> Any:
        """Get a database session.

        Returns:
            SQLAlchemy Session instance.

        Raises:
            RuntimeError: If session factory is not configured.
        """
        if self._session_factory is None:
            raise RuntimeError(
                "Database session factory not configured for ProvenanceTracker"
            )
        return self._session_factory()

    def record_stage(
        self,
        paper_id: int,
        stage: str,
        agent: str = "cerebro",
        verdict: str = "",
        details: Optional[Dict[str, Any]] = None,
        proposal_path: Optional[str] = None,
        backtest_run_id: Optional[str] = None,
        signal_class: Optional[str] = None,
    ) -> int:
        """Record a pipeline stage transition for a paper.

        Args:
            paper_id: Database ID of the ResearchPaper.
            stage: Pipeline stage name (must be in PIPELINE_STAGES).
            agent: Name of the agent/system recording this entry.
            verdict: Stage outcome (e.g., PASS, FAIL, CONDITIONAL).
            details: Optional dict of stage-specific details.
            proposal_path: Path to generated strategy proposal.
            backtest_run_id: Reference to backtest run.
            signal_class: Generated signal class name.

        Returns:
            Database ID of the new provenance entry.

        Raises:
            ValueError: If stage is not a valid pipeline stage.
            RuntimeError: If database operation fails.
        """
        if stage not in PIPELINE_STAGES:
            raise ValueError(
                f"Invalid stage '{stage}'. Must be one of: {PIPELINE_STAGES}"
            )

        session = self._get_session()
        try:
            entry = IdeaProvenance(
                paper_id=paper_id,
                stage=stage,
                agent=agent,
                verdict=verdict,
                details=json.dumps(details) if details else "",
                proposal_path=proposal_path,
                backtest_run_id=backtest_run_id,
                signal_class=signal_class,
            )

            session.add(entry)

            # Also update the paper's status
            paper = session.query(ResearchPaper).filter_by(id=paper_id).first()
            if paper is not None:
                paper.status = stage
                paper.updated_at = datetime.utcnow()

            session.commit()
            entry_id = entry.id
            logger.info(
                "Recorded provenance: paper_id=%d, stage=%s, agent=%s",
                paper_id,
                stage,
                agent,
            )
            return entry_id

        except Exception as exc:
            session.rollback()
            logger.error("Failed to record provenance: %s", exc)
            raise RuntimeError(f"Provenance recording failed: {exc}")
        finally:
            session.close()

    def get_paper_history(self, paper_id: int) -> List[Dict[str, Any]]:
        """Get the full provenance history for a paper.

        Args:
            paper_id: Database ID of the ResearchPaper.

        Returns:
            List of provenance entry dicts, ordered by creation time.
        """
        session = self._get_session()
        try:
            entries = (
                session.query(IdeaProvenance)
                .filter_by(paper_id=paper_id)
                .order_by(IdeaProvenance.created_at.asc())
                .all()
            )

            return [
                {
                    "id": e.id,
                    "stage": e.stage,
                    "agent": e.agent,
                    "verdict": e.verdict,
                    "details": self._parse_details(e.details),
                    "proposal_path": e.proposal_path,
                    "backtest_run_id": e.backtest_run_id,
                    "signal_class": e.signal_class,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
                for e in entries
            ]
        finally:
            session.close()

    def get_papers_at_stage(
        self,
        stage: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get papers currently at a specific pipeline stage.

        Args:
            stage: Pipeline stage to query.
            limit: Maximum number of results.

        Returns:
            List of paper dicts with basic info.
        """
        if stage not in PIPELINE_STAGES:
            raise ValueError(
                f"Invalid stage '{stage}'. Must be one of: {PIPELINE_STAGES}"
            )

        session = self._get_session()
        try:
            papers = (
                session.query(ResearchPaper)
                .filter_by(status=stage)
                .order_by(ResearchPaper.composite_score.desc())
                .limit(limit)
                .all()
            )

            return [
                {
                    "id": p.id,
                    "title": p.title,
                    "source": p.source,
                    "source_id": p.source_id,
                    "composite_score": p.composite_score,
                    "status": p.status,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in papers
            ]
        finally:
            session.close()

    def get_provenance_chain(self, paper_id: int) -> Dict[str, Any]:
        """Get the full provenance chain for a paper as a structured dict.

        This provides the complete paper -> proposal -> backtest -> verdict
        chain in a single view.

        Args:
            paper_id: Database ID of the ResearchPaper.

        Returns:
            Dict with paper info and ordered stage entries.
        """
        session = self._get_session()
        try:
            paper = session.query(ResearchPaper).filter_by(id=paper_id).first()
            if paper is None:
                return {"error": f"Paper {paper_id} not found"}

            entries = (
                session.query(IdeaProvenance)
                .filter_by(paper_id=paper_id)
                .order_by(IdeaProvenance.created_at.asc())
                .all()
            )

            return {
                "paper": {
                    "id": paper.id,
                    "title": paper.title,
                    "source": paper.source,
                    "url": paper.url,
                    "composite_score": paper.composite_score,
                    "status": paper.status,
                },
                "stages": [
                    {
                        "stage": e.stage,
                        "agent": e.agent,
                        "verdict": e.verdict,
                        "details": self._parse_details(e.details),
                        "proposal_path": e.proposal_path,
                        "backtest_run_id": e.backtest_run_id,
                        "created_at": e.created_at.isoformat()
                        if e.created_at
                        else None,
                    }
                    for e in entries
                ],
            }
        finally:
            session.close()

    @staticmethod
    def _parse_details(details_str: str) -> Dict[str, Any]:
        """Parse details JSON string to dict.

        Args:
            details_str: JSON string or empty string.

        Returns:
            Parsed dict or empty dict.
        """
        if not details_str:
            return {}
        try:
            return json.loads(details_str)
        except (json.JSONDecodeError, TypeError):
            return {"raw": details_str}
