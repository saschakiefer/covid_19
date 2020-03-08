# Tracking Coronavirus COVID-19

Inspired by a Ferry Djaja's [blog post on the SAP Community](https://blogs.sap.com/2020/03/05/tracking-coronavirus-covid-19-near-real-time-with-sap-hana-xsa/) I created a Python based solution.

The script uses the same data bases from the [Johns Hokins CSSE](https://github.com/CSSEGISandData/COVID-19). My visualization is based on the time series data.

> Lesson learned: I first started with the daily reports and was already finished with the web scraper. Then I realized, that the first records don't have geo data in :-(
> Mental Note: Check your data first, then start coding

Since I have only little knowledge about visualization with Python (i.e. Python at all), this article was very helpful: [Creating Map Animations with Python - Udacity Inc - Medium](https://medium.com/udacity/creating-map-animations-with-python-97e24040f17b)

## Installation

### Prerequisites

The description assumes, that `pipenv`, `geos`, `proj` and `ffmpeg` are installed on your machine. If that is not the case, go ahead and install these with

```bash
pip install pipenv
brew install geos
brew install proj
brew install ffmpeg
```

### Basics

To get the basics done, execute the following on you terminal in a directory of choice:

```bash
git clone https://github.com/saschakiefer/covid_19.git
cd covid_19
pipenv shell                     # create virtual environment
pipenv install --ignore-pipfile  # install the dependencies
```

### Cartopy

The visualization is done with [Cartopy](https://scitools.org.uk/cartopy/docs/latest/index.html). Unfortunately I was not able to install it with `virtualenv`. I only found a Conda installation. So we have to install it from the source:

```bash
git clone https://github.com/SciTools/cartopy.git
cd cartopy
python setup.py install
cd ..
```

There seems to be a weird [bug](https://stackoverflow.com/questions/60111684/geometry-must-be-a-point-or-linestring-error-using-cartopy) in Cartopy. This always caused an _'Geometry must be a Point or LineString'_-error. To fix that you have to do some manual work

First you have to find your `site-packages`-folder of `virtualenv`. Usually that is found in `/.local/share/virtualenvs/<virtual environment name>/lib/python<X.X>/site-packages`. There you have to locate the two `shapely`-folders. Delete both of them.

Then reinstall shapely from the source without the binaries:

```bash
export PIP_NO_BINARY=:all: && pipenv install shapely
```

### Little change in coding

In the file `CreateFrames.py` you have to locate the following line:

```python
os.environ['CARTOPY_USER_BACKGROUNDS'] = '/Users/sascha/git/covid_19/background'
```

Change the path to the `background`-folder, that comes with this git repository. Unfortunately relative paths seem not to work, so that needs to be set locally on your machine. This points to the background image, that I downloaded from [NASA Visible Earth - Home](https://visibleearth.nasa.gov/collection/1484/blue-marble).

## Create the Frames

The idea is based on single frames being rendered and then put together to a video. To generate the frames run

```shell
python CreateFrames.py
```

The frames are stored in the `./frames/`subfolders. I suggest to leave them there. The script checks for existing frames for a certain date and skips the generation for existing ones. This saves quite some rendering time. So you can easily keep track of the spread.

## Create the videos

```bash
./CreateVideos.sh
```

This script simply executes ffmpeg to create the videos. You can find the videos in the `videos`folder.
