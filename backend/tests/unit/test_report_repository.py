"""Unit tests for ReportRepository against an in-memory SQLite database."""

from sqlalchemy.orm import Session

from app.models.prediction import PredictionType
from app.models.report import ReportFormat, ReportStatus
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.satellite_image_repository import SatelliteImageRepository
from app.repositories.user_repository import UserRepository


def _make_project_with_prediction(db_session: Session) -> tuple[object, object]:
    """Create a project and a single prediction under it, returning both."""
    owner = UserRepository(db_session).create(
        email="reportowner@example.com", hashed_password="hashed", full_name="Owner"
    )
    project = ProjectRepository(db_session).create(owner_id=owner.id, name="Report Project")
    image = SatelliteImageRepository(db_session).create(
        project_id=project.id, file_name="r.tif", file_path="/r.tif", file_size_bytes=100
    )
    prediction = PredictionRepository(db_session).create(
        satellite_image_id=image.id,
        model_name="ndvi-calc-v1",
        prediction_type=PredictionType.VEGETATION_INDEX,
    )
    return project, prediction


def test_create_report_defaults_to_pending_pdf(db_session: Session) -> None:
    """Creating a report should default to PENDING status and PDF format."""
    project, _ = _make_project_with_prediction(db_session)
    repo = ReportRepository(db_session)
    report = repo.create(project_id=project.id, title="Monthly Summary")
    assert report.status == ReportStatus.PENDING
    assert report.format == ReportFormat.PDF
    assert report.predictions == []


def test_create_report_links_provided_predictions(db_session: Session) -> None:
    """Creating a report with prediction_ids should populate the M2M relationship."""
    project, prediction = _make_project_with_prediction(db_session)
    repo = ReportRepository(db_session)
    report = repo.create(
        project_id=project.id, title="Linked Report", prediction_ids=[prediction.id]
    )
    assert len(report.predictions) == 1
    assert report.predictions[0].id == prediction.id


def test_update_status_sets_file_path_on_completion(db_session: Session) -> None:
    """Updating status to COMPLETED with a file_path should persist both fields."""
    project, _ = _make_project_with_prediction(db_session)
    repo = ReportRepository(db_session)
    report = repo.create(project_id=project.id, title="Finalized Report")
    updated = repo.update_status(
        report, ReportStatus.COMPLETED, file_path="/data/reports/final.pdf"
    )
    assert updated.status == ReportStatus.COMPLETED
    assert updated.file_path == "/data/reports/final.pdf"


def test_list_by_project_returns_only_that_projects_reports(db_session: Session) -> None:
    """Listing by project should exclude reports belonging to other projects."""
    project_a, _ = _make_project_with_prediction(db_session)
    project_b, _ = _make_project_with_prediction(db_session)
    repo = ReportRepository(db_session)
    repo.create(project_id=project_a.id, title="A Report")
    repo.create(project_id=project_b.id, title="B Report")

    results = repo.list_by_project(project_a.id)
    assert len(results) == 1
    assert results[0].project_id == project_a.id
