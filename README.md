# AutoMorph 2022
Code for [AutoMorph: Automated Retinal Vascular Morphology Quantification via a Deep Learning Pipeline](https://tvst.arvojournals.org/article.aspx?articleid=2783477).

Please contact 	**ykzhoua@gmail.com** or **yukun.zhou.19@ucl.ac.uk** if you have questions.

Project website: https://rmaphoh.github.io/projects/automorph.html

Talks on NIHR Moorfields BRC: https://moorfieldsbrc.nihr.ac.uk/case-study/research-report/



## News
2025-05-16 update: Docker and its instructions were updated.

2024-06-27 update: PyTorch 2.3 and Python 3.11 are supported; Apple Silicon (M2) GPU support and CPU support were added (thanks to [staskh](https://github.com/staskh)).

2023-08-24 update: Added feature measurement for disc-centred images; removed unused files.
&nbsp;




## Pixel resolution

The units for vessel average width, disc/cup height and width, and calibre metrics are measured in microns. To compute them, prepare a [resolution_information.csv](https://github.com/rmaphoh/AutoMorph/blob/main/resolution_information.csv) file containing pixel resolution information. You can obtain this from FDA or DICOM files. If exact values are unavailable, you can use an approximate value such as `0.008` for Topcon 3D-OCT.

If you do not use these features or do not need micron-based units, put all images in `./images` and run:

```bash
python generate_resolution.py
```
&nbsp;


## Running AutoMorph
### Running with Colab

Use Google Colab with a free Tesla T4 GPU: [Colab notebook](https://colab.research.google.com/drive/13Qh9umwRM1OMRiNLyILbpq3k9h55FjNZ?usp=sharing).

A version prepared for the [APTOSxJSAIO 2025 hands-on tutorial](https://colab.research.google.com/drive/1ppzxBElLa_yJl-V3IWKyQQDG_2m6OWVL#scrollTo=vnEudwJimFgt) is also available.


### Running on local/virtual machine

Recommended local setup uses Conda:
```bash
conda env create -f environment.yml
conda activate automorphz
```

`environment.yml` is the source of truth for local dependencies. Full setup and run instructions are in [LOCAL.md](LOCAL.md).


### Running with Docker

If you prefer Docker, see [DOCKER.md](DOCKER.md).

&nbsp;

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

&nbsp;

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
