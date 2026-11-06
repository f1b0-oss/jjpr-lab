import unittest
from unittest.mock import patch

from stream_ranges import bounds
from stream_ranges import normalize


class BoundsTests(unittest.TestCase):
    def test_mixed_numbers(self):
        self.assertEqual(bounds([3, -2.5, 8, 0, 4.25]), (-2.5, 8))

    def test_negative_numbers(self):
        self.assertEqual(bounds([-8, -3, -12, -3]), (-12, -3))

    def test_single_value(self):
        for value in (0, -7, 2.5):
            with self.subTest(value=value):
                self.assertEqual(bounds(iter([value])), (value, value))

    def test_repeated_values(self):
        self.assertEqual(bounds([4, 4, 4]), (4, 4))

    def test_generator(self):
        values = (value * 0.5 for value in range(-6, 5))
        self.assertEqual(bounds(values), (-3.0, 2.0))
        self.assertEqual(list(values), [])

    def test_iterable_is_consumed_once(self):
        class SinglePass:
            def __init__(self):
                self.started = False

            def __iter__(self):
                if self.started:
                    raise AssertionError("iterable traversed twice")
                self.started = True
                return iter([5, -9, 12, 1])

        self.assertEqual(bounds(SinglePass()), (-9, 12))

    def test_empty_input(self):
        for values in ([], iter(()), (value for value in ())):
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    bounds(values)

    def test_arbitrarily_large_integers(self):
        large = 10 ** 1000
        self.assertEqual(bounds([large, 1.5, -large]), (-large, large))

    def test_nonfinite_values(self):
        for value in (float('inf'), float('-inf'), float('nan')):
            for values in ([value], [0, value]):
                with self.subTest(values=values):
                    with self.assertRaises(ValueError):
                        bounds(values)

    def test_nonnumeric_values(self):
        for value in ('3', None, complex(1, 2)):
            for values in ([value], [0, value]):
                with self.subTest(values=values):
                    with self.assertRaises(TypeError):
                        bounds(values)


class NormalizeTests(unittest.TestCase):
    def test_mixed_numbers_preserve_order(self):
        self.assertEqual(normalize([3, -2.5, 8, 0, 4.25]),
                         [(x + 2.5) / 10.5 for x in [3, -2.5, 8, 0, 4.25]])

    def test_negative_numbers(self):
        self.assertEqual(normalize([-8, -3, -12, -3]),
                         [4 / 9, 1.0, 0.0, 1.0])

    def test_constant_and_single_value(self):
        for values in ([0], [-7], [2.5], [4, 4, 4], [-2.5, -2.5]):
            with self.subTest(values=values):
                result = normalize(iter(values))
                self.assertEqual(result, [0.0] * len(values))
                self.assertTrue(all(type(value) is float for value in result))

    def test_generator(self):
        values = (value * 0.5 for value in range(-2, 3))
        self.assertEqual(normalize(values), [0.0, 0.25, 0.5, 0.75, 1.0])
        self.assertEqual(list(values), [])

    def test_iterable_is_consumed_once(self):
        class SinglePass:
            def __init__(self):
                self.started = False

            def __iter__(self):
                if self.started:
                    raise AssertionError("iterable traversed twice")
                self.started = True
                return iter([5, -9, 12, 1])

        self.assertEqual(normalize(SinglePass()), [14 / 21, 0.0, 1.0, 10 / 21])

    def test_empty_input(self):
        for values in ([], iter(()), (value for value in ())):
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    normalize(values)

    def test_nonfinite_values(self):
        for value in (float('inf'), float('-inf'), float('nan')):
            for values in ([value], [0, value]):
                with self.subTest(values=values):
                    with self.assertRaises(ValueError):
                        normalize(iter(values))

    def test_nonnumeric_values(self):
        for value in ('3', None, complex(1, 2)):
            for values in ([value], [0, value]):
                with self.subTest(values=values):
                    with self.assertRaises(TypeError):
                        normalize(iter(values))

    def test_extreme_finite_numbers(self):
        large = 10 ** 1000
        for values in ([-large, 0, large], [-large, 0.0, large],
                       [-1e308, 0.0, 1e308], [0.0, 1.0, large]):
            with self.subTest(values=values):
                result = normalize(values)
                self.assertEqual(result[0], 0.0)
                self.assertEqual(result[-1], 1.0)
                self.assertTrue(0.0 <= result[1] <= 1.0)
        self.assertEqual(normalize([-1e308, 0.0, 1e308]), [0.0, 0.5, 1.0])

    def test_uses_module_global_bounds_result(self):
        with patch('stream_ranges.bounds', return_value=(-10, 10)) as mocked:
            self.assertEqual(normalize(value for value in [0, 5]), [0.5, 0.75])
        mocked.assert_called_once_with([0, 5])


if __name__ == '__main__':
    unittest.main()
