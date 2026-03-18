"""Cerebro API routes for research discovery, search, and proposals.

Follows the same FastAPI router patterns as backend/api/research_routes.py.
Provides endpoints for listing papers, triggering discovery, semantic
search, and managing auto-generated proposals.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cerebro", tags=["cerebro"])


def _get_db_session_factory():
    """Get DB session factory from backend."""
    try:
        from backend.database import SessionLocal

        return SessionLocal
    except ImportError:
        return None


def _get_pipeline():
    """Create a CerebroPipeline instance."""
    from cerebro.pipeline import CerebroPipeline

    return CerebroPipeline(db_session_factory=_get_db_session_factory())


# ------------------------------------------------------------------
# Papers endpoints
# ------------------------------------------------------------------


@router.get("/papers")
async def list_papers(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
    min_score: Optional[float] = Query(
        None, description="Minimum composite score filter"
    ),
    source: Optional[str] = Query(
        None, description="Filter by source (arxiv, ssrn, blog, etc.)"
    ),
    status: Optional[str] = Query(
        None, description="Filter by status (discovered, scored, proposed, etc.)"
    ),
    sort_by: str = Query("composite_score", description="Sort field"),
    order: str = Query("desc", description="Sort order (asc/desc)"),
):
    """List discovered papers with scores and pagination.

    Returns papers sorted by composite score by default, with optional
    filters for source, status, and minimum score.
    """
    session_factory = _get_db_session_factory()
    if session_factory is None:
        raise HTTPException(
            status_code=503,
            detail="Database not available",
        )

    from cerebro.storage.models import ResearchPaper

    session = session_factory()
    try:
        query = session.query(ResearchPaper)

        # Apply filters
        if min_score is not None:
            query = query.filter(ResearchPaper.composite_score >= min_score)
        if source:
            query = query.filter(ResearchPaper.source == source)
        if status:
            query = query.filter(ResearchPaper.status == status)

        # Count total before pagination
        total = query.count()

        # Sort
        sort_column = getattr(ResearchPaper, sort_by, ResearchPaper.composite_score)
        if order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Paginate
        offset = (page - 1) * per_page
        papers = query.offset(offset).limit(per_page).all()

        return {
            "status": "success",
            "total": total,
            "page": page,
            "per_page": per_page,
            "data": [_paper_to_dict(p) for p in papers],
        }
    except Exception as exc:
        logger.error("Failed to list papers: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        session.close()


@router.get("/papers/{paper_id}")
async def get_paper(paper_id: int):
    """Get full paper details including summary and provenance history.

    Args:
        paper_id: Database ID of the paper.
    """
    session_factory = _get_db_session_factory()
    if session_factory is None:
        raise HTTPException(status_code=503, detail="Database not available")

    from cerebro.storage.models import ResearchPaper
    from cerebro.storage.provenance import ProvenanceTracker

    session = session_factory()
    try:
        paper = session.query(ResearchPaper).filter_by(id=paper_id).first()
        if paper is None:
            raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

        tracker = ProvenanceTracker(db_session_factory=session_factory)
        history = tracker.get_paper_history(paper_id)

        result = _paper_to_dict(paper)
        result["provenance"] = history

        return {
            "status": "success",
            "data": result,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to get paper %d: %s", paper_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        session.close()


# ------------------------------------------------------------------
# Discovery endpoints
# ------------------------------------------------------------------


@router.post("/discover")
async def trigger_discovery(
    background_tasks: BackgroundTasks,
    limit: int = Query(50, ge=1, le=200, description="Max papers per source"),
    days_back: int = Query(7, ge=1, le=90, description="Look back N days"),
    max_llm_calls: Optional[int] = Query(
        None, ge=1, le=100, description="Budget cap on LLM calls"
    ),
):
    """Trigger a manual discovery pipeline run.

    Runs in the background to avoid request timeout. Returns immediately
    with a confirmation message. Check /stats for progress.
    """
    since = datetime.utcnow() - __import__("datetime").timedelta(days=days_back)

    async def _run_discovery():
        try:
            pipeline = _get_pipeline()
            scored = await pipeline.run_discovery(
                since=since,
                limit=limit,
                max_llm_calls=max_llm_calls,
            )
            logger.info(
                "Manual discovery complete: %d papers scored",
                len(scored),
            )
        except Exception as exc:
            logger.error("Manual discovery failed: %s", exc, exc_info=True)

    background_tasks.add_task(_run_discovery)

    return {
        "status": "success",
        "message": (
            f"Discovery started in background (limit={limit}, "
            f"days_back={days_back}). Check /api/cerebro/stats for progress."
        ),
    }


# ------------------------------------------------------------------
# Search endpoint
# ------------------------------------------------------------------


@router.get("/search")
async def semantic_search(
    q: str = Query(..., min_length=2, description="Search query"),
    n_results: int = Query(10, ge=1, le=50, description="Max results"),
):
    """Semantic search over discovered papers via vector store.

    Uses ChromaDB embeddings for meaning-based search rather than
    keyword matching.
    """
    try:
        from cerebro.storage.vector_store import CerebroVectorStore

        store = CerebroVectorStore()
        results = store.search(query=q, n_results=n_results)

        return {
            "status": "success",
            "query": q,
            "count": len(results),
            "data": results,
        }
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Vector store dependencies not available: {exc}",
        )
    except Exception as exc:
        logger.error("Semantic search failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ------------------------------------------------------------------
# Proposal endpoints
# ------------------------------------------------------------------


@router.get("/proposals")
async def list_proposals():
    """List all auto-generated strategy proposals.

    Scans the research/strategies/ directory for files matching
    the auto_*.md pattern.
    """
    try:
        from pathlib import Path

        from cerebro.config import cerebro_config

        strategies_dir = cerebro_config.project_root / "research" / "strategies"
        if not strategies_dir.exists():
            return {"status": "success", "count": 0, "data": []}

        proposals = []
        for filepath in sorted(strategies_dir.glob("auto_*.md"), reverse=True):
            stat = filepath.stat()
            # Read first few lines for metadata
            header = _read_proposal_header(filepath)
            proposals.append(
                {
                    "filename": filepath.name,
                    "path": str(filepath),
                    "size_bytes": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    **header,
                }
            )

        return {
            "status": "success",
            "count": len(proposals),
            "data": proposals,
        }
    except Exception as exc:
        logger.error("Failed to list proposals: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/proposals/{paper_id}/generate")
async def generate_proposal(paper_id: int):
    """Generate a strategy proposal for a specific paper.

    The paper must already be scored (status = 'scored').

    Args:
        paper_id: Database ID of the paper.
    """
    session_factory = _get_db_session_factory()
    if session_factory is None:
        raise HTTPException(status_code=503, detail="Database not available")

    from cerebro.storage.models import ResearchPaper

    session = session_factory()
    try:
        paper = session.query(ResearchPaper).filter_by(id=paper_id).first()
        if paper is None:
            raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

        if paper.status not in ("scored", "summarized"):
            raise HTTPException(
                status_code=400,
                detail=f"Paper status is '{paper.status}', must be 'scored' or 'summarized'",
            )

        pipeline = _get_pipeline()
        paper_data = _paper_to_dict(paper)
        scored = pipeline._reconstruct_scored_paper(paper_data)

        if scored is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to reconstruct paper for proposal generation",
            )

        from cerebro.proposal_generator import ProposalGenerator

        generator = ProposalGenerator()
        content = generator.generate(scored)
        path = generator.save_proposal(content, scored)

        # Record provenance
        from cerebro.storage.provenance import ProvenanceTracker

        tracker = ProvenanceTracker(db_session_factory=session_factory)
        tracker.record_stage(
            paper_id=paper_id,
            stage="proposed",
            agent="cerebro-api",
            verdict="GENERATED",
            proposal_path=path,
        )

        return {
            "status": "success",
            "message": f"Proposal generated for '{paper.title[:60]}'",
            "path": path,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Proposal generation failed for paper %d: %s", paper_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        session.close()


# ------------------------------------------------------------------
# Stats endpoint
# ------------------------------------------------------------------


@router.get("/stats")
async def get_stats():
    """Get discovery statistics and cost tracking.

    Returns stats from the last pipeline run, plus aggregate DB counts.
    """
    stats: Dict[str, Any] = {}

    # Get last run stats from pipeline (if available)
    try:
        pipeline = _get_pipeline()
        stats["last_run"] = pipeline.get_stats()
    except Exception:
        stats["last_run"] = {}

    # Get aggregate DB stats
    session_factory = _get_db_session_factory()
    if session_factory is not None:
        session = session_factory()
        try:
            from cerebro.storage.models import ResearchPaper

            stats["db"] = {
                "total_papers": session.query(ResearchPaper).count(),
                "scored_papers": (
                    session.query(ResearchPaper).filter_by(status="scored").count()
                ),
                "proposed_papers": (
                    session.query(ResearchPaper).filter_by(status="proposed").count()
                ),
                "avg_composite_score": _safe_avg(
                    session.query(ResearchPaper.composite_score)
                    .filter(ResearchPaper.composite_score > 0)
                    .all()
                ),
            }
        except Exception as exc:
            logger.warning("Failed to get DB stats: %s", exc)
            stats["db"] = {"error": str(exc)}
        finally:
            session.close()

    # Get vector store count
    try:
        from cerebro.storage.vector_store import CerebroVectorStore

        store = CerebroVectorStore()
        stats["vector_store"] = {"document_count": store.count}
    except Exception:
        stats["vector_store"] = {"document_count": 0}

    return {
        "status": "success",
        "data": stats,
    }


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _paper_to_dict(paper) -> Dict[str, Any]:
    """Convert a ResearchPaper ORM instance to a dict.

    Args:
        paper: ResearchPaper instance.

    Returns:
        Dict with all paper fields.
    """
    return {
        "id": paper.id,
        "source": paper.source,
        "source_id": paper.source_id,
        "unique_key": paper.unique_key,
        "title": paper.title,
        "authors": paper.authors,
        "abstract": paper.abstract,
        "url": paper.url,
        "pdf_url": paper.pdf_url,
        "doi": paper.doi,
        "categories": paper.categories,
        "published_date": (
            paper.published_date.isoformat() if paper.published_date else None
        ),
        "one_line": paper.one_line,
        "methodology": paper.methodology,
        "signal_description": paper.signal_description,
        "asset_class": paper.asset_class,
        "expected_sharpe": paper.expected_sharpe,
        "data_requirements": paper.data_requirements,
        "implementation_complexity": paper.implementation_complexity,
        "key_findings": paper.key_findings,
        "limitations": paper.limitations,
        "novelty_claim": paper.novelty_claim,
        "backtest_period": paper.backtest_period,
        "sample_size": paper.sample_size,
        "out_of_sample": paper.out_of_sample,
        "transaction_costs_modeled": paper.transaction_costs_modeled,
        "relevance_score": paper.relevance_score,
        "quality_score": paper.quality_score,
        "novelty_score": paper.novelty_score,
        "feasibility_score": paper.feasibility_score,
        "composite_score": paper.composite_score,
        "novelty_classification": paper.novelty_classification,
        "status": paper.status,
        "created_at": paper.created_at.isoformat() if paper.created_at else None,
        "updated_at": paper.updated_at.isoformat() if paper.updated_at else None,
    }


def _read_proposal_header(filepath) -> Dict[str, str]:
    """Read the first few lines of a proposal for metadata.

    Args:
        filepath: Path to the markdown file.

    Returns:
        Dict with title and source info extracted from header.
    """
    try:
        text = filepath.read_text(encoding="utf-8")
        lines = text.split("\n", 5)
        title = ""
        source = ""
        for line in lines:
            if line.startswith("# "):
                title = line.lstrip("# ").strip()
            if "**Source:**" in line:
                source = line
                break
        return {"title": title, "source_line": source}
    except Exception:
        return {"title": "", "source_line": ""}


def _safe_avg(rows: list) -> Optional[float]:
    """Compute average from a list of single-element tuples.

    Args:
        rows: List of (value,) tuples from SQLAlchemy query.

    Returns:
        Average float or None if empty.
    """
    values = [r[0] for r in rows if r[0] is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 1)
