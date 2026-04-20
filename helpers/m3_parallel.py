from __future__ import annotations

import logging
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Callable

from helpers.config import DEFAULT_CONFIG_PATH, load_config


def resolve_feature_image_workers(config_path: str | Path | None = None) -> int:
    config = load_config(config_path or DEFAULT_CONFIG_PATH)
    workers = int(config.get("feature_measurement", {}).get("image_workers", 1))
    return max(1, workers)


def run_records_in_pool(
    items: list,
    worker: Callable,
    *,
    workers: int,
    logger: logging.Logger,
    label: str,
    progress_every: int = 10,
) -> list:
    total = len(items)
    if total == 0:
        logger.info("%s: no images to process", label)
        return []

    def run_serially() -> list:
        results = []
        for index, item in enumerate(items, start=1):
            result = worker(item)
            if index == 1 or index == total or index % progress_every == 0:
                logger.info("%s: processed %d/%d", label, index, total)
            if isinstance(result, dict) and result.get("_error"):
                logger.error("%s: %s", label, result["_error"])
            results.append(result)
        return results

    logger.info("%s: processing %d images with %d workers", label, total, workers)

    if workers <= 1:
        return run_serially()

    results = []
    try:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for index, result in enumerate(executor.map(worker, items), start=1):
                if index == 1 or index == total or index % progress_every == 0:
                    logger.info("%s: processed %d/%d", label, index, total)
                if isinstance(result, dict) and result.get("_error"):
                    logger.error("%s: %s", label, result["_error"])
                results.append(result)
    except PermissionError as exc:
        logger.warning(
            "%s: process pool unavailable (%s); falling back to serial execution",
            label,
            exc,
        )
        return run_serially()
    return results
