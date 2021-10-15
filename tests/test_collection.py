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
    
    def test_tool_concept_id(self):
        query = CollectionQuery()
        query.tool_concept_id("T1299783579-LPDAAC_ECS")

        self.assertIn("tool_concept_id", query.params)
        self.assertEqual(query.params["tool_concept_id"], ["T1299783579-LPDAAC_ECS"])

    def test_invalid_tool_concept_id(self):
        query = CollectionQuery()

        with self.assertRaises(ValueError):
            query.tool_concept_id("G1327299284-LPDAAC_ECS")

    def test_service_concept_id(self):
        query = CollectionQuery()
 
        query.service_concept_id("S1299783579-LPDAAC_ECS")

        self.assertIn("service_concept_id", query.params)
        self.assertEqual(query.params["service_concept_id"], ["S1299783579-LPDAAC_ECS"])

    def test_invalid_service_concept_id(self):
        query = CollectionQuery()

        with self.assertRaises(ValueError):
            query.service_concept_id("G1327299284-LPDAAC_ECS")    

    def test_valid_concept_id(self):
        query = CollectionQuery()

        query.concept_id("C1299783579-LPDAAC_ECS")
        self.assertEqual(query.params["concept_id"], ["C1299783579-LPDAAC_ECS"])
        
        query.concept_id(["C1299783579-LPDAAC_ECS", "C1441380236-PODAAC"])
        self.assertEqual(query.params["concept_id"], ["C1299783579-LPDAAC_ECS", "C1441380236-PODAAC"])
    
    def test_invalid_concept_id(self):
        query = CollectionQuery()

        with self.assertRaises(ValueError):
            query.concept_id("G1327299284-LPDAAC_ECS")
        
        with self.assertRaises(ValueError):
            query.concept_id(["C1299783579-LPDAAC_ECS", "G1327299284-LPDAAC_ECS"])
