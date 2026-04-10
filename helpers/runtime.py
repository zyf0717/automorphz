from __future__ import annotations

import logging
import re
from datetime import datetime
from datetime import timedelta
from datetime import timezone


LOG_TIMEZONE = timezone(timedelta(hours=8))
DEFAULT_LOG_FORMAT = "[%(asctime)s] %(message)s"


class Gmt8IsoFormatter(logging.Formatter):
    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=LOG_TIMEZONE)
        return timestamp.isoformat(timespec="seconds")


def _split_path(path: str) -> list[str]:
    return [part for part in re.split(r"[\\/]+", path) if part]


def portable_basename(path: str) -> str:
    parts = _split_path(path)
    return parts[-1] if parts else ""


def portable_parent_name(path: str) -> str:
    parts = _split_path(path)
    return parts[-2] if len(parts) >= 2 else ""


def resolve_torch_device(
    requested: str | None,
    *,
    cuda_available: bool,
    mps_available: bool,
) -> str:
    if requested and requested != "auto":
        return requested
    if cuda_available:
        return "cuda:0"
    if mps_available:
        return "mps"
    return "cpu"


def resolve_setting(
    cli_value,
    config_value,
    *,
    default=None,
):
    if cli_value is not None:
        return cli_value
    if config_value is not None:
        return config_value
    return default


def parse_image_size(value: str) -> tuple[int, int]:
    parts = [int(item.strip()) for item in str(value).split(",") if item.strip()]
    if len(parts) == 1:
        return (parts[0], parts[0])
    if len(parts) == 2:
        return (parts[0], parts[1])
    raise ValueError("im_size should be a number or a tuple of two numbers")


def configure_logging(
    *,
    level: int = logging.INFO,
    stream=None,
    fmt: str = DEFAULT_LOG_FORMAT,
) -> None:
    handler = logging.StreamHandler(stream)
    handler.setFormatter(Gmt8IsoFormatter(fmt))
    logging.basicConfig(level=level, handlers=[handler], force=True)
