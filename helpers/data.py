from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path

from helpers.config import load_config

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_IMAGES_DIR = REPO_ROOT / "sample_images"
SAMPLE_RUN_ROOT = REPO_ROOT / ".automorph_sample_run"
LOGGER = logging.getLogger(__name__)


def clear_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for child in path.iterdir():
        clear_path(child)


def clear_path(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
        return
    path.unlink()


def data_root() -> Path:
    automorph_data = os.getenv("AUTOMORPH_DATA")
    if automorph_data:
        return Path(automorph_data)
    return REPO_ROOT


def _is_same_path(left: Path, right: Path) -> bool:
    if left == right:
        return True
    if left.exists() and right.exists():
        return left.resolve() == right.resolve()
    return False


def link_or_copy_directory(destination: Path, source: Path) -> None:
    if _is_same_path(destination, source):
        return

    if destination.exists() or destination.is_symlink():
        if destination.is_symlink():
            clear_path(destination)
        elif destination.is_dir() and not any(destination.iterdir()):
            clear_path(destination)
        else:
            raise RuntimeError(
                f"Cannot replace existing non-empty images directory: {destination}"
            )

    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        destination.symlink_to(source, target_is_directory=True)
    except OSError:
        shutil.copytree(source, destination)


def resolve_config_image_dir(config_path: str | Path | None) -> Path | None:
    if config_path is None:
        return None

    config = load_config(config_path)
    image_dir = config.get("input", {}).get("image_dir")
    if not image_dir:
        return None

    resolved = Path(image_dir).expanduser()
    if resolved.is_absolute():
        return resolved
    return (Path(config_path).resolve().parent / resolved).resolve()


def resolve_input_source(
    root: Path,
    *,
    config_path: str | Path | None = None,
    use_sample_images: bool = False,
) -> Path:
    if use_sample_images:
        return SAMPLE_IMAGES_DIR

    configured_input_dir = resolve_config_image_dir(config_path)
    if configured_input_dir is not None:
        return configured_input_dir

    images_dir = root / "images"
    if images_dir.exists():
        return images_dir

    if SAMPLE_IMAGES_DIR.exists():
        return SAMPLE_IMAGES_DIR

    return images_dir


def prepare_data_dirs(
    *, config_path: str | Path | None = None, use_sample_images: bool = False
) -> Path:
    root = SAMPLE_RUN_ROOT if use_sample_images else data_root()
    if use_sample_images:
        os.environ["AUTOMORPH_DATA"] = str(root)

    root.mkdir(parents=True, exist_ok=True)
    images_dir = root / "images"
    source = resolve_input_source(root, config_path=config_path, use_sample_images=use_sample_images)

    if source == images_dir:
        ensure_images_dir(images_dir)
    else:
        if not source.exists():
            raise RuntimeError(f"Input images directory does not exist: {source}")
        link_or_copy_directory(images_dir, source)
        LOGGER.info("Using input images from %s", source)

    clear_directory(root / "Results")
    LOGGER.info("Using data root %s", root)
    return root


def ensure_images_dir(images_dir: Path) -> None:
    if images_dir.exists():
        return
    images_dir.mkdir(parents=True, exist_ok=True)


def main() -> int:
    from helpers.runtime import configure_logging

    configure_logging()
    prepare_data_dirs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
