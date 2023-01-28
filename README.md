This repository contains scripts for downloading images from the *Minghuaji* project of the Palace Museum (故宫名画记).

## Usage

[dezoomify-rs](https://github.com/lovasoa/dezoomify-rs) is required to download tiled high resolution images used in *Minghuaji*. To use dezoomify-rs in the scripts, the environment variable ``DEZOOMIFY_RS`` needs to be set as the executable file for dezoomify-rs. For example:

```
export DEZOOMIFY_RS=$HOME/dezoomify-rs/dezoomify-rs
```

To generate a list of all images and save it as `paintings.csv`:

```
python fetch_paintings.py
```

To download all images based on the data in `paintings.csv`:

```
python download_images.py
```

To download a single image with a specific id:

```
python -c "from download_images import *; download_image('0196af7228c14f098185c9bdbd19b6e7')"
```

The above command downloads image from https://minghuaji.dpm.org.cn/paint/detail?id=0196af7228c14f098185c9bdbd19b6e7. In this case, there is no need to generate `paintings.csv`.