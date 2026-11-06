"""Numeric statistics for single-pass iterables."""

from statistics import mean as _mean


def mean(values):
    """Return the arithmetic mean of finite int/float values.

    Consume values once, including when it is an iterator or generator.
    Raise ValueError if values is empty.
    """
    return _mean(values)
