from __future__ import annotations

import os
from pathlib import Path

from helpers import data


def test_resolve_config_image_dir_supports_relative_paths(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("input:\n  image_dir: nested/images\n", encoding="utf-8")

    assert data.resolve_config_image_dir(config_path) == (tmp_path / "nested" / "images")


def test_prepare_data_dirs_uses_configured_relative_input_dir(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(data, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(data, "SAMPLE_IMAGES_DIR", tmp_path / "sample_images")
    monkeypatch.setattr(data, "SAMPLE_RUN_ROOT", tmp_path / ".automorph_sample_run")
    monkeypatch.delenv("AUTOMORPH_DATA", raising=False)

    source_dir = tmp_path / "nested" / "images"
    source_dir.mkdir(parents=True)
    (source_dir / "example.png").write_text("x", encoding="utf-8")

    config_path = tmp_path / "config.yaml"
    config_path.write_text("input:\n  image_dir: nested/images\n", encoding="utf-8")

    root = data.prepare_data_dirs(config_path=config_path)

    assert root == tmp_path
    assert (tmp_path / "images" / "example.png").exists()
    assert (tmp_path / "Results").exists()


def test_prepare_data_dirs_force_sample_images_uses_isolated_root(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(data, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(data, "SAMPLE_IMAGES_DIR", tmp_path / "sample_images")
    monkeypatch.setattr(data, "SAMPLE_RUN_ROOT", tmp_path / ".automorph_sample_run")
    monkeypatch.delenv("AUTOMORPH_DATA", raising=False)

    sample_images = tmp_path / "sample_images"
    sample_images.mkdir()
    (sample_images / "example.png").write_text("x", encoding="utf-8")

    root = data.prepare_data_dirs(use_sample_images=True)

    assert root == tmp_path / ".automorph_sample_run"
    assert Path(os.environ["AUTOMORPH_DATA"]) == root
    assert (root / "images" / "example.png").exists()
    assert (root / "Results").exists()
