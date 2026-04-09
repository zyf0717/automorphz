#!/usr/bin/env python3

import argparse
import logging
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from helpers.m3_measurement import run_zone_measurement
from helpers.runtime import configure_logging

AUTOMORPH_DATA = os.getenv("AUTOMORPH_DATA", "../..")
LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--configuration",
        help="the configuration file location",
        default="resources/retipy.config",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    configure_logging()
    script_root = Path(__file__).resolve().parent
    data_root = Path(AUTOMORPH_DATA)

    run_zone_measurement(
        package_root=script_root,
        retipy_config_path=script_root / args.configuration,
        disc_cup_csv=data_root / "Results/M3/Macular_centred/Disc_cup_results.csv",
        output_csv=data_root / "Results/M3/Macular_centred/Macular_Zone_C_Measurement.csv",
        title="Macular-centred zone C",
        progress_labels={
            "binary": "[Macular Zone C][binary]",
            "artery": "[Macular Zone C][artery]",
            "vein": "[Macular Zone C][vein]",
        },
        input_dirs={
            "binary": data_root / "Results/M2/binary_vessel/macular_Zone_C_centred_binary_skeleton",
            "artery": data_root / "Results/M2/artery_vein/macular_Zone_C_centred_artery_skeleton",
            "vein": data_root / "Results/M2/artery_vein/macular_Zone_C_centred_vein_skeleton",
        },
        process_dirs={
            "binary": data_root / "Results/M2/binary_vessel/macular_Zone_C_centred_binary_process",
            "artery": data_root / "Results/M2/artery_vein/macular_Zone_C_centred_artery_process",
            "vein": data_root / "Results/M2/artery_vein/macular_Zone_C_centred_vein_process",
        },
        logger=LOGGER,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
