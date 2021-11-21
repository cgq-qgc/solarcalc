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
import datetime
import numpy as np
import pandas as pd

# To avoid "RuntimeWarning: overflow encountered in power" warnings when
# calculating tao**m, which become very large just outside of the
# sunrise and sunset times. This is not relevant here since Sd values
# before sunrise and after sunset are forced to 0 anyway.
np.seterr(over='ignore')


def getET(dayofyear: int) -> float:
    """
    Calculate the Equation of Time correction (typically a 15-20 minutes
    correction depending on calendar day).

    Source
    ------
    Equation 11.4 in Campbell, G.S. and J.M. Norman (1998). An Introduction to
    Environmental Biophysics.

    Parameters
    ----------
    dayofyear : int
        Day of year.

    Returns
    -------
    float
        Calculated Equation of Time value in hours.

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


def calc_solar_declination(dayofyear: int) -> float:
    """
    Calculate the solar declination angle.

    Source
    ------
    Equation 11.2 in Campbell, G.S. and J.M. Norman (1998). An Introduction to
    Environmental Biophysics.

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
        278.97 + 0.9856 * dayofyear +
        1.9165 * np.sin((356.6 + 0.9856 * dayofyear) * np.pi / 180)
        )
    temp2 = np.sin(temp2 * np.pi / 180)
    temp2 = np.arcsin(0.39785 * temp2)
    return temp2


def calc_zenith_angle(lat_rad: float, solar_dec: float, time: float,
                      solar_noon: float) -> float:
    """
    Zenith angle approximation.

    Source
    ------
    Equation 11.1 in Campbell, G.S. and J.M. Norman (1998). An Introduction to
    Environmental Biophysics.

    Parameters
    ----------
    lat_rad : float
        Latitude in radians.
    solar_dec : float
        Solar declination angle in radians.
    time : float
        Time of the day in hours.
    solar_noon : float
        Solar noon value in hours.

    Returns
    -------
    zenith_angle : float
        Zenith angle approximation in radians.
    """
    hour_angle = 15 * (time - solar_noon)
    zenith_angle = np.arccos(
        np.sin(lat_rad) * np.sin(solar_dec) +
        np.cos(lat_rad) * np.cos(solar_dec) *
        np.cos(hour_angle * np.pi / 180))
    return zenith_angle


def calc_halfdaylength(solar_dec: float, lat_rad: float,
                       twilight: bool = False) -> float:
    """
    Calculation of 1/2 solar day length.

    Source
    ------
    Equation 11.6 in Campbell, G.S. and J.M. Norman (1998). An Introduction to
    Environmental Biophysics.

    Parameters
    ----------
    solar_dec : float
        Solar Declination in radians.
    lat_rad : float
        Latitude of site (field) in radians.
    twilight : bool
        Whether to include twilight in the half day lenght calculation.

    Returns
    -------
    float
        1/2 day length in hours.
    """
    psi = 96 if twilight else 90
    A = np.cos(psi * np.pi / 180) - np.sin(lat_rad) * np.sin(solar_dec)
    B = np.cos(lat_rad) * np.cos(solar_dec)
    return np.arccos(A/B) * (180 / np.pi) / 15


def calc_solar_rad(lon_dd: float, lat_dd: float, alt: float,
                   climate_data: pd.DataFrame):
    """
    Predicts net radiation from only average temperature extremes
    and daily precipitation records.

    Parameters
    ----------
    dayofyears : TYPE
        DESCRIPTION.
    lon_dd : float
        Site longitude in degree decimal.
    lat_dd : float
        Site latitude in degree decimal.
    alt : float
        Altitude of the site in m.

    Returns
    -------
    None.

    """
    # Convert rain[day of year] = 1 if rain and rain = 0 if no rain.
    rain = (climate_data['ptot'] > 1).values.astype(int)
    deltaT = np.round((climate_data['tamax'] - climate_data['tamin']).values)

    daily_solar_rad = []
    tao_array = []

    # Convert lat and long to radian numbers.
    lat_rad = np.radians(lat_dd)
    lon_rad = np.radians(lon_dd)

    for i, dayofyear in enumerate(climate_data.index.dayofyear):
        # Calculate LC correction to solar noon.
        LC = getLC(lon_rad)

        # Gets correction for Equation of Time.
        ET = getET(dayofyear)

        # Calculate solar noon value.
        solarnoon = 12 - LC - ET

        # Calculate the solar declination angle
        solarD = calc_solar_declination(dayofyear)

        # Calculate the length of solar day (excluding twilight time).
        halfdaylength = calc_halfdaylength(solarD, lat_rad)

        sunrise = solarnoon - halfdaylength
        sunset = solarnoon + halfdaylength

        # Estimate the atmospheric transmittance (tao).
        tao = 0.70  # Clear sky value as  given in Gates (1980)

        # If it is raining then assume it is overcast (cloud cover).
        if rain[i] == 1:
            tao = 0.40  # from Liu and Jordan (1960)

        # If it has been raining for two days then even
        # darker (denser cloud cover).
        if rain[i] == 1 and rain[i - 1] == 1:
            # Note that we cannot asses this condition for the first day
            # of the climate serie.
            tao = 0.30

        # Assign pre-rain days to 80% of tao value ?
        if rain[i] == 0 and rain[i - 1] == 1:
            # Note that we cannot assess this condition for the last day of
            # the climate data series.
            tao = 0.60

        # If airtemperature rise is less than 10 --> lower tao value
        # unless by poles
        if np.abs(lat_dd) < 60:
            if deltaT[i] <= 10 and deltaT[i] != 0:
                tao = tao / (11 - deltaT[i])

        # Estimating direct and diffuse short wave radiation for each hour.
        time = np.arange(24)

        # Calculate the Zenith Angle.
        zenith_angle = calc_zenith_angle(lat_rad, solarD, time, solarnoon)

        # Calculate the atmospheric pressure at the observation site using
        # Equation 3.7 in Campbell and Norman (1998).
        Pa = 101 * np.exp(-1 * alt / 8200)  # TODO: correct 101 for 101.3.

        # Calculate the optical air mass number using Equation 11.12 in
        # Campbell and Norman (1998).
        m = Pa / 101.3 / np.cos(zenith_angle)

        Spo = 1360  # Solar constant in W/m2

        # Calculate the hourly beam irradiance on a horizontal surface (Sb)
        # using Equations 11.8 and 11.11 in Campbell and Norman (1998).
        Sb = Spo * np.power(tao, m) * np.cos(zenith_angle)
        Sb[(time < sunrise) | (time > sunset)] = 0

        # Calculate the diffuse sky irradiance on horizontal plane (Sd)
        # using Equation 11.13 in Campbell and Norman (1998).
        Sd = 0.3 * (1 - np.power(tao, m)) * Spo * np.cos(zenith_angle)
        Sd[(time < sunrise) | (time > sunset)] = 0

        # The global solar radiation on a horizontal surface is the sum of the
        # horizontal direct beam (Sb) and diffuse radiation (Sd).
        St = Sb + Sd

        # Check for never daylight northern latitudes.
        St[St < 0] = 0

        # Fill NaN values with zeros.
        St[pd.isnull(St)] = 0

        daily_solar_rad.extend(np.round(St, 2))
        tao_array.extend(np.ones(24) * tao)
        deltat_array.extend(np.ones(24) * deltaT[i])

    return daily_solar_rad, tao_array, deltat_array


if __name__ == '__main__':
    pass
