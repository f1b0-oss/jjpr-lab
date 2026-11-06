"""Range analysis for streams of finite numbers."""

import math


def bounds(values):
    """Return (minimum, maximum) in one pass using constant extra space.

    Values must be finite ints or floats. Empty input raises ValueError,
    nonnumeric values raise TypeError, and nonfinite floats raise ValueError.
    """
    iterator = iter(values)
    try:
        first = next(iterator)
    except StopIteration:
        raise ValueError("bounds() requires at least one value") from None

    def validate(value):
        if not isinstance(value, (int, float)):
            raise TypeError("bounds() requires int or float values")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("bounds() requires finite values")

    validate(first)
    minimum = maximum = first
    for value in iterator:
        validate(value)
        if value < minimum:
            minimum = value
        if value > maximum:
            maximum = value
    return minimum, maximum
