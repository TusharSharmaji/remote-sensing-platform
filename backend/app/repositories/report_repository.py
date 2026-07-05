"""Data access layer for Report entities."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.prediction import Prediction
from app.models.report import Report, ReportFormat, ReportStatus


class ReportRepository:
    """Encapsulates all direct database access for the Report model."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to a SQLAlchemy session."""
        self._db = db

    def create(
        self,
        *,
        project_id: uuid.UUID,
        title: str,
        format: ReportFormat = ReportFormat.PDF,
        generated_by: uuid.UUID | None = None,
        prediction_ids: list[uuid.UUID] | None = None,
    ) -> Report:
        """Persist and return a new pending report, optionally linked to predictions."""
        report = Report(
            project_id=project_id, title=title, format=format, generated_by=generated_by
        )
        if prediction_ids:
            stmt = select(Prediction).where(Prediction.id.in_(prediction_ids))
            report.predictions = list(self._db.execute(stmt).scalars().all())
        self._db.add(report)
        self._db.commit()
        self._db.refresh(report)
        return report

    def get_by_id(self, report_id: uuid.UUID) -> Report | None:
        """Return the report with the given id, or None if not found."""
        return self._db.get(Report, report_id)

    def list_by_project(self, project_id: uuid.UUID) -> list[Report]:
        """Return all reports belonging to the given project."""
        stmt = (
            select(Report)
            .where(Report.project_id == project_id)
            .order_by(Report.created_at.desc())
        )
        return list(self._db.execute(stmt).scalars().all())

    def update_status(
        self, report: Report, status: ReportStatus, *, file_path: str | None = None
    ) -> Report:
        """Update a report's status and optionally attach its generated file path."""
        report.status = status
        if file_path is not None:
            report.file_path = file_path
        self._db.commit()
        self._db.refresh(report)
        return report

    def delete(self, report: Report) -> None:
        """Delete a report record."""
        self._db.delete(report)
        self._db.commit()
