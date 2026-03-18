"""Cerebro configuration management.

Follows the Pydantic BaseSettings pattern from backend/config.py.
All settings load from environment variables with CEREBRO_ prefix.
"""

import os
from pathlib import Path
from typing import List, Tuple

from pydantic import Field
from pydantic_settings import BaseSettings

try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


class CerebroSourceConfig(BaseSettings):
    """Source connector configuration."""

    arxiv_categories: List[str] = Field(
        default_factory=lambda: ["q-fin.PM", "q-fin.ST", "q-fin.TR", "q-fin.CP"],
        description="arXiv quantitative finance categories to monitor",
    )
    arxiv_delay_seconds: float = Field(
        default=3.0,
        description="Rate limit delay between arXiv requests",
    )
    ssrn_delay_seconds: float = Field(
        default=5.0,
        description="Rate limit delay between SSRN requests",
    )
    blog_feeds: List[str] = Field(
        default_factory=lambda: [
            "https://www.aqr.com/Insights/Research/rss",
            "https://www.man.com/maninstitute/rss",
            "https://www.twosigma.com/feed/",
            "https://alphaarchitect.com/feed/",
            "https://quantocracy.com/feed/",
        ],
        description="RSS feed URLs for blog sources",
    )
    reddit_subreddits: List[str] = Field(
        default_factory=lambda: ["quant", "algotrading"],
        description="Reddit subreddits to monitor (requires PRAW)",
    )
    reddit_enabled: bool = Field(
        default=False,
        description="Enable Reddit source (requires PRAW + credentials)",
    )

    class Config:
        env_prefix = "CEREBRO_SOURCE_"


class CerebroLLMConfig(BaseSettings):
    """LLM configuration for Cerebro summarization and extraction."""

    bulk_model: str = Field(
        default="qwen-turbo",
        description="Model for bulk summarization (cheapest)",
    )
    premium_model: str = Field(
        default="qwen-plus",
        description="Model for top-scored papers (higher quality)",
    )
    max_tokens: int = Field(
        default=2000,
        description="Max tokens for LLM response",
    )
    temperature: float = Field(
        default=0.2,
        description="Low temperature for structured extraction",
    )
    daily_budget_usd: float = Field(
        default=0.50,
        description="Daily LLM cost budget in USD",
    )

    class Config:
        env_prefix = "CEREBRO_LLM_"


class CerebroStorageConfig(BaseSettings):
    """Storage configuration for Cerebro."""

    chromadb_path: str = Field(
        default="data/cerebro/chromadb",
        description="Path for ChromaDB file-based storage",
    )
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence-transformers model for embeddings",
    )
    dedup_threshold: float = Field(
        default=0.85,
        description="Cosine similarity threshold for deduplication (above = duplicate)",
    )
    novelty_threshold: float = Field(
        default=0.70,
        description="Cosine similarity threshold for novelty (above 0.7 = rehash)",
    )

    class Config:
        env_prefix = "CEREBRO_STORAGE_"


class CerebroScoringConfig(BaseSettings):
    """Scoring configuration for Cerebro."""

    # Our portfolio's primary asset classes
    target_asset_classes: List[str] = Field(
        default_factory=lambda: ["Equities", "FX"],
        description="Primary asset classes in our portfolio",
    )
    # Data sources we have access to
    available_data_sources: List[str] = Field(
        default_factory=lambda: [
            "yfinance",
            "FRED",
            "Stooq",
            "Binance",
            "IBKR",
            "Polygon",
            "ECB_FX",
        ],
        description="Data sources available in our infrastructure",
    )
    # Minimum composite score to flag for review
    min_composite_score: float = Field(
        default=50.0,
        description="Minimum composite score (0-100) to flag paper for review",
    )

    class Config:
        env_prefix = "CEREBRO_SCORING_"


class CerebroConfig:
    """Top-level Cerebro configuration aggregating all sub-configs."""

    def __init__(self) -> None:
        self.sources = CerebroSourceConfig()
        self.llm = CerebroLLMConfig()
        self.storage = CerebroStorageConfig()
        self.scoring = CerebroScoringConfig()

    @property
    def project_root(self) -> Path:
        """Return the project root directory."""
        return Path(__file__).parent.parent

    @property
    def chromadb_abs_path(self) -> Path:
        """Return absolute path to ChromaDB storage."""
        path = Path(self.storage.chromadb_path)
        if not path.is_absolute():
            path = self.project_root / path
        return path


# Global config instance
cerebro_config = CerebroConfig()
