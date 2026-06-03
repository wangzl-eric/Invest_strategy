"""SQLAlchemy models for Cerebro research paper storage.

Follows the same patterns as backend/models.py:
- Uses the shared Base from backend.models
- Consistent column naming and type conventions
- Index on frequently queried fields
"""

import logging
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

logger = logging.getLogger(__name__)

# Import the shared Base — this ensures Cerebro tables are created
# alongside existing backend tables when init_db() is called.
try:
    from backend.models import Base
except ImportError:
    # Standalone usage: create a local Base
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()


class ResearchPaper(Base):
    """A discovered research paper with extracted summary and scores.

    Stores the full lifecycle of a paper from discovery through scoring.
    Links to IdeaProvenance for tracking the paper-to-strategy pipeline.
    """

    __tablename__ = "cerebro_papers"

    id = Column(Integer, primary_key=True, index=True)

    # Source identification
    source = Column(String(50), nullable=False, index=True)
    source_id = Column(String(255), nullable=False, index=True)
    unique_key = Column(String(310), nullable=False, unique=True, index=True)

    # Paper metadata
    title = Column(Text, nullable=False)
    authors = Column(Text, default="")  # Comma-separated
    abstract = Column(Text, default="")
    url = Column(String(500), default="")
    pdf_url = Column(String(500), default="")
    doi = Column(String(100), default="", index=True)
    categories = Column(Text, default="")  # Comma-separated
    published_date = Column(DateTime, index=True)

    # LLM-extracted summary fields
    one_line = Column(Text, default="")
    methodology = Column(Text, default="")
    signal_description = Column(Text, default="")
    asset_class = Column(String(255), default="")  # Comma-separated
    expected_sharpe = Column(Float, nullable=True)
    data_requirements = Column(Text, default="")  # Comma-separated
    implementation_complexity = Column(String(10), default="MEDIUM")
    key_findings = Column(Text, default="")  # Pipe-separated
    limitations = Column(Text, default="")  # Pipe-separated
    novelty_claim = Column(Text, default="")
    backtest_period = Column(String(50), nullable=True)
    sample_size = Column(String(100), nullable=True)
    out_of_sample = Column(Boolean, default=False)
    transaction_costs_modeled = Column(Boolean, default=False)

    # Scores
    relevance_score = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    feasibility_score = Column(Float, default=0.0)
    novelty_score = Column(Float, default=0.0)
    composite_score = Column(Float, default=0.0, index=True)
    score_details = Column(Text, default="")

    # Novelty detection
    novelty_classification = Column(
        String(20), default="UNKNOWN"
    )  # NOVEL, INCREMENTAL, REHASH
    most_similar_paper_id = Column(String(310), nullable=True)
    max_similarity = Column(Float, default=0.0)

    # Feasibility
    is_feasible = Column(Boolean, default=True)
    feasibility_blockers = Column(Text, default="")
    estimated_effort_days = Column(Integer, default=0)

    # Pipeline status
    status = Column(
        String(20), default="discovered", index=True
    )  # discovered, summarized, scored, proposed, reviewed, rejected

    # Timestamps
    fetched_at = Column(DateTime, default=datetime.utcnow)
    summarized_at = Column(DateTime, nullable=True)
    scored_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    provenance_entries = relationship(
        "IdeaProvenance",
        back_populates="paper",
        cascade="all, delete-orphan",
    )


class IdeaProvenance(Base):
    """Tracks the provenance chain: paper -> proposal -> backtest -> verdict.

    Each row represents a stage in the pipeline. Multiple rows per paper
    create a full audit trail.
    """

    __tablename__ = "cerebro_provenance"

    id = Column(Integer, primary_key=True, index=True)

    # Link to the source paper
    paper_id = Column(
        Integer,
        ForeignKey("cerebro_papers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Pipeline stage
    stage = Column(
        String(30), nullable=False, index=True
    )  # discovered, summarized, scored, proposed, backtested, reviewed, approved, rejected

    # Stage-specific data
    details = Column(Text, default="")  # JSON blob with stage-specific info
    agent = Column(String(50), default="")  # Which agent/system created this entry
    verdict = Column(
        String(30), default=""
    )  # Stage outcome (e.g., PASS, FAIL, CONDITIONAL)

    # References to generated artifacts
    proposal_path = Column(
        String(500), nullable=True
    )  # Path to strategy proposal markdown
    backtest_run_id = Column(String(100), nullable=True)  # Reference to backtest run
    signal_class = Column(String(200), nullable=True)  # Generated signal class name

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    paper = relationship("ResearchPaper", back_populates="provenance_entries")
