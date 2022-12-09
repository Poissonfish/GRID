import setuptools
setuptools.setup(name='photo_grid',
                 version='1.2.25',
                 description='A GUI for field segmentation',
                 url='https://github.com/Poissonfish/GRID',
                 python_requires='>=3.6',
                 classifiers=[
                        "Programming Language :: Python :: 3.6",
                        "Programming Language :: Python :: 3.7",
                        "Programming Language :: Python :: 3.8",
                        "Programming Language :: Python :: 3.9",
                        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                        "Operating System :: MacOS :: MacOS X",
                        "Operating System :: Microsoft :: Windows :: Windows 10"
                 ],
                 author='James Chen',
                 author_email='niche@vt.edu',
                 license='GPLv3',
                 packages=['grid', 'grid.gui'],
                 include_package_data=True,
                 install_requires=['numpy', 'pandas>=0.19.2',
                                   # data processing
                                   'h5py', 'pyshp',
                                   # math, models
                                   'sklearn', 'scipy', 'matplotlib',
                                   # image processing
                                   'image', 'opencv-python',
                                   'rasterio',
                                   # GUI
                                   'PyQt6',
                                   'qdarkstyle',
                                   # misc
                                   'tqdm'])
