# automorphz

Forked from code for [AutoMorph: Automated Retinal Vascular Morphology Quantification via a Deep Learning Pipeline](https://tvst.arvojournals.org/article.aspx?articleid=2783477), repository [here](https://github.com/rmaphoh/AutoMorph).

## Pixel resolution

The units for vessel average width, disc/cup height and width, and calibre metrics are measured in microns. To compute them, prepare a [resolution_information.csv](https://github.com/rmaphoh/AutoMorph/blob/main/resolution_information.csv) file containing pixel resolution information. You can obtain this from FDA or DICOM files. If exact values are unavailable, you can use an approximate value such as `0.008` for Topcon 3D-OCT.

If you do not use these features or do not need micron-based units, put all images in `./images` and run:

```bash
python generate_resolution.py
```
&nbsp;


## Running automorphz

### Requirements

1. Linux, macOS, and Windows can use the Python entrypoint below. MinGW is not required for the documented workflow.
2. Anaconda or Miniconda must be installed.
3. Python 3.11 and PyTorch 2.3.1 are installed through the steps below.
4. GPU acceleration is strongly recommended. Apple Silicon (MPS) is supported directly by `environment.yml`. CPU execution is supported but will be much slower.

### Setup

Clone the repository:
```bash
git clone https://github.com/rmaphoh/AutoMorph.git
cd AutoMorph
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

### Configuration

Use `config.yaml` to change the default runtime settings for the pipeline, including:

* image quality assessment defaults
* vessel segmentation defaults
* artery/vein segmentation defaults
* optic disc/cup segmentation defaults

For example, you can change:

* default batch sizes
* the segmentation dataset names
* the optic disc/cup config file
* the default device for the optic disc/cup stage

If you want a one-off override, pass a CLI flag instead of editing `config.yaml`. For example:
```bash
python main.py --no-feature
python M2_lwnet_disc_cup/run_inference.py --image-size 384
python M1_Retinal_Image_quality_EyePACS/run_inference.py --batch-size 32
```

### Run

Place your input images in the `images` folder, then run:
```bash
python main.py
```

If `images/` does not exist, the pipeline falls back to `sample_images/`.

Or use the shell wrapper, which activates `automorphz` and runs from the repo root:
```bash
bash run.sh
```

Useful options:
```bash
python main.py --no-process
python main.py --no-quality
python main.py --no-segmentation
python main.py --no-feature
python main.py --config config.yaml
```

Run the regression tests:
```bash
pytest
```

## Common questions

### Memory/ram error

We use a Tesla T4 (16 GB) and 32 vCPUs (120 GB RAM). If you run into memory issues, reduce batch size or image size:

* `python M1_Retinal_Image_quality_EyePACS/run_inference.py --batch-size 32`
* `python M2_Artery_vein/run_inference.py --batch-size 4`
* `python M2_lwnet_disc_cup/run_inference.py --image-size 384`


### Invalid results

In CSV outputs, invalid values such as optic disc segmentation failures are reported as `NAN`.


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
