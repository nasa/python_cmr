import unittest

from datetime import datetime
from cmr.queries import GranuleQuery, CMR_OPS

class TestGranuleClass(unittest.TestCase):

    short_name_val = "MOD09GA"
    short_name = "short_name"

    version_val = "006"
    version = "version"

    point = "point"
    online_only = "online_only"
    downloadable = "downloadable"
    entry_id = "entry_title"
    orbit_number = "orbit_number"
    day_night_flag = "day_night_flag"
    cloud_cover = "cloud_cover"
    instrument = "instrument"
    platform = "platform"
    granule_ur = "granule_ur"

    def test_short_name(self):
        query = GranuleQuery()
        query.short_name(self.short_name_val)

        self.assertIn(self.short_name, query.params)
        self.assertEqual(query.params[self.short_name], self.short_name_val)

    def test_version(self):
        query = GranuleQuery()
        query.version(self.version_val)

        self.assertIn(self.version, query.params)
        self.assertEqual(query.params[self.version], self.version_val)

    def test_point_set(self):
        query = GranuleQuery()

        query.point(10, 15.1)

        self.assertIn(self.point, query.params)
        self.assertEqual(query.params[self.point], "10.0,15.1")

    def test_point_invalid_set(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.point("invalid", 15.1)
            query.point(10, None)

    def test_temporal_invalid_strings(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.temporal("2016", "2016-10-20T01:02:03Z")
            query.temporal("2016-10-20T01:02:03Z", "2016")

    def test_temporal_invalid_types(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.temporal(1, 2)
            query.temporal(None, None)

    def test_temporal_invalid_date_order(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.temporal(datetime(2016, 10, 12, 10, 55, 7), datetime(2016, 10, 12, 9))

    def test_temporal_set(self):
        query = GranuleQuery()

        # both strings
        query.temporal("2016-10-10T01:02:03Z", "2016-10-12T09:08:07Z")
        self.assertIn("temporal", query.params)
        self.assertEqual(query.params["temporal"][0], "2016-10-10T01:02:03Z,2016-10-12T09:08:07Z")

        # string and datetime
        query.temporal("2016-10-10T01:02:03Z", datetime(2016, 10, 12, 9))
        self.assertIn("temporal", query.params)
        self.assertEqual(query.params["temporal"][1], "2016-10-10T01:02:03Z,2016-10-12T09:00:00Z")

        # string and None
        query.temporal(datetime(2016, 10, 12, 10, 55, 7), None)
        self.assertIn("temporal", query.params)
        self.assertEqual(query.params["temporal"][2], "2016-10-12T10:55:07Z,")

        # both datetimes
        query.temporal(datetime(2016, 10, 12, 10, 55, 7), datetime(2016, 10, 12, 11))
        self.assertIn("temporal", query.params)
        self.assertEqual(query.params["temporal"][3], "2016-10-12T10:55:07Z,2016-10-12T11:00:00Z")

    def test_temporal_option_set(self):
        query = GranuleQuery()

        query.temporal("2016-10-10T01:02:03Z", "2016-10-12T09:08:07Z", exclude_boundary=True)
        self.assertIn("exclude_boundary", query.options["temporal"])
        self.assertEqual(query.options["temporal"]["exclude_boundary"], True)

    def test_online_only_set(self):
        query = GranuleQuery()

        # default to True
        query.online_only()
        self.assertIn(self.online_only, query.params)
        self.assertEqual(query.params[self.online_only], True)

        # explicitly set to False
        query.online_only(False)

        self.assertIn(self.online_only, query.params)
        self.assertEqual(query.params[self.online_only], False)

    def test_online_only_invalid(self):
        query = GranuleQuery()

        with self.assertRaises(TypeError):
            query.online_only("Invalid Type")

        self.assertNotIn(self.online_only, query.params)

    def test_downloadable_set(self):
        query = GranuleQuery()

        # default to True
        query.downloadable()

        self.assertIn(self.downloadable, query.params)
        self.assertEqual(query.params[self.downloadable], True)

        # explicitly set to False
        query.downloadable(False)

        self.assertIn(self.downloadable, query.params)
        self.assertEqual(query.params[self.downloadable], False)

    def test_downloadable_invalid(self):
        query = GranuleQuery()

        with self.assertRaises(TypeError):
            query.downloadable("Invalid Type")
        self.assertNotIn(self.downloadable, query.params)
    
    def test_flags_invalidate_the_other(self):
        query = GranuleQuery()

        # if downloadable is set, online_only should be unset
        query.downloadable()
        self.assertIn(self.downloadable, query.params)
        self.assertNotIn(self.online_only, query.params)

        # if online_only is set, downloadable should be unset
        query.online_only()
        self.assertIn(self.online_only, query.params)
        self.assertNotIn(self.downloadable, query.params)

    def test_entry_title_set(self):
        query = GranuleQuery()
        query.entry_title("DatasetId 5")

        self.assertIn(self.entry_id, query.params)
        self.assertEqual(query.params[self.entry_id], "DatasetId%205")

    def test_orbit_number_set(self):
        query = GranuleQuery()
        query.orbit_number(985)

        self.assertIn(self.orbit_number, query.params)
        self.assertEqual(query.params[self.orbit_number], 985)

    def test_orbit_number_encode(self):
        query = GranuleQuery()
        query.orbit_number("985", "986")

        self.assertIn(self.orbit_number, query.params)
        self.assertEqual(query.params[self.orbit_number], "985%2C986")

    def test_day_night_flag_day_set(self):
        query = GranuleQuery()
        query.day_night_flag('day')

        self.assertIn(self.day_night_flag, query.params)
        self.assertEqual(query.params[self.day_night_flag], 'day')

    def test_day_night_flag_night_set(self):
        query = GranuleQuery()
        query.day_night_flag('night')

        self.assertIn(self.day_night_flag, query.params)
        self.assertEqual(query.params[self.day_night_flag], 'night')

    def test_day_night_flag_unspecified_set(self):
        query = GranuleQuery()
        query.day_night_flag('unspecified')

        self.assertIn(self.day_night_flag, query.params)
        self.assertEqual(query.params[self.day_night_flag], 'unspecified')

    def test_day_night_flag_invalid_set(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.day_night_flag('invaliddaynight')
        self.assertNotIn(self.day_night_flag, query.params)

    def test_day_night_flag_invalid_type_set(self):
        query = GranuleQuery()

        with self.assertRaises(TypeError):
            query.day_night_flag(True)
        self.assertNotIn(self.day_night_flag, query.params)

    def test_cloud_cover_min_only(self):
        query = GranuleQuery()
        query.cloud_cover(-70)

        self.assertIn(self.cloud_cover, query.params)
        self.assertEqual(query.params[self.cloud_cover], "-70,100")

    def test_cloud_cover_max_only(self):
        query = GranuleQuery()
        query.cloud_cover("", 120)

        self.assertIn(self.cloud_cover, query.params)
        self.assertEqual(query.params[self.cloud_cover], ",120")

    def test_cloud_cover_all(self):
        query = GranuleQuery()
        query.cloud_cover(-70, 120)

        self.assertIn(self.cloud_cover, query.params)
        self.assertEqual(query.params[self.cloud_cover], "-70,120")

    def test_cloud_cover_none(self):
        query = GranuleQuery()
        query.cloud_cover()

        self.assertIn(self.cloud_cover, query.params)
        self.assertEqual(query.params[self.cloud_cover], "0,100")

    def test_instrument(self):
        query = GranuleQuery()

        query.instrument("1B")

        self.assertIn(self.instrument, query.params)
        self.assertEqual(query.params[self.instrument], "1B")

    def test_empty_instrument(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.instrument(None)

    def test_platform(self):
        query = GranuleQuery()

        query.platform("1B")

        self.assertIn(self.platform, query.params)
        self.assertEqual(query.params[self.platform], "1B")

    def test_empty_platform(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.platform(None)

    def test_granule_ur(self):
        query = GranuleQuery()

        query.granule_ur("1B")

        self.assertIn(self.granule_ur, query.params)
        self.assertEqual(query.params[self.granule_ur], "1B")

    def test_empty_granule_ur(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.granule_ur(None)

    def test_polygon_invalid_set(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.polygon([1, 2, 3])
            query.polygon([("invalid", 1)])
            query.polygon([(1, 1), (2, 1), (1, 1)])

    def test_polygon_set(self):
        query = GranuleQuery()

        query.polygon([(1, 1), (2, 1), (2, 2), (1, 1)])
        self.assertEqual(query.params["polygon"], "1.0,1.0,2.0,1.0,2.0,2.0,1.0,1.0")

        query.polygon([("1", 1.1), (2, 1), (2, 2), (1, 1.1)])
        self.assertEqual(query.params["polygon"], "1.0,1.1,2.0,1.0,2.0,2.0,1.0,1.1")

    def test_bounding_box_invalid_set(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.bounding_box(1, 2, 3, "invalid")

    def test_bounding_box_set(self):
        query = GranuleQuery()

        query.bounding_box(1, 2, 3, 4)
        self.assertEqual(query.params["bounding_box"], "1.0,2.0,3.0,4.0")

    def test_line_invalid_set(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.line("invalid")
            query.line([(1, 1)])
            query.line(1)

    def test_line_set(self):
        query = GranuleQuery()

        query.line([(1, 1), (2, 2)])
        self.assertEqual(query.params["line"], "1.0,1.0,2.0,2.0")

        query.line([("1", 1.1), (2, 2)])
        self.assertEqual(query.params["line"], "1.0,1.1,2.0,2.0")

    def test_invalid_spatial_state(self):
        query = GranuleQuery()

        query.point(1, 2)
        self.assertFalse(query._valid_state())

        query.polygon([(1, 1), (2, 1), (2, 2), (1, 1)])
        self.assertFalse(query._valid_state())

        query.bounding_box(1, 1, 2, 2)
        self.assertFalse(query._valid_state())

        query.line([(1, 1), (2, 2)])
        self.assertFalse(query._valid_state())

    def test_valid_spatial_state(self):
        query = GranuleQuery()

        query.point(1, 2).short_name("test")
        self.assertTrue(query._valid_state())

    def _test_get(self):
        """ Test real query """

        query = GranuleQuery()
        query.short_name('MCD43A4').version('005')
        query.temporal(datetime(2016, 1, 1), datetime(2016, 1, 1))
        results = query.get(limit=10)

        self.assertEqual(len(results), 10)
    
    def _test_hits(self):
        """ integration test for hits() """

        query = GranuleQuery()
        query.short_name("AST_L1T").version("003").temporal("2016-10-26T01:30:00Z", "2016-10-26T01:40:00Z")
        hits = query.hits()

        self.assertEqual(hits, 3)

    def test_invalid_mode(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.mode(None)

    def test_invalid_mode_constructor(self):
        with self.assertRaises(ValueError):
            query = GranuleQuery(None)
    
    def test_valid_parameters(self):
        query = GranuleQuery()

        query.parameters(short_name="AST_L1T", version="003", point=(-100, 42))

        self.assertEqual(query.params["short_name"], "AST_L1T")
        self.assertEqual(query.params["version"], "003")
        self.assertEqual(query.params["point"], "-100.0,42.0")
    
    def test_invalid_parameters(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.parameters(fake=123)
            query.parameters(point=(-100, "badvalue"))

    def test_valid_formats(self):
        query = GranuleQuery()
        formats = ["json", "xml", "echo10", "iso", "iso19115", "csv", "atom", "kml", "native"]

        for _format in formats:
            query.format(_format)
            self.assertEqual(query._format, _format)
    
    def test_invalid_format(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.format("invalid")
            query.format("jsonn")
            query.format("iso19116")

    def test_lowercase_bool_url(self):
        query = GranuleQuery()
        query.parameters(short_name="AST_LIT", online_only=True, downloadable=False)

        url = query._build_url()
        self.assertNotIn("True", url)
        self.assertNotIn("False", url)
