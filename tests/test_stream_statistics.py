import unittest
from unittest.mock import patch

from stream_statistics import mean, population_variance


class MeanTests(unittest.TestCase):
    def test_integer_values(self):
        self.assertEqual(mean([1, 2, 6]), 3)
        self.assertEqual(mean([1, 2]), 1.5)

    def test_negative_and_mixed_values(self):
        self.assertEqual(mean([-8, -4, -3]), -5)
        self.assertEqual(mean([-3, 1.5, 6]), 1.5)
        self.assertEqual(mean([-2, 0, 2]), 0)

    def test_float_values(self):
        self.assertAlmostEqual(mean([0.1, 0.2, 0.3]), 0.2)

    def test_single_value(self):
        for value in (0, -7, 2.5):
            with self.subTest(value=value):
                self.assertEqual(mean(iter([value])), value)

    def test_generator(self):
        consumed = []

        def values():
            for value in (2, -4, 8):
                consumed.append(value)
                yield value

        stream = values()
        self.assertEqual(mean(stream), 2)
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
                return iter((1, 3, 5))

        self.assertEqual(mean(SinglePass()), 3)

    def test_empty_input(self):
        for values in ([], iter(()), (value for value in ())):
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    mean(values)

    def test_large_finite_floats_do_not_overflow(self):
        self.assertEqual(mean(iter([1e308, 1e308])), 1e308)
        self.assertEqual(mean(iter([-1e308, 1e308])), 0)

    def test_cancellation_preserves_small_contribution(self):
        self.assertEqual(mean(iter([1e16, 1, -1e16])), 1 / 3)

    def test_large_integers(self):
        value = 10 ** 400
        self.assertEqual(mean(iter([value, value])), value)


class PopulationVarianceTests(unittest.TestCase):
    def test_population_divisor(self):
        self.assertEqual(population_variance([1, 3]), 1)
        self.assertEqual(population_variance([2, 4, 4, 4, 5, 5, 7, 9]), 4)

    def test_negative_and_mixed_values(self):
        self.assertEqual(population_variance([-8, -4, -3]), 14 / 3)
        self.assertEqual(population_variance([-2, 0.5, 3]), 25 / 6)

    def test_float_values(self):
        self.assertAlmostEqual(population_variance([0.1, 0.2, 0.3]), 1 / 150)

    def test_singleton_and_constant_values(self):
        for value in (0, -7, 2.5, 1e308, 10 ** 400):
            with self.subTest(value=value):
                self.assertEqual(population_variance(iter([value])), 0)
                self.assertEqual(population_variance(iter([value] * 3)), 0)

    def test_generator(self):
        consumed = []

        def values():
            for value in (2, -4, 8):
                consumed.append(value)
                yield value

        stream = values()
        self.assertEqual(population_variance(stream), 24)
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
                return iter((1, 3, 5))

        self.assertEqual(population_variance(SinglePass()), 8 / 3)

    def test_empty_input(self):
        for values in ([], iter(()), (value for value in ())):
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    population_variance(values)

    def test_uses_module_global_mean_to_compute_deviations(self):
        with patch('stream_statistics.mean', return_value=0) as mocked_mean:
            self.assertEqual(population_variance(iter([1, 3])), 5)
        mocked_mean.assert_called_once_with([1, 3])


if __name__ == '__main__':
    unittest.main()
