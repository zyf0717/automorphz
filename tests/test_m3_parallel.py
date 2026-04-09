from __future__ import annotations

from pathlib import Path

from helpers.m3_parallel import resolve_feature_image_workers


def test_resolve_feature_image_workers_from_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("feature_measurement:\n  image_workers: 3\n", encoding="utf-8")

    assert resolve_feature_image_workers(config_path) == 3
