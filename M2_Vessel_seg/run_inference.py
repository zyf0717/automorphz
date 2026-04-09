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

from config_utils import load_config
SCRIPT_DIR = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run vessel segmentation.")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--learning-rate", type=float, default=None)
    parser.add_argument("--validation-ratio", type=float, default=None)
    parser.add_argument("--alpha", type=float, default=None)
    parser.add_argument("--beta", type=float, default=None)
    parser.add_argument("--gamma", type=float, default=None)
    parser.add_argument("--dataset", default=None)
    parser.add_argument("--seed-num", type=int, default=None)
    parser.add_argument("--pre-threshold", type=float, default=None)
    parser.add_argument("--cuda-device", default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cfg = load_config(args.config).get("vessel_segmentation", {})
    epochs = args.epochs if args.epochs is not None else cfg["epochs"]
    batch_size = args.batch_size if args.batch_size is not None else cfg["batch_size"]
    learning_rate = args.learning_rate if args.learning_rate is not None else cfg["learning_rate"]
    validation_ratio = args.validation_ratio if args.validation_ratio is not None else cfg["validation_ratio"]
    alpha = args.alpha if args.alpha is not None else cfg["alpha"]
    beta = args.beta if args.beta is not None else cfg["beta"]
    gamma = args.gamma if args.gamma is not None else cfg["gamma"]
    dataset = args.dataset if args.dataset is not None else cfg["dataset"]
    seed_num = args.seed_num if args.seed_num is not None else cfg["seed_num"]
    pre_threshold = args.pre_threshold if args.pre_threshold is not None else cfg["pre_threshold"]
    cuda_device = args.cuda_device if args.cuda_device is not None else cfg["cuda_device"]
    automorph_data = os.getenv("AUTOMORPH_DATA", "..")
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(cuda_device)
    job_name = cfg["job_name_template"].format(dataset=dataset)
    uniform = "True" if cfg.get("uniform", True) else "False"

    subprocess.run(
        [
            sys.executable,
            "test_outside_integrated.py",
            f"--epochs={epochs}",
            f"--batchsize={batch_size}",
            f"--learning_rate={learning_rate}",
            f"--validation_ratio={validation_ratio}",
            f"--alpha={alpha}",
            f"--beta={beta}",
            f"--gamma={gamma}",
            f"--dataset={dataset}",
            f"--dataset_test={dataset}",
            f"--uniform={uniform}",
            f"--jn={job_name}",
            f"--worker_num={cfg['worker_num']}",
            f"--save_model={cfg['save_model']}",
            f"--train_test_mode={cfg['train_test_mode']}",
            f"--pre_threshold={pre_threshold}",
            f"--seed_num={seed_num}",
            f"--out_test={automorph_data}/Results/M2/binary_vessel/",
        ],
        cwd=SCRIPT_DIR,
        env=env,
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
