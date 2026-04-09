from __future__ import annotations

from pathlib import Path

import main


def test_main_runs_stages_in_order(monkeypatch) -> None:
    calls: list[tuple[list[str], Path]] = []
    prepare_calls: list[bool] = []

    def fake_run_command(command, *, cwd=main.REPO_ROOT, env_overrides=None):
        calls.append((command, cwd))

    def fake_prepare_data_dirs(*, config_path=None, use_sample_images=False):
        assert config_path == main.DEFAULT_CONFIG_PATH
        prepare_calls.append(use_sample_images)

    monkeypatch.setattr(main, "run_command", fake_run_command)
    monkeypatch.setattr(main, "prepare_data_dirs", fake_prepare_data_dirs)
    monkeypatch.setattr(main, "configure_logging", lambda: None)
    monkeypatch.setattr(main, "timestamp", lambda: "ts")
    monkeypatch.setattr(main.sys, "argv", ["main.py"])

    assert main.main() == 0
    assert prepare_calls == [False]

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
    prepare_calls: list[bool] = []

    def fake_run_command(command, *, cwd=main.REPO_ROOT, env_overrides=None):
        calls.append((command, cwd))

    def fake_prepare_data_dirs(*, config_path=None, use_sample_images=False):
        assert config_path == main.DEFAULT_CONFIG_PATH
        prepare_calls.append(use_sample_images)

    monkeypatch.setattr(main, "run_command", fake_run_command)
    monkeypatch.setattr(main, "prepare_data_dirs", fake_prepare_data_dirs)
    monkeypatch.setattr(main, "configure_logging", lambda: None)
    monkeypatch.setattr(main, "timestamp", lambda: "ts")
    monkeypatch.setattr(main.sys, "argv", ["main.py", "--no-process", "--no-feature"])

    assert main.main() == 0
    assert prepare_calls == [False]

    assert calls == [
        ([main.sys.executable, "run_inference.py", "--config", str(main.DEFAULT_CONFIG_PATH)], main.REPO_ROOT / "M1_Retinal_Image_quality_EyePACS"),
        ([main.sys.executable, "run_inference.py", "--config", str(main.DEFAULT_CONFIG_PATH)], main.REPO_ROOT / "M2_Vessel_seg"),
        ([main.sys.executable, "run_inference.py", "--config", str(main.DEFAULT_CONFIG_PATH)], main.REPO_ROOT / "M2_Artery_vein"),
        ([main.sys.executable, "run_inference.py", "--config", str(main.DEFAULT_CONFIG_PATH)], main.REPO_ROOT / "M2_lwnet_disc_cup"),
    ]


def test_apply_global_resolution_writes_resolution_csv(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(main, "data_root", lambda: tmp_path)

    images_dir = tmp_path / "images"
    images_dir.mkdir()
    (images_dir / "example.png").write_text("x", encoding="utf-8")
    config_path = tmp_path / "config.yaml"
    config_path.write_text("input:\n  global_resolution: 0.00185\n", encoding="utf-8")

    main.apply_global_resolution(config_path)

    assert (tmp_path / "resolution_information.csv").read_text(encoding="utf-8") == (
        "fundus,res\nexample.png,0.00185\n"
    )


def test_main_can_force_sample_images(monkeypatch, tmp_path: Path) -> None:
    prepare_calls: list[bool] = []

    def fake_prepare_data_dirs(*, config_path=None, use_sample_images=False):
        assert config_path == main.DEFAULT_CONFIG_PATH
        prepare_calls.append(use_sample_images)

    monkeypatch.setattr(main, "prepare_data_dirs", fake_prepare_data_dirs)
    monkeypatch.setattr(main, "configure_logging", lambda: None)
    monkeypatch.setattr(main, "timestamp", lambda: "ts")
    monkeypatch.setattr(main, "run_preprocess", lambda: None)
    monkeypatch.setattr(main, "run_quality", lambda config_path: None)
    monkeypatch.setattr(main, "run_segmentation", lambda config_path: None)
    monkeypatch.setattr(main, "run_feature_measurement", lambda: None)
    monkeypatch.setattr(main.sys, "argv", ["main.py", "--use-sample-images"])

    assert main.main() == 0
    assert prepare_calls == [True]
