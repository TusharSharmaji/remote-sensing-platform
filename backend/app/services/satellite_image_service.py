"""Business logic for SatelliteImage operations."""

import uuid
from pathlib import Path

from fastapi import HTTPException, status

from app.models.satellite_image import SatelliteImage
from app.repositories.satellite_image_repository import SatelliteImageRepository
from app.services.geotiff_metadata_service import GeoTIFFMetadataService
from app.services.preview_generator import PreviewGenerator


class SatelliteImageService:
    """Coordinates satellite image business logic."""

    def __init__(self, image_repository: SatelliteImageRepository) -> None:
        self._images = image_repository

    def register_upload(
        self,
        *,
        project_id: uuid.UUID,
        file_name: str,
        file_path: str,
        file_size_bytes: int,
    ) -> SatelliteImage:
        """Create an image record and extract GeoTIFF metadata."""

        image = self._images.create(
            project_id=project_id,
            file_name=file_name,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
        )

        extension = Path(file_path).suffix.lower()

        if extension in {".tif", ".tiff"}:

            metadata = GeoTIFFMetadataService.extract(file_path)

            preview_directory = (
                Path(file_path).parent
                / f"{Path(file_path).stem}_preview"
            )

            preview_path, thumbnail_path = PreviewGenerator.generate(
                raster_path=file_path,
                output_directory=str(preview_directory),
            )

            image = self._images.update_metadata(
                image,
                sensor_type=metadata.driver,
                crs=metadata.crs,
                width_px=metadata.width,
                height_px=metadata.height,
                band_count=metadata.band_count,
                preview_path=preview_path,
                thumbnail_path=thumbnail_path,
            )

        return image

    def list_for_project(
        self,
        project_id: uuid.UUID,
    ) -> list[SatelliteImage]:
        return self._images.list_by_project(project_id)

    def get_image(
        self,
        *,
        project_id: uuid.UUID,
        image_id: uuid.UUID,
    ) -> SatelliteImage:

        image = self._images.get_by_project_and_id(
            project_id=project_id,
            image_id=image_id,
        )

        if image is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Satellite image not found.",
            )

        return image

    def delete_image(
        self,
        *,
        project_id: uuid.UUID,
        image_id: uuid.UUID,
    ) -> None:

        image = self.get_image(
            project_id=project_id,
            image_id=image_id,
        )

        image_path = Path(image.file_path)

        if image_path.exists():
            image_path.unlink()

        if image.preview_path:
            preview = Path(image.preview_path)
            if preview.exists():
                preview.unlink()

        if image.thumbnail_path:
            thumbnail = Path(image.thumbnail_path)
            if thumbnail.exists():
                thumbnail.unlink()

        preview_folder = (
            image_path.parent
            / f"{image_path.stem}_preview"
        )

        if preview_folder.exists():
            try:
                preview_folder.rmdir()
            except OSError:
                pass

        self._images.delete(image)