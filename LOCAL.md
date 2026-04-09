## Running on local/virtual machine

### Requirements

1. Linux or macOS is recommended. On Windows, install [MinGW-w64](https://www.mingw-w64.org/) if you want to use the shell commands below.
2. Anaconda or Miniconda must be installed.
3. Python 3.11 and PyTorch 2.3.1 are installed through the steps below.
4. GPU acceleration is strongly recommended: Apple Silicon (MPS) is supported directly by `environment.yml`. CPU execution is supported but will be much slower.


### Package installation

Step 1: clone the repository:
```bash
git clone https://github.com/rmaphoh/AutoMorph.git
cd AutoMorph
```

Step 2: create the Conda environment from `environment.yml`:
```bash
conda env create -f environment.yml
conda activate automorphz
```

If you already have an `automorphz` environment, update it instead:
```bash
conda env update -n automorphz -f environment.yml --prune
conda activate automorphz
```

This installs all required Python packages directly from Conda using `environment.yml`.

### Running

Place your input images in the `images` folder, then run:
```bash
python main.py
```

Useful options:
```bash
python main.py --no-process
python main.py --no-quality
python main.py --no-segmentation
python main.py --no-feature
```

`resolution_information.csv` stores per-image pixel resolution. For custom data, prepare this file in the same format.
