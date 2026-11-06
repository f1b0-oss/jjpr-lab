import unittest
from itertools import count, islice

from stream_rolling import windows


class WindowsTests(unittest.TestCase):
    def test_overlapping_numeric_windows(self):
        self.assertEqual(
            list(windows([3, -2, 1.5, -4.25, 0], 3)),
            [(3, -2, 1.5), (-2, 1.5, -4.25), (1.5, -4.25, 0)],
        )

    def test_width_one(self):
        self.assertEqual(list(windows([2, -1.5, 0], 1)), [(2,), (-1.5,), (0,)])

    def test_exact_width(self):
        self.assertEqual(list(windows(iter([1, 2, 3]), 3)), [(1, 2, 3)])

    def test_empty_and_short_inputs(self):
        for values, width in [([], 1), ([], 3), ([1, 2], 3), ([1], 10**100)]:
            with self.subTest(values=values, width=width):
                self.assertEqual(list(windows(iter(values), width)), [])

    def test_invalid_width_types_are_rejected_immediately(self):
        for width in [True, False, 1.0, 2.5, "2", None, 1 + 0j]:
            for values in [[], [1, 2]]:
                with self.subTest(width=width, values=values):
                    with self.assertRaises(TypeError):
                        windows(values, width)

    def test_nonpositive_widths_are_rejected_immediately(self):
        for width in [0, -1, -100]:
            for values in [[], [1, 2]]:
                with self.subTest(width=width, values=values):
                    with self.assertRaises(ValueError):
                        windows(values, width)

    def test_generator_is_consumed_lazily_once(self):
        consumed = []

        def source():
            for value in range(5):
                consumed.append(value)
                yield value

        result = windows(source(), 3)
        self.assertEqual(consumed, [])
        first = next(result)
        self.assertEqual(first, (0, 1, 2))
        self.assertEqual(consumed, [0, 1, 2])
        self.assertEqual(next(result), (1, 2, 3))
        self.assertEqual(consumed, [0, 1, 2, 3])
        self.assertEqual(list(result), [(2, 3, 4)])
        self.assertEqual(consumed, [0, 1, 2, 3, 4])
        self.assertEqual(first, (0, 1, 2))

    def test_iterable_is_only_iterated_once(self):
        class SinglePass:
            def __init__(self):
                self.started = False

            def __iter__(self):
                if self.started:
                    raise AssertionError("input was iterated more than once")
                self.started = True
                return iter([1, 2, 3, 4])

        self.assertEqual(list(windows(SinglePass(), 2)), [(1, 2), (2, 3), (3, 4)])

    def test_unbounded_input_can_be_consumed_incrementally(self):
        self.assertEqual(
            list(islice(windows(count(), 2), 3)),
            [(0, 1), (1, 2), (2, 3)],
        )


if __name__ == "__main__":
    unittest.main()
