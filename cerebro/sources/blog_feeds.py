"""Blog RSS feed source connector for industry research.

Monitors RSS feeds from major quantitative finance research publishers:
AQR Insights, Man Institute, Two Sigma, Alpha Architect, Quantocracy.
"""

import asyncio
import logging
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from cerebro.config import cerebro_config
from cerebro.sources.base import BaseSource, RawPaper

logger = logging.getLogger(__name__)

# Human-readable names for known feed URLs
FEED_NAMES: Dict[str, str] = {
    "aqr.com": "aqr_insights",
    "man.com": "man_institute",
    "twosigma.com": "two_sigma",
    "alphaarchitect.com": "alpha_architect",
    "quantocracy.com": "quantocracy",
}


def _infer_feed_name(url: str) -> str:
    """Infer a short name from feed URL domain.

    Args:
        url: RSS feed URL.

    Returns:
        Short name string for the feed.
    """
    for domain_fragment, name in FEED_NAMES.items():
        if domain_fragment in url:
            return name
    # Fallback: extract domain
    match = re.search(r"https?://(?:www\.)?([^/]+)", url)
    if match:
        return match.group(1).replace(".", "_")
    return "unknown_blog"


class BlogFeedSource(BaseSource):
    """Fetches articles from quantitative finance blog RSS feeds."""

    def __init__(self) -> None:
        super().__init__(name="blog_feeds")
        self._feed_urls = cerebro_config.sources.blog_feeds

    async def fetch_recent(
        self,
        since: datetime,
        limit: int = 50,
    ) -> List[RawPaper]:
        """Fetch recent articles from all configured blog RSS feeds.

        Args:
            since: Only return articles published after this datetime.
            limit: Maximum number of articles to return.

        Returns:
            List of RawPaper instances, newest first.
        """
        try:
            import feedparser  # noqa: F401
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
        """Synchronous fetch from all blog feeds — runs in thread pool.

        Args:
            since: Filter articles published after this date.
            limit: Max total results.

        Returns:
            List of RawPaper instances sorted by date descending.
        """
        all_papers: List[RawPaper] = []

        for feed_url in self._feed_urls:
            feed_name = _infer_feed_name(feed_url)
            try:
                feed_papers = self._parse_single_feed(
                    feed_url=feed_url,
                    feed_name=feed_name,
                    since=since,
                )
                all_papers.extend(feed_papers)
            except Exception as exc:
                self.logger.error(
                    "Error parsing blog feed '%s' (%s): %s",
                    feed_name,
                    feed_url,
                    exc,
                )

            # Small delay between feeds to be polite
            time.sleep(1.0)

        # Sort by published date descending, take top N
        all_papers.sort(key=lambda p: p.published_date, reverse=True)
        return all_papers[:limit]

    def _parse_single_feed(
        self,
        feed_url: str,
        feed_name: str,
        since: datetime,
    ) -> List[RawPaper]:
        """Parse a single RSS feed.

        Args:
            feed_url: URL of the RSS feed.
            feed_name: Human-readable feed name.
            since: Filter articles published after this date.

        Returns:
            List of RawPaper instances from this feed.
        """
        import feedparser

        self.logger.debug("Parsing blog feed: %s (%s)", feed_name, feed_url)
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
        entry: dict,
        feed_name: str,
    ) -> Optional[RawPaper]:
        """Convert a feedparser entry to a RawPaper.

        Args:
            entry: Single RSS feed entry.
            feed_name: Name of the source blog.

        Returns:
            RawPaper or None if the entry cannot be parsed.
        """
        try:
            title = entry.get("title", "").strip()
            if not title:
                return None

            link = entry.get("link", "")
            published = self._parse_date(entry)
            if published is None:
                published = datetime.utcnow()

            # Generate a stable source_id from link or title
            source_id = link or f"{feed_name}-{hash(title)}"

            # Extract summary/description
            summary = entry.get("summary", entry.get("description", ""))
            summary = self._strip_html(summary).strip()

            # Truncate very long summaries
            if len(summary) > 2000:
                summary = summary[:2000] + "..."

            # Extract authors
            authors = self._extract_authors(entry)

            # Extract tags/categories
            tags = self._extract_tags(entry)

            return RawPaper(
                source=f"blog_{feed_name}",
                source_id=source_id,
                title=title,
                authors=authors,
                abstract=summary,
                published_date=published,
                url=link,
                pdf_url=None,
                categories=tags,
            )
        except Exception as exc:
            self.logger.warning(
                "Failed to parse blog entry from '%s': %s", feed_name, exc
            )
            return None

    def _parse_date(self, entry: dict) -> Optional[datetime]:
        """Parse publication date from feed entry.

        Args:
            entry: feedparser entry dict.

        Returns:
            Parsed datetime or None.
        """
        date_fields = ["published_parsed", "updated_parsed", "created_parsed"]
        for field in date_fields:
            parsed = entry.get(field)
            if parsed is not None:
                try:
                    return datetime(*parsed[:6])
                except (ValueError, TypeError):
                    continue
        return None

    def _extract_authors(self, entry: dict) -> Tuple[str, ...]:
        """Extract author names from feed entry.

        Args:
            entry: feedparser entry dict.

        Returns:
            Tuple of author name strings.
        """
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

    def _extract_tags(self, entry: dict) -> Tuple[str, ...]:
        """Extract category/tag labels from feed entry.

        Args:
            entry: feedparser entry dict.

        Returns:
            Tuple of tag strings.
        """
        tags = entry.get("tags", [])
        if tags:
            return tuple(
                t.get("term", "").strip() for t in tags if t.get("term", "").strip()
            )
        return ()

    @staticmethod
    def _strip_html(text: str) -> str:
        """Remove HTML tags from text.

        Args:
            text: Potentially HTML-containing string.

        Returns:
            Plain text string.
        """
        return re.sub(r"<[^>]+>", "", text)
