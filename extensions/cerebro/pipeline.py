"""Cerebro pipeline orchestrator.

Orchestrates the full discovery flow: fetch from sources, deduplicate,
summarize via LLM, score on relevance/quality/novelty, store results,
and return ranked papers. Cost budget is enforced per run.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from cerebro.config import CerebroConfig, cerebro_config
from cerebro.processing.deduplicator import SemanticDeduplicator
from cerebro.processing.llm_summarizer import CerebroLLMClient
from cerebro.processing.structured_extractor import PaperSummary, extract_paper_summary
from cerebro.scoring.feasibility_scorer import FeasibilityScorer
from cerebro.scoring.novelty_detector import NoveltyDetector
from cerebro.scoring.quality_scorer import QualityScorer
from cerebro.scoring.relevance_scorer import RelevanceScorer
from cerebro.sources.base import BaseSource, RawPaper
from cerebro.storage.models import ResearchPaper
from cerebro.storage.provenance import ProvenanceTracker
from cerebro.storage.vector_store import CerebroVectorStore

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ScoredPaper:
    """Immutable representation of a paper with all scores attached.

    Attributes:
        paper: The original RawPaper from a source connector.
        summary: LLM-extracted structured summary.
        relevance_score: Relevance to our portfolio (0-100).
        quality_score: Methodological quality (0-100).
        novelty_score: Novelty vs existing corpus (0-100).
        composite_score: Weighted average of all scores.
    """

    paper: RawPaper
    summary: PaperSummary
    relevance_score: float
    quality_score: float
    novelty_score: float
    composite_score: float


class CerebroPipeline:
    """Orchestrate: discover -> dedup -> summarize -> score -> rank -> propose."""

    # Default composite score weights
    DEFAULT_WEIGHTS = {
        "relevance": 0.4,
        "quality": 0.3,
        "novelty": 0.3,
    }

    def __init__(
        self,
        config: Optional[CerebroConfig] = None,
        db_session_factory: Any = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> None:
        """Initialize the pipeline with all sub-components.

        Args:
            config: CerebroConfig instance (uses global default if None).
            db_session_factory: SQLAlchemy session factory for DB operations.
            weights: Dict of score weights (relevance, quality, novelty).
        """
        self._config = config or cerebro_config
        self._weights = weights or self.DEFAULT_WEIGHTS
        self._db_session_factory = db_session_factory

        # Processing
        self._llm_client = CerebroLLMClient()
        self._deduplicator = SemanticDeduplicator()

        # Scoring
        self._relevance_scorer = RelevanceScorer()
        self._quality_scorer = QualityScorer()
        self._feasibility_scorer = FeasibilityScorer()
        self._novelty_detector = NoveltyDetector()

        # Storage
        self._vector_store = CerebroVectorStore()
        self._provenance = ProvenanceTracker(db_session_factory=db_session_factory)

        # Sources (loaded lazily)
        self._sources: Optional[List[BaseSource]] = None

        # Run statistics
        self._last_run_stats: Dict[str, Any] = {}

    def _load_sources(self) -> List[BaseSource]:
        """Load all enabled source connectors.

        Returns:
            List of configured BaseSource instances.
        """
        if self._sources is not None:
            return self._sources

        sources: List[BaseSource] = []

        try:
            from cerebro.sources.arxiv import ArxivSource

            sources.append(ArxivSource())
        except Exception as exc:
            logger.warning("Failed to load ArxivSource: %s", exc)

        try:
            from cerebro.sources.ssrn import SSRNSource

            sources.append(SSRNSource())
        except Exception as exc:
            logger.warning("Failed to load SSRNSource: %s", exc)

        try:
            from cerebro.sources.blog_feeds import BlogFeedSource

            sources.append(BlogFeedSource())
        except Exception as exc:
            logger.warning("Failed to load BlogFeedSource: %s", exc)

        try:
            from cerebro.sources.kaggle import KaggleSource

            sources.append(KaggleSource())
        except Exception as exc:
            logger.warning("Failed to load KaggleSource: %s", exc)

        if self._config.sources.reddit_enabled:
            try:
                from cerebro.sources.reddit import RedditSource

                sources.append(RedditSource())
            except Exception as exc:
                logger.warning("Failed to load RedditSource: %s", exc)

        self._sources = sources
        logger.info("Loaded %d source connectors", len(sources))
        return sources

    async def run_discovery(
        self,
        since: Optional[datetime] = None,
        limit: int = 50,
        max_llm_calls: Optional[int] = None,
    ) -> List[ScoredPaper]:
        """Execute the full discovery pipeline.

        Steps:
        1. Fetch from all enabled sources (parallel)
        2. Deduplicate against existing corpus
        3. Summarize with LLM (respects cost budget)
        4. Score (relevance + quality + novelty -> composite)
        5. Store in DB + vector store
        6. Return top-N sorted by composite score

        Args:
            since: Only discover papers after this date. Defaults to 7 days ago.
            limit: Max papers per source.
            max_llm_calls: Budget cap on LLM calls. Defaults to limit.

        Returns:
            List of ScoredPaper sorted by composite score descending.
        """
        since = since or (datetime.utcnow() - timedelta(days=7))
        max_llm_calls = max_llm_calls or limit

        stats = {
            "started_at": datetime.utcnow().isoformat(),
            "papers_fetched": 0,
            "papers_after_dedup": 0,
            "papers_summarized": 0,
            "papers_scored": 0,
            "llm_calls_used": 0,
            "errors": [],
        }

        # Step 1: Fetch from all sources in parallel
        raw_papers = await self._fetch_all_sources(since, limit)
        stats["papers_fetched"] = len(raw_papers)
        logger.info("Fetched %d raw papers from all sources", len(raw_papers))

        if not raw_papers:
            self._last_run_stats = stats
            return []

        # Step 2: Deduplicate against DB and within batch
        unique_papers = self._deduplicate(raw_papers)
        stats["papers_after_dedup"] = len(unique_papers)
        logger.info(
            "After dedup: %d unique papers (removed %d)",
            len(unique_papers),
            len(raw_papers) - len(unique_papers),
        )

        if not unique_papers:
            self._last_run_stats = stats
            return []

        # Step 3: Summarize with LLM (budget-limited)
        summaries = await self._summarize_papers(
            unique_papers, max_calls=max_llm_calls, stats=stats
        )
        stats["papers_summarized"] = len(summaries)

        if not summaries:
            self._last_run_stats = stats
            return []

        # Step 4: Score all summarized papers
        scored = self._score_papers(summaries)
        stats["papers_scored"] = len(scored)

        # Step 5: Store in DB and vector store
        self._store_results(scored)

        # Sort by composite score descending
        ranked = sorted(scored, key=lambda sp: sp.composite_score, reverse=True)

        stats["completed_at"] = datetime.utcnow().isoformat()
        self._last_run_stats = stats

        logger.info(
            "Discovery complete: %d papers scored. Top score: %.1f",
            len(ranked),
            ranked[0].composite_score if ranked else 0.0,
        )

        return ranked

    async def generate_proposals(
        self,
        min_score: float = 60.0,
        top_n: int = 3,
    ) -> List[str]:
        """Generate strategy proposals for top-scored papers.

        Queries the DB for papers above the score threshold and generates
        markdown proposal files via ProposalGenerator.

        Args:
            min_score: Minimum composite score to consider.
            top_n: Maximum number of proposals to generate.

        Returns:
            List of file paths to generated proposal markdown files.
        """
        from cerebro.proposal_generator import ProposalGenerator

        generator = ProposalGenerator()
        proposals: List[str] = []

        # Query papers above threshold from DB
        papers = self._get_top_papers_from_db(min_score, top_n)

        for paper_data in papers:
            try:
                scored = self._reconstruct_scored_paper(paper_data)
                if scored is None:
                    continue

                content = generator.generate(scored)
                path = generator.save_proposal(content, scored)
                proposals.append(path)

                # Record provenance
                self._record_proposal_provenance(paper_data, path)

                logger.info(
                    "Generated proposal for '%s' -> %s",
                    scored.paper.title[:60],
                    path,
                )
            except Exception as exc:
                logger.error(
                    "Failed to generate proposal for paper_id=%s: %s",
                    paper_data.get("id"),
                    exc,
                )

        return proposals

    def get_recent_papers(self, days: int = 7) -> List[Dict[str, Any]]:
        """Query storage for recently discovered papers.

        Args:
            days: Number of days to look back.

        Returns:
            List of paper dicts ordered by composite score descending.
        """
        if self._db_session_factory is None:
            return []

        from datetime import timedelta as _td

        cutoff = datetime.utcnow() - _td(days=days)
        session = self._db_session_factory()
        try:
            papers = (
                session.query(ResearchPaper)
                .filter(ResearchPaper.created_at >= cutoff)
                .order_by(ResearchPaper.composite_score.desc())
                .all()
            )
            return [self._paper_to_dict(p) for p in papers]
        finally:
            session.close()

    def search_papers(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Semantic search for papers via vector store.

        Args:
            query: Free-text search query.
            n_results: Maximum results to return.

        Returns:
            List of search result dicts with id, text, metadata, distance.
        """
        return self._vector_store.search(query=query, n_results=n_results)

    def get_stats(self) -> Dict[str, Any]:
        """Return pipeline statistics.

        Returns comprehensive stats including DB counts by status/source,
        average scores, and vector store size. Falls back to last run
        stats if DB is unavailable.

        Returns:
            Dict with discovery stats including papers found, scored,
            proposed counts, and timing information.
        """
        base_stats = dict(self._last_run_stats)

        if self._db_session_factory is None:
            return base_stats

        session = self._db_session_factory()
        try:
            from sqlalchemy import func

            total = session.query(func.count(ResearchPaper.id)).scalar() or 0

            status_counts = dict(
                session.query(ResearchPaper.status, func.count(ResearchPaper.id))
                .group_by(ResearchPaper.status)
                .all()
            )
            source_counts = dict(
                session.query(ResearchPaper.source, func.count(ResearchPaper.id))
                .group_by(ResearchPaper.source)
                .all()
            )
            avg_score = (
                session.query(func.avg(ResearchPaper.composite_score)).scalar() or 0.0
            )
            above_threshold = (
                session.query(func.count(ResearchPaper.id))
                .filter(
                    ResearchPaper.composite_score
                    >= self._config.scoring.min_composite_score
                )
                .scalar()
                or 0
            )

            vector_count = 0
            try:
                vector_count = self._vector_store.count
            except Exception:
                pass

            db_stats = {
                "total_papers": total,
                "by_status": status_counts,
                "by_source": source_counts,
                "avg_composite_score": round(float(avg_score), 2),
                "above_threshold": above_threshold,
                "min_composite_threshold": self._config.scoring.min_composite_score,
                "vector_store_count": vector_count,
                "configured_sources": [s.name for s in (self._sources or [])],
            }

            return {**base_stats, **db_stats}
        except Exception as exc:
            logger.warning("Failed to query DB stats: %s", exc)
            return base_stats
        finally:
            session.close()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _fetch_all_sources(
        self,
        since: datetime,
        limit: int,
    ) -> List[RawPaper]:
        """Fetch papers from all enabled sources in parallel.

        Args:
            since: Only return papers after this date.
            limit: Max papers per source.

        Returns:
            Flat list of all fetched RawPaper instances.
        """
        sources = self._load_sources()
        if not sources:
            logger.warning("No source connectors loaded")
            return []

        tasks = [source.safe_fetch(since=since, limit=limit) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_papers: List[RawPaper] = []
        for source, result in zip(sources, results):
            if isinstance(result, Exception):
                logger.error("Source %s raised exception: %s", source.name, result)
                continue
            all_papers.extend(result)

        return all_papers

    def _deduplicate(self, papers: List[RawPaper]) -> List[RawPaper]:
        """Deduplicate papers against DB (by source_id) and semantically.

        First checks source_id against existing ResearchPaper entries,
        then runs semantic deduplication on remaining papers.

        Args:
            papers: Raw papers to deduplicate.

        Returns:
            List of unique papers.
        """
        # Phase 1: Check source_id against DB
        db_filtered = self._filter_known_source_ids(papers)

        if not db_filtered:
            return []

        # Phase 2: Semantic deduplication
        unique, _results = self._deduplicator.deduplicate_batch(db_filtered)
        return unique

    def _filter_known_source_ids(
        self,
        papers: List[RawPaper],
    ) -> List[RawPaper]:
        """Filter out papers whose source_id already exists in the DB.

        Args:
            papers: Papers to filter.

        Returns:
            Papers not already in the database.
        """
        if self._db_session_factory is None:
            return papers

        try:
            session = self._db_session_factory()
            try:
                existing_keys = set(
                    row[0] for row in session.query(ResearchPaper.unique_key).all()
                )
            finally:
                session.close()

            novel = [p for p in papers if p.unique_key not in existing_keys]
            removed = len(papers) - len(novel)
            if removed > 0:
                logger.info("DB dedup removed %d already-known papers", removed)
            return novel
        except Exception as exc:
            logger.warning("DB dedup check failed, skipping: %s", exc)
            return papers

    async def _summarize_papers(
        self,
        papers: List[RawPaper],
        max_calls: int,
        stats: Dict[str, Any],
    ) -> List[tuple]:
        """Summarize papers via LLM, respecting budget limits.

        Args:
            papers: Papers to summarize.
            max_calls: Maximum number of LLM API calls.
            stats: Mutable stats dict to update.

        Returns:
            List of (RawPaper, PaperSummary) tuples for successful extractions.
        """
        if not self._llm_client.is_configured:
            logger.warning(
                "LLM client not configured (no API key). " "Skipping summarization."
            )
            return []

        to_process = papers[:max_calls]
        results: List[tuple] = []

        for paper in to_process:
            try:
                summary = await extract_paper_summary(
                    raw_paper=paper,
                    llm_client=self._llm_client,
                )
                results.append((paper, summary))
                stats["llm_calls_used"] = stats.get("llm_calls_used", 0) + 1
            except Exception as exc:
                logger.error(
                    "Summarization failed for '%s': %s",
                    paper.title[:60],
                    exc,
                )
                stats.setdefault("errors", []).append(
                    f"Summarization: {paper.source_id} - {exc}"
                )

        return results

    def _score_papers(
        self,
        summaries: List[tuple],
    ) -> List[ScoredPaper]:
        """Score all summarized papers.

        Args:
            summaries: List of (RawPaper, PaperSummary) tuples.

        Returns:
            List of ScoredPaper with composite scores.
        """
        scored: List[ScoredPaper] = []

        for paper, summary in summaries:
            try:
                rel = self._relevance_scorer.score(summary)
                qual = self._quality_scorer.score(summary)
                novelty = self._novelty_detector.detect(summary)

                composite = (
                    self._weights["relevance"] * rel.total
                    + self._weights["quality"] * qual.total
                    + self._weights["novelty"] * novelty.novelty_score
                )

                scored_paper = ScoredPaper(
                    paper=paper,
                    summary=summary,
                    relevance_score=rel.total,
                    quality_score=qual.total,
                    novelty_score=novelty.novelty_score,
                    composite_score=round(composite, 1),
                )
                scored.append(scored_paper)

                # Add to novelty corpus for future comparisons
                self._novelty_detector.add_to_corpus(
                    paper_id=paper.unique_key,
                    title=paper.title,
                    summary=summary,
                )
            except Exception as exc:
                logger.error(
                    "Scoring failed for '%s': %s",
                    paper.title[:60],
                    exc,
                )

        return scored

    def _store_results(self, scored_papers: List[ScoredPaper]) -> None:
        """Store scored papers in the database and vector store.

        Args:
            scored_papers: Papers with scores to persist.
        """
        for sp in scored_papers:
            # Store in vector store
            try:
                text = (
                    f"{sp.paper.title} {sp.summary.one_line} "
                    f"{sp.summary.methodology}"
                )
                self._vector_store.add_paper(
                    paper_id=sp.paper.unique_key,
                    text=text,
                    metadata={
                        "title": sp.paper.title,
                        "source": sp.paper.source,
                        "composite_score": sp.composite_score,
                        "relevance_score": sp.relevance_score,
                        "quality_score": sp.quality_score,
                        "novelty_score": sp.novelty_score,
                    },
                )
            except Exception as exc:
                logger.error(
                    "Vector store failed for '%s': %s",
                    sp.paper.unique_key,
                    exc,
                )

            # Store in SQL DB
            self._store_paper_in_db(sp)

    def _store_paper_in_db(self, sp: ScoredPaper) -> None:
        """Persist a single ScoredPaper to the SQL database.

        Args:
            sp: ScoredPaper to store.
        """
        if self._db_session_factory is None:
            return

        session = self._db_session_factory()
        try:
            record = ResearchPaper(
                source=sp.paper.source,
                source_id=sp.paper.source_id,
                unique_key=sp.paper.unique_key,
                title=sp.paper.title,
                authors=", ".join(sp.paper.authors),
                abstract=sp.paper.abstract,
                url=sp.paper.url,
                pdf_url=sp.paper.pdf_url or "",
                doi=sp.paper.doi or "",
                categories=", ".join(sp.paper.categories),
                published_date=sp.paper.published_date,
                one_line=sp.summary.one_line,
                methodology=sp.summary.methodology,
                signal_description=sp.summary.signal_description,
                asset_class=", ".join(sp.summary.asset_class),
                expected_sharpe=sp.summary.expected_sharpe,
                data_requirements=", ".join(sp.summary.data_requirements),
                implementation_complexity=sp.summary.implementation_complexity,
                key_findings=" | ".join(sp.summary.key_findings),
                limitations=" | ".join(sp.summary.limitations),
                novelty_claim=sp.summary.novelty_claim,
                backtest_period=sp.summary.backtest_period,
                sample_size=sp.summary.sample_size,
                out_of_sample=sp.summary.out_of_sample,
                transaction_costs_modeled=sp.summary.transaction_costs_modeled,
                relevance_score=sp.relevance_score,
                quality_score=sp.quality_score,
                novelty_score=sp.novelty_score,
                composite_score=sp.composite_score,
                status="scored",
                fetched_at=sp.paper.fetched_at,
                summarized_at=sp.summary.extracted_at,
                scored_at=datetime.utcnow(),
            )

            session.add(record)
            session.commit()

            # Record provenance
            self._provenance.record_stage(
                paper_id=record.id,
                stage="scored",
                agent="cerebro-pipeline",
                verdict="PASS",
                details={
                    "relevance": sp.relevance_score,
                    "quality": sp.quality_score,
                    "novelty": sp.novelty_score,
                    "composite": sp.composite_score,
                },
            )
        except Exception as exc:
            session.rollback()
            logger.error(
                "DB store failed for '%s': %s",
                sp.paper.unique_key,
                exc,
            )
        finally:
            session.close()

    def _get_top_papers_from_db(
        self,
        min_score: float,
        top_n: int,
    ) -> List[Dict[str, Any]]:
        """Query top-scored papers from the database.

        Args:
            min_score: Minimum composite score.
            top_n: Maximum results.

        Returns:
            List of paper dicts from the database.
        """
        if self._db_session_factory is None:
            return []

        session = self._db_session_factory()
        try:
            papers = (
                session.query(ResearchPaper)
                .filter(ResearchPaper.composite_score >= min_score)
                .filter(ResearchPaper.status.in_(["scored", "summarized"]))
                .order_by(ResearchPaper.composite_score.desc())
                .limit(top_n)
                .all()
            )

            return [
                {
                    "id": p.id,
                    "source": p.source,
                    "source_id": p.source_id,
                    "unique_key": p.unique_key,
                    "title": p.title,
                    "authors": p.authors,
                    "abstract": p.abstract,
                    "url": p.url,
                    "pdf_url": p.pdf_url,
                    "doi": p.doi,
                    "categories": p.categories,
                    "published_date": p.published_date,
                    "one_line": p.one_line,
                    "methodology": p.methodology,
                    "signal_description": p.signal_description,
                    "asset_class": p.asset_class,
                    "expected_sharpe": p.expected_sharpe,
                    "data_requirements": p.data_requirements,
                    "implementation_complexity": p.implementation_complexity,
                    "key_findings": p.key_findings,
                    "limitations": p.limitations,
                    "novelty_claim": p.novelty_claim,
                    "backtest_period": p.backtest_period,
                    "sample_size": p.sample_size,
                    "out_of_sample": p.out_of_sample,
                    "transaction_costs_modeled": p.transaction_costs_modeled,
                    "relevance_score": p.relevance_score,
                    "quality_score": p.quality_score,
                    "novelty_score": p.novelty_score,
                    "composite_score": p.composite_score,
                }
                for p in papers
            ]
        finally:
            session.close()

    def _reconstruct_scored_paper(
        self,
        data: Dict[str, Any],
    ) -> Optional[ScoredPaper]:
        """Reconstruct a ScoredPaper from DB data dict.

        Args:
            data: Paper data dict from DB query.

        Returns:
            ScoredPaper or None if reconstruction fails.
        """
        try:
            authors = tuple(
                a.strip() for a in (data.get("authors") or "").split(",") if a.strip()
            )
            categories = tuple(
                c.strip()
                for c in (data.get("categories") or "").split(",")
                if c.strip()
            )

            paper = RawPaper(
                source=data["source"],
                source_id=data["source_id"],
                title=data["title"],
                authors=authors,
                abstract=data.get("abstract", ""),
                published_date=data.get("published_date") or datetime.utcnow(),
                url=data.get("url", ""),
                pdf_url=data.get("pdf_url"),
                categories=categories,
                doi=data.get("doi"),
            )

            asset_classes = tuple(
                a.strip()
                for a in (data.get("asset_class") or "").split(",")
                if a.strip()
            )
            data_reqs = tuple(
                d.strip()
                for d in (data.get("data_requirements") or "").split(",")
                if d.strip()
            )
            findings = tuple(
                f.strip()
                for f in (data.get("key_findings") or "").split("|")
                if f.strip()
            )
            limitations = tuple(
                l.strip()
                for l in (data.get("limitations") or "").split("|")
                if l.strip()
            )

            summary = PaperSummary(
                title=data["title"],
                one_line=data.get("one_line", ""),
                methodology=data.get("methodology", ""),
                signal_description=data.get("signal_description", ""),
                asset_class=asset_classes,
                expected_sharpe=data.get("expected_sharpe"),
                data_requirements=data_reqs,
                implementation_complexity=data.get(
                    "implementation_complexity", "MEDIUM"
                ),
                key_findings=findings,
                limitations=limitations,
                novelty_claim=data.get("novelty_claim", ""),
                backtest_period=data.get("backtest_period"),
                sample_size=data.get("sample_size"),
                out_of_sample=data.get("out_of_sample", False),
                transaction_costs_modeled=data.get("transaction_costs_modeled", False),
                source_id=data["source_id"],
                source=data["source"],
            )

            return ScoredPaper(
                paper=paper,
                summary=summary,
                relevance_score=data.get("relevance_score", 0.0),
                quality_score=data.get("quality_score", 0.0),
                novelty_score=data.get("novelty_score", 0.0),
                composite_score=data.get("composite_score", 0.0),
            )
        except Exception as exc:
            logger.error("Failed to reconstruct ScoredPaper: %s", exc)
            return None

    @staticmethod
    def _paper_to_dict(paper: ResearchPaper) -> Dict[str, Any]:
        """Convert a ResearchPaper ORM object to a plain dict.

        Args:
            paper: ResearchPaper instance.

        Returns:
            Dict representation of the paper.
        """
        return {
            "id": paper.id,
            "source": paper.source,
            "source_id": paper.source_id,
            "unique_key": paper.unique_key,
            "title": paper.title,
            "authors": paper.authors,
            "url": paper.url,
            "published_date": (
                paper.published_date.isoformat() if paper.published_date else None
            ),
            "one_line": paper.one_line,
            "methodology": paper.methodology,
            "signal_description": paper.signal_description,
            "asset_class": paper.asset_class,
            "composite_score": paper.composite_score,
            "relevance_score": paper.relevance_score,
            "quality_score": paper.quality_score,
            "novelty_score": paper.novelty_score,
            "novelty_classification": paper.novelty_classification,
            "is_feasible": paper.is_feasible,
            "implementation_complexity": paper.implementation_complexity,
            "status": paper.status,
            "created_at": paper.created_at.isoformat() if paper.created_at else None,
        }

    def _record_proposal_provenance(
        self,
        paper_data: Dict[str, Any],
        proposal_path: str,
    ) -> None:
        """Record provenance entry for a generated proposal.

        Args:
            paper_data: DB paper dict.
            proposal_path: File path to the proposal markdown.
        """
        try:
            self._provenance.record_stage(
                paper_id=paper_data["id"],
                stage="proposed",
                agent="cerebro-pipeline",
                verdict="GENERATED",
                proposal_path=proposal_path,
            )
        except Exception as exc:
            logger.error(
                "Failed to record proposal provenance for paper %s: %s",
                paper_data.get("id"),
                exc,
            )
