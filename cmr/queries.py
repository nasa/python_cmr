"""
Contains all CMR query types.
"""

try:
    from urllib.parse import quote
except ImportError:
    from urllib import pathname2url as quote

from datetime import datetime
from requests import get, exceptions

class Query(object):
    """
    Base class for all CMR queries.
    """

    base_url = ""

    def __init__(self, base_url):
        self.params = {}
        self.options = {}
        self.base_url = base_url

    def _urlencodestring(self, value):
        """
        Returns a URL-Encoded version of the given value parameter.

        :param value: value to encode
        :returns: the URL encoded version of value
        """

        return quote(value)

    def online_only(self, online_only):
        """
        Only match granules that are listed online and not available for download.
        The opposite of this method is downloadable().

        :param online_only: True to require granules only be online
        :returns: Query instance
        """

        if not isinstance(online_only, bool):
            raise TypeError("Online_only must be of type bool")

        self.params['online_only'] = online_only

        return self

    def temporal(self, date_from, date_to, exclude_boundary=False):
        """
        Filter by an open or closed date range.
        
        Dates can be provided as a datetime objects or ISO 8601 formatted strings. Multiple
        ranges can be provided by successive calls to this method before calling execute().

        :param date_from: earliest date of temporal range
        :param date_to: latest date of temporal range
        :param exclude_boundary: whether or not to exclude the date_from/to in the matched range
        :returns: GranueQuery instance
        """

        iso_8601 = "%Y-%m-%dT%H:%M:%SZ"

        # process each date into a datetime object
        def convert_to_string(date):
            """
            Returns the argument as an ISO 8601 or empty string.
            """

            if not date:
                return ""

            try:
                # see if it's datetime-like
                return date.strftime(iso_8601)
            except AttributeError:
                try:
                    # maybe it already is an ISO 8601 string
                    datetime.strptime(date, iso_8601)
                    return date
                except TypeError:
                    raise ValueError(
                        "Please provide None, datetime objects, or ISO 8601 formatted strings."
                    )

        date_from = convert_to_string(date_from)
        date_to = convert_to_string(date_to)

        # if we have both dates, make sure from isn't later than to
        if date_from and date_to:
            if date_from > date_to:
                raise ValueError("date_from must be earlier than date_to.")

        # good to go, make sure we have a param list
        if "temporal" not in self.params:
            self.params["temporal"] = []

        self.params["temporal"].append("{},{}".format(date_from, date_to))

        if exclude_boundary:
            self.options["temporal"] = {
                "exclude_boundary": True
            }

        return self

    def short_name(self, short_name):
        """
        Filter by short name (aka product or collection name).

        :param short_name: name of collection
        :returns: Query instance
        """

        if not short_name:
            return self

        self.params['short_name'] = short_name
        return self

    def version(self, version):
        """
        Filter by version. Note that CMR defines this as a string. For example,
        MODIS version 6 products must be searched for with "006".

        :param version: version string
        :returns: Query instance
        """

        if not version:
            return self

        self.params['version'] = version
        return self

    def point(self, lon, lat):
        """
        Filter by granules that include a geographic point.

        :param lon: longitude of geographic point
        :param lat: latitude of geographic point
        :returns: Query instance
        """

        if not lat or not lon:
            return self

        # coordinates must be a float
        lon = float(lon)
        lat = float(lat)

        self.params['point'] = "{},{}".format(lon, lat)

        return self

    def polygon(self, coordinates):
        """
        Filter by granules that overlap a polygonal area. Must be used in combination with a
        collection filtering parameter such as short_name or entry_title.

        :param coordinates: list of (lon, lat) tuples
        :returns: Query instance
        """

        if not coordinates:
            return self

        # polygon requires at least 4 pairs of coordinates
        if len(coordinates) < 4:
            raise ValueError("A polygon requires at least 4 pairs of coordinates.")

        # convert to floats
        as_floats = []
        for lon, lat in coordinates:
            as_floats.extend([float(lon), float(lat)])

        # last point must match first point to complete polygon
        if as_floats[0] != as_floats[-2] or as_floats[1] != as_floats[-1]:
            raise ValueError("Coordinates of the last pair must match the first pair.")

        # convert to strings
        as_strs = [str(val) for val in as_floats]

        self.params["polygon"] = ",".join(as_strs)

        return self

    def bounding_box(self, lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat):
        """
        Filter by granules that overlap a bounding box. Must be used in combination with
        a collection filtering parameter such as short_name or entry_title.

        :param lower_left_lon: lower left longitude of the box
        :param lower_left_lat: lower left latitude of the box
        :param upper_right_lon: upper right longitude of the box
        :param upper_right_lat: upper right latitude of the box
        :returns: Query instance
        """

        self.params["bounding_box"] = "{},{},{},{}".format(
            float(lower_left_lon),
            float(lower_left_lat),
            float(upper_right_lon),
            float(upper_right_lat)
        )

        return self

    def line(self, coordinates):
        """
        Filter by granules that overlap a series of connected points. Must be used in combination
        with a collection filtering parameter such as short_name or entry_title.

        :param coordinates: a list of (lon, lat) tuples
        :returns: Query instance
        """

        if not coordinates:
            return self

        # need at least 2 pairs of coordinates
        if len(coordinates) < 2:
            raise ValueError("A line requires at least 2 pairs of coordinates.")

        # make sure they're all floats
        as_floats = []
        for lon, lat in coordinates:
            as_floats.extend([float(lon), float(lat)])

        # cast back to string for join
        as_strs = [str(val) for val in as_floats]

        self.params["line"] = ",".join(as_strs)

        return self

    def downloadable(self, downloadable):
        """
        Only match granules that are available for download. The opposite of this
        method is online_only().

        :param downloadable: True to require granules be downloadable
        :returns: Query instance
        """
        if not isinstance(downloadable, bool):
            raise TypeError("Downloadable must be of type bool")

        self.params['downloadable'] = downloadable

        return self

    def entry_title(self, entry_title):
        """
        Filter by the collection entry title.

        :param entry_title: Entry title of the collection
        :returns: Query instance
        """

        entry_title = self._urlencodestring(entry_title)

        self.params['entry_title'] = entry_title

        return self

    def query(self):
        """
        Queries the CMR and return the response as a dictionary.

        :returns: list of dictionaries, with each dictionary describing one granule
        """

        # last chance validation for parameters
        if not self._valid_state():
            raise RuntimeError(("Spatial parameters must be accompanied by a collection "
                                "filter (ex: short_name or entry_title)."))

        # encode params
        formatted_params = []
        for key, val in self.params.items():

            # list params require slightly different formatting
            if isinstance(val, list):
                for list_val in val:
                    formatted_params.append("{}[]={}".format(key, list_val))
            else:
                formatted_params.append("{}={}".format(key, val))

        params_as_string = "&".join(formatted_params)

        # encode options
        formatted_options = []
        for param_key in self.options:
            for option_key, val in self.options[param_key].items():

                # all CMR options must be booleans
                if not isinstance(val, bool):
                    raise ValueError("parameter '{}' with option '{}' must be a boolean".format(
                        param_key,
                        option_key
                    ))

                formatted_options.append("options[{}][{}]={}".format(
                    param_key,
                    option_key,
                    val
                ))

        options_as_string = "&".join(formatted_options)

        url = "{}?{}&{}".format(self.base_url, params_as_string, options_as_string)
        response = get(url)

        try:
            response.raise_for_status()
        except exceptions.HTTPError as ex:
            raise RuntimeError(ex.response.text)

        return response.json()["feed"]["entry"]

    def _valid_state(self):
        """
        Determines if the Query is in a valid state based on the parameters and options
        that have been set. This should be implemented by the subclasses.

        :returns: True if the state is valid, otherwise False
        """

        raise NotImplementedError()


class GranuleQuery(Query):
    """
    Class for querying granules from the CMR.
    """

    def __init__(self):
        Query.__init__(self, "https://cmr.earthdata.nasa.gov/search/granules.json")

    def orbit_number(self, orbit1, orbit2=None):
        """"
        Filter by the orbit number the granule was acquired during. Either a single
        orbit can be targeted or a range of orbits.
        
        :param orbit1: orbit to target (lower limit of range when orbit2 is provided)
        :param orbit2: upper limit of range
        :returns: Query instance
        """

        if orbit2:
            self.params['orbit_number'] = self._urlencodestring(
                '{},{}'.format(str(orbit1), str(orbit2))
            )
        else:
            self.params['orbit_number'] = orbit1

        return self

    def day_night_flag(self, day_night_flag):
        """
        Filter by period of the day the granule was collected during.

        :param day_night_flag: "day", "night", or "unspecified"
        :returns: Query instance
        """

        if not isinstance(day_night_flag, str):
            raise TypeError("day_night_flag must be of type str.")

        day_night_flag = day_night_flag.lower()

        if day_night_flag not in ['day', 'night', 'unspecified']:
            raise ValueError("day_night_flag must be day, night or unspecified.")

        self.params['day_night_flag'] = day_night_flag
        return self

    def cloud_cover(self, min_cover=0, max_cover=100):
        """
        Filter by the percentage of cloud cover present in the granule.

        :param min_cover: minimum percentage of cloud cover
        :param max_cover: maximum percentage of cloud cover
        :returns: Query instance 
        """

        if not min_cover and not max_cover:
            raise ValueError("Please provide at least min_cover, max_cover or both")

        if min_cover and max_cover:
            try:
                minimum = float(min_cover)
                maxiumum = float(max_cover)

                if minimum > maxiumum:
                    raise ValueError("Please ensure min_cloud_cover is lower than max cloud cover")
            except ValueError:
                raise ValueError("Please ensure min_cover and max_cover are both floats")

        self.params['cloud_cover'] = "{},{}".format(min_cover, max_cover)
        return self

    def instrument(self, instrument=""):
        """
        Filter by the instrument associated with the granule.

        :param instrument: name of the instrument
        :returns: Query instance
        """

        if not instrument:
            raise ValueError("Please provide a value for instrument")

        self.params['instrument'] = instrument
        return self

    def platform(self, platform=""):
        """
        Filter by the satellite platform the granule came from.

        :param platform: name of the satellite
        :returns: Query instance
        """

        if not platform:
            raise ValueError("Please provide a value for platform")

        self.params['platform'] = platform
        return self

    def granule_ur(self, granule_ur=""):
        """
        Filter by the granules unique ID. Note this will result in at most one granule
        being returned.

        :param granule_ur: UUID of a granule
        :returns: Query instance
        """

        if not granule_ur:
            raise ValueError("Please provide a value for platform")

        self.params['granule_ur'] = granule_ur
        return self

    def _valid_state(self):

        # spatial params must be paired with a collection limiting parameter
        spatial_keys = ["point", "polygon", "bounding_box", "line"]
        collection_keys = ["short_name", "entry_title"]

        if any(key in self.params for key in spatial_keys):
            if not any(key in self.params for key in collection_keys):
                return False

        # all good then
        return True


class CollectionsQuery(Query):
    """
    Class for querying collections from the CMR. Largely unimplemented.
    """

    def __init__(self):
        Query.__init__(self, "https://cmr.earthdata.nasa.gov/search/collections.json")

    def first_ten(self):
        """
        Returns the first 10 results from a basic CMR collection search.
        """

        response = get(self.base_url)
        collections = response.json()["feed"]["entry"]

        return collections

    def _valid_state(self):
        return True
