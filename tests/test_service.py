import unittest

from cmr.queries import ServiceQuery

class TestServiceClass(unittest.TestCase):

    def test_name(self):
        query = ServiceQuery()
        query.name("name")

        self.assertIn("name", query.params)
        self.assertEqual(query.params["name"], "name")
    
    def test_provider(self):
        query = ServiceQuery()
        query.provider("provider")

        self.assertIn("provider", query.params)
        self.assertEqual(query.params["provider"], "provider")

    def test_native_id(self):
        query = ServiceQuery()
        query.native_id("native_id")

        self.assertIn("native_id", query.params)
        self.assertEqual(query.params["native_id"], ["native_id"])

    def test_native_ids(self):
        query = ServiceQuery()
        query.native_id(["native_id1", "native_id2"])

        self.assertIn("native_id", query.params)
        self.assertEqual(query.params["native_id"], ["native_id1", "native_id2"])
    
    def test_valid_formats(self):
        query = ServiceQuery()
        formats = [
            "json", "xml", "echo10", "iso", "iso19115",
            "csv", "atom", "kml", "native", "dif", "dif10",
            "opendata", "umm_json", "umm_json_v1_1" "umm_json_v1_9"]

        for _format in formats:
            query.format(_format)
            self.assertEqual(query._format, _format)
    
    def test_invalid_format(self):
        query = ServiceQuery()

        with self.assertRaises(ValueError):
            query.format("invalid")
            query.format("jsonn")
            query.format("iso19116")
    
    def test_valid_concept_id(self):
        query = ServiceQuery()

        query.concept_id("S1299783579-LPDAAC_ECS")
        self.assertEqual(query.params["concept_id"], ["S1299783579-LPDAAC_ECS"])
        
        query.concept_id(["S1299783579-LPDAAC_ECS", "S1441380236-PODAAC"])
        self.assertEqual(query.params["concept_id"], ["S1299783579-LPDAAC_ECS", "S1441380236-PODAAC"])
    
    def test_invalid_concept_id(self):
        query = ServiceQuery()

        with self.assertRaises(ValueError):
            query.concept_id("G1327299284-LPDAAC_ECS")
        
        with self.assertRaises(ValueError):
            query.concept_id(["C1299783579-LPDAAC_ECS", "G1327299284-LPDAAC_ECS"])

