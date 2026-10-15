import unittest
from app import money_to_cents, money

class MoneyTests(unittest.TestCase):
    def test_whole_rand(self):
        self.assertEqual(money_to_cents("25"), 2500)

    def test_cents(self):
        self.assertEqual(money_to_cents("25.50"), 2550)

    def test_comma_decimal(self):
        self.assertEqual(money_to_cents("25,50"), 2550)

    def test_format(self):
        self.assertEqual(money(12345), "R123.45")

    def test_negative_rejected(self):
        with self.assertRaises(ValueError):
            money_to_cents("-1")

if __name__ == "__main__":
    unittest.main()
