import unittest
from metrics import total


class TotalTests(unittest.TestCase):
    def test_single_pass_and_empty(self):
        self.assertEqual(total(iter([3, -2, 8])), 9)
        self.assertEqual(total(iter([])), 0)


if __name__ == '__main__':
    unittest.main()
