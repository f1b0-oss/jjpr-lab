"""Streaming helpers for rolling numeric analysis."""

from collections import deque
from statistics import mean


def windows(values, width):
    """Return consecutive full-width tuples from a single pass over values.

    Width must be a positive integer (excluding bool), even for empty input.
    Values are consumed lazily, with at most ``width`` values buffered.
    Empty inputs and inputs shorter than width yield no windows.
    """
    if isinstance(width, bool) or not isinstance(width, int):
        raise TypeError("width must be a positive integer")
    if width <= 0:
        raise ValueError("width must be positive")

    def generate():
        buffer = deque()
        for value in values:
            buffer.append(value)
            if len(buffer) == width:
                yield tuple(buffer)
                buffer.popleft()

    return generate()


def moving_average(values, width):
    """Return arithmetic means of consecutive full-width windows.

    Consume a finite iterable once, returning [] when it has fewer than width
    values. Width validation and window construction are delegated to windows.
    """
    return [mean(window) for window in windows(values, width)]
