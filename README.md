# SolarCalc
[![license](https://img.shields.io/pypi/l/appconfigs.svg)](./LICENSE)
[![pypi version](https://img.shields.io/pypi/v/solarcalc.svg)](https://pypi.org/project/solarcalc/)

The SolarcCalc module is used to predict hourly global solar
radiation on a horizontal surface from daily average temperature
extremes and total precipitation records.
The method used in the calculations is based on that presented in
[An Introduction to Environmental Biophysics](https://link.springer.com/book/10.1007/978-1-4612-1626-1)
by Campbell, G.S. and J.M. Norman (1998).
<br><br>
Version 1.0 of the SolarcCalc module is based on the source code of
SolarCalc.jar (version 1.1, Jan. 2006), a computer program  that was
developped by the USDA Agricultural Research Service and that is
available free of charge at [https://data.nal.usda.gov/dataset/solarcalc-10](https://data.nal.usda.gov/dataset/solarcalc-10).
<br><br>
Subsequent versions of the SolarcCalc module implemented performance
improvements and fixed some issues with the original code and method.


## Installation

`SolarCalc` can be installed with `pip` by running:

```commandlines
pip install solarcalc
```

## Requirements

- [numpy](https://github.com/numpy/numpy) :  The fundamental package for scientific computing with Python.
- [pandas](https://github.com/pandas-dev/pandas) : Flexible and powerful data analysis / manipulation library for Python.

## Example

```
>>> from solarcalc import load_demo_climatedata, calc_solar_rad

>>> climate_data = load_demo_climatedata()
>>> solarcalc = calc_solar_rad(
>>>     lon_dd=-76.4687209,
>>>     lat_dd=56.5213541,
>>>     alt=100,
>>>     climate_data=climate_data)
>>> print(solarcalc)

                     solar_rad_W/m2  deltat_degC       tau
1980-01-01 00:00:00             0.0          8.0  0.233333
1980-01-01 01:00:00             0.0          8.0  0.233333
1980-01-01 02:00:00             0.0          8.0  0.233333
1980-01-01 03:00:00             0.0          8.0  0.233333
1980-01-01 04:00:00             0.0          8.0  0.233333
                            ...          ...       ...
2020-12-31 19:00:00             0.0          5.0  0.116667
2020-12-31 20:00:00             0.0          5.0  0.116667
2020-12-31 21:00:00             0.0          5.0  0.116667
2020-12-31 22:00:00             0.0          5.0  0.116667
2020-12-31 23:00:00             0.0          5.0  0.116667

[359424 rows x 3 columns]

```
