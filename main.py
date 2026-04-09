#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from config_utils import DEFAULT_CONFIG_PATH
from runtime_utils import configure_logging

REPO_ROOT = Path(__file__).resolve().parent
LOGGER = logging.getLogger(__name__)


def timestamp() -> str:
    return datetime.now().astimezone().strftime("%a %b %d %H:%M:%S %Z %Y")


def format_command(command: list[str]) -> str:
    return shlex.join(command)


def run_command(
    command: list[str],
    *,
    cwd: Path = REPO_ROOT,
    env_overrides: dict[str, str] | None = None,
) -> None:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)

    LOGGER.info("$ %s", format_command(command))
    subprocess.run(command, cwd=cwd, env=env, check=True)


def clear_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for child in path.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def prepare_data_dirs() -> None:
    automorph_data = os.getenv("AUTOMORPH_DATA")
    if automorph_data:
        data_path = Path(automorph_data)
        data_path.mkdir(parents=True, exist_ok=True)
        (data_path / "images").mkdir(exist_ok=True)
        (data_path / "Results").mkdir(exist_ok=True)
        clear_directory(data_path / "Results")
        LOGGER.info("AUTOMORPH_DATA set to %s", automorph_data)
        return

    clear_directory(REPO_ROOT / "Results")
    LOGGER.info("AUTOMORPH_DATA not set, using default directory")


def run_preprocess() -> None:
    LOGGER.info("### Preprocess Start ###")
    run_command([sys.executable, "EyeQ_process_main.py"], cwd=REPO_ROOT / "M0_Preprocess")


def run_quality(config_path: Path | None) -> None:
    LOGGER.info("### Image Quality Assessment ###")
    command = [sys.executable, "run_inference.py"]
    if config_path is not None:
        command.extend(["--config", str(config_path)])
    run_command(command, cwd=REPO_ROOT / "M1_Retinal_Image_quality_EyePACS")


def run_segmentation(config_path: Path | None) -> None:
    LOGGER.info("### Segmentation Modules ###")
    command = [sys.executable, "run_inference.py"]
    if config_path is not None:
        command.extend(["--config", str(config_path)])
    run_command(command, cwd=REPO_ROOT / "M2_Vessel_seg")
    run_command(command, cwd=REPO_ROOT / "M2_Artery_vein")
    run_command(command, cwd=REPO_ROOT / "M2_lwnet_disc_cup")


def run_feature_measurement() -> None:
    LOGGER.info("### Feature Measuring ###")

    zone_cwd = REPO_ROOT / "M3_feature_zone" / "retipy"
    for script_name in [
        "create_datasets_disc_centred_B.py",
        "create_datasets_disc_centred_C.py",
        "create_datasets_macular_centred_B.py",
        "create_datasets_macular_centred_C.py",
    ]:
        run_command([sys.executable, script_name], cwd=zone_cwd)

    whole_pic_cwd = REPO_ROOT / "M3_feature_whole_pic" / "retipy"
    for script_name in [
        "create_datasets_macular_centred.py",
        "create_datasets_disc_centred.py",
    ]:
        run_command([sys.executable, script_name], cwd=whole_pic_cwd)

    run_command([sys.executable, "csv_merge.py"], cwd=REPO_ROOT)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the AutoMorph pipeline.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the pipeline config YAML.",
    )
    parser.add_argument("--no-process", "--no_process", dest="no_process", action="store_true")
    parser.add_argument("--no-quality", "--no_quality", dest="no_quality", action="store_true")
    parser.add_argument(
        "--no-segmentation",
        "--no_segmentation",
        dest="no_segmentation",
        action="store_true",
    )
    parser.add_argument("--no-feature", "--no_feature", dest="no_feature", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    configure_logging()
    LOGGER.info(timestamp())
    prepare_data_dirs()

    if args.no_process:
        LOGGER.info("### Skipping Preprocessing ###")
    else:
        run_preprocess()

    if args.no_quality:
        LOGGER.info("### Skipping Image Quality Assessment ###")
    else:
        run_quality(args.config)

    if args.no_segmentation:
        LOGGER.info("### Skipping Segmentation Modules ###")
    else:
        run_segmentation(args.config)

    if args.no_feature:
        LOGGER.info("### Skipping Feature Measurement ###")
    else:
        run_feature_measurement()

    LOGGER.info("### Done ###")
    LOGGER.info(timestamp())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
