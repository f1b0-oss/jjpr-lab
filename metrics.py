"""Baseline API shared by the isolated streaming-metrics tasks."""

import math
from itertools import chain


def total(values, *, start=0):
    """Sum a finite iterable, including start in floating-point compensation.

    Consume the source once and buffer it to choose numeric semantics. Built-in
    int/float inputs use math.fsum when a float is present or start is integer
    zero (the default). Those results are floats and inherit fsum's precision,
    conversion, overflow, and non-finite-value behavior.

    Otherwise preserve Python sum semantics, including exact integer totals,
    other numeric types, and an unchanged start for empty inputs. The default
    empty result is 0.0. Buffering requires memory proportional to input size.
    """
    values = list(values)
    default_start = type(start) is int and start == 0
    builtin_reals = type(start) in (int, float) and all(
        type(value) in (int, float) for value in values
    )
    has_float = type(start) is float or any(
        type(value) is float for value in values
    )
    if builtin_reals and (default_start or (values and has_float)):
        return math.fsum(chain((start,), values))
    return sum(values, start)
