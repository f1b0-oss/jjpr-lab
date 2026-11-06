import unittest

from stream_ranges import bounds


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


if __name__ == '__main__':
    unittest.main()
