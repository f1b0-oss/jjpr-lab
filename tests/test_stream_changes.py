import unittest

from stream_changes import differences


class DifferencesTests(unittest.TestCase):
    def test_successive_differences_preserve_order(self):
        values = [3, 8, 2, 2, 10]
        self.assertEqual(differences(values), [5, -6, 0, 8])
        self.assertEqual(values, [3, 8, 2, 2, 10])

    def test_negative_and_mixed_numbers(self):
        self.assertEqual(differences([-8, -3, -12, 0]), [5, -9, 12])
        self.assertEqual(differences((-2, 0.5, -1.25, 3)),
                         [2.5, -1.75, 4.25])

    def test_float_rounding(self):
        result = differences([0.1, 0.2, 0.3])
        self.assertEqual(len(result), 2)
        for value in result:
            self.assertAlmostEqual(value, 0.1)

    def test_empty_and_singleton_inputs(self):
        for values in ([], [0], [-7], [2.5]):
            for kind in (list, iter):
                with self.subTest(values=values, kind=kind):
                    self.assertEqual(differences(kind(values)), [])
        self.assertEqual(differences(value for value in ()), [])

    def test_generator_consumed_once(self):
        consumed = []

        def values():
            for value in (2, -4, 8):
                consumed.append(value)
                yield value

        stream = values()
        self.assertEqual(differences(stream), [-6, 12])
        self.assertEqual(consumed, [2, -4, 8])
        self.assertEqual(list(stream), [])

    def test_iterable_can_only_be_traversed_once(self):
        class SinglePass:
            def __init__(self):
                self.started = False

            def __iter__(self):
                if self.started:
                    raise AssertionError('iterable was traversed twice')
                self.started = True
                return iter((1, 3, 8))

        self.assertEqual(differences(SinglePass()), [2, 5])

    def test_arbitrarily_large_integers(self):
        large = 10 ** 1000
        self.assertEqual(differences([large, large + 1, -large]),
                         [1, -2 * large - 1])

    def test_nonfinite_values(self):
        for value in (float('inf'), float('-inf'), float('nan')):
            for values in ([value], [0, value], [0, 1, value]):
                with self.subTest(values=values):
                    with self.assertRaises(ValueError):
                        differences(iter(values))

    def test_nonnumeric_values(self):
        for value in ('3', None, complex(1, 2)):
            for values in ([value], [0, value], [0, 1, value]):
                with self.subTest(values=values):
                    with self.assertRaises(TypeError):
                        differences(iter(values))

    def test_extreme_float_result_follows_python_subtraction(self):
        self.assertEqual(differences([-1e308, 1e308]), [float('inf')])


if __name__ == '__main__':
    unittest.main()
