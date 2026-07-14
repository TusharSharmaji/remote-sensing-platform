"""Data access layer for SatelliteImage entities."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.satellite_image import ImageStatus, SatelliteImage


class SatelliteImageRepository:
    """Repository for SatelliteImage."""

    def __init__(self, db: Session) -> None:
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

    def get_by_id(
        self,
        image_id: uuid.UUID,
    ) -> SatelliteImage | None:
        return self._db.get(SatelliteImage, image_id)

    def get_by_project_and_id(
        self,
        *,
        project_id: uuid.UUID,
        image_id: uuid.UUID,
    ) -> SatelliteImage | None:
        stmt = select(SatelliteImage).where(
            SatelliteImage.id == image_id,
            SatelliteImage.project_id == project_id,
        )

        return self._db.execute(stmt).scalar_one_or_none()

    def list_by_project(
        self,
        project_id: uuid.UUID,
    ) -> list[SatelliteImage]:
        stmt = (
            select(SatelliteImage)
            .where(SatelliteImage.project_id == project_id)
            .order_by(SatelliteImage.created_at.desc())
        )

        return list(self._db.execute(stmt).scalars().all())

    def update_status(
        self,
        image: SatelliteImage,
        status: ImageStatus,
    ) -> SatelliteImage:

        image.status = status

        self._db.commit()
        self._db.refresh(image)

        return image

    def update_metadata(
        self,
        image: SatelliteImage,
        *,
        sensor_type: str | None = None,
        crs: str | None = None,
        width_px: int | None = None,
        height_px: int | None = None,
        band_count: int | None = None,
        preview_path: str | None = None,
        thumbnail_path: str | None = None,
    ) -> SatelliteImage:

        image.sensor_type = sensor_type
        image.crs = crs
        image.width_px = width_px
        image.height_px = height_px
        image.band_count = band_count

        image.preview_path = preview_path
        image.thumbnail_path = thumbnail_path

        self._db.commit()
        self._db.refresh(image)

        return image

    def delete(
        self,
        image: SatelliteImage,
    ) -> None:

        self._db.delete(image)
        self._db.commit()