"""Pydantic schemas for SatelliteImage create/response payloads."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.satellite_image import ImageStatus


class SatelliteImageCreate(BaseModel):
    """Payload required to register an uploaded satellite image's metadata."""

    project_id: uuid.UUID
    file_name: str = Field(min_length=1, max_length=255)
    file_path: str = Field(min_length=1, max_length=512)
    file_size_bytes: int = Field(gt=0)
    sensor_type: str | None = Field(default=None, max_length=100)
    crs: str | None = Field(default=None, max_length=50)
    width_px: int | None = Field(default=None, gt=0)
    height_px: int | None = Field(default=None, gt=0)
    band_count: int | None = Field(default=None, gt=0)
    captured_at: datetime | None = None
    footprint: dict[str, Any] | None = Field(
        default=None, description="GeoJSON Polygon geometry of the image footprint."
    )


class SatelliteImageResponse(BaseModel):
    """Public representation of a satellite image record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    file_name: str
    file_path: str
    file_size_bytes: int
    sensor_type: str | None
    crs: str | None
    width_px: int | None
    height_px: int | None
    band_count: int | None
    captured_at: datetime | None
    status: ImageStatus
    created_at: datetime
    updated_at: datetime
