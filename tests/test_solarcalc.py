# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © Jean-Sébastien Gosselin
# Licensed under the terms of the MIT License
# (https://github.com/jnsebgosselin/appconfigs)
# -----------------------------------------------------------------------------

# ---- Standard imports
import os
import os.path as osp
from datetime import datetime

# ---- Third party imports
import pytest
import pandas as pd
import numpy as np

# ---- Local imports
from solarcalc import calc_long_corr, calc_eqn_of_time


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


if __name__ == "__main__":
    pytest.main(['-x', osp.basename(__file__), '-vv', '-rw', '-s'])
