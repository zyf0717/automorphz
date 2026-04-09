#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent


def timestamp() -> str:
    return datetime.now().astimezone().strftime("%a %b %d %H:%M:%S %Z %Y")


def print_timestamp() -> None:
    print(timestamp(), flush=True)


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

    print(f"$ {format_command(command)}", flush=True)
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
        print(f"AUTOMORPH_DATA set to {automorph_data}", flush=True)
        return

    clear_directory(REPO_ROOT / "Results")
    print("AUTOMORPH_DATA not set, using default directory", flush=True)


def module_env(*, add_pythonpath: bool = False) -> dict[str, str]:
    env: dict[str, str] = {}
    if add_pythonpath:
        pythonpath = os.environ.get("PYTHONPATH")
        env["PYTHONPATH"] = f".{os.pathsep}{pythonpath}" if pythonpath else "."
    return env


def data_ref(default_relative: str) -> str:
    return os.getenv("AUTOMORPH_DATA", default_relative)


def run_preprocess() -> None:
    print("### Preprocess Start ###", flush=True)
    run_command([sys.executable, "EyeQ_process_main.py"], cwd=REPO_ROOT / "M0_Preprocess")


def run_quality() -> None:
    print("### Image Quality Assessment ###", flush=True)
    run_command([sys.executable, "run_inference.py"], cwd=REPO_ROOT / "M1_Retinal_Image_quality_EyePACS")


def run_segmentation() -> None:
    print("### Segmentation Modules ###", flush=True)
    run_command([sys.executable, "run_inference.py"], cwd=REPO_ROOT / "M2_Vessel_seg")
    run_command([sys.executable, "run_inference.py"], cwd=REPO_ROOT / "M2_Artery_vein")
    run_command([sys.executable, "run_inference.py"], cwd=REPO_ROOT / "M2_lwnet_disc_cup")


def run_feature_measurement() -> None:
    print("### Feature Measuring ###", flush=True)

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

    print_timestamp()
    prepare_data_dirs()

    if args.no_process:
        print("### Skipping Preprocessing ###", flush=True)
    else:
        run_preprocess()

    if args.no_quality:
        print("### Skipping Image Quality Assessment ###", flush=True)
    else:
        run_quality()

    if args.no_segmentation:
        print("### Skipping Segmentation Modules ###", flush=True)
    else:
        run_segmentation()

    if args.no_feature:
        print("### Skipping Feature Measurement ###", flush=True)
    else:
        run_feature_measurement()

    print("### Done ###", flush=True)
    print_timestamp()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
