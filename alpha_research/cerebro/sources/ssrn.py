"""SSRN source connector for financial economics research papers.

Uses feedparser to parse SSRN RSS feeds. No scraping required.
Rate limits to 5-second delays between requests.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from cerebro.config import cerebro_config
from cerebro.sources.base import BaseSource, RawPaper

logger = logging.getLogger(__name__)

# SSRN RSS feed URLs for financial economics categories
SSRN_FEEDS: Dict[str, str] = {
    "financial_economics": (
        "https://papers.ssrn.com/sol3/Jeljour_results.cfm"
        "?form_name=journalBrowse&journal_id=2966286&Network=no&lim=false&npage=1"
        "&SortOrder=ab_approval_date&stype=rss"
    ),
    "capital_markets": (
        "https://papers.ssrn.com/sol3/Jeljour_results.cfm"
        "?form_name=journalBrowse&journal_id=2966309&Network=no&lim=false&npage=1"
        "&SortOrder=ab_approval_date&stype=rss"
    ),
    "risk_management": (
        "https://papers.ssrn.com/sol3/Jeljour_results.cfm"
        "?form_name=journalBrowse&journal_id=2966339&Network=no&lim=false&npage=1"
        "&SortOrder=ab_approval_date&stype=rss"
    ),
}


class SSRNSource(BaseSource):
    """Fetches financial economics papers from SSRN RSS feeds."""

    def __init__(self) -> None:
        super().__init__(name="ssrn")
        self._delay = cerebro_config.sources.ssrn_delay_seconds
        self._feeds = SSRN_FEEDS

    async def fetch_recent(
        self,
        since: datetime,
        limit: int = 50,
    ) -> List[RawPaper]:
        """Fetch recent papers from SSRN RSS feeds.

        Iterates through all configured SSRN category feeds, parses entries,
        and filters by publication date.

        Args:
            since: Only return papers published after this datetime.
            limit: Maximum number of papers to return.

        Returns:
            List of RawPaper instances, newest first.
        """
        try:
            import feedparser
        except ImportError:
            self.logger.error(
                "feedparser library not installed. Run: pip install feedparser"
            )
            return []

        papers = await asyncio.get_event_loop().run_in_executor(
            None,
            self._fetch_all_feeds_sync,
            since,
            limit,
        )

        return papers

    def _fetch_all_feeds_sync(
        self,
        since: datetime,
        limit: int,
    ) -> List[RawPaper]:
        """Synchronous fetch from all SSRN feeds — runs in thread pool.

        Args:
            since: Filter papers published after this date.
            limit: Max total results.

        Returns:
            List of RawPaper instances sorted by date descending.
        """
        all_papers: List[RawPaper] = []
        seen_ids: set = set()

        for feed_name, feed_url in self._feeds.items():
            try:
                feed_papers = self._parse_single_feed(
                    feed_name=feed_name,
                    feed_url=feed_url,
                    since=since,
                )
                for paper in feed_papers:
                    if paper.source_id not in seen_ids:
                        seen_ids.add(paper.source_id)
                        all_papers.append(paper)
            except Exception as exc:
                self.logger.error("Error parsing SSRN feed '%s': %s", feed_name, exc)

            # Rate limiting between feeds
            time.sleep(self._delay)

        # Sort by published date descending, take top N
        all_papers.sort(key=lambda p: p.published_date, reverse=True)
        return all_papers[:limit]

    def _parse_single_feed(
        self,
        feed_name: str,
        feed_url: str,
        since: datetime,
    ) -> List[RawPaper]:
        """Parse a single SSRN RSS feed.

        Args:
            feed_name: Human-readable name for logging.
            feed_url: URL of the RSS feed.
            since: Filter papers published after this date.

        Returns:
            List of RawPaper instances from this feed.
        """
        import feedparser

        self.logger.debug("Parsing SSRN feed: %s", feed_name)
        feed = feedparser.parse(feed_url)

        if feed.bozo and feed.bozo_exception:
            self.logger.warning(
                "Feed parse warning for '%s': %s",
                feed_name,
                feed.bozo_exception,
            )

        papers: List[RawPaper] = []
        for entry in feed.entries:
            paper = self._entry_to_raw_paper(entry, feed_name)
            if paper is None:
                continue
            if paper.published_date < since:
                continue
            papers.append(paper)

        return papers

    def _entry_to_raw_paper(
        self,
        entry: "feedparser.FeedParserDict",
        feed_name: str,
    ) -> Optional[RawPaper]:
        """Convert a feedparser entry to a RawPaper.

        Args:
            entry: Single RSS feed entry.
            feed_name: Name of the feed for categorization.

        Returns:
            RawPaper or None if entry cannot be parsed.
        """
        try:
            title = entry.get("title", "").strip()
            if not title:
                return None

            # Parse publication date
            published = self._parse_date(entry)
            if published is None:
                published = datetime.utcnow()

            # Extract SSRN abstract ID from link
            link = entry.get("link", "")
            source_id = self._extract_ssrn_id(link)

            # Extract authors
            authors = self._extract_authors(entry)

            abstract = entry.get("summary", entry.get("description", "")).strip()
            # Clean HTML tags from abstract
            abstract = self._strip_html(abstract)

            return RawPaper(
                source="ssrn",
                source_id=source_id or f"ssrn-{hash(title)}",
                title=title,
                authors=authors,
                abstract=abstract,
                published_date=published,
                url=link,
                pdf_url=None,  # SSRN PDFs require login
                categories=(feed_name,),
            )
        except Exception as exc:
            self.logger.warning("Failed to parse SSRN entry: %s", exc)
            return None

    def _parse_date(self, entry: dict) -> Optional[datetime]:
        """Parse publication date from feed entry.

        Args:
            entry: feedparser entry dict.

        Returns:
            Parsed datetime or None.
        """
        import time as time_mod

        date_fields = ["published_parsed", "updated_parsed", "created_parsed"]
        for field in date_fields:
            parsed = entry.get(field)
            if parsed is not None:
                try:
                    return datetime(*parsed[:6])
                except (ValueError, TypeError):
                    continue
        return None

    def _extract_ssrn_id(self, url: str) -> str:
        """Extract SSRN abstract ID from URL.

        Args:
            url: SSRN paper URL.

        Returns:
            SSRN abstract ID string, or empty string.
        """
        # URLs look like: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1234567
        if "abstract_id=" in url:
            return url.split("abstract_id=")[-1].split("&")[0]
        # Fallback: last numeric segment
        parts = url.rstrip("/").split("/")
        for part in reversed(parts):
            if part.isdigit():
                return part
        return ""

    def _extract_authors(self, entry: dict) -> Tuple[str, ...]:
        """Extract author names from feed entry.

        Args:
            entry: feedparser entry dict.

        Returns:
            Tuple of author name strings.
        """
        # feedparser may put authors in 'authors' list or 'author' string
        authors_list = entry.get("authors", [])
        if authors_list:
            return tuple(
                a.get("name", "").strip()
                for a in authors_list
                if a.get("name", "").strip()
            )
        author_str = entry.get("author", "")
        if author_str:
            return tuple(name.strip() for name in author_str.split(",") if name.strip())
        return ()

    @staticmethod
    def _strip_html(text: str) -> str:
        """Remove HTML tags from text.

        Args:
            text: Potentially HTML-containing string.

        Returns:
            Plain text string.
        """
        import re

        return re.sub(r"<[^>]+>", "", text).strip()
