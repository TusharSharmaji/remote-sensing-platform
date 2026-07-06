"""Report ORM model and its many-to-many association with predictions."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, String, Table, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.prediction import Prediction
    from app.models.project import Project
    from app.models.user import User


class ReportFormat(str, enum.Enum):
    """Output file format of a generated report."""

    PDF = "PDF"
    DOCX = "DOCX"
    HTML = "HTML"


class ReportStatus(str, enum.Enum):
    """Generation lifecycle status of a report."""

    PENDING = "PENDING"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


report_predictions = Table(
    "report_predictions",
    Base.metadata,
    Column(
        "report_id",
        Uuid(as_uuid=True),
        ForeignKey("reports.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "prediction_id",
        Uuid(as_uuid=True),
        ForeignKey("predictions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Report(Base):
    """Represents a generated report summarizing one or more predictions for a project."""

    __tablename__ = "reports"
    __table_args__ = (Index("ix_reports_project_id_status", "project_id", "status"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    generated_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    format: Mapped[ReportFormat] = mapped_column(
        Enum(ReportFormat, name="report_format"), default=ReportFormat.PDF, nullable=False
    )
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="report_status"), default=ReportStatus.PENDING, nullable=False
    )
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    project: Mapped["Project"] = relationship(back_populates="reports")
    generated_by_user: Mapped["User | None"] = relationship(back_populates="reports_generated")
    predictions: Mapped[list["Prediction"]] = relationship(
        secondary=report_predictions, back_populates="reports"
    )

    def __repr__(self) -> str:
        """Return a debug-friendly representation of the report."""
        return f"<Report id={self.id} title={self.title} status={self.status}>"
