#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run retinal image quality assessment.")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--cuda-device", default="0")
    parser.add_argument("--model", default="efficientnet")
    parser.add_argument("--round", type=int, default=0)
    parser.add_argument("--seed-num", type=int, default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    seed_num = args.seed_num if args.seed_num is not None else 42 - 2 * args.round
    automorph_data = os.getenv("AUTOMORPH_DATA", "..")
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f".{os.pathsep}{pythonpath}" if pythonpath else "."
    env["CUDA_VISIBLE_DEVICES"] = args.cuda_device

    subprocess.run(
        [
            sys.executable,
            "test_outside.py",
            "--e=1",
            f"--b={args.batch_size}",
            "--task_name=Retinal_quality",
            f"--model={args.model}",
            f"--round={args.round}",
            "--train_on_dataset=EyePACS_quality",
            "--test_on_dataset=customised_data",
            f"--test_csv_dir={automorph_data}/Results/M0/images/",
            "--n_class=3",
            f"--seed_num={seed_num}",
        ],
        cwd=SCRIPT_DIR,
        env=env,
        check=True,
    )
    subprocess.run([sys.executable, "merge_quality_assessment.py"], cwd=SCRIPT_DIR, env=env, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
