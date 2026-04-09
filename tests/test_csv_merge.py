from __future__ import annotations

from pathlib import Path

import pandas as pd

from helpers.csv_merge import cleanup_intermediate_dirs, merge_feature_tables, write_feature_tables


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def test_merge_feature_tables_and_cleanup(tmp_path: Path) -> None:
    disc_rows = [
        {
            "Name": "img1.png",
            "Disc_height": 1,
            "Disc_width": 2,
            "Cup_height": 3,
            "Cup_width": 4,
            "CDR_vertical": 0.5,
            "CDR_horizontal": 0.6,
            "whole_only": -1,
        }
    ]
    zone_b_rows = [
        {
            "Name": "img1.png",
            "Disc_height": 1,
            "Disc_width": 2,
            "Cup_height": 3,
            "Cup_width": 4,
            "CDR_vertical": 0.5,
            "CDR_horizontal": 0.6,
            "zone_b_only": 10,
        }
    ]
    zone_c_rows = [
        {
            "Name": "img1.png",
            "Disc_height": 1,
            "Disc_width": 2,
            "Cup_height": 3,
            "Cup_width": 4,
            "CDR_vertical": 0.5,
            "CDR_horizontal": 0.6,
            "zone_c_only": 11,
        }
    ]

    results_dir = tmp_path / "Results" / "M3"
    write_csv(results_dir / "Disc_centred" / "Disc_Measurement.csv", disc_rows)
    write_csv(results_dir / "Disc_centred" / "Disc_Zone_B_Measurement.csv", zone_b_rows)
    write_csv(results_dir / "Disc_centred" / "Disc_Zone_C_Measurement.csv", zone_c_rows)
    write_csv(results_dir / "Macular_centred" / "Macular_Measurement.csv", disc_rows)
    write_csv(results_dir / "Macular_centred" / "Macular_Zone_B_Measurement.csv", zone_b_rows)
    write_csv(results_dir / "Macular_centred" / "Macular_Zone_C_Measurement.csv", zone_c_rows)

    disc_all, macular_all = merge_feature_tables(tmp_path)

    assert disc_all.loc[0, "whole_only"] == ""
    assert disc_all.loc[0, "zone_b_only"] == 10
    assert disc_all.loc[0, "zone_c_only"] == 11
    assert macular_all.loc[0, "Name"] == "img1.png"

    disc_output, macular_output = write_feature_tables(tmp_path)
    assert disc_output.exists()
    assert macular_output.exists()

    cleanup_intermediate_dirs(tmp_path)
    assert not (results_dir / "Disc_centred").exists()
    assert not (results_dir / "Macular_centred").exists()
