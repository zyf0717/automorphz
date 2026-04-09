from __future__ import annotations

import os
import shutil
from pathlib import Path

import pandas as pd


JOIN_COLUMNS = [
    "Name",
    "Disc_height",
    "Disc_width",
    "Cup_height",
    "Cup_width",
    "CDR_vertical",
    "CDR_horizontal",
]


def m3_results_dir(base_dir: str | Path | None = None) -> Path:
    root = Path(base_dir) if base_dir is not None else Path(os.getenv("AUTOMORPH_DATA", "."))
    return root / "Results" / "M3"


def merge_feature_tables(base_dir: str | Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    results_dir = m3_results_dir(base_dir)
    disc_dir = results_dir / "Disc_centred"
    macular_dir = results_dir / "Macular_centred"

    disc_whole = pd.read_csv(disc_dir / "Disc_Measurement.csv")
    disc_zone_b = pd.read_csv(disc_dir / "Disc_Zone_B_Measurement.csv")
    disc_zone_c = pd.read_csv(disc_dir / "Disc_Zone_C_Measurement.csv")

    macular_whole = pd.read_csv(macular_dir / "Macular_Measurement.csv")
    macular_zone_b = pd.read_csv(macular_dir / "Macular_Zone_B_Measurement.csv")
    macular_zone_c = pd.read_csv(macular_dir / "Macular_Zone_C_Measurement.csv")

    disc_zone = disc_zone_b.merge(
        disc_zone_c,
        how="outer",
        on=JOIN_COLUMNS,
        suffixes=("_zone_b", "_zone_c"),
    )
    disc_all = disc_whole.merge(disc_zone, how="outer", on=JOIN_COLUMNS)

    macular_zone = macular_zone_b.merge(
        macular_zone_c,
        how="outer",
        on=JOIN_COLUMNS,
        suffixes=("_zone_b", "_zone_c"),
    )
    macular_all = macular_whole.merge(macular_zone, how="outer", on=JOIN_COLUMNS)

    disc_all.replace(-1, "", inplace=True)
    macular_all.replace(-1, "", inplace=True)
    return disc_all, macular_all


def write_feature_tables(base_dir: str | Path | None = None) -> tuple[Path, Path]:
    results_dir = m3_results_dir(base_dir)
    disc_all, macular_all = merge_feature_tables(base_dir)
    disc_output = results_dir / "Disc_Features.csv"
    macular_output = results_dir / "Macular_Features.csv"
    disc_all.to_csv(disc_output, index=False)
    macular_all.to_csv(macular_output, index=False)
    return disc_output, macular_output


def cleanup_intermediate_dirs(base_dir: str | Path | None = None) -> None:
    results_dir = m3_results_dir(base_dir)
    shutil.rmtree(results_dir / "Disc_centred", ignore_errors=True)
    shutil.rmtree(results_dir / "Macular_centred", ignore_errors=True)


def main() -> int:
    base_dir = os.getenv("AUTOMORPH_DATA", ".")
    write_feature_tables(base_dir)
    cleanup_intermediate_dirs(base_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
