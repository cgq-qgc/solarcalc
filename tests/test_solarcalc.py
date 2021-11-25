# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © INRS
# Licensed under the terms of the MIT License
# https://github.com/cgq-qgc/solarcalc
# -----------------------------------------------------------------------------

# ---- Standard imports
import os.path as osp
from datetime import datetime

# ---- Third party imports
import pytest
import pandas as pd
import numpy as np

# ---- Local imports
from solarcalc import (calc_long_corr, calc_eqn_of_time, calc_solar_rad)


@pytest.fixture
def datetimes():
    return pd.to_datetime([
        datetime(2000, 1, 1),
        datetime(2000, 3, 31),
        datetime(2000, 6, 19),
        datetime(2000, 8, 18),
        datetime(2000, 11, 26)
        ])


@pytest.fixture
def climate_data():
    dataf = pd.DataFrame(
        data=[],
        index=pd.to_datetime([
            "1980-01-01", "1980-01-02", "1980-01-03", "1980-01-04",
            "1980-01-05", "1980-01-06"
            ])
        )

    # The first reading test the condition deltaT[i] <= 10 and when
    # tamax and tamin values are inverted.
    # The second reading test the condition deltaT[i] > 10
    # The other readings test the condition deltaT[i] == 0
    dataf['tamin_degC'] = [-20.8, -14.0, -28.7, -32.84, -33.4, -29.6]
    dataf['tamax_degC'] = [-14.8, -24.4, -28.7, -32.84, -33.4, -29.6]

    # The first reading test the overcast condition at the start of the series.
    # The second reading test the clear sky condition.
    # The third reading test the pre-rain condition.
    # The fourth reading test the overcast condition.
    # The fifth reading test the denser cloud cover condition.
    # The sixth reading thes the clear sky condition at the end of the series.
    dataf['ptot_mm'] = [1.54, 0.41, 0.00, 2.35, 1.92, 0.21]
    return dataf


# =============================================================================
# ---- Tests
# =============================================================================
def test_calc_eqn_of_time(datetimes):
    """
    Test that the Equation of Time is calculated as expected.
    """
    results = calc_eqn_of_time(datetimes.dayofyear.values) * 60

    # Table 11.1 in Campbell, G.S. and J.M. Norman (1998).
    expected_results = np.array([-0.057, -0.072, -0.019, -0.065, 0.213]) * 60
    err = np.abs(results - expected_results)
    assert np.all(err < 0.3)

    # https://gml.noaa.gov/grad/solcalc/
    expected_results = np.array([-3.19, -4.1, -1.4, -3.83, 12.65])
    err = np.abs(results - expected_results)
    assert np.all(err < 0.3)


def test_calc_solar_noon(datetimes):
    """
    Test that solar noon is calculated as expected.
    """
    lon_dd = -74.351267
    LC = calc_long_corr(lon_dd)
    ET = calc_eqn_of_time(datetimes.dayofyear.values)
    solarnoon = 12 - LC - ET

    # https://gml.noaa.gov/grad/solcalc/
    # Values corrected for daylight saving time change.
    expected_results = np.array([
        12 + 0/60 + 50/3600 + 1,
        13 + 1/60 + 38/3600,
        12 + 58/60 + 55/3600,
        13 + 1/60 + 7/3600,
        11 + 44/60 + 55/3600 + 1
        ])

    err = np.abs(solarnoon - expected_results)
    assert np.all(err < 0.0035)


def test_solar_calc(climate_data):
    """
    Test that global solar radiation is calculated as expected.
    """
    # climate_data = load_demo_climatedata()
    solar_rad = calc_solar_rad(
        lon_dd=-76.4687209,
        lat_dd=56.5213541,
        alt=100,
        climate_data=climate_data
        )

    assert np.all(
        solar_rad['deltat_degC'].round(12).values ==
        np.repeat([6, 10.4, 0, 0, 0, 0], 24)
        )
    assert np.all(
        solar_rad['tau'].round(12).values ==
        np.repeat([0.4 / (11 - 6), 0.7, 0.6, 0.4, 0.3, 0.7], 24)
        )
    expected_results = np.array([ 
        0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,
        0.  ,   6.98,  41.6 ,  64.28,  73.5 ,  68.62,  49.97,  18.82,
        0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,
        0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,
        0.  ,   7.19,  45.07,  81.08,  98.82,  89.54,  57.65,  19.67,
        0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,
        0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,
        0.  ,   7.44,  43.02,  71.64,  85.66,  78.56,  53.7 ,  20.5 ,
        0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,
        0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,
        0.  ,   7.75,  42.7 ,  66.27,  76.57,  71.6 ,  52.44,  21.4 ,
        0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,
        0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,
        0.  ,   8.11,  43.15,  66.4 ,  76.26,  71.69,  53.23,  22.35,
        0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,
        0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,
        0.  ,   8.53,  47.46,  85.16, 104.19,  95.5 ,  63.03,  23.46,
        0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ,   0.  ])
    assert np.all(
        expected_results ==
        solar_rad['solar_rad_W/m2'].round(12).values
        )


if __name__ == "__main__":
    pytest.main(['-x', osp.basename(__file__), '-vv', '-rw', '-s'])
