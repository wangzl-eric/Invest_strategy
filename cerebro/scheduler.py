"""Cerebro scheduler integration with APScheduler.

Provides two modes:
1. CerebroScheduler — standalone scheduler with start/stop/run_now
2. setup_cerebro_scheduler() — hook into an existing APScheduler instance

Follows the same patterns as backend/scheduler.py.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

from cerebro.config import CerebroConfig, cerebro_config

logger = logging.getLogger(__name__)


class CerebroScheduler:
    """Standalone scheduler for Cerebro discovery and digest jobs.

    Wraps APScheduler's AsyncIOScheduler to run:
    - Daily discovery at 06:00 UTC
    - Weekly digest on Monday at 08:00 UTC

    Includes rate limiting between source fetches via the pipeline's
    per-source safe_fetch delays (configured in CerebroSourceConfig).
    """

    def __init__(
        self,
        config: Optional[CerebroConfig] = None,
        discovery_hour: int = 6,
        discovery_minute: int = 0,
    ) -> None:
        """Initialize the Cerebro scheduler.

        Args:
            config: CerebroConfig instance. Uses global default if None.
            discovery_hour: UTC hour for daily discovery (0-23).
            discovery_minute: UTC minute for daily discovery (0-59).
        """
        self._config = config or cerebro_config
        self._discovery_hour = discovery_hour
        self._discovery_minute = discovery_minute
        self._scheduler = None
        self._running = False

    @property
    def is_running(self) -> bool:
        """Whether the scheduler is currently active."""
        return self._running and self._scheduler is not None

    def start(self) -> None:
        """Start the scheduler with all Cerebro jobs.

        Creates an AsyncIOScheduler and adds the discovery + digest jobs.
        Safe to call multiple times (idempotent).

        Raises:
            ImportError: If APScheduler is not installed.
        """
        if self._running:
            logger.warning("CerebroScheduler is already running")
            return

        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from apscheduler.triggers.cron import CronTrigger
        except ImportError:
            raise ImportError("apscheduler not installed. Run: pip install apscheduler")

        self._scheduler = AsyncIOScheduler()

        # Daily discovery
        self._scheduler.add_job(
            _run_cerebro_discovery,
            trigger=CronTrigger(
                hour=self._discovery_hour,
                minute=self._discovery_minute,
            ),
            args=[self._config],
            id="cerebro_daily_discovery",
            name="Cerebro daily research discovery",
            replace_existing=True,
        )

        # Weekly digest on Monday at 08:00 UTC
        self._scheduler.add_job(
            _generate_weekly_digest,
            trigger=CronTrigger(day_of_week="mon", hour=8, minute=0),
            args=[self._config],
            id="cerebro_weekly_digest",
            name="Cerebro weekly research digest",
            replace_existing=True,
        )

        self._scheduler.start()
        self._running = True

        logger.info(
            "CerebroScheduler started: daily discovery at %02d:%02d UTC, "
            "weekly digest Monday 08:00 UTC",
            self._discovery_hour,
            self._discovery_minute,
        )

    def stop(self) -> None:
        """Stop the scheduler gracefully.

        Waits for currently running jobs to finish. Safe to call
        multiple times (idempotent).
        """
        if not self._running or self._scheduler is None:
            logger.debug("CerebroScheduler is not running; nothing to stop")
            return

        self._scheduler.shutdown(wait=True)
        self._running = False
        logger.info("CerebroScheduler stopped")

    async def run_now(self) -> None:
        """Trigger an immediate discovery run (bypasses schedule).

        Useful for manual triggers via CLI or API endpoint.
        Does not require the scheduler to be running.
        """
        logger.info("Manual Cerebro discovery triggered via run_now()")
        await _run_cerebro_discovery(config=self._config)


async def _run_cerebro_discovery(
    config: Optional[CerebroConfig] = None,
) -> None:
    """Execute a full Cerebro discovery pipeline run.

    Called by APScheduler on the configured schedule. Creates a fresh
    pipeline instance for each run to avoid stale state.

    Args:
        config: CerebroConfig instance. Uses global default if None.
    """
    config = config or cerebro_config

    logger.info("Starting scheduled Cerebro discovery run")
    start_time = datetime.utcnow()

    try:
        from cerebro.pipeline import CerebroPipeline

        # Attempt to get DB session factory from backend
        db_session_factory = _get_db_session_factory()

        pipeline = CerebroPipeline(
            config=config,
            db_session_factory=db_session_factory,
        )

        scored = await pipeline.run_discovery()

        if scored:
            # Auto-generate proposals for high-scoring papers
            min_score = config.scoring.min_composite_score
            proposals = await pipeline.generate_proposals(
                min_score=min_score,
                top_n=3,
            )

            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                "Cerebro discovery complete: %d papers scored, %d proposals "
                "generated in %.1fs",
                len(scored),
                len(proposals),
                elapsed,
            )
        else:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                "Cerebro discovery complete: no new papers found (%.1fs)",
                elapsed,
            )

    except Exception as exc:
        logger.error(
            "Cerebro discovery run failed: %s",
            exc,
            exc_info=True,
        )


async def _generate_weekly_digest(
    config: Optional[CerebroConfig] = None,
) -> None:
    """Generate a weekly digest of top discoveries.

    Queries the database for the top papers discovered in the last
    7 days and writes a digest markdown file.

    Args:
        config: CerebroConfig instance. Uses global default if None.
    """
    config = config or cerebro_config

    logger.info("Generating weekly Cerebro digest")

    try:
        from cerebro.storage.models import ResearchPaper

        db_session_factory = _get_db_session_factory()
        if db_session_factory is None:
            logger.warning("No DB session factory available for digest")
            return

        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(days=7)

        session = db_session_factory()
        try:
            papers = (
                session.query(ResearchPaper)
                .filter(ResearchPaper.created_at >= cutoff)
                .order_by(ResearchPaper.composite_score.desc())
                .limit(10)
                .all()
            )

            if not papers:
                logger.info("No papers found for weekly digest")
                return

            digest = _format_digest(papers)
            _save_digest(digest, config)

            logger.info(
                "Weekly digest generated with %d papers",
                len(papers),
            )
        finally:
            session.close()

    except Exception as exc:
        logger.error(
            "Weekly digest generation failed: %s",
            exc,
            exc_info=True,
        )


def setup_cerebro_scheduler(
    scheduler: Any,
    config: Optional[CerebroConfig] = None,
) -> None:
    """Add Cerebro jobs to an existing APScheduler instance.

    This function should be called during application startup to
    register Cerebro's scheduled jobs alongside the backend's
    existing scheduled jobs.

    Args:
        scheduler: APScheduler AsyncIOScheduler or BackgroundScheduler.
        config: CerebroConfig instance. Uses global default if None.
    """
    config = config or cerebro_config

    try:
        from apscheduler.triggers.cron import CronTrigger

        # Job 1: Daily discovery at 06:00 UTC
        scheduler.add_job(
            _run_cerebro_discovery,
            trigger=CronTrigger(hour=6, minute=0),
            args=[config],
            id="cerebro_daily_discovery",
            name="Cerebro daily research discovery",
            replace_existing=True,
        )

        # Job 2: Weekly digest on Monday at 08:00 UTC
        scheduler.add_job(
            _generate_weekly_digest,
            trigger=CronTrigger(day_of_week="mon", hour=8, minute=0),
            args=[config],
            id="cerebro_weekly_digest",
            name="Cerebro weekly research digest",
            replace_existing=True,
        )

        logger.info(
            "Cerebro scheduler registered: daily discovery (06:00 UTC), "
            "weekly digest (Monday 08:00 UTC)"
        )

    except ImportError:
        logger.warning(
            "apscheduler not available. Cerebro scheduled jobs not registered."
        )
    except Exception as exc:
        logger.error("Failed to register Cerebro scheduler jobs: %s", exc)


def _get_db_session_factory() -> Any:
    """Attempt to get the DB session factory from the backend.

    Returns:
        SessionLocal factory or None if unavailable.
    """
    try:
        from backend.database import SessionLocal

        return SessionLocal
    except ImportError:
        logger.debug("backend.database not available for Cerebro scheduler")
        return None


def _format_digest(papers: list) -> str:
    """Format a list of ResearchPaper records into a markdown digest.

    Args:
        papers: List of ResearchPaper ORM instances.

    Returns:
        Markdown string.
    """
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    lines = [
        f"# Cerebro Weekly Digest - {date_str}",
        "",
        f"Top {len(papers)} papers discovered this week:",
        "",
    ]

    for i, paper in enumerate(papers, 1):
        lines.extend(
            [
                f"## {i}. {paper.title}",
                "",
                f"- **Source:** {paper.source} | "
                f"**Score:** {paper.composite_score:.1f}/100 | "
                f"**Status:** {paper.status}",
                f"- **Summary:** {paper.one_line}",
                f"- **URL:** {paper.url}",
                "",
            ]
        )

    lines.append(f"---\n*Generated by Cerebro on {date_str}*")

    return "\n".join(lines)


def _save_digest(content: str, config: CerebroConfig) -> None:
    """Save digest markdown to the research directory.

    Args:
        content: Markdown content string.
        config: CerebroConfig for project root.
    """
    from pathlib import Path

    digest_dir = config.project_root / "research" / "digests"
    digest_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.utcnow().strftime("%Y%m%d")
    filepath = digest_dir / f"digest_{date_str}.md"
    filepath.write_text(content, encoding="utf-8")

    logger.info("Saved weekly digest: %s", filepath)
