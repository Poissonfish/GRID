Installation
============

Step 1: Python
----------------

GRID is developed in **Python 3**. 
Follow the `official instruction <https://www.python.org/downloads/>`_
to set up Python.

Step 2: Rasterio
------------------

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

    python3 -m pip install photo_grid

After finishing this step, you should be good to go.
Otherwise, check what dependencies you miss or report any issue to
the `GitHub repository <https://github.com/Poissonfish/GRID/issues>`_ .

.. NOTE::
    If your system can't find the command ``pip``,
    follow the `link <https://pip.pypa.io/en/stable/installing/>`_ 
    to install it.
