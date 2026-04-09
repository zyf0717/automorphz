from __future__ import annotations

from pathlib import Path

import pytest

from config_utils import load_config


def test_load_config_reads_mapping(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("quality:\n  batch_size: 4\n", encoding="utf-8")

    assert load_config(config_path) == {"quality": {"batch_size": 4}}


def test_load_config_rejects_non_mapping_root(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("- item\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_config(config_path)
