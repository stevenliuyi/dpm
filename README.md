This repository contains scripts for downloading images from the Palace Museum. It supports both [*Minghuaji*](https://minghuaji.dpm.org.cn/) (故宫名画记) and [the collections on the official website](https://www.dpm.org.cn/explore/collections.html) .

## Usage

### Prerequisites
[dezoomify-rs](https://github.com/lovasoa/dezoomify-rs) is required to download tiled high resolution images used in *Minghuaji*. To use dezoomify-rs in the scripts, the environment variable ``DEZOOMIFY_RS`` needs to be set as the executable file for dezoomify-rs. For example:

```
export DEZOOMIFY_RS=$HOME/dezoomify-rs/dezoomify-rs
```

The run `pip install -r requirements.txt` to ensure that you have the required Python dependencies.

### Preparation
To download a list of images, you must first create a CSV file named `paintings.csv` (skip this step if you only need to download images individually). The file should contain IDs of all images you'd like to download. For instance:

```
id,title
2c558301d5ff4dbf8e19ad07ed36adfe,磨镜图页
5f6895a548884d4e889ed9b791bc3bd7,周官观灯倡咏图卷
...
```
All columns except `id` are optional.

You may also use the provided script to generate a list of all images on the specified website, which can generate `paintings.csv` automatically:

```
python fetch_paintings.py [website]
```

The parameter `website` should be one of `mhj` (for *Minghuaji*) and `collection` (for the official website).

### Download
To download all images based on the data provided in `paintings.csv`:

```
python download_images.py [website]
```

To download a single image with a specific id (no need to generate `paintings.csv` in this case):

```
python -c "from download_images import *; download_image([website], [paint_id])"
```

For instance, the following command downloads image from https://minghuaji.dpm.org.cn/paint/detail?id=0196af7228c14f098185c9bdbd19b6e7.

```
python -c "from download_images import *; download_image('mhj', '0196af7228c14f098185c9bdbd19b6e7')"
```
