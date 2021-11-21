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


def calc_solar_declination(dayofyear: int) -> float:
    """
    Calculate the solar declination angle.

    Source
    ------
    Equation 11.2 in Campbell, G.S. and J.M. Norman (1998). An Introduction to
    Environmental Biophysics.

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


def calc_halfdaylength(solar_dec: float, lat_rad: float) -> float:
    """
    Calculation of 1/2 solar day length.

    Parameters
    ----------
    solar_dec : float
        Solar Declination in radians.
    lat_rad : float
        Latitude of site (field) in radians.

    Returns
    -------
    float
        1/2 day length.
    """
    temp3 = np.cos(90 * np.pi / 180) - np.sin(lat_rad) * np.sin(solar_dec)
    temp3 = temp3 / (np.cos(solar_dec) * np.cos(lat_rad))
    temp3 = (np.arccos(temp3) * 180 / np.pi) / 15
    return temp3


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
        # Step 1. Calculate corrections to solar noon value
        # (See Campbell and Norman (1998))

        # Calculate LC correction to solar noon (hours) needs
        # longitude correction for location of field site.
        LC = getLC(lon_rad)

        # Gets correction for ET.
        ET = getET(dayofyear)

        # Calculate solar noon value.
        solarnoon = 12 - LC - ET

        # Step 2. Calculate Solar Declination angle
        solarD = calc_solar_declination(dayofyear)

        # Step 4. calcualte length of solar day (including twilight time)
        # formula from Campbell and Norman, 1998 [Eq. 11.6] {1/2 daylight}
        halfdaylength = calc_halfdaylength(solarD, lat_rad)

        sunrise = solarnoon - halfdaylength
        sunset = solarnoon + halfdaylength

        # Approximatation of Sp.

        # tao is atmospheric transmission :
        # overcast = 0.4 --> from Liu and Jordan (1960)
        # clear = 0.70 --> as given in Gates (1980)
        tao = 0.70

        # If it is raining then assume it is overcast (cloud cover).
        if rain[i] == 1:
            tao = 0.40

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

        # Estimation of diffuse radiation

        # Liu, B.Y.H.; Jordan, R.C. The interrelationship and characteristic
        # distribution of direct, diffuse and total solar radiation.
        # Sol. Energy 1960, 4, 1–19.

        # Sd is in Watts m^-2

        Pa = 101 * np.exp(-1 * alt / 8200)
        m = Pa / 101.3 / np.cos(zenith_angle)
        Spo = 1360  # Solar constant in W/m2

        Sp = Spo * np.power(tao, m)
        Sp[(time < sunrise) | (time > sunset)] = 0

        # Beam irradiance on a horizontal surface.
        Sb = Sp * np.cos(zenith_angle)

        # Diffuse sky irradiance on horizontal plane (Sd)
        # Formula given in Campbell and Norman (1998)
        Sd = 0.3 * (1 - np.power(tao, m)) * np.cos(zenith_angle) * Spo
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

    return daily_solar_rad, tao_array


if __name__ == '__main__':
    pass
