"""Unit tests for ProjectRepository against an in-memory SQLite database."""

from sqlalchemy.orm import Session

from app.models.project import ProjectStatus
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository


def _make_owner(db_session: Session) -> object:
    """Create and return a user to act as a project owner."""
    return UserRepository(db_session).create(
        email="owner@example.com", hashed_password="hashed", full_name="Owner"
    )


def test_create_project_persists_with_default_status(db_session: Session) -> None:
    """Creating a project should default its status to ACTIVE."""
    owner = _make_owner(db_session)
    repo = ProjectRepository(db_session)
    project = repo.create(owner_id=owner.id, name="Crop Study", description="Kharif season")
    assert project.id is not None
    assert project.status == ProjectStatus.ACTIVE
    assert project.owner_id == owner.id


def test_get_by_id_returns_none_for_unknown_id(db_session: Session) -> None:
    """Fetching a nonexistent project id should return None."""
    import uuid

    repo = ProjectRepository(db_session)
    assert repo.get_by_id(uuid.uuid4()) is None


def test_list_by_owner_returns_only_that_owners_projects(db_session: Session) -> None:
    """Listing by owner should exclude projects belonging to other users."""
    owner = _make_owner(db_session)
    other_owner = UserRepository(db_session).create(
        email="other@example.com", hashed_password="hashed", full_name="Other"
    )
    repo = ProjectRepository(db_session)
    repo.create(owner_id=owner.id, name="Mine 1")
    repo.create(owner_id=owner.id, name="Mine 2")
    repo.create(owner_id=other_owner.id, name="Not Mine")

    results = repo.list_by_owner(owner.id)
    assert len(results) == 2
    assert all(p.owner_id == owner.id for p in results)


def test_update_status_persists_new_status(db_session: Session) -> None:
    """Updating a project's status should persist the change."""
    owner = _make_owner(db_session)
    repo = ProjectRepository(db_session)
    project = repo.create(owner_id=owner.id, name="Archivable")
    updated = repo.update_status(project, ProjectStatus.ARCHIVED)
    assert updated.status == ProjectStatus.ARCHIVED


def test_delete_removes_project(db_session: Session) -> None:
    """Deleting a project should make it unfetchable afterward."""
    owner = _make_owner(db_session)
    repo = ProjectRepository(db_session)
    project = repo.create(owner_id=owner.id, name="Temp")
    project_id = project.id
    repo.delete(project)
    assert repo.get_by_id(project_id) is None
