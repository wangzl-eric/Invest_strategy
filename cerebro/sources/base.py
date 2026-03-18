"""Base classes for research source connectors.

Defines the RawPaper frozen dataclass and BaseSource ABC that all
source connectors must implement.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RawPaper:
    """Immutable representation of a raw research paper/article.

    This is the common interchange format between source connectors
    and the processing pipeline. All fields are populated on a
    best-effort basis by each connector.

    Attributes:
        source: Origin of the paper (e.g., "arxiv", "ssrn", "aqr_blog").
        source_id: Unique identifier from the source (e.g., arXiv ID, SSRN ID).
        title: Title of the paper or article.
        authors: Tuple of author names (frozen for immutability).
        abstract: Abstract or summary text.
        published_date: Publication or posting date.
        url: Direct URL to the paper or article.
        pdf_url: URL to the PDF if available.
        categories: Tuple of category/topic tags from the source.
        doi: Digital Object Identifier if available.
        fetched_at: Timestamp when this paper was fetched.
    """

    source: str
    source_id: str
    title: str
    authors: Tuple[str, ...]
    abstract: str
    published_date: datetime
    url: str
    pdf_url: Optional[str] = None
    categories: Tuple[str, ...] = ()
    doi: Optional[str] = None
    fetched_at: datetime = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        """Set fetched_at to now if not provided."""
        if self.fetched_at is None:
            # Workaround for frozen dataclass: use object.__setattr__
            object.__setattr__(self, "fetched_at", datetime.utcnow())

    @property
    def unique_key(self) -> str:
        """Return a unique key combining source and source_id."""
        return f"{self.source}:{self.source_id}"


class BaseSource(ABC):
    """Abstract base class for research paper source connectors.

    All source connectors must implement `fetch_recent()` which returns
    a list of RawPaper instances. Connectors should:
    - Handle rate limiting internally
    - Return frozen RawPaper dataclasses
    - Log errors and continue (never crash the pipeline)
    - Respect the `since` and `limit` parameters
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.logger = logging.getLogger(f"cerebro.sources.{name}")

    @abstractmethod
    async def fetch_recent(
        self,
        since: datetime,
        limit: int = 50,
    ) -> List[RawPaper]:
        """Fetch recently published papers from this source.

        Args:
            since: Only return papers published after this datetime.
            limit: Maximum number of papers to return.

        Returns:
            List of RawPaper instances, newest first.
        """
        ...

    async def safe_fetch(
        self,
        since: datetime,
        limit: int = 50,
    ) -> List[RawPaper]:
        """Fetch with error handling — logs errors, returns empty list on failure.

        This is the recommended entry point for pipeline orchestration.
        It wraps fetch_recent() with try/except so one broken connector
        does not crash the entire discovery run.

        Args:
            since: Only return papers published after this datetime.
            limit: Maximum number of papers to return.

        Returns:
            List of RawPaper instances, or empty list on error.
        """
        try:
            papers = await self.fetch_recent(since=since, limit=limit)
            self.logger.info(
                "Fetched %d papers from %s (since=%s)",
                len(papers),
                self.name,
                since.isoformat(),
            )
            return papers
        except Exception as exc:
            self.logger.error(
                "Failed to fetch from %s: %s",
                self.name,
                exc,
                exc_info=True,
            )
            return []
