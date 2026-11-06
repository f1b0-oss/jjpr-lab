"""Streaming helpers for rolling numeric analysis."""

from collections import deque


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
