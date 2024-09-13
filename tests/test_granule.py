import inspect
import os
from datetime import datetime, timezone, timedelta
import json
from vcr.unittest import VCRTestCase

from cmr.queries import GranuleQuery


class TestGranuleClass(VCRTestCase):  # type: ignore
    short_name_val = "MOD09GA"
    short_name = "short_name"

    version_val = "006"
    version = "version"

    point = "point"
    circle = "circle"
    online_only = "online_only"
    downloadable = "downloadable"
    entry_id = "entry_title"
    orbit_number = "orbit_number"
    day_night_flag = "day_night_flag"
    cloud_cover = "cloud_cover"
    instrument = "instrument"
    platform = "platform"
    granule_ur = "granule_ur"
    readable_granule_name = "readable_granule_name"

    sort_key = "sort_key"

    def _get_vcr_kwargs(self, **kwargs):
        kwargs['decode_compressed_response'] = True
        return kwargs

    def _get_cassette_library_dir(self):
        testdir = os.path.dirname(inspect.getfile(self.__class__))
        return os.path.join(testdir, "fixtures", "vcr_cassettes")

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
        self.assertEqual(query.params[self.point], ["10.0,15.1"])

    def test_points_set(self):
        query = GranuleQuery()

        query.point(10, 15.1).point(20.4, 10.2)

        self.assertIn(self.point, query.params)
        self.assertEqual(query.params[self.point], ["10.0,15.1", "20.4,10.2"])

    def test_point_invalid_set(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.point("invalid", 15.1)

        with self.assertRaises(TypeError):
            print(query.point(10, None))  # type: ignore[arg-type]

    def test_circle_set(self):
        query = GranuleQuery()

        query.circle(10.0, 15.1, 1000)

        self.assertIn(self.circle, query.params)
        self.assertEqual(query.params[self.circle], "10.0,15.1,1000")

    def test_revision_date(self):
        query = GranuleQuery()
        granules = query.short_name("SWOT_L2_HR_RiverSP_reach_2.0").revision_date("2024-07-05", "2024-07-05").format(
            "umm_json").get_all()
        granule_dict = {}
        for granule in granules:
            granule_json = json.loads(granule)
            for item in granule_json["items"]:
                native_id = item["meta"]["native-id"]
                granule_dict[native_id] = item

        self.assertIn("SWOT_L2_HR_RiverSP_Reach_017_312_AS_20240630T042656_20240630T042706_PIC0_01_swot",
                      granule_dict.keys())
        self.assertIn("SWOT_L2_HR_RiverSP_Reach_017_310_SI_20240630T023426_20240630T023433_PIC0_01_swot",
                      granule_dict.keys())
        self.assertIn("SWOT_L2_HR_RiverSP_Reach_017_333_EU_20240630T225156_20240630T225203_PIC0_01_swot",
                      granule_dict.keys())

    def test_temporal_invalid_strings(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.temporal("abc", "2016-10-20T01:02:03Z")

        with self.assertRaises(ValueError):
            query.temporal("2016-10-20T01:02:03Z", "abc")

    def test_temporal_invalid_types(self):
        query = GranuleQuery()

        with self.assertRaises(TypeError):
            query.temporal(1, None)  # type: ignore[arg-type]

    def test_temporal_invalid_date_order(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.temporal(datetime(2016, 10, 12, 10, 55, 7), datetime(2016, 10, 12, 9))

    def test_temporal_rounding(self):
        query = GranuleQuery()

        # one whole year
        query.temporal("2016", "2016")
        self.assertIn("temporal", query.params)
        self.assertEqual(query.params["temporal"][0], "2016-01-01T00:00:00Z,2016-12-31T23:59:59Z")

        # one whole month
        query.temporal("2016-10", "2016-10")
        self.assertEqual(query.params["temporal"][1], "2016-10-01T00:00:00Z,2016-10-31T23:59:59Z")

        # one whole day, wrong way
        query.temporal("2016-10-10", datetime(2016, 10, 10))
        self.assertNotEqual(query.params["temporal"][2], "2016-10-10T00:00:00Z,2016-10-10T23:59:59Z")

        # one whole day, right way
        query.temporal("2016-10-10", datetime(2016, 10, 10).date())
        self.assertEqual(query.params["temporal"][3], "2016-10-10T00:00:00Z,2016-10-10T23:59:59Z")

    def test_temporal_tz_aware(self):
        query = GranuleQuery()

        tz = timezone(timedelta(hours=-3))
        query.temporal("2016-10-10T00:02:01-03:00", datetime(2016, 10, 10, 0, 2, 1, tzinfo=tz))
        self.assertIn("temporal", query.params)
        self.assertEqual(query.params["temporal"][0], "2016-10-10T03:02:01Z,2016-10-10T03:02:01Z")

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
            query.online_only("Invalid Type")  # type: ignore[arg-type]

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
            query.downloadable("Invalid Type")  # type: ignore[arg-type]
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
            query.day_night_flag("invaliddaynight")  # type: ignore[arg-type]
        self.assertNotIn(self.day_night_flag, query.params)

    def test_day_night_flag_invalid_type_set(self):
        query = GranuleQuery()

        with self.assertRaises(TypeError):
            query.day_night_flag(True)  # type: ignore[arg-type]
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
            query.instrument(None)  # type: ignore[arg-type]

    def test_platform(self):
        query = GranuleQuery()

        query.platform("1B")

        self.assertIn(self.platform, query.params)
        self.assertEqual(query.params[self.platform], "1B")

    def test_sort_key(self):
        query = GranuleQuery()
        # Various sort keys using this as an example
        query.sort_key("-start_date")

        self.assertIn(self.sort_key, query.params)
        self.assertEqual(query.params[self.sort_key], "-start_date")

    def test_sort_key_none(self):
        query = GranuleQuery()
        with self.assertRaises(ValueError):
            query.sort_key(None)  # type: ignore[arg-type]

    def test_empty_platform(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.platform(None)  # type: ignore[arg-type]

    def test_granule_ur(self):
        query = GranuleQuery()

        query.granule_ur("1B")

        self.assertIn(self.granule_ur, query.params)
        self.assertEqual(query.params[self.granule_ur], "1B")

    def test_empty_granule_ur(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.granule_ur(None)  # type: ignore[arg-type]

    def test_polygon_invalid_set(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.polygon([1, 2, 3])  # type: ignore[list-item]

        with self.assertRaises(ValueError):
            query.polygon([("invalid", 1)])

        with self.assertRaises(ValueError):
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
            query.line("invalid")  # type: ignore[arg-type]
            query.line([(1, 1)])
            query.line(1)  # type: ignore[arg-type]

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

        query.circle(1, 2, 3)
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

    def test_stac_output(self):
        """ Test real query with STAC output type """
        # HLSL30: https://cmr.earthdata.nasa.gov/search/concepts/C2021957657-LPCLOUD
        query = GranuleQuery()
        search = query.parameters(point=(-105.78, 35.79),
                                  temporal=('2021-02-01', '2021-03-01'),
                                  collection_concept_id='C2021957657-LPCLOUD'
                                  )
        results = search.format("stac").get()
        feature_collection = json.loads(results[0])

        self.assertEqual(len(results), 1)
        self.assertEqual(feature_collection['type'], 'FeatureCollection')
        self.assertEqual(feature_collection['numberMatched'], 2)
        self.assertEqual(len(feature_collection['features']), 2)

    def _test_hits(self):
        """ integration test for hits() """

        query = GranuleQuery()
        query.short_name("AST_L1T").version("003").temporal("2016-10-26T01:30:00Z", "2016-10-26T01:40:00Z")
        hits = query.hits()

        self.assertEqual(hits, 3)

    def test_invalid_mode(self):
        query = GranuleQuery()

        with self.assertRaises(ValueError):
            query.mode(None)  # type: ignore[arg-type]

    def test_invalid_mode_constructor(self):
        with self.assertRaises(ValueError):
            GranuleQuery(None)  # type: ignore[arg-type]

    def test_valid_parameters(self):
        query = GranuleQuery()

        query.parameters(short_name="AST_L1T", version="003", point=(-100, 42))

        self.assertEqual(query.params["short_name"], "AST_L1T")
        self.assertEqual(query.params["version"], "003")
        self.assertEqual(query.params["point"], ["-100.0,42.0"])

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

        # ensure True is not found with parameters that add to options
        query.parameters(readable_granule_name="A")
        url = query._build_url()
        self.assertNotIn("True", url)

    def test_valid_concept_id(self):
        query = GranuleQuery()

        query.concept_id("C1299783579-LPDAAC_ECS")
        self.assertEqual(query.params["concept_id"], ["C1299783579-LPDAAC_ECS"])

        query.concept_id(["C1299783579-LPDAAC_ECS", "G1441380236-PODAAC"])
        self.assertEqual(query.params["concept_id"], ["C1299783579-LPDAAC_ECS", "G1441380236-PODAAC"])

    def test_token(self):
        query = GranuleQuery()

        query.token("123TOKEN")
        self.assertIn("Authorization", query.headers)
        self.assertEqual(query.headers["Authorization"], "123TOKEN")

    def bearer_test_token(self):
        query = GranuleQuery()

        query.bearer_token("123TOKEN")

        self.assertIn("Authorization", query.headers)
        self.assertEqual(query.headers["Authorization"], "Bearer 123TOKEN")

    def test_readable_granule_name(self):
        query = GranuleQuery()

        query.readable_granule_name("*a*")
        self.assertEqual(query.params[self.readable_granule_name], ["*a*"])
        self.assertIn("pattern", query.options["readable_granule_name"])
        self.assertEqual(query.options["readable_granule_name"]["pattern"], True)

        query.readable_granule_name(["*a*", "*b*"])
        self.assertEqual(query.params[self.readable_granule_name], ["*a*", "*b*"])
