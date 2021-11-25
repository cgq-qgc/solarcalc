# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © INRS
# https://github.com/cgq-qgc/solarcalc
#
# This code is licensed under the terms of the MIT License as published
# by the Open Source Initiative. For more details, see the MIT license at
# https://opensource.org/licenses/MIT/.
#
# This file is a derivative work of codes taken from the SolarCalc 1.0 program,
# licensed under the terms of the Creative Commons CCZero License as published
# by the Creative Commons nonprofit organization. For more details, see the
# CC0 1.0 License at https://creativecommons.org/publicdomain/zero/1.0/.
#
# Source:
# USDA Agricultural Research Service (2019). SolarCalc 1.0. United States
# Department of Agriculture. https://data.nal.usda.gov/dataset/solarcalc-10/.
# Accessed 2021-11-19.
# -----------------------------------------------------------------------------

"""
Global Solar Radiation Estimator

Predicts hourly global solar radiation on a horizontal surface from
daily average temperature extremes and total precipitation records.
"""

from __future__ import annotations
import os.path as osp
import numpy as np
import pandas as pd

__version__ = "1.0"
__project_url__ = "https://github.com/cgq-qgc/solarcalc"

# To avoid "RuntimeWarning: overflow encountered in power" warnings when
# calculating tau**m, which become very large just outside of the
# sunrise and sunset times. This is not relevant here since Sd values
# before sunrise and after sunset are forced to 0 anyway.
np.seterr(over='ignore')


def load_demo_climatedata() -> pd.DataFrame:
    """
    Return a pandas dataframe containing climate data to run
    a demo of solarcalc.
    """
    return pd.read_csv(
        osp.join(osp.dirname(__file__), 'demo_climatedata.csv'),
        parse_dates=['datetime'],
        index_col='datetime',
        dtype={'tamin_degC': 'float',
               'tamax_degC': 'float',
               'ptot_mm': 'float'}
        )


def calc_eqn_of_time(dayofyear: int) -> float:
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
    f = (279.575 + 0.98565 * dayofyear) * np.pi / 180

    return (
        -104.7 * np.sin(f) +
        596.2 * np.sin(2 * f) +
        4.3 * np.sin(3 * f) +
        -12.7 * np.sin(4 * f) +
        -429.3 * np.cos(f) +
        -2.0 * np.cos(2 * f) +
        19.3 * np.cos(3 * f)
        ) / 3600


def calc_long_corr(lon_dd: float) -> float:
    """
    Calculate the longitudinal correction.

    Parameters
    ----------
    lon_dd : float
        Longitude of fieldsite in decimal degrees. Negative value if West
        of meridian and positive value if East of meridian.

    Returns
    -------
    float
        Longitudinal correction in hours.
    """
    # Calculate the local standard time meridian.
    lstm = lon_dd - lon_dd % (np.sign(lon_dd) * 15)

    # Calculate the longitudinal correction in hours.
    long_corr = (lon_dd - lstm) * (24 / 360)

    return long_corr


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
    hour_angle = 15 * (solar_noon - time) * np.pi / 180
    zenith_angle = np.arccos(
        np.sin(lat_rad) * np.sin(solar_dec) +
        np.cos(lat_rad) * np.cos(solar_dec) * np.cos(hour_angle)
        )
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
                   climate_data: pd.DataFrame) -> pd.DataFrame:
    """
    Predict hourly global solar radiation on a horizontal surface.

    Parameters
    ----------
    lon_dd : float
        Site longitude in degree decimal.
    lat_dd : float
        Site latitude in degree decimal.
    alt : float
        Altitude of the site in m.
    climate_data : pd.DataFrame
        A pandas dataframe containing the consecutive (no missing value) daily
        meterological data that are required for the calculatations in the
        following columns :
            * tamax_degC : daily maximum temperature in Celcius.
            * tamin_degC : daily minimum temperature in Celcius.
            * ptot_mm : daily total precipitations in mm.
        The index of the dataframe must contain the date for each daily
        reading in a pandas DatetimeIndex.

    Returns
    -------
    A pandas dataframe that contain the hourly values estimated by the model
    in the following columns:
        * solar_rad_W/m2 : hourly global solar radiation on a horizontal
          surface in W/m2.
        * deltat_degC : daily temperature total variation.
        * tau : atmospheric transmittance.
    The index of the dataframe contains the date and time for each hourly
    reading in a pandas DatetimeIndex.
    """
    # Convert rain[day of year] = 1 if rain and rain = 0 if no rain.
    rain = (climate_data['ptot_mm'] > 1).values.astype(int)
    deltaT = (climate_data['tamax_degC'] -
              climate_data['tamin_degC']).abs().values

    daily_solar_rad = []
    tao_array = []
    deltat_array = []

    # Convert lat and long to radian numbers.
    lat_rad = np.radians(lat_dd)
    lon_rad = np.radians(lon_dd)

    for i, dayofyear in enumerate(climate_data.index.dayofyear):
        # Calculate the longitudinal correction to solar noon.
        LC = calc_long_corr(lon_dd)

        # Gets correction for Equation of Time.
        ET = calc_eqn_of_time(dayofyear)

        # Calculate solar noon value.
        solarnoon = 12 - LC - ET

        # Calculate the solar declination angle
        solarD = calc_solar_declination(dayofyear)

        # Calculate the length of solar day (excluding twilight time).
        halfdaylength = calc_halfdaylength(solarD, lat_rad)

        sunrise = solarnoon - halfdaylength
        sunset = solarnoon + halfdaylength

        # Estimate the atmospheric transmittance (tau).
        tau = 0.70  # Clear sky value as  given in Gates (1980)

        # If it is raining then assume it is overcast (cloud cover).
        if rain[i] == 1:
            tau = 0.40  # from Liu and Jordan (1960)

        # If it has been raining for two days then even
        # darker (denser cloud cover).
        if i > 0 and rain[i] == 1 and rain[i - 1] == 1:
            tau = 0.30

        # Assign pre-rain days to 80% of tau value ?
        if i < (len(climate_data) - 1) and rain[i] == 0 and rain[i + 1] == 1:
            tau = 0.60

        # If airtemperature rise is less than 10 --> lower tau value
        # unless by poles
        if np.abs(lat_dd) < 60:
            if deltaT[i] <= 10 and deltaT[i] != 0:
                tau = tau / (11 - deltaT[i])

        # Estimating direct and diffuse short wave radiation for each hour.
        time = np.arange(24)

        # Calculate the Zenith Angle.
        zenith_angle = calc_zenith_angle(lat_rad, solarD, time, solarnoon)

        # Calculate the atmospheric pressure at the observation site using
        # Equation 3.7 in Campbell and Norman (1998).
        Pa = 101.3 * np.exp(-1 * alt / 8200)

        # Calculate the optical air mass number using Equation 11.12 in
        # Campbell and Norman (1998).
        m = Pa / 101.3 / np.cos(zenith_angle)

        Spo = 1360  # Solar constant in W/m2

        # Calculate the hourly beam irradiance on a horizontal surface (Sb)
        # using Equations 11.8 and 11.11 in Campbell and Norman (1998).
        Sb = Spo * np.power(tau, m) * np.cos(zenith_angle)
        Sb[(time < sunrise) | (time > sunset)] = 0

        # Calculate the diffuse sky irradiance on horizontal plane (Sd)
        # using Equation 11.13 in Campbell and Norman (1998).
        Sd = 0.3 * (1 - np.power(tau, m)) * Spo * np.cos(zenith_angle)
        Sd[(time < sunrise) | (time > sunset)] = 0

        # The global solar radiation on a horizontal surface is the sum of the
        # horizontal direct beam (Sb) and diffuse radiation (Sd).
        St = Sb + Sd

        # Check for never daylight northern latitudes.
        St[St < 0] = 0

        # Fill NaN values with zeros.
        St[pd.isnull(St)] = 0

        daily_solar_rad.extend(np.round(St, 2))
        tao_array.extend(np.ones(24) * tau)
        deltat_array.extend(np.ones(24) * deltaT[i])

    # Prepare the results output.
    solarcalc = pd.DataFrame(
        [],
        index=pd.date_range(
            start=climate_data.index[0],
            end=climate_data.index[-1] + pd.Timedelta('23H'),
            freq='H'))
    solarcalc.index.name = 'datetime'
    solarcalc['solar_rad_W/m2'] = daily_solar_rad
    solarcalc['deltat_degC'] = deltat_array
    solarcalc['tau'] = tao_array

    return solarcalc


if __name__ == '__main__':
    climate_data = load_demo_climatedata()
    solarcalc = calc_solar_rad(
        lon_dd=-76.4687209,
        lat_dd=56.5213541,
        alt=100,
        climate_data=climate_data)
    solarcalc.to_csv('output_solarcalc_demo.csv')
    print(solarcalc)
