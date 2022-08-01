<p align="center"><img src = "res/GRID_banner.png" width = 300></p>

[![](https://img.shields.io/pypi/pyversions/photo_grid.svg?logo=python&logoColor=white)](https://pypi.org/project/photo-grid/)
[![](https://img.shields.io/pypi/dm/photo_grid.svg?label=pypi%20downloads&logo=python&logoColor=white)](https://pypi.org/project/photo-grid/)
[![](https://img.shields.io/pypi/v/photo_grid.svg?label=pypi%20version&logo=python&logoColor=white)](https://pypi.org/project/photo-grid/)
[![](https://api.codacy.com/project/badge/Grade/626008b19df543ecb33a78e8f82f5e91)](https://app.codacy.com/manual/Poissonfish/photo_grid/dashboard)
[![](https://img.shields.io/github/license/poissonfish/photo_grid)](https://github.com/Poissonfish/GRID/blob/master/LICENSE)
[![](https://img.shields.io/github/languages/code-size/poissonfish/photo_grid)](https://github.com/Poissonfish/GRID/search?l=Python)

<img src = "res/abstract.png" width = 999>

### [Software Page (zzlab.net)](https://zzlab.net/GRID)

### [User Manual](https://poissonfish.github.io/GRID/index.html)

## Get Started
### Installation (Windows users)

The easiest way to install Rasterio in Windows is to build it from binaries. (see the [official instruction](https://rasterio.readthedocs.io/en/latest/installation.html) for further details)

Please download correct versions of `.whl` from
[Rasterio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#rasterio) and
[GDAL](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal), and use `pip` to install them.
For example, if you want to run GRID in **64-bit** Windows 10 using Python **3.9**,
the `.whl` names and the commands should be:

```bash
    python -m pip install GDAL-3.4.3-cp39-cp39-win_amd64.whl
    python -m pip install rasterio-1.2.10-cp39-cp39-win_amd64.whl
```

### Installation (Other users)

***Highly recommended install GRID in [Conda](https://poissonfish.github.io/GRID/installation.html) environment***

```python -m pip install photo_grid```

### Launch GRID
```python -m grid```