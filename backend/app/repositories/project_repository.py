"""Data access layer for Project entities."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project, ProjectStatus


class ProjectRepository:
    """Encapsulates all direct database access for the Project model."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to a SQLAlchemy session."""
        self._db = db

    def create(self, *, owner_id: uuid.UUID, name: str, description: str | None = None) -> Project:
        """Persist and return a new project owned by the given user."""
        project = Project(owner_id=owner_id, name=name, description=description)
        self._db.add(project)
        self._db.commit()
        self._db.refresh(project)
        return project

    def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        """Return the project with the given id, or None if not found."""
        return self._db.get(Project, project_id)

    def list_by_owner(self, owner_id: uuid.UUID) -> list[Project]:
        """Return all projects owned by the given user, most recent first."""
        stmt = (
            select(Project)
            .where(Project.owner_id == owner_id)
            .order_by(Project.created_at.desc())
        )
        return list(self._db.execute(stmt).scalars().all())

    def update_status(self, project: Project, status: ProjectStatus) -> Project:
        """Update and persist a project's status."""
        project.status = status
        self._db.commit()
        self._db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        """Delete a project and cascade to its images and reports."""
        self._db.delete(project)
        self._db.commit()
