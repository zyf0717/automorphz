from __future__ import annotations

from pathlib import Path

import pytest

from helpers.flatten_nested import flatten_nested_images, iter_nested_images


def test_flatten_nested_images_copies_recursive_images(tmp_path: Path) -> None:
    source = tmp_path / "nested_folder"
    destination = tmp_path / "images"
    (source / "nxg101" / "fam").mkdir(parents=True)
    (source / "nxg101" / "run").mkdir(parents=True)
    (source / "nxg101" / "fam" / "left.png").write_text("left", encoding="utf-8")
    (source / "nxg101" / "run" / "right.jpg").write_text("right", encoding="utf-8")
    (source / "nxg101" / "run" / "notes.txt").write_text("ignore", encoding="utf-8")

    images = iter_nested_images(source)
    copied = flatten_nested_images(source, destination)

    assert [path.name for path in images] == ["left.png", "right.jpg"]
    assert [path.name for path in copied] == ["left.png", "right.jpg"]
    assert (destination / "left.png").exists()
    assert (destination / "right.jpg").exists()


def test_flatten_nested_images_rejects_duplicate_basenames(tmp_path: Path) -> None:
    source = tmp_path / "nested_folder"
    destination = tmp_path / "images"
    (source / "nxg101" / "fam").mkdir(parents=True)
    (source / "nxg101" / "run").mkdir(parents=True)
    (source / "nxg101" / "fam" / "duplicate.png").write_text("a", encoding="utf-8")
    (source / "nxg101" / "run" / "duplicate.png").write_text("b", encoding="utf-8")

    with pytest.raises(ValueError):
        flatten_nested_images(source, destination)
