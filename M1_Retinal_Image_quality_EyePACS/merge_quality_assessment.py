import logging
import os
import shutil
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from helpers.runtime import configure_logging

LOGGER = logging.getLogger(__name__)


def quality_results_dir(base_dir: str | Path | None = None) -> Path:
    root = Path(base_dir) if base_dir is not None else Path(os.getenv("AUTOMORPH_DATA", ".."))
    return root / "Results" / "M1"


def split_quality_assessment(base_dir: str | Path | None = None) -> tuple[int, int]:
    results_dir = quality_results_dir(base_dir)
    good_dir = results_dir / "Good_quality"
    bad_dir = results_dir / "Bad_quality"
    good_dir.mkdir(parents=True, exist_ok=True)
    bad_dir.mkdir(parents=True, exist_ok=True)

    results = pd.read_csv(results_dir / "results_ensemble.csv")
    eye_good = 0
    eye_bad = 0

    for _, row in results.iterrows():
        name = row["Name"]
        prediction = row["Prediction"]
        softmax_bad = row["softmax_bad"]
        if prediction == 0 or (prediction == 1 and softmax_bad < 0.25):
            eye_good += 1
            shutil.copy(name, good_dir)
        else:
            eye_bad += 1
            shutil.copy(name, bad_dir)

    LOGGER.info("Gradable cases by EyePACS_QA is %s", eye_good)
    LOGGER.info("Ungradable cases by EyePACS_QA is %s", eye_bad)
    return eye_good, eye_bad


def main() -> int:
    configure_logging()
    split_quality_assessment()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
