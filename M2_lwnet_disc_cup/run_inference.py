#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run optic disc and cup segmentation.")
    parser.add_argument(
        "--config-file",
        default="experiments/wnet_All_three_1024_disc_cup/30/config.cfg",
    )
    parser.add_argument("--image-size", type=int, default=512)
    parser.add_argument("--device", default="cuda:0")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    subprocess.run(
        [
            sys.executable,
            "generate_av_results.py",
            "--config_file",
            args.config_file,
            "--im_size",
            str(args.image_size),
            "--device",
            args.device,
        ],
        cwd=SCRIPT_DIR,
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
