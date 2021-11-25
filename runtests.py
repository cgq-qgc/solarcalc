# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © SolarCalc Project Contributors
# Licensed under the terms of the MIT License
# https://github.com/cgq-qgc/solarcalc
# -----------------------------------------------------------------------------

"""
File for running tests programmatically.
"""
import os
import pytest


def main():
    """Run pytest tests."""
    if os.environ.get('AZURE', None):
        errno = pytest.main(['-x', '.', '-v', '-rw', '--durations=10',
                             '--cov=solarcalc', '-o', 'junit_family=xunit2',
                             '--no-coverage-upload'])
    else:
        errno = pytest.main(['-x', '.', '-v', '-rw', '--durations=10',
                             '--cov=solarcalc', '-o', 'junit_family=xunit2'])

    if errno != 0:
        raise SystemExit(errno)


if __name__ == '__main__':
    main()
