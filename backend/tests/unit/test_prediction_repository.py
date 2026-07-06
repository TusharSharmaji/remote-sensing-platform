"""Unit tests for PredictionRepository against an in-memory SQLite database."""

from sqlalchemy.orm import Session

from app.models.prediction import PredictionStatus, PredictionType
from app.repositories.project_repository import ProjectRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.satellite_image_repository import SatelliteImageRepository
from app.repositories.user_repository import UserRepository


def _make_image(db_session: Session) -> object:
    """Create and return a satellite image to attach predictions to."""
    owner = UserRepository(db_session).create(
        email="predowner@example.com", hashed_password="hashed", full_name="Owner"
    )
    project = ProjectRepository(db_session).create(owner_id=owner.id, name="Prediction Project")
    return SatelliteImageRepository(db_session).create(
        project_id=project.id, file_name="s.tif", file_path="/s.tif", file_size_bytes=100
    )


def test_create_prediction_defaults_to_pending(db_session: Session) -> None:
    """Creating a prediction should default its status to PENDING."""
    image = _make_image(db_session)
    repo = PredictionRepository(db_session)
    prediction = repo.create(
        satellite_image_id=image.id,
        model_name="unet-landcover-v1",
        prediction_type=PredictionType.LAND_COVER_CLASSIFICATION,
    )
    assert prediction.status == PredictionStatus.PENDING
    assert prediction.result_data is None


def test_complete_sets_status_and_result_payload(db_session: Session) -> None:
    """Completing a prediction should set status COMPLETED and store its result data."""
    image = _make_image(db_session)
    repo = PredictionRepository(db_session)
    prediction = repo.create(
        satellite_image_id=image.id,
        model_name="ndvi-calc-v1",
        prediction_type=PredictionType.VEGETATION_INDEX,
    )
    completed = repo.complete(
        prediction, result_data={"mean_ndvi": 0.62}, confidence_score=0.91
    )
    assert completed.status == PredictionStatus.COMPLETED
    assert completed.result_data == {"mean_ndvi": 0.62}
    assert completed.confidence_score == 0.91


def test_fail_sets_status_and_error_message(db_session: Session) -> None:
    """Failing a prediction should set status FAILED and record the error message."""
    image = _make_image(db_session)
    repo = PredictionRepository(db_session)
    prediction = repo.create(
        satellite_image_id=image.id,
        model_name="segformer-v2",
        prediction_type=PredictionType.SEGMENTATION,
    )
    failed = repo.fail(prediction, error_message="CUDA out of memory")
    assert failed.status == PredictionStatus.FAILED
    assert failed.error_message == "CUDA out of memory"


def test_list_by_satellite_image_returns_only_matching_predictions(db_session: Session) -> None:
    """Listing by satellite image should exclude predictions for other images."""
    image_a = _make_image(db_session)
    image_b = _make_image(db_session)
    repo = PredictionRepository(db_session)
    repo.create(
        satellite_image_id=image_a.id,
        model_name="m1",
        prediction_type=PredictionType.CROP_ANALYSIS,
    )
    repo.create(
        satellite_image_id=image_b.id,
        model_name="m2",
        prediction_type=PredictionType.CROP_ANALYSIS,
    )

    results = repo.list_by_satellite_image(image_a.id)
    assert len(results) == 1
    assert results[0].satellite_image_id == image_a.id
