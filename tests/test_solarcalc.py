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
from solarcalc import (calc_long_corr, calc_eqn_of_time, calc_solar_rad,
                       load_demo_climatedata)


@pytest.fixture
def datetimes():
    return pd.to_datetime([
        datetime(2000, 1, 1),
        datetime(2000, 3, 31),
        datetime(2000, 6, 19),
        datetime(2000, 8, 18),
        datetime(2000, 11, 26)
        ])


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


def test_solar_calc():
    """
    Test that global solar radiation is calculated as expected.
    """
    expected_results = pd.read_csv(
        osp.join(osp.dirname(__file__), 'output_solarcalc_demo.csv'),
        header=0,
        parse_dates=['datetime'],
        index_col='datetime',
        dtype={'solar_rad_W/m2': 'float',
               'solar_rad_W/m2': 'float',
               'tau': 'float'}
        ).round(8)

    climate_data = load_demo_climatedata()
    solar_rad = calc_solar_rad(
        lon_dd=-76.4687209,
        lat_dd=56.5213541,
        alt=100,
        climate_data=climate_data
        ).round(8)

    assert (expected_results.index == solar_rad.index).all()
    assert expected_results.values.tolist() == solar_rad.values.tolist()


if __name__ == "__main__":
    pytest.main(['-x', osp.basename(__file__), '-vv', '-rw', '-s'])
