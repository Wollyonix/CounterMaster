import unittest

from printout_formatter import build_pail_printout, build_printout


class PrintoutFormatterTests(unittest.TestCase):
    def test_formats_product_and_material_rows(self):
        report = build_printout(
            "lacquer bg",
            [
                ("lacquer sp", "230,831"),
                ("yellow mj", "53,408"),
                ("50 medium", "270,873"),
                ("magenta mj", "5,888"),
            ],
        )
        self.assertEqual(
            report,
            "Lacquer bg:\n\nLacquer sp 230,831\nYellow mj 53,408\n50 medium 270,873\nMagenta mj 5,888",
        )

    def test_skips_incomplete_or_invalid_material_rows(self):
        report = build_printout("Sample", [("Material A", "1.25"), ("", "3"), ("Material B", "bad")])
        self.assertEqual(report, "Sample:\n\nMaterial A 1,25")

    def test_product_can_be_empty(self):
        report = build_printout("", [("Material A", "2")])
        self.assertEqual(report, "Material A 2")

    def test_formats_pail_output_from_requested_example(self):
        report = build_pail_printout(
            "pr",
            [
                ("lacquer sp", "230,831"),
                ("yellow mj", "53,408"),
                ("50 medium", "270,873"),
                ("magenta mj", "5,888"),
            ],
        )
        self.assertEqual(
            report,
            "pr:\n\nlacquer sp 15 pail\nyellow mj 3 pail\n50 medium 18 pail\nmagenta mj 1 pail",
        )

    def test_positive_quantity_below_15_kg_is_one_pail(self):
        self.assertEqual(build_pail_printout("", [("Material A", "14,999")]), "Material A 1 pail")

    def test_zero_quantity_is_zero_pails(self):
        self.assertEqual(build_pail_printout("", [("Material A", "0")]), "Material A 0 pail")


if __name__ == "__main__":
    unittest.main()
