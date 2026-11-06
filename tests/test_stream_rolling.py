import unittest

from stream_rolling import windows


class WindowsTests(unittest.TestCase):
    def test_overlapping_numeric_windows(self):
        self.assertEqual(
            list(windows([3, -2, 1.5, -4.25, 0], 3)),
            [(3, -2, 1.5), (-2, 1.5, -4.25), (1.5, -4.25, 0)],
        )

    def test_width_one_and_exact_width(self):
        self.assertEqual(list(windows([2, -0.5, 0], 1)), [(2,), (-0.5,), (0,)])
        self.assertEqual(list(windows(iter([1, 2, 3]), 3)), [(1, 2, 3)])

    def test_empty_and_short_inputs(self):
        for values in ([], [1], [1, 2]):
            with self.subTest(values=values):
                self.assertEqual(list(windows(iter(values), 3)), [])

    def test_invalid_width_is_rejected_immediately_even_when_empty(self):
        for width in (True, False, 1.0, 2.5, "2", None):
            with self.subTest(width=width):
                with self.assertRaises(TypeError):
                    windows(iter([]), width)
        for width in (0, -1, -100):
            with self.subTest(width=width):
                with self.assertRaises(ValueError):
                    windows(iter([]), width)

    def test_generator_is_consumed_only_as_needed(self):
        consumed = []

        def source():
            for value in (1, -2, 3.5, 4):
                consumed.append(value)
                yield value

        result = iter(windows(source(), 2))
        self.assertEqual(consumed, [])
        first = next(result)
        self.assertEqual(first, (1, -2))
        self.assertEqual(consumed, [1, -2])
        self.assertEqual(next(result), (-2, 3.5))
        self.assertEqual(consumed, [1, -2, 3.5])
        self.assertEqual(list(result), [(3.5, 4)])
        self.assertEqual(first, (1, -2))

    def test_iterable_is_requested_only_once(self):
        class SinglePass:
            def __init__(self):
                self.started = False

            def __iter__(self):
                if self.started:
                    raise AssertionError("source iterated twice")
                self.started = True
                return iter([1, 2, 3, 4])

        self.assertEqual(list(windows(SinglePass(), 2)), [(1, 2), (2, 3), (3, 4)])


if __name__ == "__main__":
    unittest.main()
