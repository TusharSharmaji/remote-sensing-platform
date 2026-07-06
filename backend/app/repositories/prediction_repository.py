"""Data access layer for Prediction entities."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.prediction import Prediction, PredictionStatus, PredictionType


class PredictionRepository:
    """Encapsulates all direct database access for the Prediction model."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to a SQLAlchemy session."""
        self._db = db

    def create(
        self,
        *,
        satellite_image_id: uuid.UUID,
        model_name: str,
        prediction_type: PredictionType,
        model_version: str | None = None,
    ) -> Prediction:
        """Persist and return a new pending prediction job for a satellite image."""
        prediction = Prediction(
            satellite_image_id=satellite_image_id,
            model_name=model_name,
            model_version=model_version,
            prediction_type=prediction_type,
        )
        self._db.add(prediction)
        self._db.commit()
        self._db.refresh(prediction)
        return prediction

    def get_by_id(self, prediction_id: uuid.UUID) -> Prediction | None:
        """Return the prediction with the given id, or None if not found."""
        return self._db.get(Prediction, prediction_id)

    def list_by_satellite_image(self, satellite_image_id: uuid.UUID) -> list[Prediction]:
        """Return all predictions generated for the given satellite image."""
        stmt = (
            select(Prediction)
            .where(Prediction.satellite_image_id == satellite_image_id)
            .order_by(Prediction.created_at.desc())
        )
        return list(self._db.execute(stmt).scalars().all())

    def complete(
        self,
        prediction: Prediction,
        *,
        result_data: dict[str, Any] | None = None,
        result_geometry: Any | None = None,
        confidence_score: float | None = None,
    ) -> Prediction:
        """Mark a prediction as completed and attach its result payload."""
        prediction.status = PredictionStatus.COMPLETED
        prediction.result_data = result_data
        prediction.result_geometry = result_geometry
        prediction.confidence_score = confidence_score
        self._db.commit()
        self._db.refresh(prediction)
        return prediction

    def fail(self, prediction: Prediction, *, error_message: str) -> Prediction:
        """Mark a prediction as failed and record the error message."""
        prediction.status = PredictionStatus.FAILED
        prediction.error_message = error_message
        self._db.commit()
        self._db.refresh(prediction)
        return prediction

    def delete(self, prediction: Prediction) -> None:
        """Delete a prediction record."""
        self._db.delete(prediction)
        self._db.commit()
