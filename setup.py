# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © INRS
# https://github.com/cgq-qgc/solarcalc
#
# This code is licensed under the terms of the MIT License as published
# by the Open Source Initiative. For more details, see the MIT license at
# https://opensource.org/licenses/MIT/.
# -----------------------------------------------------------------------------

"""Installation script """

import setuptools
from setuptools import setup
from solarcalc import __version__, __project_url__

LONG_DESCRIPTION = (
    "The SolarcCalc module is used to predict hourly global solar "
    "radiation on a horizontal surface from daily average temperature "
    "extremes and total precipitation records. "
    "The method used in the calculations is based on that presented in "
    "[An Introduction to Environmental Biophysics]"
    "(https://link.springer.com/book/10.1007/978-1-4612-1626-1) "
    "by Campbell, G.S. and J.M. Norman (1998)."
    "<br><br>"
    "Version 1.0 of the SolarcCalc module is based on the source code of "
    "SolarCalc.jar (version 1.1, Jan. 2006), a computer program  that was "
    "developped by the USDA Agricultural Research Service and that is "
    "available free of charge at "
    "[https://data.nal.usda.gov/dataset/solarcalc-10]"
    "(https://data.nal.usda.gov/dataset/solarcalc-10)."
    "<br><br>"
    "Subsequent versions of the SolarcCalc module implemented performance "
    "improvements and fixed some issues with the original code and method."
    )

INSTALL_REQUIRES = ['numpy, pandas']

setup(name='solarcalc',
      version=__version__,
      description=("Hourly global solar radiation estimator."),
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      license='MIT',
      author='Jean-Sébastien Gosselin',
      author_email='jean-sebastien.gosselin@outlook.ca',
      url=__project_url__,
      ext_modules=[],
      packages=setuptools.find_packages(),
      package_data={},
      include_package_data=True,
      install_requires=INSTALL_REQUIRES,
      classifiers=["Programming Language :: Python :: 3",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Intended Audience :: Science/Research",
                   "Intended Audience :: Education",
                   "Topic :: Scientific/Engineering"
                   ],
      )
