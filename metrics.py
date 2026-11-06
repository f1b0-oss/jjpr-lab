"""Baseline API shared by the isolated streaming-metrics tasks."""


def total(values, *, start=0):
    """Sum a finite iterable of numbers, starting from start as in Python's sum."""
    return sum(values, start)
