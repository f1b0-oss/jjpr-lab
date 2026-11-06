import unittest

from metrics import total


class TotalAccuracyTests(unittest.TestCase):
    def test_cancellation_preserves_small_contribution(self):
        self.assertEqual(total([1e16, 1.0, -1e16]), 1.0)

    def test_start_participates_in_compensated_sum(self):
        self.assertEqual(total([1e16, 1, -1e16], start=2), 3.0)
        self.assertEqual(total([1.0, -1e16], start=1e16), 1.0)

    def test_cancellation_with_start_consumes_source_once(self):
        class SinglePass:
            def __init__(self):
                self.calls = 0

            def __iter__(self):
                self.calls += 1
                if self.calls != 1:
                    raise AssertionError('iterable was traversed twice')
                yield from (1e16, 1, -1e16)

        values = SinglePass()
        self.assertEqual(total(values, start=2), 3.0)
        self.assertEqual(values.calls, 1)

    def test_empty_inputs_preserve_nonzero_start(self):
        start = 2.5
        for values in ([], iter(()), (value for value in ())):
            with self.subTest(values=values):
                result = total(values, start=start)
                self.assertEqual(result, start)
                self.assertIs(type(result), type(start))

    def test_nonzero_integer_start_preserves_exact_integer_total(self):
        result = total(iter([10**400, 1]), start=2)
        self.assertEqual(result, 10**400 + 3)
        self.assertIs(type(result), int)

    def test_repeated_small_contributions(self):
        self.assertEqual(total([0.1] * 10), 1.0)

    def test_empty_inputs_return_float_zero(self):
        for values in ([], iter(()), (value for value in ())):
            with self.subTest(values=values):
                result = total(values)
                self.assertEqual(result, 0.0)
                self.assertIsInstance(result, float)

    def test_integer_inputs_return_float(self):
        result = total([3, -2, 8])
        self.assertEqual(result, 9.0)
        self.assertIsInstance(result, float)

    def test_integer_inputs_follow_float_precision(self):
        self.assertEqual(total([2**53 + 1]), float(2**53))

    def test_one_shot_generator(self):
        consumed = []

        def source():
            for value in (1e16, 1.0, -1e16):
                consumed.append(value)
                yield value

        values = source()
        self.assertEqual(total(values), 1.0)
        self.assertEqual(consumed, [1e16, 1.0, -1e16])
        self.assertEqual(list(values), [])

    def test_iterable_is_requested_once(self):
        class SinglePass:
            def __init__(self):
                self.started = False

            def __iter__(self):
                if self.started:
                    raise AssertionError('iterable was traversed twice')
                self.started = True
                return iter((1e16, 1.0, -1e16))

        self.assertEqual(total(SinglePass()), 1.0)


if __name__ == '__main__':
    unittest.main()
