from __future__ import annotations

import argparse
import logging
import os
import shutil
from pathlib import Path

from helpers.config import REPO_ROOT
from helpers.runtime import configure_logging

LOGGER = logging.getLogger(__name__)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


def default_source_dir() -> Path:
    return REPO_ROOT / "nested_folder"


def default_destination_dir() -> Path:
    automorph_data = os.getenv("AUTOMORPH_DATA")
    if automorph_data:
        return Path(automorph_data) / "images"
    return REPO_ROOT / "images"


def iter_nested_images(source_dir: Path) -> list[Path]:
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

    return sorted(
        path
        for path in source_dir.rglob("*")
        if path.is_file()
        and path.suffix.lower() in IMAGE_SUFFIXES
        and not any(part.startswith(".") for part in path.relative_to(source_dir).parts)
    )


def prepare_destination_dir(destination_dir: Path) -> None:
    if destination_dir.is_symlink():
        resolved = destination_dir.resolve()
        sample_images = (REPO_ROOT / "sample_images").resolve()
        if resolved == sample_images:
            destination_dir.unlink()
        else:
            raise ValueError(
                f"Destination directory is a symlink to {resolved}; remove it before flattening Fundus data"
            )

    destination_dir.mkdir(parents=True, exist_ok=True)


def flatten_nested_images(
    source_dir: str | Path | None = None,
    destination_dir: str | Path | None = None,
    *,
    overwrite: bool = False,
) -> list[Path]:
    source = Path(source_dir) if source_dir is not None else default_source_dir()
    destination = (
        Path(destination_dir)
        if destination_dir is not None
        else default_destination_dir()
    )

    image_files = iter_nested_images(source)
    if not image_files:
        raise ValueError(f"No suitable image files found under {source}")

    basenames: dict[str, Path] = {}
    for path in image_files:
        previous = basenames.get(path.name)
        if previous is not None and previous != path:
            raise ValueError(
                f"Duplicate image filename {path.name} found in {previous} and {path}"
            )
        basenames[path.name] = path

    prepare_destination_dir(destination)

    copied: list[Path] = []
    for name, source_path in sorted(basenames.items()):
        target = destination / name
        if target.exists() and not overwrite:
            raise FileExistsError(f"Destination file already exists: {target}")
        shutil.copy2(source_path, target)
        copied.append(target)

    return copied


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Flatten recursively nested image files into the flat images directory used by the pipeline."
    )
    parser.add_argument("source", nargs="?", type=Path, default=default_source_dir())
    parser.add_argument("--destination", type=Path, default=default_destination_dir())
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    args = build_parser().parse_args(argv)
    copied = flatten_nested_images(args.source, args.destination, overwrite=args.overwrite)
    LOGGER.info("Copied %d images into %s", len(copied), args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
