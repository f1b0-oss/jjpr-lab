"""Successive changes in streams of finite numbers."""

import math


def differences(values):
    """Return each next value minus its predecessor, in input order.

    Consume finite int/float inputs once, retaining only the previous value
    besides the result list. Empty and singleton inputs return an empty list.
    Invalid types raise TypeError; nonfinite floats raise ValueError.
    Results follow Python subtraction, including float rounding and overflow.
    """
    result = []
    have_previous = False
    previous = None
    for value in values:
        if not isinstance(value, (int, float)):
            raise TypeError("differences() requires int or float values")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("differences() requires finite values")
        if have_previous:
            result.append(value - previous)
        previous = value
        have_previous = True
    return result


def total_change(values):
    """Sum successive differences, returning zero for fewer than two values.

    Consume the input once through differences(), inheriting its validation
    and Python arithmetic behavior (including rounding and overflow).
    """
    return sum(differences(values))
