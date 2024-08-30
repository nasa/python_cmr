import inspect
import os
from vcr.unittest import VCRTestCase

from cmr.queries import CollectionQuery


class TestCollectionClass(VCRTestCase):  # type: ignore

    def _get_vcr_kwargs(self, **kwargs):
        kwargs['decode_compressed_response'] = True
        return kwargs

    def _get_cassette_library_dir(self):
        testdir = os.path.dirname(inspect.getfile(self.__class__))
        return os.path.join(testdir, "fixtures", "vcr_cassettes")

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

    def test_token(self):
        query = CollectionQuery()

        query.token("123TOKEN")

        self.assertIn("Authorization", query.headers)
        self.assertEqual(query.headers["Authorization"], "123TOKEN")

    def bearer_test_token(self):
        query = CollectionQuery()

        query.bearer_token("123TOKEN")

        self.assertIn("Authorization", query.headers)
        self.assertEqual(query.headers["Authorization"], "Bearer 123TOKEN")

    def test_cloud_hosted(self):
        query = CollectionQuery()
        query.cloud_hosted(True)

        self.assertIn("cloud_hosted", query.params)
        self.assertEqual(query.params["cloud_hosted"], True)

    def test_invalid_cloud_hosted(self):
        query = CollectionQuery()

        with self.assertRaises(TypeError):
            query.cloud_hosted("Test_string_for_cloud_hosted_param")  # type: ignore[arg-type]

    def test_platform(self):
        query = CollectionQuery()

        query.platform("1B")

        self.assertIn("platform", query.params)
        self.assertEqual(query.params["platform"], "1B")

    def test_empty_platform(self):
        query = CollectionQuery()

        with self.assertRaises(ValueError):
            query.platform(None)  # type: ignore[arg-type]

    def test_revision_date(self):
        query = CollectionQuery()
        collections = query.short_name("SWOT_L2_HR_RiverSP_reach_2.0").revision_date("2022-05-16", "2024-06-30").get_all()
        self.assertEqual(collections[0]["dataset_id"], "SWOT Level 2 River Single-Pass Vector Reach Data Product, Version 2.0")
