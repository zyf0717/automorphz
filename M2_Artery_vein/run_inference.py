#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from helpers.config import load_config
SCRIPT_DIR = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run artery and vein segmentation.")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--dataset", default=None)
    parser.add_argument("--checkstart", type=int, default=None)
    parser.add_argument("--job-name", default=None)
    parser.add_argument("--cuda-device", default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cfg = load_config(args.config).get("artery_vein", {})
    batch_size = args.batch_size if args.batch_size is not None else cfg["batch_size"]
    dataset = args.dataset if args.dataset is not None else cfg["dataset"]
    checkstart = args.checkstart if args.checkstart is not None else cfg["checkstart"]
    job_name = args.job_name if args.job_name is not None else cfg["job_name"]
    cuda_device = args.cuda_device if args.cuda_device is not None else cfg["cuda_device"]
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f".{os.pathsep}{pythonpath}" if pythonpath else "."
    env["CUDA_VISIBLE_DEVICES"] = str(cuda_device)
    uniform = "True" if cfg.get("uniform", True) else "False"

    subprocess.run(
        [
            sys.executable,
            "test_outside.py",
            f"--batch-size={batch_size}",
            f"--dataset={dataset}",
            f"--job_name={job_name}",
            f"--checkstart={checkstart}",
            f"--uniform={uniform}",
        ],
        cwd=SCRIPT_DIR,
        env=env,
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
