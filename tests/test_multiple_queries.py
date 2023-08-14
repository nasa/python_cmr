import unittest
import requests_mock
import json

import vcr
import urllib.request

from cmr.queries import GranuleQuery

my_vcr = vcr.VCR(
    record_mode='once',
    decode_compressed_response=True,
    match_on=['method', 'scheme', 'host', 'port', 'path', 'query', 'headers']
)

class TestMultipleQueries(unittest.TestCase):

    def test_get_some(self):
        with my_vcr.use_cassette('fixtures/vcr_cassettes/MOD02QKM.yaml') as cass:
            api = GranuleQuery()

            granules = api.short_name("MOD02QKM").get(3000)
            self.assertEqual(len(granules), 3000)
            self.assertEqual(len(cass), 2)
    '''
    def test_get_limit_many(self):
        api = GranuleQuery()
        granules = api.short_name("MOD02QKM").get()
        self.assertEqual(len(granules), 2000)
    
    @vcr.use_cassette('fixtures/vcr_cassettes/MOD02QKM_150.yaml')   
    def test_get_limit_some(self):
        api = GranuleQuery()
        granules = api.short_name("MOD02QKM").get()
        self.assertEqual(len(granules), 150)

    def test_get_all_mutiple_pages(self):
        api = GranuleQuery()
        granules = api.short_name("MOD02QKM").get_all()
        self.assertEqual(len(granules), 3050)
        
    def test_get_all_mutiple_pages(self):
        api = GranuleQuery()
        granules = api.short_name("MOD02QKM").get_all()
        self.assertEqual(len(granules), 3050)'''
