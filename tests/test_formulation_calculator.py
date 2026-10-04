import unittest
from decimal import Decimal

from formulation_calculator import calculate_formulation


class FormulationCalculatorTests(unittest.TestCase):
    def setUp(self):
        self.gramasi = [156, 60, 34, 10, 40]

    def test_scales_formula_to_27_kg(self):
        rows, total_gramasi = calculate_formulation(self.gramasi, 27)
        self.assertEqual(total_gramasi, Decimal("300"))
        self.assertEqual([row.percentage.quantize(Decimal("0.01")) for row in rows], [
            Decimal("52.00"), Decimal("20.00"), Decimal("11.33"), Decimal("3.33"), Decimal("13.33")
        ])
        self.assertEqual([row.quantity_kg.quantize(Decimal("0.001")) for row in rows], [
            Decimal("14.040"), Decimal("5.400"), Decimal("3.060"), Decimal("0.900"), Decimal("3.600")
        ])
        self.assertEqual(sum((row.quantity_kg for row in rows), Decimal("0")), Decimal("27"))

    def test_scales_formula_to_15_kg(self):
        rows, _ = calculate_formulation(self.gramasi, 15)
        self.assertEqual([row.quantity_kg for row in rows], [
            Decimal("7.80"), Decimal("3.00"), Decimal("1.70"), Decimal("0.50"), Decimal("2.00")
        ])

    def test_accepts_comma_decimal(self):
        rows, _ = calculate_formulation(["1,5", "2,5"], "10,0")
        self.assertEqual([row.percentage for row in rows], [Decimal("37.5"), Decimal("62.5")])
        self.assertEqual([row.quantity_kg for row in rows], [Decimal("3.750"), Decimal("6.250")])

    def test_rejects_zero_gramasi(self):
        with self.assertRaises(ValueError):
            calculate_formulation([10, 0], 5)

    def test_rejects_empty_rows(self):
        with self.assertRaises(ValueError):
            calculate_formulation([], 5)

    def test_rejects_zero_total(self):
        with self.assertRaises(ValueError):
            calculate_formulation([10], 0)

if __name__ == "__main__":
    unittest.main()
