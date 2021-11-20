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


def getLC(long2: float):
    """
    Calculate the longitudal correction.

    Parameters
    ----------
    long2 : float
        longitude of fieldsite in radians. Negative value if West of meridian
        and positive value if East of meridian.

    Returns
    -------
    TYPE
        DESCRIPTION.
    """
    # We assume longitude is in decimal format.
    # Translates to 4 minutes for each degree
    return long2 / 360 * 24


def solarDeclination(dayofyear1: int) -> float:
    """
    Calculate the solar declination angle.

    Formula from Campbell and Norman, 1998 [Eq. 11.2].
    Corrected for day of year (Jan. 1 = 1, etc.)

    Parameters
    ----------
    dayofyear : int
        Day of year.

    Returns
    -------
    temp2 : float
        Solar declination angle in radians.

    """
    temp2 = (
        278.97 + 0.9856 * dayofyear1 +
        1.9165 * np.sin((356.6 + 0.9856 * dayofyear1) * np.pi / 180)
        )
    temp2 = np.sin(temp2 * np.pi / 180)
    temp2 = np.arcsin(0.39785 * temp2)
    return temp2


def Zenith(lat: float, sD: float, te: float, sn: float) -> float:
    """
    Zenith angle approximation.

    Parameters
    ----------
    lat : float
        Latitude in radians.
    sD : float
        Solar declination angle in radians.
    te : float
        DESCRIPTION.
    sn : float
        Solar noon value.

    Returns
    -------
    float
        Zenith angle approximation at time te.
    """
    temp = (
        np.sin(lat) * np.sin(sD) +
        np.cos(lat) * np.cos(sD) * np.cos(15 * (te - sn) * np.pi / 180))
    return np.arccos(temp)


def CalcHalfDayLength(solarD2: float, latitude2: float) -> float:
    """
    Calculation of 1/2 solar day length.

    Parameters
    ----------
    solarD2 : float
        Solar Declination in radians.
    latitude2 : float
        Latitude of site (field) in radians.

    Returns
    -------
    float
        1/2 day length.
    """
    temp3 = np.cos(90 * np.pi / 180) - np.sin(latitude2) * np.sin(solarD2)
    temp3 = temp3 / (np.cos(solarD2) * np.cos(latitude2))
    temp3 = (np.arccos(temp3) * 180 / np.pi) / 15
    return temp3


def stefan_boltzman(airtemp: float):
    """
    Return black body radiation in Watts/m2  emitted from body.

    Parameters
    ----------
    airtemp : float
        airtemp or temperature of body.

    Returns
    -------
    float
        Emitted radiation (W/m2).
    """
    return 5.67E-08 * np.power(airtemp + 273.16, 4)


