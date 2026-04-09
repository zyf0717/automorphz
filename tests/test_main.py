from __future__ import annotations

from pathlib import Path

import main


def test_main_runs_stages_in_order(monkeypatch) -> None:
    calls: list[tuple[list[str], Path]] = []

    def fake_run_command(command, *, cwd=main.REPO_ROOT, env_overrides=None):
        calls.append((command, cwd))

    monkeypatch.setattr(main, "run_command", fake_run_command)
    monkeypatch.setattr(main, "prepare_data_dirs", lambda: None)
    monkeypatch.setattr(main, "configure_logging", lambda: None)
    monkeypatch.setattr(main, "timestamp", lambda: "ts")
    monkeypatch.setattr(main.sys, "argv", ["main.py"])

    assert main.main() == 0

    expected = [
        (["main.py"], None),  # placeholder for shape only
    ]
    del expected

    assert calls == [
        ([main.sys.executable, "EyeQ_process_main.py"], main.REPO_ROOT / "M0_Preprocess"),
        ([main.sys.executable, "run_inference.py", "--config", str(main.DEFAULT_CONFIG_PATH)], main.REPO_ROOT / "M1_Retinal_Image_quality_EyePACS"),
        ([main.sys.executable, "run_inference.py", "--config", str(main.DEFAULT_CONFIG_PATH)], main.REPO_ROOT / "M2_Vessel_seg"),
        ([main.sys.executable, "run_inference.py", "--config", str(main.DEFAULT_CONFIG_PATH)], main.REPO_ROOT / "M2_Artery_vein"),
        ([main.sys.executable, "run_inference.py", "--config", str(main.DEFAULT_CONFIG_PATH)], main.REPO_ROOT / "M2_lwnet_disc_cup"),
        ([main.sys.executable, "create_datasets_disc_centred_B.py"], main.REPO_ROOT / "M3_feature_zone" / "retipy"),
        ([main.sys.executable, "create_datasets_disc_centred_C.py"], main.REPO_ROOT / "M3_feature_zone" / "retipy"),
        ([main.sys.executable, "create_datasets_macular_centred_B.py"], main.REPO_ROOT / "M3_feature_zone" / "retipy"),
        ([main.sys.executable, "create_datasets_macular_centred_C.py"], main.REPO_ROOT / "M3_feature_zone" / "retipy"),
        ([main.sys.executable, "create_datasets_macular_centred.py"], main.REPO_ROOT / "M3_feature_whole_pic" / "retipy"),
        ([main.sys.executable, "create_datasets_disc_centred.py"], main.REPO_ROOT / "M3_feature_whole_pic" / "retipy"),
        ([main.sys.executable, "-m", "helpers.csv_merge"], main.REPO_ROOT),
    ]


def test_main_respects_skip_flags(monkeypatch) -> None:
    calls: list[tuple[list[str], Path]] = []

    def fake_run_command(command, *, cwd=main.REPO_ROOT, env_overrides=None):
        calls.append((command, cwd))

    monkeypatch.setattr(main, "run_command", fake_run_command)
    monkeypatch.setattr(main, "prepare_data_dirs", lambda: None)
    monkeypatch.setattr(main, "configure_logging", lambda: None)
    monkeypatch.setattr(main, "timestamp", lambda: "ts")
    monkeypatch.setattr(main.sys, "argv", ["main.py", "--no-process", "--no-feature"])

    assert main.main() == 0

    assert calls == [
        ([main.sys.executable, "run_inference.py", "--config", str(main.DEFAULT_CONFIG_PATH)], main.REPO_ROOT / "M1_Retinal_Image_quality_EyePACS"),
        ([main.sys.executable, "run_inference.py", "--config", str(main.DEFAULT_CONFIG_PATH)], main.REPO_ROOT / "M2_Vessel_seg"),
        ([main.sys.executable, "run_inference.py", "--config", str(main.DEFAULT_CONFIG_PATH)], main.REPO_ROOT / "M2_Artery_vein"),
        ([main.sys.executable, "run_inference.py", "--config", str(main.DEFAULT_CONFIG_PATH)], main.REPO_ROOT / "M2_lwnet_disc_cup"),
    ]


def test_prepare_data_dirs_uses_sample_images_when_images_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(main, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(main, "SAMPLE_IMAGES_DIR", tmp_path / "sample_images")
    monkeypatch.delenv("AUTOMORPH_DATA", raising=False)

    sample_images = tmp_path / "sample_images"
    sample_images.mkdir()
    (sample_images / "example.png").write_text("x", encoding="utf-8")

    main.prepare_data_dirs()

    assert (tmp_path / "images" / "example.png").exists()
    assert (tmp_path / "Results").exists()
