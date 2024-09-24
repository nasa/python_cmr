import inspect
import json
import os
from datetime import datetime
from itertools import islice

from typing_extensions import Any, Sequence
from vcr.unittest import VCRTestCase

from cmr.queries import GranuleQuery


def assert_unique_granules_from_results(granules: Sequence[Any]) -> bool:
    """
    When we invoke a search request multiple times we want to ensure that we don't
    get the same results back. This is a one shot test as the results are preserved
    by VCR but still useful.
    """
    return len(granules) == len({str(granule) for granule in granules})


class TestMultipleQueries(VCRTestCase):  # type: ignore

    def _get_vcr_kwargs(self, **kwargs):
        kwargs['decode_compressed_response'] = True
        kwargs['match_on'] = ["method", "scheme", "host", "port", "path", "query", "headers"]
        kwargs['filter_headers'] = ["user-agent"]
        return kwargs

    def _get_cassette_library_dir(self):
        testdir = os.path.dirname(inspect.getfile(self.__class__))
        return os.path.join(testdir, "fixtures", "vcr_cassettes")

    def test_get_unparsed_format(self):
        """
        If we execute a get with a limit of more than 2000
        then we expect multiple invocations of a cmr granule search and
        to not fetch back more results than we ask for
        """
        api = GranuleQuery().format("umm_json")

        pages = api.short_name("MOD02QKM").get(2)
        granules = [
            granule for page in pages for granule in json.loads(page)["items"]
        ]
        self.assertEqual(2, len(granules))
        assert_unique_granules_from_results(granules)
        # Assert that we performed only 1 search request
        self.assertEqual(1, len(self.cassette))
        self.assertIsNone((api.headers or {}).get("cmr-search-after"))

    def test_results_unparsed_format(self):
        """
        If we execute a get for an unparsed format we expect pages to be returned instead of items
        """
        api = GranuleQuery().format("umm_json")

        pages = list(islice(api.short_name("MOD02QKM").results(page_size=2), 10))
        granules = [
            granule for page in pages for granule in json.loads(page)["items"]
        ]
        self.assertEqual(20, len(granules))
        assert_unique_granules_from_results(granules)
        # Assert that we performed 5 search requests
        self.assertEqual(10, len(self.cassette))
        self.assertIsNone((api.headers or {}).get("cmr-search-after"))

    def test_get_more_than_2000(self):
        """
        If we execute a get with a limit of more than 2000
        then we expect multiple invocations of a cmr granule search and
        to not fetch back more results than we ask for
        """
        api = GranuleQuery()

        granules = api.short_name("MOD02QKM").get(3000)
        self.assertEqual(3000, len(granules))
        assert_unique_granules_from_results(granules)
        # Assert that we performed two search results queries
        self.assertEqual(2, len(self.cassette))
        self.assertIsNone((api.headers or {}).get("cmr-search-after"))

    def test_results_more_than_2000(self):
        """
        If we execute a get with a limit of more than 2000
        then we expect multiple invocations of a cmr granule search and
        to not fetch back more results than we ask for
        """
        api = GranuleQuery()

        granules = list(islice(api.short_name("MOD02QKM").results(page_size=1000), 3000))
        self.assertEqual(3000, len(granules))
        assert_unique_granules_from_results(granules)
        # Assert that we performed 3 search results queries
        self.assertEqual(3, len(self.cassette))
        self.assertIsNone((api.headers or {}).get("cmr-search-after"))

    def test_get(self):
        """
        If we execute a get with no arguments then we expect
        to get the maximum no. of granules from a single CMR call (2000)
        in a single request
        """
        api = GranuleQuery()
        granules = api.short_name("MOD02QKM").get()
        self.assertEqual(2000, len(granules))
        assert_unique_granules_from_results(granules)
        # Assert that we performed 1 search results query
        self.assertEqual(1, len(self.cassette))
        self.assertIsNone((api.headers or {}).get("cmr-search-after"))

    def test_results(self):
        """
        If we execute a get with no arguments then we expect
        to get all results
        """
        api = GranuleQuery()
        granules = list(api.short_name("TELLUS_GRAC_L3_JPL_RL06_LND_v04").results())
        self.assertEqual(163, len(granules))
        assert_unique_granules_from_results(granules)
        # Assert that we performed 2 search results query
        self.assertEqual(2, len(self.cassette))
        self.assertIsNone((api.headers or {}).get("cmr-search-after"))

    def test_get_all_less_than_2k(self):
        """
        If we execute a get_all then we expect multiple
        invocations of a cmr granule search and
        to not fetch back more results than we ask for
        """
        api = GranuleQuery()
        granules = api.short_name("TELLUS_GRAC_L3_JPL_RL06_LND_v04").get_all()
        self.assertEqual(163, len(granules))
        assert_unique_granules_from_results(granules)
        # Assert that we performed a hits query and one search results query
        self.assertEqual(2, len(self.cassette))
        self.assertIsNone((api.headers or {}).get("cmr-search-after"))

    def test_get_all_more_than_2k(self):
        """
        If we execute a get_all then we expect multiple
        invocations of a cmr granule search and
        to not fetch back more results than we ask for
        """
        api = GranuleQuery()
        granules = api.short_name("CYGNSS_NOAA_L2_SWSP_25KM_V1.2").get_all()
        self.assertEqual(2689, len(granules))
        assert_unique_granules_from_results(granules)
        # Assert that we performed a hits query and two search results queries
        self.assertEqual(3, len(self.cassette))
        self.assertIsNone((api.headers or {}).get("cmr-search-after"))

    def test_zero_hits_query(self):
        """
        If we execute a get that has zero
        hits, cmr-search-after is not sent in
        the response headers
        """
        api = GranuleQuery()
        granules = (
            api.short_name("MOD09GA")
            .version("061")
            .temporal(datetime(1990, 1, 1), datetime(1990, 1, 2))
            .get()
        )
        self.assertEqual(0, len(granules))
        self.assertIsNone((api.headers or {}).get("cmr-search-after"))

    def test_zero_hits_query_results(self):
        """
        If we execute a get that has zero
        hits, cmr-search-after is not sent in
        the response headers
        """
        api = GranuleQuery()
        granules = list(
            api.short_name("MOD09GA")
            .version("061")
            .temporal(datetime(1990, 1, 1), datetime(1990, 1, 2))
            .results()
        )
        self.assertEqual(0, len(granules))
        self.assertIsNone((api.headers or {}).get("cmr-search-after"))
