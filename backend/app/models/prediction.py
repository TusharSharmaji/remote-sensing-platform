"""Prediction ORM model representing AI inference output for a satellite image."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from geoalchemy2 import Geometry
from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Index, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.report import Report
    from app.models.satellite_image import SatelliteImage


class PredictionType(str, enum.Enum):
    """Category of AI analysis performed on a satellite image."""

    SEGMENTATION = "SEGMENTATION"
    LAND_COVER_CLASSIFICATION = "LAND_COVER_CLASSIFICATION"
    VEGETATION_INDEX = "VEGETATION_INDEX"
    CROP_ANALYSIS = "CROP_ANALYSIS"


class PredictionStatus(str, enum.Enum):
    """Execution status of a prediction job."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Prediction(Base):
    """Represents a single AI inference run against a satellite image."""

    __tablename__ = "predictions"
    __table_args__ = (
        Index("ix_predictions_satellite_image_id_type", "satellite_image_id", "prediction_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    satellite_image_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("satellite_images.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    prediction_type: Mapped[PredictionType] = mapped_column(
        Enum(PredictionType, name="prediction_type"), nullable=False
    )
    status: Mapped[PredictionStatus] = mapped_column(
        Enum(PredictionStatus, name="prediction_status"),
        default=PredictionStatus.PENDING,
        nullable=False,
    )
    result_geometry: Mapped[Any | None] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=True), nullable=True
    )
    result_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"), nullable=True
    )
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
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

    satellite_image: Mapped["SatelliteImage"] = relationship(back_populates="predictions")
    reports: Mapped[list["Report"]] = relationship(
        secondary="report_predictions", back_populates="predictions"
    )

    def __repr__(self) -> str:
        """Return a debug-friendly representation of the prediction."""
        return f"<Prediction id={self.id} type={self.prediction_type} status={self.status}>"
