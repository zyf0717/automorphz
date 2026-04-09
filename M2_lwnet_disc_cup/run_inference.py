#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from helpers.config import load_config
from helpers.runtime import resolve_torch_device
SCRIPT_DIR = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run optic disc and cup segmentation.")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--config-file", default=None)
    parser.add_argument("--image-size", type=int, default=None)
    parser.add_argument("--device", default=None)
    return parser

def main() -> int:
    args = build_parser().parse_args()
    cfg = load_config(args.config).get("optic_disc_cup", {})
    config_file = args.config_file if args.config_file is not None else cfg["config_file"]
    image_size = args.image_size if args.image_size is not None else cfg["image_size"]
    raw_device = args.device if args.device is not None else cfg.get("device")
    device = resolve_torch_device(
        raw_device,
        cuda_available=torch.cuda.is_available(),
        mps_available=torch.backends.mps.is_available(),
    )
    subprocess.run(
        [
            sys.executable,
            "generate_av_results.py",
            "--config_file",
            config_file,
            "--im_size",
            str(image_size),
            "--device",
            device,
        ],
        cwd=SCRIPT_DIR,
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
