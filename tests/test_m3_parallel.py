from __future__ import annotations

import logging
import os
import time
from pathlib import Path

from helpers.m3_parallel import resolve_feature_image_workers
from helpers.m3_parallel import run_records_in_pool


def _parallel_pid_worker(item: int) -> dict[str, int]:
    time.sleep(0.1)
    return {"item": item, "pid": os.getpid()}


def _serial_error_worker(item: int) -> dict[str, int | str]:
    if item == 2:
        return {"item": item, "_error": "bad image"}
    return {"item": item}


def test_resolve_feature_image_workers_from_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("feature_measurement:\n  image_workers: 3\n", encoding="utf-8")

    assert resolve_feature_image_workers(config_path) == 3


def test_resolve_feature_image_workers_clamps_to_at_least_one(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("feature_measurement:\n  image_workers: 0\n", encoding="utf-8")

    assert resolve_feature_image_workers(config_path) == 1


def test_run_records_in_pool_uses_multiple_processes_and_preserves_order(caplog) -> None:
    logger = logging.getLogger("tests.m3_parallel.process_pool")
    items = [1, 2, 3, 4, 5, 6]

    with caplog.at_level(logging.INFO, logger=logger.name):
        results = run_records_in_pool(
            items,
            _parallel_pid_worker,
            workers=3,
            logger=logger,
            label="zone",
            progress_every=2,
        )

    assert [result["item"] for result in results] == items
    assert len({result["pid"] for result in results}) >= 2
    assert "zone: processing 6 images with 3 workers" in caplog.text
    assert "zone: processed 6/6" in caplog.text


def test_run_records_in_pool_serial_path_logs_errors(caplog) -> None:
    logger = logging.getLogger("tests.m3_parallel.serial")

    with caplog.at_level(logging.INFO, logger=logger.name):
        results = run_records_in_pool(
            [1, 2, 3],
            _serial_error_worker,
            workers=1,
            logger=logger,
            label="whole",
            progress_every=2,
        )

    assert results == [{"item": 1}, {"item": 2, "_error": "bad image"}, {"item": 3}]
    assert "whole: processing 3 images with 1 workers" in caplog.text
    assert "whole: processed 3/3" in caplog.text
    assert "whole: bad image" in caplog.text


def test_run_records_in_pool_handles_empty_input(caplog) -> None:
    logger = logging.getLogger("tests.m3_parallel.empty")

    with caplog.at_level(logging.INFO, logger=logger.name):
        results = run_records_in_pool(
            [],
            _parallel_pid_worker,
            workers=4,
            logger=logger,
            label="binary",
        )

    assert results == []
    assert "binary: no images to process" in caplog.text
