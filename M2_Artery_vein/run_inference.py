#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run artery and vein segmentation.")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--dataset", default="ALL-AV")
    parser.add_argument("--checkstart", type=int, default=1401)
    parser.add_argument("--job-name", default="20210724_ALL-AV_randomseed")
    parser.add_argument("--cuda-device", default="0")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f".{os.pathsep}{pythonpath}" if pythonpath else "."
    env["CUDA_VISIBLE_DEVICES"] = args.cuda_device

    subprocess.run(
        [
            sys.executable,
            "test_outside.py",
            f"--batch-size={args.batch_size}",
            f"--dataset={args.dataset}",
            f"--job_name={args.job_name}",
            f"--checkstart={args.checkstart}",
            "--uniform=True",
        ],
        cwd=SCRIPT_DIR,
        env=env,
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
