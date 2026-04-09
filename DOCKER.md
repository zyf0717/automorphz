## Running with Docker

First, create an `images` folder and place all input images inside it. Also prepare a `resolution_information.csv` file for those images. An example is included in the repository. More details are available [here](https://github.com/rmaphoh/AutoMorph?tab=readme-ov-file#pixel-resolution:~:text=removed%20unused%20files.-,Pixel%20resolution,-The%20units%20for).
```
├──images
    ├──1.jpg
    ├──2.jpg
    ├──3.jpg
├──resolution_information.csv
```

Then pull the [Docker image](https://hub.docker.com/repository/docker/yukunzhou/image_automorph/general):
```bash
docker pull yukunzhou/image_automorph:latest
```

Replace `{images_path}` with the path to your `images` folder, for example `/home/AutoMorph/images`. Replace `{results_path}` with the directory where you want to save the results, for example `/home/AutoMorph/Results`.

```bash
docker run --rm   --shm-size=2g   -v {images_path}:/app/AutoMorph/images   -v {results_path}:/app/AutoMorph/Results   -ti   --runtime=nvidia   -e NVIDIA_DRIVER_CAPABILITIES=compute,utility   -e NVIDIA_VISIBLE_DEVICES=all   yukunzhou/image_automorph
```
