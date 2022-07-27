Installation
============

Step 1: Python
----------------

GRID is developed in **Python 3**.
Follow the `official instruction <https://www.python.org/downloads/>`_
to set up Python.

Step 2: Rasterio (Windows Users)
---------------------------------
The easiest way to install Rasterio in Windows is to build it from binaries
`(Official instruction) <https://rasterio.readthedocs.io/en/latest/installation.html>`_.
Please download correct versions of ``.whl`` from
`Rasterio <https://www.lfd.uci.edu/~gohlke/pythonlibs/#rasterio>`_ and
`GDAL <https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal>`_, and use ``pip``` to install them.

For example, if you want to run GRID in **64-bit** Windows 10 using Python **3.9**,
the ``.whl`` names and the commands should be:

.. prompt:: bash

    python -m pip install GDAL-3.4.3-cp39-cp39-win_amd64.whl
    python -m pip install rasterio-1.2.10-cp39-cp39-win_amd64.whl

Step 2: Rasterio (Other Users)
---------------------------------
`Rasterio <https://rasterio.readthedocs.io/en/latest/index.html>`_ 
is the only GRID dependency that can't be installed via 
`PyPI <https://pip.pypa.io/en/stable/>`_.
Below are the alternatives:

* **Anaconda (Recommended)**
    Install Anaconda `here <https://www.anaconda.com/products/individual>`_, 
    and run the following commands in **Anaconda Prompt**: 

    .. prompt:: bash
        
        conda config --add channels conda-forge
        conda install rasterio 

* `Install from binaries <https://rasterio.readthedocs.io/en/latest/installation.html#installing-from-binaries>`_

* `Install from the source distribution <https://rasterio.readthedocs.io/en/latest/installation.html#installing-from-the-source-distribution>`_

Step 3: Install GRID via PyPI
--------------------------------

Finally, to install GRID, in the prompt 
(or Anaconda Prompts if you installed Rasterio via Anaconda):

.. prompt:: bash

    python -m pip install photo_grid

After finishing this step, you should be good to go.
Otherwise, check what dependencies you miss or report any issue to
the `GitHub repository <https://github.com/Poissonfish/GRID/issues>`_ .

.. NOTE::
    If your system can't find the command ``pip``,
    follow the `link <https://pip.pypa.io/en/stable/installing/>`_ 
    to install it.
