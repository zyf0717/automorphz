from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from helpers.extract_pdf_fundus import crop_bright_margins
from helpers.extract_pdf_fundus import iter_pdfs
from helpers.extract_pdf_fundus import select_primary_image


def test_iter_pdfs_finds_recursive_pdfs(tmp_path: Path) -> None:
    source = tmp_path / "eye"
    (source / "nested").mkdir(parents=True)
    (source / "a.pdf").write_bytes(b"%PDF-1.4")
    (source / "nested" / "b.pdf").write_bytes(b"%PDF-1.4")
    (source / "notes.txt").write_text("x", encoding="utf-8")

    assert [path.name for path in iter_pdfs(source)] == ["a.pdf", "b.pdf"]


def test_select_primary_image_prefers_large_color_image() -> None:
    candidates = [
        {"width": 996, "height": 150, "colorspace": 3, "image": b"small"},
        {"width": 5078, "height": 2676, "colorspace": 1, "image": b"gray"},
        {"width": 5078, "height": 2676, "colorspace": 3, "image": b"color"},
    ]

    selected = select_primary_image(candidates)

    assert selected["image"] == b"color"


def test_crop_bright_margins_removes_white_border() -> None:
    image = np.full((10, 12, 3), 255, dtype=np.uint8)
    image[2:8, 3:9] = 10

    cropped = crop_bright_margins(image)

    assert cropped.shape[:2] == (6, 6)


def test_select_primary_image_requires_candidates() -> None:
    with pytest.raises(ValueError):
        select_primary_image([])
