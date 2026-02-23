"""SQLAlchemy models for dataset registry / lineage metadata.

This is intentionally separate from the IBKR analytics DB models (`backend/models.py`).
You can point it at SQLite for local dev or Postgres in production.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


QuantMetaBase = declarative_base()


class Dataset(QuantMetaBase):
    __tablename__ = "qdata_datasets"
    __table_args__ = (
        UniqueConstraint("provider", "kind", "universe", "frequency", name="uq_qdata_dataset_identity"),
    )

    id = Column(Integer, primary_key=True)
    provider = Column(String, nullable=False, index=True)
    kind = Column(String, nullable=False, index=True)
    universe = Column(String, nullable=False, index=True)
    frequency = Column(String, nullable=False, index=True)

    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    versions = relationship("DatasetVersion", back_populates="dataset", cascade="all, delete-orphan")


class DatasetVersion(QuantMetaBase):
    __tablename__ = "qdata_dataset_versions"
    __table_args__ = (
        UniqueConstraint("dataset_id", "version", name="uq_qdata_dataset_version"),
    )

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("qdata_datasets.id"), nullable=False, index=True)
    version = Column(String, nullable=False, index=True)  # e.g. 2026-01-12T00:00Z or semantic

    # Optional range/size metadata (populate when known)
    start_date = Column(String, default="")
    end_date = Column(String, default="")
    row_count = Column(Integer, default=0)
    file_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    dataset = relationship("Dataset", back_populates="versions")
    runs = relationship("IngestionRun", back_populates="dataset_version", cascade="all, delete-orphan")


class IngestionRun(QuantMetaBase):
    __tablename__ = "qdata_ingestion_runs"

    id = Column(Integer, primary_key=True)
    dataset_version_id = Column(Integer, ForeignKey("qdata_dataset_versions.id"), nullable=False, index=True)

    status = Column(String, nullable=False, default="started")  # started/success/failed
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime)

    parameters_json = Column(Text, default="{}")  # keep sqlite-friendly
    error = Column(Text, default="")

    dataset_version = relationship("DatasetVersion", back_populates="runs")

