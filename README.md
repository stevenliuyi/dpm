This repository contains scripts for downloading images from the Palace Museum. It supports both [*Minghuaji*](https://minghuaji.dpm.org.cn/) (故宫名画记) and [the collections on the official website](https://www.dpm.org.cn/explore/collections.html) .

## Usage

[dezoomify-rs](https://github.com/lovasoa/dezoomify-rs) is required to download tiled high resolution images used in *Minghuaji*. To use dezoomify-rs in the scripts, the environment variable ``DEZOOMIFY_RS`` needs to be set as the executable file for dezoomify-rs. For example:

```
export DEZOOMIFY_RS=$HOME/dezoomify-rs/dezoomify-rs
```

To generate a list of all images on the website and save it as `paintings.csv`:

```
python fetch_paintings.py [website]
```

The parameter `website` should be one of `mhj` (for *Minghuaji*) and `collection` (for the official website).

To download all images based on the data in `paintings.csv`:

```
python download_images.py [website]
```

To download a single image with a specific id:

```
python -c "from download_images import *; download_image([website], [paint_id])"
```

For instance, the following command downloads image from https://minghuaji.dpm.org.cn/paint/detail?id=0196af7228c14f098185c9bdbd19b6e7. In this case, there is no need to generate `paintings.csv` using `fetch_paintings.csv`.

```
python -c "from download_images import *; download_image('mhj', '0196af7228c14f098185c9bdbd19b6e7')"
```
