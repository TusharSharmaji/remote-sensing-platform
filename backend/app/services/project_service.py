"""Business logic for Project CRUD operations."""

import uuid

from app.core.exceptions import ProjectAccessDeniedException, ProjectNotFoundException
from app.models.project import Project
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate


class ProjectService:
    """Coordinates project-related business logic."""

    def __init__(self, project_repository: ProjectRepository) -> None:
        self._projects = project_repository

    def create_project(
        self,
        current_user: User,
        payload: ProjectCreate,
    ) -> Project:
        """Create a new project for the authenticated user."""
        return self._projects.create(
            owner_id=current_user.id,
            name=payload.name,
            description=payload.description,
        )

    def list_projects(
        self,
        current_user: User,
    ) -> list[Project]:
        """Return all projects belonging to the authenticated user."""
        return self._projects.list_by_owner(current_user.id)

    def get_project(
        self,
        project_id: uuid.UUID,
        current_user: User,
    ) -> Project:
        """Return a single project after ownership validation."""
        project = self._projects.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundException()

        if project.owner_id != current_user.id:
            raise ProjectAccessDeniedException()

        return project

    def delete_project(
        self,
        project_id: uuid.UUID,
        current_user: User,
    ) -> None:
        """Delete a project after ownership validation."""
        project = self.get_project(
            project_id,
            current_user,
        )

        self._projects.delete(project)