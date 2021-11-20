# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © INRS
# https://github.com/cgq-qgc/rsesq-bulletin

# This code is licensed under the terms of the MIT License as published
# by the Open Source Initiative. For more details, see the MIT license at
# https://opensource.org/licenses/MIT.

# This file is a derivative work of codes taken from the SolarCalc 1.0 program,
# licensed under the terms of the Creative Commons CCZero License as published
# by the Creative Commons nonprofit organization. For more details, see the
# CC0 1.0 License at https://creativecommons.org/publicdomain/zero/1.0/.

# Source:
# USDA Agricultural Research Service. (2019). SolarCalc 1.0. United States
# Department of Agriculture. https://data.nal.usda.gov/dataset/solarcalc-10.
# Accessed 2021-11-19.
# -----------------------------------------------------------------------------

from __future__ import annotations
import numpy as np
import pandas as pd


def getET(dayofyear: int) -> float:
    """
    Calculate the ET (equation of time) correction typically a 15-20 minute
    correction depending on calendar day.

    Parameters
    ----------
    dayofyear : int
        Day of year.

    Returns
    -------
    float
        Calculated ET value.

    """
    ETcalc = (279.575 + 0.9856 * dayofyear) * np.pi / 180

    return (
        -104.7 * np.sin(ETcalc) + 596.2 * np.sin(ETcalc * 2) +
        4.3 * np.sin(3 * ETcalc) + -12.7 * np.sin(4 * ETcalc) +
        -429.3 * np.cos(ETcalc) + -2.0 * np.cos(2 * ETcalc) +
        19.3 * np.cos(3 * ETcalc)
        ) / 3600

