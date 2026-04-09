# automorphz

Forked from code for [AutoMorph: Automated Retinal Vascular Morphology Quantification via a Deep Learning Pipeline](https://tvst.arvojournals.org/article.aspx?articleid=2783477), repository [here](https://github.com/rmaphoh/AutoMorph).

## Pixel resolution

The units for vessel average width, disc/cup height and width, and calibre metrics are measured in microns. This repo generates `resolution_information.csv` at runtime from `config.yaml`; the file is not committed.

The active setting is:

```yaml
input:
  global_resolution: 0.0055
```

`main.py` writes `resolution_information.csv` automatically before preprocessing. Keep `generate_resolution.py` only for manual or mixed workflows where you want to regenerate the file outside the main pipeline.

If `resolution_information.csv` is missing:

* it is not an issue when you run `python main.py` with `input.global_resolution` set
* it is an issue if you run preprocessing directly or unset `input.global_resolution`, because `M0_Preprocess/EyeQ_process_main.py` reads that file explicitly

A committed template is available at [resolution_information.sample.csv](/Users/yifei/repos/automorphz/resolution_information.sample.csv).


## Running automorphz

### Requirements

1. Linux, macOS, and Windows can use the Python entrypoint below.
2. Anaconda or Miniconda must be installed.
3. Python 3.11 and PyTorch 2.3.1 are installed through the steps below.
4. GPU acceleration is strongly recommended. Apple Silicon (MPS) is supported directly by `environment.yml`. CPU execution is supported but will be much slower.

### Setup

Clone the repository:
```bash
git clone <your-repo-url>
cd automorphz
```

Create the Conda environment:
```bash
conda env create -f environment.yml
conda activate automorphz
```

If you already have an `automorphz` environment, update it instead:
```bash
conda env update -n automorphz -f environment.yml --prune
conda activate automorphz
```

`environment.yml` is the source of truth for local dependencies.
Runtime defaults for the pipeline and stage wrappers live in `config.yaml`. Command-line flags still override those defaults.
`pytest` is included for the small regression test suite in `tests/`.
`pymupdf` is installed via `pip` inside the Conda environment for the PDF extraction helper.

### Configuration

Use `config.yaml` to change the default runtime settings for the pipeline, including:

* input image folder
* global image resolution for `resolution_information.csv`
* image quality assessment defaults
* vessel segmentation defaults
* artery/vein segmentation defaults
* optic disc/cup segmentation defaults
* feature-measurement worker count

For example, you can change:

* `input.image_dir` to point the pipeline at a different input image folder
* `input.global_resolution` to apply one device-wide value to every image automatically
* default batch sizes
* the segmentation dataset names
* the optic disc/cup config file
* the default device for the optic disc/cup stage
* `feature_measurement.image_workers` to control per-image multiprocessing in the M3 stage

If you want a one-off override, pass a CLI flag instead of editing `config.yaml`. For example:
```bash
python main.py --no-feature
python M2_lwnet_disc_cup/run_inference.py --image-size 384
python M1_Retinal_Image_quality_EyePACS/run_inference.py --batch-size 32
```

If `input.global_resolution` is set, `main.py` writes `resolution_information.csv` automatically before preprocessing.
If `input.image_dir` is set, `main.py` uses that folder as the image source. Relative paths are resolved from the location of `config.yaml`.
If `feature_measurement.image_workers` is set, each M3 feature script processes images with a local worker pool.

### Run

Set the input folder in `config.yaml`, then run:
```yaml
input:
  image_dir: images
  global_resolution: 0.0055
```

Then run:
```bash
python main.py
```

To use the bundled sample data through the config file:
```yaml
input:
  image_dir: sample_images
  global_resolution: 0.0055
```

To force a run against `sample_images/` even when `images/` exists, use:
```bash
python main.py --use-sample-images
```

That runs in an isolated `.automorph_sample_run/` data directory so your normal `images/` and `Results/` are left alone.

Or use the shell wrapper, which activates `automorphz` and runs from the repo root:
```bash
bash run.sh
```

If your raw data is stored recursively under a nested folder, flatten it into the required flat image layout first:
```bash
python -m helpers.flatten_nested path/to/nested_folder
```

If your raw data is stored as one-PDF-per-eye exports, extract the primary fundus image from each PDF at native embedded raster size with:
```bash
python -m helpers.extract_pdf_fundus eye
```

That helper logs:

* how many PDFs were found
* how many embedded images each PDF contains
* which embedded image was selected
* native decoded size
* whether bright margins were trimmed
* where each PNG was written

Useful options:
```bash
python main.py --no-process
python main.py --no-quality
python main.py --no-segmentation
python main.py --no-feature
python main.py --config config.yaml
python main.py --use-sample-images
```

Run the regression tests:
```bash
pytest
```

## Common questions

### Invalid results

In CSV outputs, invalid values such as optic disc segmentation failures are reported as `NAN`.

### Resolution choice

If you use the native PDF extraction helper and assume the extracted image spans the full `50°` field, `0.0055 mm/pixel` is the current working value in `config.yaml`.

### Feature measurement speed

The M3 feature-measurement stage is CPU-bound and does not use the GPU. The repo now parallelizes work within each M3 script at the per-image level.

The active default is:

```yaml
feature_measurement:
  image_workers: 6
```

Reduce `image_workers` if your machine becomes oversubscribed. If M3 is still slow after that, the remaining bottleneck is inside the per-image retipy calculations rather than the top-level pipeline orchestration.


### Components

1. Vessel segmentation [BF-Net](https://github.com/rmaphoh/Learning-AVSegmentation.git)

2. Image preprocessing [EyeQ](https://github.com/HzFu/EyeQ.git)

3. Optic disc segmentation [lwnet](https://github.com/agaldran/lwnet.git)

4. Feature measurement [retipy](https://github.com/alevalv/retipy.git)

## Citation

```
@article{zhou2022automorph,
  title={AutoMorph: Automated Retinal Vascular Morphology Quantification Via a Deep Learning Pipeline},
  author={Zhou, Yukun and Wagner, Siegfried K and Chia, Mark A and Zhao, An and Xu, Moucheng and Struyven, Robbert and Alexander, Daniel C and Keane, Pearse A and others},
  journal={Translational vision science \& technology},
  volume={11},
  number={7},
  pages={12--12},
  year={2022},
  publisher={The Association for Research in Vision and Ophthalmology}
}
```
