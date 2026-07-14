"""
Generate preview and thumbnail images from GeoTIFF rasters.
"""

from pathlib import Path

import cv2
import numpy as np
import rasterio


class PreviewGenerator:
    """Creates PNG previews for uploaded GeoTIFFs."""

    @staticmethod
    def generate(
        raster_path: str,
        output_directory: str,
    ) -> tuple[str, str]:

        raster_path = Path(raster_path)
        output_directory = Path(output_directory)

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        with rasterio.open(raster_path) as dataset:

            bands = dataset.count

            if bands >= 3:

                red = dataset.read(1).astype(np.float32)
                green = dataset.read(2).astype(np.float32)
                blue = dataset.read(3).astype(np.float32)

                rgb = np.dstack([red, green, blue])

            else:

                gray = dataset.read(1).astype(np.float32)

                rgb = np.dstack(
                    [
                        gray,
                        gray,
                        gray,
                    ]
                )

        rgb = np.nan_to_num(rgb)

        rgb -= rgb.min()

        if rgb.max() > 0:
            rgb /= rgb.max()

        rgb *= 255

        rgb = rgb.astype(np.uint8)

        preview_path = output_directory / "preview.png"

        thumbnail_path = output_directory / "thumbnail.png"

        cv2.imwrite(
            str(preview_path),
            cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR),
        )

        thumbnail = cv2.resize(
            rgb,
            (256, 256),
            interpolation=cv2.INTER_AREA,
        )

        cv2.imwrite(
            str(thumbnail_path),
            cv2.cvtColor(thumbnail, cv2.COLOR_RGB2BGR),
        )

        return (
            str(preview_path),
            str(thumbnail_path),
        )