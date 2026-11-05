"""Baseline API shared by the isolated streaming-metrics tasks."""


def total(values):
    """Sum a finite iterable of numbers."""
    return sum(values)
