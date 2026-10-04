import unittest
from decimal import Decimal

from pail_calculator import calculate_pails, calculate_total, parse_quantity


class PailCalculatorTests(unittest.TestCase):
    def test_exact_pail_multiple_does_not_round_up_extra(self):
        result = calculate_pails("30")
        self.assertEqual(result.equivalent_pails, Decimal("2"))
        self.assertEqual(result.whole_pails, 2)

    def test_fraction_below_half_rounds_down(self):
        result = calculate_pails("63.45")
        self.assertEqual(result.whole_pails, 4)

    def test_fraction_above_half_rounds_up(self):
        result = calculate_pails("70.5")
        self.assertEqual(result.whole_pails, 5)

    def test_exact_half_rounds_up(self):
        result = calculate_pails("67.5")
        self.assertEqual(result.whole_pails, 5)

    def test_fractional_quantity(self):
        result = calculate_pails("7,5")
        self.assertEqual(result.quantity_kg, Decimal("7.5"))
        self.assertEqual(result.equivalent_pails, Decimal("0.5"))
        self.assertEqual(result.whole_pails, 1)

    def test_zero_kg_needs_zero_pails(self):
        self.assertEqual(calculate_pails("0").whole_pails, 0)

    def test_total_from_example_is_300_kg(self):
        total = calculate_total([156, 60, 34, 10, 40])
        self.assertEqual(total.quantity_kg, Decimal("300"))
        self.assertEqual(total.equivalent_pails, Decimal("20"))
        self.assertEqual(total.whole_pails, 20)

    def test_material_pails_are_rounded_individually(self):
        quantities = [156, 60, 34, 10, 40]
        self.assertEqual(sum(calculate_pails(q).whole_pails for q in quantities), 20)

    def test_rejects_negative_quantity(self):
        with self.assertRaises(ValueError):
            calculate_pails("-0.1")

    def test_rejects_invalid_quantity(self):
        with self.assertRaises(ValueError):
            calculate_pails("abc")

    def test_rejects_empty_quantity(self):
        with self.assertRaises(ValueError):
            parse_quantity("  ")


if __name__ == "__main__":
    unittest.main()
