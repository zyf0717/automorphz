#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run vessel segmentation.")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--validation-ratio", type=float, default=10.0)
    parser.add_argument("--alpha", type=float, default=0.08)
    parser.add_argument("--beta", type=float, default=1.1)
    parser.add_argument("--gamma", type=float, default=0.5)
    parser.add_argument("--dataset", default="ALL-SIX")
    parser.add_argument("--seed-num", type=int, default=42)
    parser.add_argument("--pre-threshold", type=float, default=40.0)
    parser.add_argument("--cuda-device", default="0")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    automorph_data = os.getenv("AUTOMORPH_DATA", "..")
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = args.cuda_device
    job_name = f"20210630_uniform_thres40_{args.dataset}"

    subprocess.run(
        [
            sys.executable,
            "test_outside_integrated.py",
            f"--epochs={args.epochs}",
            f"--batchsize={args.batch_size}",
            f"--learning_rate={args.learning_rate}",
            f"--validation_ratio={args.validation_ratio}",
            f"--alpha={args.alpha}",
            f"--beta={args.beta}",
            f"--gamma={args.gamma}",
            f"--dataset={args.dataset}",
            f"--dataset_test={args.dataset}",
            "--uniform=True",
            f"--jn={job_name}",
            "--worker_num=2",
            "--save_model=best",
            "--train_test_mode=test",
            f"--pre_threshold={args.pre_threshold}",
            f"--seed_num={args.seed_num}",
            f"--out_test={automorph_data}/Results/M2/binary_vessel/",
        ],
        cwd=SCRIPT_DIR,
        env=env,
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
