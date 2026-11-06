import unittest
from decimal import Decimal
from fractions import Fraction

from metrics import total


class TotalStartTests(unittest.TestCase):
    def test_default_start_remains_zero(self):
        self.assertEqual(total([3, -2, 8]), 9)
        self.assertEqual(total([]), 0)

    def test_accumulate_onto_existing_total(self):
        self.assertEqual(total([3, -2, 8], start=10), 19)
        self.assertEqual(total([1, 2], start=-10), -7)

    def test_start_is_keyword_only(self):
        with self.assertRaises(TypeError):
            total([1, 2], 10)

    def test_empty_inputs_return_start_unchanged(self):
        start = Decimal('12.50')
        for values in ([], iter(()), (value for value in ())):
            with self.subTest(values=values):
                self.assertIs(total(values, start=start), start)

    def test_generator_is_consumed_once(self):
        consumed = []

        def values():
            for value in (3, -2, 8):
                consumed.append(value)
                yield value

        stream = values()
        self.assertEqual(total(stream, start=10), 19)
        self.assertEqual(consumed, [3, -2, 8])
        self.assertEqual(list(stream), [])

    def test_iterable_is_requested_once(self):
        class SinglePass:
            def __init__(self):
                self.started = False

            def __iter__(self):
                if self.started:
                    raise AssertionError('iterable was traversed twice')
                self.started = True
                return iter((3, -2, 8))

        self.assertEqual(total(SinglePass(), start=10), 19)

    def test_numeric_results_follow_python_sum(self):
        cases = (
            ([1e16, 1.0, -1e16], 1.0),
            ([10 ** 400, 1], 10 ** 400),
            ([1, 2.5], 0.5),
            ([1 + 2j, 3], 4j),
            ([Decimal('0.1'), Decimal('0.2')], Decimal('1.0')),
            ([Fraction(1, 3), Fraction(1, 6)], Fraction(1, 2)),
        )
        for values, start in cases:
            with self.subTest(values=values, start=start):
                expected = sum(values, start)
                actual = total(iter(values), start=start)
                self.assertEqual(actual, expected)
                self.assertIs(type(actual), type(expected))

    def test_invalid_operands_follow_python_sum(self):
        for values, start in (([], ''), ([], b''), ([], bytearray()),
                              ([1], None), (['2'], 0)):
            with self.subTest(values=values, start=start):
                with self.assertRaises(TypeError) as expected:
                    sum(values, start)
                with self.assertRaises(TypeError) as actual:
                    total(iter(values), start=start)
                self.assertEqual(str(actual.exception), str(expected.exception))


if __name__ == '__main__':
    unittest.main()
