"""GeoTIFF metadata extraction service."""

from dataclasses import dataclass
from pathlib import Path

import rasterio
from rasterio.errors import RasterioIOError


@dataclass(slots=True)
class GeoTIFFMetadata:
    """Container for metadata extracted from a GeoTIFF."""

    driver: str | None
    width: int
    height: int
    band_count: int
    crs: str | None
    transform: str
    bounds: tuple[float, float, float, float]
    resolution: tuple[float, float]
    dtype: str | None
    nodata: float | int | None


class GeoTIFFMetadataService:
    """Extract metadata from a GeoTIFF using Rasterio."""

    @staticmethod
    def extract(file_path: str | Path) -> GeoTIFFMetadata:
        """
        Open a GeoTIFF and extract its metadata.

        Args:
            file_path: Path to the GeoTIFF.

        Returns:
            GeoTIFFMetadata containing extracted information.

        Raises:
            ValueError: If the file cannot be opened as a raster.
        """

        try:
            with rasterio.open(file_path) as dataset:
                return GeoTIFFMetadata(
                    driver=dataset.driver,
                    width=dataset.width,
                    height=dataset.height,
                    band_count=dataset.count,
                    crs=str(dataset.crs) if dataset.crs else None,
                    transform=str(dataset.transform),
                    bounds=(
                        dataset.bounds.left,
                        dataset.bounds.bottom,
                        dataset.bounds.right,
                        dataset.bounds.top,
                    ),
                    resolution=dataset.res,
                    dtype=dataset.dtypes[0] if dataset.dtypes else None,
                    nodata=dataset.nodata,
                )

        except RasterioIOError as exc:
            raise ValueError(
                f"Unable to read GeoTIFF '{file_path}'."
            ) from exc
        