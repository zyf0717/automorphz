#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import torch


SCRIPT_DIR = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run optic disc and cup segmentation.")
    parser.add_argument(
        "--config-file",
        default="experiments/wnet_All_three_1024_disc_cup/30/config.cfg",
    )
    parser.add_argument("--image-size", type=int, default=512)
    parser.add_argument("--device", default=None)
    return parser


def resolve_device(device: str | None) -> str:
    if device:
        return device
    if torch.cuda.is_available():
        return "cuda:0"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def main() -> int:
    args = build_parser().parse_args()
    device = resolve_device(args.device)
    subprocess.run(
        [
            sys.executable,
            "generate_av_results.py",
            "--config_file",
            args.config_file,
            "--im_size",
            str(args.image_size),
            "--device",
            device,
        ],
        cwd=SCRIPT_DIR,
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
