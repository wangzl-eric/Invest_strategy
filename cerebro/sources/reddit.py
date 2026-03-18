"""Reddit source connector for quant finance discussions.

Optional connector that requires PRAW (Python Reddit API Wrapper) and
Reddit API credentials. Monitors r/quant and r/algotrading for
research-quality posts.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import List, Optional, Tuple

from cerebro.config import cerebro_config
from cerebro.sources.base import BaseSource, RawPaper

logger = logging.getLogger(__name__)

# Minimum score (upvotes) for a post to be considered research-quality
MIN_SCORE = 10

# Flair/tag keywords that indicate research content
RESEARCH_FLAIRS = frozenset(
    {
        "research",
        "paper",
        "academic",
        "strategy",
        "backtesting",
        "quantitative",
        "analysis",
        "data",
        "machine learning",
        "ml",
        "statistical",
        "alpha",
        "factor",
    }
)


class RedditSource(BaseSource):
    """Fetches research-quality posts from quant finance subreddits.

    Requires PRAW and Reddit API credentials:
    - REDDIT_CLIENT_ID
    - REDDIT_CLIENT_SECRET
    - REDDIT_USER_AGENT
    """

    def __init__(self) -> None:
        super().__init__(name="reddit")
        self._subreddits = cerebro_config.sources.reddit_subreddits
        self._enabled = cerebro_config.sources.reddit_enabled

    async def fetch_recent(
        self,
        since: datetime,
        limit: int = 50,
    ) -> List[RawPaper]:
        """Fetch research-quality posts from configured subreddits.

        Only fetches if Reddit source is enabled in config. Posts are
        filtered by minimum score and optionally by research-related flair.

        Args:
            since: Only return posts created after this datetime.
            limit: Maximum number of posts to return.

        Returns:
            List of RawPaper instances, newest first.
        """
        if not self._enabled:
            self.logger.debug("Reddit source disabled in config")
            return []

        try:
            import praw  # noqa: F401
        except ImportError:
            self.logger.error("praw library not installed. Run: pip install praw")
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
        """Synchronous fetch from Reddit API — runs in thread pool.

        Args:
            since: Filter posts created after this date.
            limit: Max total results.

        Returns:
            List of RawPaper instances sorted by date descending.
        """
        import os

        import praw

        client_id = os.getenv("REDDIT_CLIENT_ID", "")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
        user_agent = os.getenv(
            "REDDIT_USER_AGENT",
            "cerebro-research-bot:v0.1 (research discovery)",
        )

        if not client_id or not client_secret:
            self.logger.error("REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set")
            return []

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

        all_papers: List[RawPaper] = []
        since_timestamp = since.timestamp()

        for subreddit_name in self._subreddits:
            try:
                posts = self._fetch_subreddit(
                    reddit=reddit,
                    subreddit_name=subreddit_name,
                    since_timestamp=since_timestamp,
                    limit=limit,
                )
                all_papers.extend(posts)
            except Exception as exc:
                self.logger.error("Error fetching from r/%s: %s", subreddit_name, exc)

            time.sleep(2.0)  # Rate limiting between subreddits

        # Sort by date descending, take top N
        all_papers.sort(key=lambda p: p.published_date, reverse=True)
        return all_papers[:limit]

    def _fetch_subreddit(
        self,
        reddit: "praw.Reddit",
        subreddit_name: str,
        since_timestamp: float,
        limit: int,
    ) -> List[RawPaper]:
        """Fetch research posts from a single subreddit.

        Args:
            reddit: Authenticated PRAW Reddit instance.
            subreddit_name: Name of the subreddit (without r/).
            since_timestamp: Unix timestamp cutoff.
            limit: Max posts to fetch.

        Returns:
            List of RawPaper instances.
        """
        subreddit = reddit.subreddit(subreddit_name)
        papers: List[RawPaper] = []

        # Fetch recent "hot" and "new" posts
        for post in subreddit.new(limit=min(limit * 2, 100)):
            if post.created_utc < since_timestamp:
                break

            if post.score < MIN_SCORE:
                continue

            paper = self._post_to_raw_paper(post, subreddit_name)
            if paper is not None:
                papers.append(paper)

            if len(papers) >= limit:
                break

        return papers

    def _post_to_raw_paper(
        self,
        post: "praw.models.Submission",
        subreddit_name: str,
    ) -> Optional[RawPaper]:
        """Convert a Reddit submission to a RawPaper.

        Args:
            post: PRAW Submission object.
            subreddit_name: Name of the subreddit.

        Returns:
            RawPaper or None if the post is not research-relevant.
        """
        try:
            title = post.title.strip()
            if not title:
                return None

            # Build abstract from selftext (truncated)
            selftext = (post.selftext or "").strip()
            if len(selftext) > 2000:
                selftext = selftext[:2000] + "..."

            published = datetime.utcfromtimestamp(post.created_utc)

            flair = (post.link_flair_text or "").lower()
            categories = self._build_categories(subreddit_name, flair)

            return RawPaper(
                source="reddit",
                source_id=f"reddit-{post.id}",
                title=title,
                authors=(str(post.author),) if post.author else (),
                abstract=selftext,
                published_date=published,
                url=f"https://reddit.com{post.permalink}",
                pdf_url=post.url if post.url.endswith(".pdf") else None,
                categories=categories,
            )
        except Exception as exc:
            self.logger.warning("Failed to parse Reddit post: %s", exc)
            return None

    def _build_categories(
        self,
        subreddit_name: str,
        flair: str,
    ) -> Tuple[str, ...]:
        """Build category tags from subreddit name and post flair.

        Args:
            subreddit_name: Name of the subreddit.
            flair: Post flair text (lowercase).

        Returns:
            Tuple of category strings.
        """
        cats = [f"r/{subreddit_name}"]
        if flair:
            cats.append(flair)
        return tuple(cats)
