"""Kaggle source connector for finance competition writeups.

Fetches winning solutions and notable notebooks from Kaggle finance
competitions via the Kaggle API.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import List, Optional

from cerebro.sources.base import BaseSource, RawPaper

logger = logging.getLogger(__name__)

# Notable Kaggle finance competitions to monitor
FINANCE_COMPETITIONS = (
    "jane-street-market-prediction",
    "optiver-realized-volatility-prediction",
    "optiver-trading-at-the-close",
    "g-research-crypto-forecasting",
    "ubiquant-market-prediction",
    "two-sigma-financial-modeling",
    "two-sigma-financial-news",
    "jpx-tokyo-stock-exchange-prediction",
)


class KaggleSource(BaseSource):
    """Fetches notable notebooks and solutions from Kaggle finance competitions."""

    def __init__(self) -> None:
        super().__init__(name="kaggle")
        self._competitions = FINANCE_COMPETITIONS

    async def fetch_recent(
        self,
        since: datetime,
        limit: int = 50,
    ) -> List[RawPaper]:
        """Fetch recent top notebooks from Kaggle finance competitions.

        Uses the Kaggle API to list kernels for known finance competitions,
        filtering by vote count and recency.

        Args:
            since: Only return notebooks updated after this datetime.
            limit: Maximum number of notebooks to return.

        Returns:
            List of RawPaper instances, newest first.
        """
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi  # noqa: F401
        except ImportError:
            self.logger.error(
                "kaggle library not installed or not configured. "
                "Run: pip install kaggle && configure ~/.kaggle/kaggle.json"
            )
            return []

        papers = await asyncio.get_event_loop().run_in_executor(
            None,
            self._fetch_sync,
            since,
            limit,
        )

        return papers

    def _fetch_sync(
        self,
        since: datetime,
        limit: int,
    ) -> List[RawPaper]:
        """Synchronous fetch from Kaggle API — runs in thread pool.

        Args:
            since: Filter notebooks updated after this date.
            limit: Max total results.

        Returns:
            List of RawPaper instances sorted by date descending.
        """
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        try:
            api.authenticate()
        except Exception as exc:
            self.logger.error("Kaggle authentication failed: %s", exc)
            return []

        all_papers: List[RawPaper] = []

        for competition in self._competitions:
            try:
                notebooks = self._fetch_competition_notebooks(
                    api=api,
                    competition=competition,
                    since=since,
                )
                all_papers.extend(notebooks)
            except Exception as exc:
                self.logger.warning(
                    "Failed to fetch Kaggle competition '%s': %s",
                    competition,
                    exc,
                )

            # Rate limiting between competitions
            time.sleep(1.0)

        # Sort by date descending, take top N
        all_papers.sort(key=lambda p: p.published_date, reverse=True)
        return all_papers[:limit]

    def _fetch_competition_notebooks(
        self,
        api: "KaggleApi",
        competition: str,
        since: datetime,
    ) -> List[RawPaper]:
        """Fetch top notebooks for a single competition.

        Args:
            api: Authenticated Kaggle API client.
            competition: Competition slug.
            since: Filter by last run date.

        Returns:
            List of RawPaper instances.
        """
        try:
            kernels = api.kernels_list(
                competition=competition,
                sort_by="voteCount",
                page_size=20,
            )
        except Exception as exc:
            self.logger.warning("Kaggle API error for '%s': %s", competition, exc)
            return []

        papers: List[RawPaper] = []
        for kernel in kernels:
            paper = self._kernel_to_raw_paper(kernel, competition)
            if paper is None:
                continue
            if paper.published_date < since:
                continue
            papers.append(paper)

        return papers

    def _kernel_to_raw_paper(
        self,
        kernel: "KaggleApi.KernelMetadata",
        competition: str,
    ) -> Optional[RawPaper]:
        """Convert a Kaggle kernel metadata object to RawPaper.

        Args:
            kernel: Kaggle kernel metadata.
            competition: Competition slug for context.

        Returns:
            RawPaper or None if parsing fails.
        """
        try:
            title = getattr(kernel, "title", "")
            if not title:
                return None

            author = getattr(kernel, "author", "")
            ref = getattr(kernel, "ref", "")
            last_run = getattr(kernel, "lastRunTime", None)

            if last_run and isinstance(last_run, str):
                try:
                    published = datetime.fromisoformat(
                        last_run.replace("Z", "+00:00")
                    ).replace(tzinfo=None)
                except ValueError:
                    published = datetime.utcnow()
            elif last_run and isinstance(last_run, datetime):
                published = last_run.replace(tzinfo=None)
            else:
                published = datetime.utcnow()

            url = f"https://www.kaggle.com/code/{ref}" if ref else ""

            return RawPaper(
                source="kaggle",
                source_id=ref or f"kaggle-{hash(title)}",
                title=f"[Kaggle] {title}",
                authors=(author,) if author else (),
                abstract=f"Kaggle notebook for competition: {competition}",
                published_date=published,
                url=url,
                pdf_url=None,
                categories=(competition, "kaggle_competition"),
            )
        except Exception as exc:
            self.logger.warning("Failed to parse Kaggle kernel: %s", exc)
            return None
