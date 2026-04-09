from __future__ import annotations

import csv
from pathlib import Path

from helpers.resolution import iter_image_names, write_global_resolution_csv


def test_iter_image_names_filters_supported_images(tmp_path: Path) -> None:
    (tmp_path / "a.png").write_text("a", encoding="utf-8")
    (tmp_path / "b.jpg").write_text("b", encoding="utf-8")
    (tmp_path / ".hidden.png").write_text("c", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("d", encoding="utf-8")

    assert iter_image_names(tmp_path) == ["a.png", "b.jpg"]


def test_write_global_resolution_csv_writes_flat_table(tmp_path: Path) -> None:
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    (images_dir / "left.png").write_text("x", encoding="utf-8")
    (images_dir / "right.png").write_text("y", encoding="utf-8")

    output_path = write_global_resolution_csv(images_dir, tmp_path / "resolution_information.csv", 0.00185)

    with output_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows == [
        {"fundus": "left.png", "res": "0.00185"},
        {"fundus": "right.png", "res": "0.00185"},
    ]
