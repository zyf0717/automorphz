from __future__ import annotations

import csv
from pathlib import Path


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


def iter_image_names(images_dir: str | Path) -> list[str]:
    path = Path(images_dir)
    if not path.exists():
        raise FileNotFoundError(f"Images directory does not exist: {path}")

    return sorted(
        child.name
        for child in path.iterdir()
        if child.is_file()
        and not child.name.startswith(".")
        and child.suffix.lower() in IMAGE_SUFFIXES
    )


def write_global_resolution_csv(
    images_dir: str | Path,
    output_csv: str | Path,
    pixel_resolution: float,
) -> Path:
    image_names = iter_image_names(images_dir)
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["fundus", "res"])
        for image_name in image_names:
            writer.writerow([image_name, pixel_resolution])

    return output_path
