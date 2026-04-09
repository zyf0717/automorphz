from __future__ import annotations

from runtime_utils import (
    parse_image_size,
    portable_basename,
    portable_parent_name,
    resolve_setting,
    resolve_torch_device,
)


def test_portable_basename_handles_posix_and_windows_paths() -> None:
    assert portable_basename("/tmp/images/example.png") == "example.png"
    assert portable_basename(r"C:\tmp\images\example.png") == "example.png"


def test_portable_parent_name_handles_posix_and_windows_paths() -> None:
    assert portable_parent_name("/tmp/artery_binary_process/output.png") == "artery_binary_process"
    assert portable_parent_name(r"C:\tmp\vein_binary_process\output.png") == "vein_binary_process"


def test_resolve_torch_device_prefers_requested_value_then_available_accelerator() -> None:
    assert resolve_torch_device("cpu", cuda_available=True, mps_available=True) == "cpu"
    assert resolve_torch_device("auto", cuda_available=True, mps_available=False) == "cuda:0"
    assert resolve_torch_device(None, cuda_available=False, mps_available=True) == "mps"
    assert resolve_torch_device(None, cuda_available=False, mps_available=False) == "cpu"


def test_resolve_setting_preserves_manual_override() -> None:
    assert resolve_setting("manual", "config", default="fallback") == "manual"
    assert resolve_setting(None, "config", default="fallback") == "config"
    assert resolve_setting(None, None, default="fallback") == "fallback"


def test_parse_image_size_accepts_square_and_rectangular_values() -> None:
    assert parse_image_size("512") == (512, 512)
    assert parse_image_size("600,400") == (600, 400)
