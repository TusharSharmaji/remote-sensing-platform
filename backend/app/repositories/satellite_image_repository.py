"""Data access layer for SatelliteImage entities."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.satellite_image import ImageStatus, SatelliteImage


class SatelliteImageRepository:
    """Encapsulates all direct database access for the SatelliteImage model."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to a SQLAlchemy session."""
        self._db = db

    def create(
        self,
        *,
        project_id: uuid.UUID,
        file_name: str,
        file_path: str,
        file_size_bytes: int,
        sensor_type: str | None = None,
        crs: str | None = None,
        width_px: int | None = None,
        height_px: int | None = None,
        band_count: int | None = None,
        captured_at: datetime | None = None,
        footprint: Any | None = None,
    ) -> SatelliteImage:
        """Persist and return a new satellite image record for a project."""
        image = SatelliteImage(
            project_id=project_id,
            file_name=file_name,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            sensor_type=sensor_type,
            crs=crs,
            width_px=width_px,
            height_px=height_px,
            band_count=band_count,
            captured_at=captured_at,
            footprint=footprint,
        )
        self._db.add(image)
        self._db.commit()
        self._db.refresh(image)
        return image

    def get_by_id(self, image_id: uuid.UUID) -> SatelliteImage | None:
        """Return the satellite image with the given id, or None if not found."""
        return self._db.get(SatelliteImage, image_id)

    def list_by_project(self, project_id: uuid.UUID) -> list[SatelliteImage]:
        """Return all satellite images belonging to the given project."""
        stmt = (
            select(SatelliteImage)
            .where(SatelliteImage.project_id == project_id)
            .order_by(SatelliteImage.created_at.desc())
        )
        return list(self._db.execute(stmt).scalars().all())

    def update_status(self, image: SatelliteImage, status: ImageStatus) -> SatelliteImage:
        """Update and persist a satellite image's processing status."""
        image.status = status
        self._db.commit()
        self._db.refresh(image)
        return image

    def delete(self, image: SatelliteImage) -> None:
        """Delete a satellite image and cascade to its predictions."""
        self._db.delete(image)
        self._db.commit()
