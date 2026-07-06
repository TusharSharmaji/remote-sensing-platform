"""Unit tests for SatelliteImageRepository against an in-memory SQLite database."""

from sqlalchemy.orm import Session

from app.models.satellite_image import ImageStatus
from app.repositories.project_repository import ProjectRepository
from app.repositories.satellite_image_repository import SatelliteImageRepository
from app.repositories.user_repository import UserRepository


def _make_project(db_session: Session) -> object:
    """Create and return a project to attach satellite images to."""
    owner = UserRepository(db_session).create(
        email="imgowner@example.com", hashed_password="hashed", full_name="Owner"
    )
    return ProjectRepository(db_session).create(owner_id=owner.id, name="Image Project")


def test_create_satellite_image_defaults_to_uploaded(db_session: Session) -> None:
    """Creating a satellite image should default its status to UPLOADED."""
    project = _make_project(db_session)
    repo = SatelliteImageRepository(db_session)
    image = repo.create(
        project_id=project.id,
        file_name="scene.tif",
        file_path="/data/uploads/scene.tif",
        file_size_bytes=1024,
    )
    assert image.status == ImageStatus.UPLOADED
    assert image.footprint is None


def test_list_by_project_returns_only_images_for_that_project(db_session: Session) -> None:
    """Listing by project should return only images belonging to that project."""
    project_a = _make_project(db_session)
    project_b = _make_project(db_session)
    repo = SatelliteImageRepository(db_session)
    repo.create(project_id=project_a.id, file_name="a1.tif", file_path="/a1.tif", file_size_bytes=10)
    repo.create(project_id=project_a.id, file_name="a2.tif", file_path="/a2.tif", file_size_bytes=20)
    repo.create(project_id=project_b.id, file_name="b1.tif", file_path="/b1.tif", file_size_bytes=30)

    results = repo.list_by_project(project_a.id)
    assert len(results) == 2
    assert all(img.project_id == project_a.id for img in results)


def test_update_status_transitions_image_state(db_session: Session) -> None:
    """Updating a satellite image's status should persist the transition."""
    project = _make_project(db_session)
    repo = SatelliteImageRepository(db_session)
    image = repo.create(
        project_id=project.id, file_name="p.tif", file_path="/p.tif", file_size_bytes=100
    )
    updated = repo.update_status(image, ImageStatus.PROCESSED)
    assert updated.status == ImageStatus.PROCESSED


def test_delete_removes_satellite_image(db_session: Session) -> None:
    """Deleting a satellite image should make it unfetchable afterward."""
    project = _make_project(db_session)
    repo = SatelliteImageRepository(db_session)
    image = repo.create(
        project_id=project.id, file_name="d.tif", file_path="/d.tif", file_size_bytes=50
    )
    image_id = image.id
    repo.delete(image)
    assert repo.get_by_id(image_id) is None
