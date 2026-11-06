import unittest
from itertools import count, islice
from unittest.mock import patch

from stream_rolling import moving_average, windows


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


class MovingAverageTests(unittest.TestCase):
    def test_overlapping_mixed_numeric_windows(self):
        self.assertEqual(
            moving_average([3, -2, 1.5, -4.25, 0], 3),
            [2.5 / 3, -4.75 / 3, -2.75 / 3],
        )

    def test_width_one_and_exact_width(self):
        self.assertEqual(moving_average([2, -1.5, 0], 1), [2.0, -1.5, 0.0])
        self.assertEqual(moving_average(iter([1, 2, 3]), 3), [2.0])
        self.assertEqual(moving_average([-3, -2], 2), [-2.5])

    def test_empty_and_short_inputs_return_lists(self):
        for values, width in [([], 1), ([], 3), ([1, 2], 3), ([1], 10**100)]:
            with self.subTest(values=values, width=width):
                result = moving_average(iter(values), width)
                self.assertIsInstance(result, list)
                self.assertEqual(result, [])

    def test_width_errors_match_windows_exactly(self):
        for width in [True, False, 1.0, 2.5, "2", None, 1 + 0j, 0, -1, -100]:
            for values in [[], [1, 2]]:
                with self.subTest(width=width, values=values):
                    try:
                        windows(values, width)
                    except (TypeError, ValueError) as expected:
                        with self.assertRaises(type(expected)) as caught:
                            moving_average(iter(values), width)
                        self.assertEqual(str(caught.exception), str(expected))
                    else:
                        self.fail("windows accepted an invalid width")

    def test_invalid_width_does_not_consume_input(self):
        def source():
            self.fail("input consumed before width validation")
            yield 1

        for width, error in [(True, TypeError), (0, ValueError)]:
            with self.subTest(width=width):
                with self.assertRaises(error):
                    moving_average(source(), width)

    def test_generator_is_consumed_once(self):
        consumed = []

        def source():
            for value in [1, 2, 3, 4]:
                consumed.append(value)
                yield value

        self.assertEqual(moving_average(source(), 2), [1.5, 2.5, 3.5])
        self.assertEqual(consumed, [1, 2, 3, 4])

    def test_single_pass_iterable(self):
        class SinglePass:
            def __init__(self):
                self.started = False

            def __iter__(self):
                if self.started:
                    raise AssertionError("input was iterated more than once")
                self.started = True
                return iter([1, 2, 3, 4])

        self.assertEqual(moving_average(SinglePass(), 2), [1.5, 2.5, 3.5])

    def test_uses_module_global_windows_to_compute_result(self):
        values = iter([100, 200, 300])
        with patch("stream_rolling.windows", return_value=iter([(2, 6), (-4, 1)])) as mocked:
            self.assertEqual(moving_average(values, 2), [4.0, -1.5])
        mocked.assert_called_once_with(values, 2)


if __name__ == "__main__":
    unittest.main()
