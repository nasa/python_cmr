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
