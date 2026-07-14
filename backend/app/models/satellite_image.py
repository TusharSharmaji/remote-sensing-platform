"""SatelliteImage ORM model representing an uploaded and processed raster asset."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from geoalchemy2 import Geometry
from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.prediction import Prediction
    from app.models.project import Project


class ImageStatus(str, enum.Enum):
    """Processing lifecycle status of an uploaded satellite image."""

    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class SatelliteImage(Base):
    """Represents a single uploaded satellite raster and its extracted metadata."""

    __tablename__ = "satellite_images"
    __table_args__ = (
        Index("ix_satellite_images_project_id_status", "project_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sensor_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    crs: Mapped[str | None] = mapped_column(String(50), nullable=True)
    width_px: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_px: Mapped[int | None] = mapped_column(Integer, nullable=True)
    band_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    footprint: Mapped[Any | None] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=True), nullable=True
    )
    status: Mapped[ImageStatus] = mapped_column(
        Enum(ImageStatus, name="image_status"), default=ImageStatus.UPLOADED, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    project: Mapped["Project"] = relationship(back_populates="satellite_images")
    predictions: Mapped[list["Prediction"]] = relationship(
        back_populates="satellite_image", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Return a debug-friendly representation of the satellite image."""
        return f"<SatelliteImage id={self.id} file_name={self.file_name} status={self.status}>" 
    preview_path = mapped_column(String, nullable=True)
thumbnail_path = mapped_column(String, nullable=True)
