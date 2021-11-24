# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © INRS
# Licensed under the terms of the MIT License
# https://github.com/cgq-qgc/solarcalc
# -----------------------------------------------------------------------------

"""
File for running tests programmatically.
"""

import pytest


def main():
    """Run pytest tests."""
    errno = pytest.main(['-x', 'solarcalc', '-v', '-rw', '--durations=10',
                         '--cov=gwire', '-o', 'junit_family=xunit2',
                         '--no-coverage-upload'])
    if errno != 0:
        raise SystemExit(errno)


if __name__ == '__main__':
    main()
