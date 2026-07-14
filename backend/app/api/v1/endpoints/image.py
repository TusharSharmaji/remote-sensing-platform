"""Satellite image upload, listing and deletion endpoints."""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.repositories.satellite_image_repository import SatelliteImageRepository
from app.schemas.satellite_image import SatelliteImageResponse
from app.services.project_service import ProjectService
from app.services.satellite_image_service import SatelliteImageService

router = APIRouter(
    prefix="/projects/{project_id}/images",
    tags=["satellite-images"],
)

settings = get_settings()

ALLOWED_EXTENSIONS = {
    ".tif",
    ".tiff",
    ".png",
    ".jpg",
    ".jpeg",
}


def get_project_service(
    db: Session = Depends(get_db),
) -> ProjectService:
    return ProjectService(ProjectRepository(db))


def get_image_service(
    db: Session = Depends(get_db),
) -> SatelliteImageService:
    return SatelliteImageService(
        SatelliteImageRepository(db),
    )


@router.post(
    "",
    response_model=SatelliteImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
    image_service: SatelliteImageService = Depends(get_image_service),
) -> SatelliteImageResponse:
    """Upload a satellite image."""

    project = project_service.get_project(
        project_id,
        current_user,
    )

    original_name = file.filename or "upload"

    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {extension}",
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    max_size = settings.max_upload_size_mb * 1024 * 1024

    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Maximum upload size is {settings.max_upload_size_mb} MB.",
        )

    project_dir = Path(settings.storage_root) / str(project.id)
    project_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_filename = f"{uuid.uuid4()}{extension}"

    destination = project_dir / stored_filename

    destination.write_bytes(contents)

    image = image_service.register_upload(
        project_id=project.id,
        file_name=original_name,
        file_path=str(destination),
        file_size_bytes=len(contents),
    )

    return SatelliteImageResponse.model_validate(image)


@router.get(
    "",
    response_model=list[SatelliteImageResponse],
)
async def list_images(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
    image_service: SatelliteImageService = Depends(get_image_service),
) -> list[SatelliteImageResponse]:

    project_service.get_project(
        project_id,
        current_user,
    )

    images = image_service.list_for_project(
        project_id,
    )

    return [
        SatelliteImageResponse.model_validate(image)
        for image in images
    ]


@router.delete(
    "/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_image(
    project_id: uuid.UUID,
    image_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
    image_service: SatelliteImageService = Depends(get_image_service),
) -> None:

    project_service.get_project(
        project_id,
        current_user,
    )

    image_service.delete_image(
        project_id=project_id,
        image_id=image_id,
    )