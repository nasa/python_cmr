import unittest
from datetime import datetime

import vcr

from cmr.queries import GranuleQuery

my_vcr = vcr.VCR(
    record_mode='once',
    decode_compressed_response=True,
    # Header matching is not set by default, we need that to test the
    # search-after functionality is performing correctly.
    match_on=['method', 'scheme', 'host', 'port', 'path', 'query', 'headers']
)


def assert_unique_granules_from_results(granules):
    """
    When we invoke a search request multiple times we want to ensure that we don't
    get the same results back. This is a one shot test as the results are preserved
    by VCR but still useful.
    """
    granule_ids = []
    for granule in granules:
        granule_ids.append(granule['title'])

    unique_granules = set(granule_ids)
    return len(unique_granules) == len(granule_ids)


class TestMultipleQueries(unittest.TestCase):

    def test_get_more_than_2000(self):
        """
        If we execute a get with a limit of more than 2000
        then we expect multiple invocations of a cmr granule search and
        to not fetch back more results than we ask for
        """
        with my_vcr.use_cassette('tests/fixtures/vcr_cassettes/MOD02QKM.yaml') as cass:
            api = GranuleQuery()

            granules = api.short_name("MOD02QKM").get(3000)
            self.assertEqual(3000, len(granules))
            # Assert all 3000 qranule results have unique granule ids
            assert_unique_granules_from_results(granules)
            # Assert that we performed two search results queries
            self.assertEqual(2, len(cass))
            self.assertIsNone(api.headers.get('cmr-search-after'))

    def test_get(self):
        """
        If we execute a get with no arguments then we expect
        to get the maximum no. of granules from a single CMR call (2000)
        in a single request
        """
        with my_vcr.use_cassette('tests/fixtures/vcr_cassettes/MOD02QKM_2000.yaml') as cass:
            api = GranuleQuery()
            granules = api.short_name("MOD02QKM").get()
            self.assertEqual(2000, len(granules))
            # Assert all 2000 qranule results have unique granule ids
            assert_unique_granules_from_results(granules)
            # Assert that we performed one search results query
            self.assertEqual(1, len(cass))
            self.assertIsNone(api.headers.get('cmr-search-after'))

    def test_get_all_less_than_2k(self):
        """
        If we execute a get_all then we expect multiple
        invocations of a cmr granule search and
        to not fetch back more results than we ask for
        """
        with my_vcr.use_cassette('tests/fixtures/vcr_cassettes/TELLUS_GRAC.yaml') as cass:
            api = GranuleQuery()
            granules = api.short_name("TELLUS_GRAC_L3_JPL_RL06_LND_v04").get_all()
            self.assertEqual(163, len(granules))
            # Assert all 163 qranule results have unique granule ids
            assert_unique_granules_from_results(granules)
            # Assert that we performed a hits query and one search results query
            self.assertEqual(2, len(cass))
            self.assertIsNone(api.headers.get('cmr-search-after'))

    def test_get_all_more_than_2k(self):
        """
        If we execute a get_all then we expect multiple
        invocations of a cmr granule search and
        to not fetch back more results than we ask for
        """
        with my_vcr.use_cassette('tests/fixtures/vcr_cassettes/CYGNSS.yaml') as cass:
            api = GranuleQuery()
            granules = api.short_name("CYGNSS_NOAA_L2_SWSP_25KM_V1.2").get_all()
            self.assertEqual(2285, len(granules))
            # Assert all 2285 qranule results have unique granule ids
            assert_unique_granules_from_results(granules)
            # Assert that we performed a hits query and two search results queries
            self.assertEqual(3, len(cass))
            self.assertIsNone(api.headers.get('cmr-search-after'))

    def test_zero_hits_query(self):
        """
        If we execute a get that has zero
        hits, cmr-search-after is not sent in
        the response headers
        """
        with my_vcr.use_cassette('tests/fixtures/vcr_cassettes/MOD09GA061_nohits.yaml'):
            api = GranuleQuery()
            granules = (
                api.short_name("MOD09GA")
                .version("061")
                .temporal(datetime(1990, 1, 1), datetime(1990, 1, 2))
                .get()
            )
            self.assertEqual(0, len(granules))
            self.assertIsNone(api.headers.get('cmr-search-after'))
