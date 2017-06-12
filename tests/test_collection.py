import unittest

from cmr.queries import CollectionQuery

class TestCollectionClass(unittest.TestCase):

    def test_archive_center(self):
        query = CollectionQuery()
        query.archive_center("LP DAAC")

        self.assertIn("archive_center", query.params)
        self.assertEqual(query.params["archive_center"], "LP DAAC")
    
    def test_keyword(self):
        query = CollectionQuery()
        query.keyword("AST_*")

        self.assertIn("keyword", query.params)
        self.assertEqual(query.params["keyword"], "AST_*")
    
    def test_valid_formats(self):
        query = CollectionQuery()
        formats = [
            "json", "xml", "echo10", "iso", "iso19115",
            "csv", "atom", "kml", "native", "dif", "dif10",
            "opendata", "umm_json", "umm_json_v1_1" "umm_json_v1_9"]

        for _format in formats:
            query.format(_format)
            self.assertEqual(query._format, _format)
    
    def test_invalid_format(self):
        query = CollectionQuery()

        with self.assertRaises(ValueError):
            query.format("invalid")
            query.format("jsonn")
            query.format("iso19116")
