"""Metadata DB engine/session helpers for quant datasets."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from quant_data.meta_models import QuantMetaBase
from quant_data.qconfig import QuantDataSettings


def create_meta_engine(settings: QuantDataSettings | None = None):
    s = settings or QuantDataSettings.from_env()
    return create_engine(s.meta_db_url)


def init_meta_db(settings: QuantDataSettings | None = None) -> None:
    engine = create_meta_engine(settings)
    QuantMetaBase.metadata.create_all(bind=engine)


def create_session_factory(settings: QuantDataSettings | None = None):
    engine = create_meta_engine(settings)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_meta_db_context(settings: QuantDataSettings | None = None) -> Generator[Session, None, None]:
    """Context manager that commits/rolls back like backend.get_db_context()."""

    SessionLocal = create_session_factory(settings)
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

