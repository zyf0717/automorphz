from __future__ import annotations

import argparse
import logging
from pathlib import Path

import cv2
import numpy as np

from helpers.config import REPO_ROOT
from helpers.data import data_root
from helpers.runtime import configure_logging

LOGGER = logging.getLogger(__name__)


def default_source_dir() -> Path:
    return REPO_ROOT / "eye"


def default_destination_dir() -> Path:
    return data_root() / "images"


def iter_pdfs(source_dir: Path) -> list[Path]:
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

    return sorted(
        path
        for path in source_dir.rglob("*.pdf")
        if path.is_file() and not any(part.startswith(".") for part in path.relative_to(source_dir).parts)
    )


def _looks_grayscale(candidate: dict) -> bool:
    colorspace = candidate.get("colorspace")
    if isinstance(colorspace, int):
        return colorspace <= 1
    if isinstance(colorspace, str):
        return "gray" in colorspace.lower()
    return False


def select_primary_image(candidates: list[dict]) -> dict:
    if not candidates:
        raise ValueError("No embedded images found in PDF page")

    selected = max(
        candidates,
        key=lambda item: (
            int(not _looks_grayscale(item)),
            int(item.get("width", 0)) * int(item.get("height", 0)),
            len(item.get("image", b"")),
        ),
    )
    LOGGER.info(
        "Selected embedded image %sx%s colorspace=%s",
        selected.get("width"),
        selected.get("height"),
        selected.get("colorspace"),
    )
    return selected


def decode_image_bytes(image_bytes: bytes) -> np.ndarray:
    encoded = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Failed to decode embedded image bytes")
    return image


def crop_bright_margins(
    image: np.ndarray,
    *,
    threshold: int = 245,
    min_fraction: float = 0.01,
) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mask = gray < threshold
    coords = np.argwhere(mask)
    if coords.size == 0:
        LOGGER.info("No bright margins detected; keeping original image size %sx%s", image.shape[1], image.shape[0])
        return image

    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1

    cropped = image[y0:y1, x0:x1]
    if cropped.size == 0:
        LOGGER.info("Detected crop was empty; keeping original image size %sx%s", image.shape[1], image.shape[0])
        return image

    min_height = max(1, int(image.shape[0] * min_fraction))
    min_width = max(1, int(image.shape[1] * min_fraction))
    if cropped.shape[0] < min_height or cropped.shape[1] < min_width:
        LOGGER.info(
            "Detected crop %sx%s was too small; keeping original image size %sx%s",
            cropped.shape[1],
            cropped.shape[0],
            image.shape[1],
            image.shape[0],
        )
        return image
    LOGGER.info(
        "Trimmed bright margins from %sx%s to %sx%s",
        image.shape[1],
        image.shape[0],
        cropped.shape[1],
        cropped.shape[0],
    )
    return cropped


def extract_pdf_fundus_image(
    pdf_path: Path,
    *,
    crop_margins: bool = True,
) -> np.ndarray:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError(
            "PyMuPDF is required for PDF extraction. Install pymupdf in the environment."
        ) from exc

    with fitz.open(pdf_path) as document:
        if document.page_count == 0:
            raise ValueError(f"PDF has no pages: {pdf_path}")

        page = document[0]
        LOGGER.info("Processing %s", pdf_path)
        candidates: list[dict] = []
        for image_entry in page.get_images(full=True):
            xref = image_entry[0]
            info = document.extract_image(xref)
            if not info:
                continue
            candidates.append(info)

        LOGGER.info("Found %d embedded images in %s", len(candidates), pdf_path.name)

        primary = select_primary_image(candidates)
        image = decode_image_bytes(primary["image"])
        LOGGER.info("Decoded native image size %sx%s", image.shape[1], image.shape[0])
        if crop_margins:
            return crop_bright_margins(image)
        return image


def extract_pdf_directory(
    source_dir: str | Path | None = None,
    destination_dir: str | Path | None = None,
    *,
    overwrite: bool = False,
    crop_margins: bool = True,
) -> list[Path]:
    source = Path(source_dir) if source_dir is not None else default_source_dir()
    destination = Path(destination_dir) if destination_dir is not None else default_destination_dir()
    pdf_files = iter_pdfs(source)
    if not pdf_files:
        raise ValueError(f"No PDF files found under {source}")

    destination.mkdir(parents=True, exist_ok=True)
    LOGGER.info("Extracting fundus images from %d PDFs in %s", len(pdf_files), source)
    written: list[Path] = []
    for pdf_path in pdf_files:
        output_path = destination / f"{pdf_path.stem}.png"
        if output_path.exists() and not overwrite:
            raise FileExistsError(f"Destination file already exists: {output_path}")
        image = extract_pdf_fundus_image(pdf_path, crop_margins=crop_margins)
        if not cv2.imwrite(str(output_path), image):
            raise RuntimeError(f"Failed to write PNG: {output_path}")
        LOGGER.info("Wrote %s", output_path)
        written.append(output_path)
    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract the primary fundus image from first-page PDFs into flat PNG files."
    )
    parser.add_argument("source", nargs="?", type=Path, default=default_source_dir())
    parser.add_argument("--destination", type=Path, default=default_destination_dir())
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--no-crop-margins",
        dest="crop_margins",
        action="store_false",
        help="Keep the extracted embedded image exactly as stored without trimming bright margins.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    args = build_parser().parse_args(argv)
    written = extract_pdf_directory(
        args.source,
        args.destination,
        overwrite=args.overwrite,
        crop_margins=args.crop_margins,
    )
    LOGGER.info("Extracted %d PDF fundus images into %s", len(written), args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
