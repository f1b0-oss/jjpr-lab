"""Numeric statistics for single-pass iterables."""

from statistics import mean as _mean


def mean(values):
    """Return the arithmetic mean of finite int/float values.

    Consume values once, including when it is an iterator or generator.
    Raise ValueError if values is empty.
    """
    return _mean(values)


def population_variance(values):
    """Return the population variance of finite int/float values.

    Consume the input once and retain its values to compute deviations from
    mean(values). Raise ValueError for empty input.
    """
    values = list(values)
    average = mean(values)
    return sum((value - average) ** 2 for value in values) / len(values)
