from __future__ import annotations

import logging
import re
import sys


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


def configure_logging(*, level: int = logging.INFO, stream=None, fmt: str = "%(message)s") -> None:
    logging.basicConfig(level=level, format=fmt, stream=stream, force=True)
