## Running on local/virtual machine

### Requirements

1. Linux or Mac are preferred. For windows, install [MinGW-w64](https://www.mingw-w64.org/) for using commands below to set enviroment.
2. Anaconda or miniconda installed.
3. Python 3.11 and PyTorch 2.3.1 (installation steps below)
4. GPU acceleration is strongly recommended: Apple Silicon (MPS) is supported directly by `environment.yml`. CPU execution is supported but will be much slower.


### Package installation

Step 1: clone the code:
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

Put the images in folder 'images' and
```bash
python main.py
```

Please note that resolution_information.csv includes the resolution for image, i.e., size for each pixel. Please prepare it for the customised data in the same format.
