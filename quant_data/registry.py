"""Dataset registry helpers.

These helpers keep metadata DB usage simple and explicit.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from quant_data.meta_models import Dataset, DatasetVersion, IngestionRun
from quant_data.spec import DatasetId


def _utc_now_tag() -> str:
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class RegisterResult:
    dataset_id: int
    dataset_version_id: int
    version: str


def get_or_create_dataset(db: Session, *, ds: DatasetId, description: str = "") -> Dataset:
    existing = (
        db.query(Dataset)
        .filter(
            Dataset.provider == ds.provider,
            Dataset.kind == ds.kind.value,
            Dataset.universe == ds.universe,
            Dataset.frequency == ds.frequency.value,
        )
        .one_or_none()
    )
    if existing:
        return existing

    created = Dataset(
        provider=ds.provider,
        kind=ds.kind.value,
        universe=ds.universe,
        frequency=ds.frequency.value,
        description=description,
    )
    db.add(created)
    db.flush()
    return created


def register_dataset_version(
    db: Session,
    *,
    ds: DatasetId,
    version: Optional[str] = None,
    description: str = "",
    start_date: str = "",
    end_date: str = "",
    row_count: int = 0,
    file_count: int = 0,
) -> RegisterResult:
    dataset = get_or_create_dataset(db, ds=ds, description=description)
    tag = version or _utc_now_tag()

    existing = (
        db.query(DatasetVersion)
        .filter(DatasetVersion.dataset_id == dataset.id, DatasetVersion.version == tag)
        .one_or_none()
    )
    if existing:
        return RegisterResult(dataset_id=dataset.id, dataset_version_id=existing.id, version=existing.version)

    dv = DatasetVersion(
        dataset_id=dataset.id,
        version=tag,
        start_date=start_date,
        end_date=end_date,
        row_count=row_count,
        file_count=file_count,
    )
    db.add(dv)
    db.flush()
    return RegisterResult(dataset_id=dataset.id, dataset_version_id=dv.id, version=dv.version)


def start_ingestion_run(
    db: Session,
    *,
    dataset_version_id: int,
    parameters: dict[str, Any] | None = None,
) -> IngestionRun:
    run = IngestionRun(
        dataset_version_id=dataset_version_id,
        status="started",
        parameters_json=json.dumps(parameters or {}, sort_keys=True),
    )
    db.add(run)
    db.flush()
    return run


def finish_ingestion_run(db: Session, *, run_id: int, status: str, error: str = "") -> None:
    run = db.query(IngestionRun).filter(IngestionRun.id == run_id).one()
    run.status = status
    run.error = error
    run.finished_at = datetime.utcnow()
    db.add(run)

