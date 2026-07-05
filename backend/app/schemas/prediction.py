"""Pydantic schemas for Prediction create/response payloads."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.prediction import PredictionStatus, PredictionType


class PredictionCreate(BaseModel):
    """Payload required to enqueue a new prediction job."""

    satellite_image_id: uuid.UUID
    model_name: str = Field(min_length=1, max_length=255)
    model_version: str | None = Field(default=None, max_length=50)
    prediction_type: PredictionType


class PredictionResponse(BaseModel):
    """Public representation of a prediction record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    satellite_image_id: uuid.UUID
    model_name: str
    model_version: str | None
    prediction_type: PredictionType
    status: PredictionStatus
    result_geometry: dict[str, Any] | None = Field(
        default=None, description="GeoJSON geometry of the prediction result, if any."
    )
    result_data: dict[str, Any] | None
    confidence_score: float | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
