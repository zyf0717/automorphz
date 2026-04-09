from __future__ import annotations

import importlib
import logging
import sys
from pathlib import Path

import pandas as pd

from helpers.m3_parallel import resolve_feature_image_workers
from helpers.m3_parallel import run_records_in_pool
from helpers.runtime import portable_basename

WINDOW_SIZE = 912

BINARY_COLUMNS = [
    "Name",
    "Fractal_dimension",
    "Vessel_density",
    "Average_width",
    "Distance_tortuosity",
    "Squared_curvature_tortuosity",
    "Tortuosity_density",
]

ZONE_ARTERY_COLUMNS = [
    "Name",
    "Artery_Fractal_dimension",
    "Artery_Vessel_density",
    "Artery_Average_width",
    "Artery_Distance_tortuosity",
    "Artery_Squared_curvature_tortuosity",
    "Artery_Tortuosity_density",
    "CRAE_Hubbard",
    "CRAE_Knudtson",
]

ZONE_VEIN_COLUMNS = [
    "Name",
    "Vein_Fractal_dimension",
    "Vein_Vessel_density",
    "Vein_Average_width",
    "Vein_Distance_tortuosity",
    "Vein_Squared_curvature_tortuosity",
    "Vein_Tortuosity_density",
    "CRVE_Hubbard",
    "CRVE_Knudtson",
]

WHOLE_ARTERY_COLUMNS = [
    "Name",
    "Artery_Fractal_dimension",
    "Artery_Vessel_density",
    "Artery_Average_width",
    "Artery_Distance_tortuosity",
    "Artery_Squared_curvature_tortuosity",
    "Artery_Tortuosity_density",
]

WHOLE_VEIN_COLUMNS = [
    "Name",
    "Vein_Fractal_dimension",
    "Vein_Vessel_density",
    "Vein_Average_width",
    "Vein_Distance_tortuosity",
    "Vein_Squared_curvature_tortuosity",
    "Vein_Tortuosity_density",
]


def _load_retipy_components(package_root: str | Path):
    root = str(Path(package_root).resolve())
    if root not in sys.path:
        sys.path.insert(0, root)
    configuration = importlib.import_module("retipy.configuration")
    retina = importlib.import_module("retipy.retina")
    tortuosity_measures = importlib.import_module("retipy.tortuosity_measures")
    return configuration, retina, tortuosity_measures


def _base_row(
    name: str,
    *,
    prefix: str,
    fd: float,
    vd: float,
    average_width: float,
    distance_tortuosity: float,
    squared_curvature_tortuosity: float,
    tortuosity_density: float,
) -> dict[str, float | str]:
    return {
        "Name": name,
        f"{prefix}Fractal_dimension": fd,
        f"{prefix}Vessel_density": vd,
        f"{prefix}Average_width": average_width,
        f"{prefix}Distance_tortuosity": distance_tortuosity,
        f"{prefix}Squared_curvature_tortuosity": squared_curvature_tortuosity,
        f"{prefix}Tortuosity_density": tortuosity_density,
    }


def _error_row(name: str, columns: list[str], message: str) -> dict[str, float | str]:
    row: dict[str, float | str] = {column: -1 for column in columns if column != "Name"}
    row["Name"] = name
    row["_error"] = message
    return row


def _zone_worker(task: tuple[str, str, str, int, int, float, str]) -> dict[str, float | str]:
    phase, filename, package_root, pixels_per_window, sampling_size, r2_threshold, store_path = task
    name = portable_basename(filename)
    _, retina, tortuosity_measures = _load_retipy_components(package_root)
    try:
        segmented_image = retina.Retina(None, filename, store_path=store_path)
        window = retina.Window(segmented_image, WINDOW_SIZE, min_pixels=pixels_per_window)
        result = tortuosity_measures.evaluate_window(
            window,
            pixels_per_window,
            sampling_size,
            r2_threshold,
            store_path=store_path,
        )
        fd, vd, average_width, t2, t4, td = result[:6]
        if phase == "binary":
            return _base_row(
                name,
                prefix="",
                fd=fd,
                vd=vd,
                average_width=average_width,
                distance_tortuosity=t2,
                squared_curvature_tortuosity=t4,
                tortuosity_density=td,
            )
        if phase == "artery":
            row = _base_row(
                name,
                prefix="Artery_",
                fd=fd,
                vd=vd,
                average_width=average_width,
                distance_tortuosity=t2,
                squared_curvature_tortuosity=t4,
                tortuosity_density=td,
            )
            row["CRAE_Hubbard"] = result[9]
            row["CRAE_Knudtson"] = result[11]
            return row
        row = _base_row(
            name,
            prefix="Vein_",
            fd=fd,
            vd=vd,
            average_width=average_width,
            distance_tortuosity=t2,
            squared_curvature_tortuosity=t4,
            tortuosity_density=td,
        )
        row["CRVE_Hubbard"] = result[10]
        row["CRVE_Knudtson"] = result[12]
        return row
    except Exception as exc:
        columns = (
            BINARY_COLUMNS
            if phase == "binary"
            else ZONE_ARTERY_COLUMNS
            if phase == "artery"
            else ZONE_VEIN_COLUMNS
        )
        return _error_row(name, columns, f"[{phase}] {filename}: {exc}")


def _whole_worker(task: tuple[str, str, str, int, int, float, str]) -> dict[str, float | str]:
    phase, filename, package_root, pixels_per_window, sampling_size, r2_threshold, store_path = task
    name = portable_basename(filename)
    _, retina, tortuosity_measures = _load_retipy_components(package_root)
    try:
        segmented_image = retina.Retina(None, filename, store_path=store_path)
        window = retina.Window(segmented_image, WINDOW_SIZE, min_pixels=pixels_per_window)
        fd, vd, average_width, t2, t4, td = tortuosity_measures.evaluate_window(
            window,
            pixels_per_window,
            sampling_size,
            r2_threshold,
            store_path=store_path,
        )
        prefix = "" if phase == "binary" else "Artery_" if phase == "artery" else "Vein_"
        return _base_row(
            name,
            prefix=prefix,
            fd=fd,
            vd=vd,
            average_width=average_width,
            distance_tortuosity=t2,
            squared_curvature_tortuosity=t4,
            tortuosity_density=td,
        )
    except Exception as exc:
        columns = (
            BINARY_COLUMNS
            if phase == "binary"
            else WHOLE_ARTERY_COLUMNS
            if phase == "artery"
            else WHOLE_VEIN_COLUMNS
        )
        return _error_row(name, columns, f"[{phase}] {filename}: {exc}")


def _run_phase(
    *,
    files: list[str],
    phase: str,
    package_root: Path,
    pixels_per_window: int,
    sampling_size: int,
    r2_threshold: float,
    store_path: Path,
    worker,
    workers: int,
    logger: logging.Logger,
    label: str,
) -> list[dict[str, float | str]]:
    tasks = [
        (
            phase,
            filename,
            str(package_root),
            pixels_per_window,
            sampling_size,
            r2_threshold,
            str(store_path),
        )
        for filename in files
    ]
    return run_records_in_pool(tasks, worker, workers=workers, logger=logger, label=label)


def run_zone_measurement(
    *,
    package_root: Path,
    retipy_config_path: Path,
    disc_cup_csv: Path,
    output_csv: Path,
    title: str,
    progress_labels: dict[str, str],
    input_dirs: dict[str, Path],
    process_dirs: dict[str, Path],
    logger: logging.Logger,
) -> None:
    configuration, _, _ = _load_retipy_components(package_root)
    config = configuration.Configuration(str(retipy_config_path))
    workers = resolve_feature_image_workers()
    (output_csv.parent / "Width").mkdir(parents=True, exist_ok=True)

    binary_files = sorted(str(path) for path in input_dirs["binary"].glob("*.png"))
    artery_files = sorted(str(path) for path in input_dirs["artery"].glob("*.png"))
    vein_files = sorted(str(path) for path in input_dirs["vein"].glob("*.png"))
    logger.info(
        "%s: %d binary, %d artery, %d vein images",
        title,
        len(binary_files),
        len(artery_files),
        len(vein_files),
    )

    binary_rows = _run_phase(
        files=binary_files,
        phase="binary",
        package_root=package_root,
        pixels_per_window=config.pixels_per_window,
        sampling_size=config.sampling_size,
        r2_threshold=config.r_2_threshold,
        store_path=process_dirs["binary"],
        worker=_zone_worker,
        workers=workers,
        logger=logger,
        label=progress_labels["binary"],
    )
    artery_rows = _run_phase(
        files=artery_files,
        phase="artery",
        package_root=package_root,
        pixels_per_window=config.pixels_per_window,
        sampling_size=config.sampling_size,
        r2_threshold=config.r_2_threshold,
        store_path=process_dirs["artery"],
        worker=_zone_worker,
        workers=workers,
        logger=logger,
        label=progress_labels["artery"],
    )
    vein_rows = _run_phase(
        files=vein_files,
        phase="vein",
        package_root=package_root,
        pixels_per_window=config.pixels_per_window,
        sampling_size=config.sampling_size,
        r2_threshold=config.r_2_threshold,
        store_path=process_dirs["vein"],
        worker=_zone_worker,
        workers=workers,
        logger=logger,
        label=progress_labels["vein"],
    )

    disc_file = pd.read_csv(disc_cup_csv).astype({"Name": "object"})
    binary_df = pd.DataFrame(binary_rows, columns=BINARY_COLUMNS).astype({"Name": "object"})
    artery_df = pd.DataFrame(artery_rows, columns=ZONE_ARTERY_COLUMNS).astype({"Name": "object"})
    vein_df = pd.DataFrame(vein_rows, columns=ZONE_VEIN_COLUMNS).astype({"Name": "object"})

    disc_file_binary = pd.merge(disc_file, binary_df, how="outer", on=["Name"])
    artery_vein = pd.merge(artery_df, vein_df, how="outer", on=["Name"])
    merged = pd.merge(disc_file_binary, artery_vein, how="outer", on=["Name"])
    merged["AVR_Hubbard"] = merged["CRAE_Hubbard"] / merged["CRVE_Hubbard"]
    merged["AVR_Knudtson"] = merged["CRAE_Knudtson"] / merged["CRVE_Knudtson"]
    merged.to_csv(output_csv, index=None, encoding="utf8")
    logger.info("Wrote %s", output_csv)


def run_whole_measurement(
    *,
    package_root: Path,
    retipy_config_path: Path,
    disc_cup_csv: Path,
    output_csv: Path,
    title: str,
    progress_labels: dict[str, str],
    input_dirs: dict[str, Path],
    process_dirs: dict[str, Path],
    logger: logging.Logger,
) -> None:
    configuration, _, _ = _load_retipy_components(package_root)
    config = configuration.Configuration(str(retipy_config_path))
    workers = resolve_feature_image_workers()
    (output_csv.parent / "Width").mkdir(parents=True, exist_ok=True)

    binary_files = sorted(str(path) for path in input_dirs["binary"].glob("*.png"))
    artery_files = sorted(str(path) for path in input_dirs["artery"].glob("*.png"))
    vein_files = sorted(str(path) for path in input_dirs["vein"].glob("*.png"))
    logger.info(
        "%s: %d binary, %d artery, %d vein images",
        title,
        len(binary_files),
        len(artery_files),
        len(vein_files),
    )

    binary_rows = _run_phase(
        files=binary_files,
        phase="binary",
        package_root=package_root,
        pixels_per_window=config.pixels_per_window,
        sampling_size=config.sampling_size,
        r2_threshold=config.r_2_threshold,
        store_path=process_dirs["binary"],
        worker=_whole_worker,
        workers=workers,
        logger=logger,
        label=progress_labels["binary"],
    )
    artery_rows = _run_phase(
        files=artery_files,
        phase="artery",
        package_root=package_root,
        pixels_per_window=config.pixels_per_window,
        sampling_size=config.sampling_size,
        r2_threshold=config.r_2_threshold,
        store_path=process_dirs["artery"],
        worker=_whole_worker,
        workers=workers,
        logger=logger,
        label=progress_labels["artery"],
    )
    vein_rows = _run_phase(
        files=vein_files,
        phase="vein",
        package_root=package_root,
        pixels_per_window=config.pixels_per_window,
        sampling_size=config.sampling_size,
        r2_threshold=config.r_2_threshold,
        store_path=process_dirs["vein"],
        worker=_whole_worker,
        workers=workers,
        logger=logger,
        label=progress_labels["vein"],
    )

    disc_file = pd.read_csv(disc_cup_csv).astype({"Name": "object"})
    binary_df = pd.DataFrame(binary_rows, columns=BINARY_COLUMNS).astype({"Name": "object"})
    artery_df = pd.DataFrame(artery_rows, columns=WHOLE_ARTERY_COLUMNS).astype({"Name": "object"})
    vein_df = pd.DataFrame(vein_rows, columns=WHOLE_VEIN_COLUMNS).astype({"Name": "object"})

    disc_file_binary = pd.merge(disc_file, binary_df, how="outer", on=["Name"])
    artery_vein = pd.merge(artery_df, vein_df, how="outer", on=["Name"])
    merged = pd.merge(disc_file_binary, artery_vein, how="outer", on=["Name"])
    merged.to_csv(output_csv, index=None, encoding="utf8")
    logger.info("Wrote %s", output_csv)
