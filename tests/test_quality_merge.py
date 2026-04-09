from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pandas as pd


MODULE_PATH = Path(__file__).resolve().parents[1] / "M1_Retinal_Image_quality_EyePACS" / "merge_quality_assessment.py"
SPEC = spec_from_file_location("merge_quality_assessment", MODULE_PATH)
merge_quality_assessment = module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(merge_quality_assessment)


def test_split_quality_assessment_routes_files(tmp_path: Path) -> None:
    results_dir = tmp_path / "Results" / "M1"
    results_dir.mkdir(parents=True)

    image_a = tmp_path / "a.png"
    image_b = tmp_path / "b.png"
    image_c = tmp_path / "c.png"
    image_a.write_text("a", encoding="utf-8")
    image_b.write_text("b", encoding="utf-8")
    image_c.write_text("c", encoding="utf-8")

    pd.DataFrame(
        [
            {"Name": str(image_a), "Prediction": 0, "softmax_bad": 0.9, "usable_sd": 0.0},
            {"Name": str(image_b), "Prediction": 1, "softmax_bad": 0.2, "usable_sd": 0.0},
            {"Name": str(image_c), "Prediction": 1, "softmax_bad": 0.4, "usable_sd": 0.0},
        ]
    ).to_csv(results_dir / "results_ensemble.csv", index=False)

    good, bad = merge_quality_assessment.split_quality_assessment(tmp_path)

    assert (results_dir / "Good_quality" / "a.png").exists()
    assert (results_dir / "Good_quality" / "b.png").exists()
    assert (results_dir / "Bad_quality" / "c.png").exists()
    assert (good, bad) == (2, 1)
