from __future__ import annotations

import json
from pathlib import Path

from M2_lwnet_disc_cup import generate_av_results


def test_resolve_runtime_options_prefers_cli_values(tmp_path: Path) -> None:
    config_path = tmp_path / "config.cfg"
    config_path.write_text(
        json.dumps(
            {
                "model_name": "wnet",
                "im_size": "512",
                "device": "cpu",
            }
        ),
        encoding="utf-8",
    )

    config, image_size, device = generate_av_results.resolve_runtime_options(
        config_file=str(config_path),
        cli_im_size="600,400",
        cli_device="mps",
        cuda_available=True,
        mps_available=True,
    )

    assert config["model_name"] == "wnet"
    assert image_size == (600, 400)
    assert str(device) == "mps"


def test_resolve_runtime_options_uses_config_defaults(tmp_path: Path) -> None:
    config_path = tmp_path / "config.cfg"
    config_path.write_text(
        json.dumps(
            {
                "model_name": "wnet",
                "im_size": "384",
                "device": "auto",
            }
        ),
        encoding="utf-8",
    )

    _, image_size, device = generate_av_results.resolve_runtime_options(
        config_file=str(config_path),
        cli_im_size=None,
        cli_device=None,
        cuda_available=False,
        mps_available=False,
    )

    assert image_size == (384, 384)
    assert str(device) == "cpu"
