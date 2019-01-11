from unittest import TestCase

from db.heat_handler import SQLHeatHandler


class TestSQLHeatHandler(TestCase):
    def test_get_most_popular_entity_id_list(self):
        handler = SQLHeatHandler()
        result_list = handler.get_most_popular_entity_id_list()
        print(result_list)
        self.assertIsNotNone(result_list)
        self.assertEqual(len(result_list), 10)

    def test_get_api_heat_by_apiID(self):
        handler = SQLHeatHandler()
        result = handler.get_api_heat_by_apiID(10)
        print(result)
