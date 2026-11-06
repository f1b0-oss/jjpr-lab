"""Streaming rolling-window helpers."""

from collections import deque


def windows(values, width):
    """Return consecutive full-width tuples from a single pass over values.

    Validate width immediately, even for empty input. Values are consumed
    lazily, with at most width items buffered; incomplete windows are omitted.
    """
    if isinstance(width, bool) or not isinstance(width, int):
        raise TypeError("width must be a positive integer")
    if width <= 0:
        raise ValueError("width must be a positive integer")

    def generate():
        window = deque()
        for value in values:
            window.append(value)
            if len(window) == width:
                yield tuple(window)
                window.popleft()

    return generate()
