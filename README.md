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
### Installation
***Highly recommended install GRID in [Conda](https://poissonfish.github.io/GRID/installation.html) environment***

```pip install photo_grid```
### Launch GRID
```python -m grid```

## Update Log

### Aug 25, 2021 (1.2.16)
    * Handle large images (pixel dimension > 32767)

### Sep 28, 2020 (1.2.13)
    * Impore handling of floating-encoded images

### Aug 27, 2020 (1.1.99)
    * Bug fixes of showing tabular information

### Jul 27, 2020 (1.1.96)
    * Fix the shapefile with imprecise coordinates
    * Add Coordinate reference system (CRS) to the shapefile (.prj)

### Jul 6, 2020 (1.1.9)
    * Fix crash when add/delete anchors

### Jul 1, 2020 (1.1.7)
    * Add a output image "Seg_ID.png" to show plot's ID
    * Improve the stability and flexibility in the step to segmentation
    * Bug fixes in the searching centroids step

### Jun 17, 2020 (1.1)
    * The shapefile can be used for the same field taken from different season

### Jun 10, 2020 (1.0.2)
    * The shapefile can match the coordinate system in GeoTiff now
   
### May 29, 2020 (1.0.1)
    * Minor bug fixes (visualization of layout detection)

### Apr 28, 2020 (0.3.5)
    * Support exporting ESRI shapefile

### Apr 23, 2020 (0.3.41)
    * Support drag and drop for file loading
    * Support manual adjustment for centroids

### Apr 16, 2020 (0.3.4)
    * New interface for angle detection
  
### Feb 20, 2020 (0.3.0)
    * Support different display modes in the center detection step
    * Support auto-update feature
    * Bug fixes

### Dec 19, 2019 (0.2.46)
    * Add plot variation in the output file
    * Support saving segmentated images as H5 file
    * Now it's possible to display RGB in the plot searching panel.
    * Other minor bug fixes

### Dec 9, 2019 (0.2.45)
    * Bug fixes for image rotating issue
    * Support map with duplicated names

### Oct 29, 2019 (0.2.0)
    * Add progress bars
    * Enhance the support for low resolution monitors
    * Improve UI
  
### Oct 22, 2019 (0.1.3)
    * Optimize default setting of refining parameters
    * Fix wrong angle detection
    * Minor bug fixes

### Oct 19, 2019 (0.1.2)
    * Support rhombus field layout
    * Bug fixes

### Sep 17, 2019 (0.0.16)
    * Improve memory efficiency on Windows OS

### Sep 12, 2019 (0.0.15)
    * Fix problems wiht fixed segmentation
    * Organize file structure
    * Add dark mode
