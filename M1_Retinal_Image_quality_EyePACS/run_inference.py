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
    parser = argparse.ArgumentParser(description="Run retinal image quality assessment.")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--cuda-device", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--round", type=int, default=None)
    parser.add_argument("--seed-num", type=int, default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cfg = load_config(args.config).get("quality", {})
    batch_size = args.batch_size if args.batch_size is not None else cfg["batch_size"]
    cuda_device = args.cuda_device if args.cuda_device is not None else cfg["cuda_device"]
    model = args.model if args.model is not None else cfg["model"]
    round_num = args.round if args.round is not None else cfg["round"]
    seed_num = args.seed_num if args.seed_num is not None else cfg.get("seed_num")
    if seed_num is None:
        seed_num = 42 - 2 * round_num
    automorph_data = os.getenv("AUTOMORPH_DATA", "..")
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f".{os.pathsep}{pythonpath}" if pythonpath else "."
    env["CUDA_VISIBLE_DEVICES"] = str(cuda_device)

    subprocess.run(
        [
            sys.executable,
            "test_outside.py",
            "--e=1",
            f"--b={batch_size}",
            f"--task_name={cfg['task_name']}",
            f"--model={model}",
            f"--round={round_num}",
            f"--train_on_dataset={cfg['train_on_dataset']}",
            f"--test_on_dataset={cfg['test_on_dataset']}",
            f"--test_csv_dir={automorph_data}/Results/M0/images/",
            f"--n_class={cfg['n_class']}",
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
