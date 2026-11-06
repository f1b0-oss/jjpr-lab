"""Range analysis for streams of finite numbers."""

import math
from fractions import Fraction


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


def normalize(values):
    """Return values scaled to [0, 1], preserving their input order.

    Accept a single-pass iterable of finite ints or floats. Empty input
    raises ValueError; a constant range produces one 0.0 per value.
    """
    values = list(values)
    minimum, maximum = bounds(values)
    if minimum == maximum:
        return [0.0] * len(values)

    try:
        span = maximum - minimum
        if not isinstance(span, float) or math.isfinite(span):
            return [(value - minimum) / span for value in values]
    except OverflowError:
        pass

    # Exact arithmetic avoids overflow for extreme finite floats or mixed
    # floats and integers too large to convert to float.
    minimum = Fraction(minimum)
    span = Fraction(maximum) - minimum
    return [float((Fraction(value) - minimum) / span) for value in values]
