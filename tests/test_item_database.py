import tempfile
import unittest
from pathlib import Path

from item_database import ItemDatabase, search_items, search_product_names


class ItemDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = ItemDatabase(Path(self.temp_dir.name) / "items.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_list_delete_product_and_material(self):
        self.assertTrue(self.database.add_item("material", "Yellow MJ"))
        self.assertTrue(self.database.add_item("product", "Lacquer BG"))
        self.assertEqual([name for _, name in self.database.list_items("material")], ["Yellow MJ"])
        self.assertEqual([name for _, name in self.database.list_items("product")], ["Lacquer BG"])
        item_id, _ = self.database.list_items("material")[0]
        self.database.delete_item(item_id)
        self.assertEqual(self.database.list_items("material"), [])

    def test_duplicate_name_is_case_insensitive(self):
        self.assertTrue(self.database.add_item("material", "Yellow MJ"))
        self.assertFalse(self.database.add_item("material", " yellow   mj "))

    def test_empty_name_is_rejected(self):
        with self.assertRaises(ValueError):
            self.database.add_item("product", "  ")

    def test_fuzzy_substring_tokens_match_in_any_order(self):
        items = [(1, "Yellow MJ"), (2, "Magenta MJ"), (3, "NC TOB Black G02")]
        self.assertEqual(search_items(items, "w mj"), [(1, "Yellow MJ")])
        self.assertEqual(search_items(items, "yell mj"), [(1, "Yellow MJ")])
        self.assertEqual(search_items(items, "llow mj"), [(1, "Yellow MJ")])
        self.assertEqual(search_items(items, "y mj"), [(1, "Yellow MJ")])
        self.assertEqual(search_items(items, "ta mj"), [(2, "Magenta MJ")])

    def test_fuzzy_acronym_query_can_return_multiple_choices(self):
        items = [(1, "Yellow MJ"), (2, "Magenta MJ")]
        self.assertEqual(search_items(items, "ymj"), [(1, "Yellow MJ")])
        self.assertEqual(search_items(items, "mj"), items)

    def test_product_name_search_includes_material_itemlist_entries(self):
        products = [(10, "Lacquer BG")]
        materials = [(20, "Yellow MJ"), (21, "Magenta MJ")]
        self.assertEqual(search_product_names(products, materials, "y mj"), [(20, "Yellow MJ")])
        self.assertEqual(
            search_product_names(products, materials, "mj"),
            [(20, "Yellow MJ"), (21, "Magenta MJ")],
        )

    def test_product_search_prefers_and_deduplicates_product_names(self):
        products = [(10, "Yellow MJ")]
        materials = [(20, "yellow   mj")]
        self.assertEqual(search_product_names(products, materials, "y mj"), [(10, "Yellow MJ")])


if __name__ == "__main__":
    unittest.main()
