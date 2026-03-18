"""arXiv source connector for quantitative finance papers.

Uses the `arxiv` library to search q-fin.* categories.
Rate limits to 3-second delays between API calls per arXiv guidelines.
"""

import asyncio
import logging
from datetime import datetime
from typing import List

from cerebro.config import cerebro_config
from cerebro.sources.base import BaseSource, RawPaper

logger = logging.getLogger(__name__)


class ArxivSource(BaseSource):
    """Fetches quantitative finance papers from arXiv.

    Monitors these categories by default:
    - q-fin.PM (Portfolio Management)
    - q-fin.ST (Statistical Finance)
    - q-fin.TR (Trading and Market Microstructure)
    - q-fin.CP (Computational Finance)
    """

    def __init__(self) -> None:
        super().__init__(name="arxiv")
        self._categories = cerebro_config.sources.arxiv_categories
        self._delay = cerebro_config.sources.arxiv_delay_seconds

    def _build_query(self, categories: List[str]) -> str:
        """Build arXiv API query string for multiple categories.

        Args:
            categories: List of arXiv category strings.

        Returns:
            Query string combining categories with OR.
        """
        cat_queries = [f"cat:{cat}" for cat in categories]
        return " OR ".join(cat_queries)

    async def fetch_recent(
        self,
        since: datetime,
        limit: int = 50,
    ) -> List[RawPaper]:
        """Fetch recent papers from arXiv q-fin categories.

        Args:
            since: Only return papers published after this datetime.
            limit: Maximum number of papers to return.

        Returns:
            List of RawPaper instances, newest first.

        Raises:
            ImportError: If the arxiv library is not installed.
        """
        try:
            import arxiv
        except ImportError:
            self.logger.error("arxiv library not installed. Run: pip install arxiv")
            return []

        query = self._build_query(self._categories)
        self.logger.info(
            "Searching arXiv: query='%s', limit=%d, since=%s",
            query,
            limit,
            since.isoformat(),
        )

        # Run the blocking arxiv API call in a thread pool
        papers = await asyncio.get_event_loop().run_in_executor(
            None,
            self._fetch_sync,
            query,
            limit,
            since,
        )

        return papers

    def _fetch_sync(
        self,
        query: str,
        limit: int,
        since: datetime,
    ) -> List[RawPaper]:
        """Synchronous fetch — runs in thread pool.

        Args:
            query: arXiv API query string.
            limit: Max results to fetch.
            since: Filter papers published after this date.

        Returns:
            List of RawPaper instances.
        """
        import time

        import arxiv

        client = arxiv.Client(
            page_size=min(limit, 100),
            delay_seconds=self._delay,
            num_retries=3,
        )

        search = arxiv.Search(
            query=query,
            max_results=limit * 2,  # Over-fetch to account for date filtering
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        papers: List[RawPaper] = []
        try:
            for result in client.results(search):
                published = result.published.replace(tzinfo=None)

                if published < since:
                    # Results are sorted newest-first; stop when we pass the cutoff
                    break

                paper = self._result_to_raw_paper(result, published)
                papers.append(paper)

                if len(papers) >= limit:
                    break

                # Additional rate limiting between processing results
                time.sleep(0.1)

        except Exception as exc:
            self.logger.error("Error during arXiv fetch: %s", exc)

        return papers

    def _result_to_raw_paper(
        self,
        result: "arxiv.Result",
        published: datetime,
    ) -> RawPaper:
        """Convert an arxiv.Result to a RawPaper.

        Args:
            result: arXiv search result object.
            published: Pre-parsed publication datetime.

        Returns:
            Frozen RawPaper dataclass.
        """
        authors = tuple(author.name for author in result.authors)
        categories = tuple(result.categories)

        pdf_url = result.pdf_url if result.pdf_url else None
        doi = result.doi if result.doi else None

        # arXiv IDs look like "2301.12345v1"
        source_id = result.entry_id.split("/abs/")[-1] if result.entry_id else ""

        return RawPaper(
            source="arxiv",
            source_id=source_id,
            title=result.title.strip(),
            authors=authors,
            abstract=result.summary.strip() if result.summary else "",
            published_date=published,
            url=result.entry_id,
            pdf_url=pdf_url,
            categories=categories,
            doi=doi,
        )
