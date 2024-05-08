"""
Contains all CMR query types.
"""

from abc import abstractmethod
from datetime import date, datetime, timezone
from inspect import getmembers, ismethod
from re import search
from typing_extensions import (
    Any,
    List,
    Literal,
    MutableMapping,
    Optional,
    Sequence,
    Self,
    Set,
    SupportsFloat,
    Tuple,
    TypeAlias,
    Union,
    override,
)
from urllib.parse import quote

import requests
from dateutil.parser import parse as dateutil_parse

CMR_OPS = "https://cmr.earthdata.nasa.gov/search/"
CMR_UAT = "https://cmr.uat.earthdata.nasa.gov/search/"
CMR_SIT = "https://cmr.sit.earthdata.nasa.gov/search/"

DateLike: TypeAlias = Union[str, date, datetime]
DayNightFlag: TypeAlias = Union[
    Literal["day"], Literal["night"], Literal["unspecified"]
]
FloatLike: TypeAlias = Union[str, SupportsFloat]
PointLike: TypeAlias = Tuple[FloatLike, FloatLike]

class Query:
    """
    Base class for all CMR queries.
    """

    _base_url = ""
    _route = ""
    _format = "json"
    _valid_formats_regex = [
        "json", "xml", "echo10", "iso", "iso19115",
        "csv", "atom", "kml", "native"
    ]

    def __init__(self, route: str, mode: str = CMR_OPS):
        self.params: MutableMapping[str, Any] = {}
        self.options: MutableMapping[str, Any] = {}
        self._route = route
        self.mode(mode)
        self.concept_id_chars: Set[str] = set()
        self.headers: MutableMapping[str, str] = {}

    def get(self, limit: int = 2000) -> Sequence[Any]:
        """
        Get all results up to some limit, even if spanning multiple pages.

        :limit: The number of results to return
        :returns: query results as a list
        """

        url = self._build_url()

        results = []
        headers = dict(self.headers or {})
        more_results = True
        n_results = 0

        while more_results:
            # Only get what we need on the last page.
            page_size = min(limit - n_results, 2000)
            response = requests.get(
                url, headers=headers, params={"page_size": page_size}
            )
            response.raise_for_status()

            # Explicitly track the number of results we have because the length
            # of the results list will only match the number of entries fetched
            # when the format is JSON.  Otherwise, the length of the results
            # list is the number of *pages* fetched, not the number of *items*.
            n_results += page_size

            results.extend(
                response.json()["feed"]["entry"]
                if self._format == "json"
                else [response.text]
            )

            if cmr_search_after := response.headers.get("cmr-search-after"):
                headers["cmr-search-after"] = cmr_search_after

            more_results = n_results < limit and cmr_search_after is not None

        return results

    def hits(self) -> int:
        """
        Returns the number of hits the current query will return. This is done by
        making a lightweight query to CMR and inspecting the returned headers.

        :returns: number of results reproted by CMR
        """

        url = self._build_url()

        response = requests.get(url, headers=self.headers, params={"page_size": 0})
        response.raise_for_status()

        return int(response.headers["CMR-Hits"])

    def get_all(self) -> Sequence[Any]:
        """
        Returns all of the results for the query. This will call hits() first to determine how many
        results their are, and then calls get() with that number. This method could take quite
        awhile if many requests have to be made.

        :returns: query results as a list
        """

        return self.get(self.hits())

    def parameters(self, **kwargs: Any) -> Self:
        """
        Provide query parameters as keyword arguments. The keyword needs to match the name
        of the method, and the value should either be the value or a tuple of values.

        Example: parameters(short_name="AST_L1T", point=(42.5, -101.25))

        :returns: self
        """

        methods = dict(getmembers(self, predicate=ismethod))

        for key, val in kwargs.items():
            # verify the key matches one of our methods
            if key not in methods:
                raise ValueError(f"Unknown key {key}")

            # call the method
            if isinstance(val, tuple):
                methods[key](*val)
            else:
                methods[key](val)

        return self

    def format(self, output_format: str = "json") -> Self:
        """
        Sets the format for the returned results.

        :param output_format: Preferred output format
        :returns: self
        """

        if not output_format:
            output_format = "json"

        # check requested format against the valid format regex's
        for _format in self._valid_formats_regex:
            if search(_format, output_format):
                self._format = output_format
                return self

        # if we got here, we didn't find a matching format
        raise ValueError(f"Unsupported format: '{output_format}'")

    def _build_url(self) -> str:
        """
        Builds the URL that will be used to query CMR.

        :returns: the url as a string
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
                    formatted_params.append(f"{key}[]={list_val}")
            elif isinstance(val, bool):
                formatted_params.append(f"{key}={str(val).lower()}")
            else:
                formatted_params.append(f"{key}={val}")

        params_as_string = "&".join(formatted_params)

        # encode options
        formatted_options: List[str] = []
        for param_key in self.options:
            for option_key, val in self.options[param_key].items():

                # all CMR options must be booleans
                if not isinstance(val, bool):
                    raise TypeError(
                        f"parameter '{param_key}' with option '{option_key}' must be a boolean"
                    )

                formatted_options.append(f"options[{param_key}][{option_key}]={str(val).lower()}")

        options_as_string = "&".join(formatted_options)
        res = f"{self._base_url}.{self._format}?{params_as_string}&{options_as_string}"
        return res.rstrip('&')

    def concept_id(self, IDs: Union[str, Sequence[str]]) -> Self:
        """
        Filter by concept ID (ex: C1299783579-LPDAAC_ECS or G1327299284-LPDAAC_ECS, T12345678-LPDAAC_ECS, S12345678-LPDAAC_ECS)

        Collections, granules, tools, services are uniquely identified with this ID.
        If providing a collection's concept ID here, it will filter by granules associated with that collection.
        If providing a granule's concept ID here, it will uniquely identify those granules.
        If providing a tool's concept ID here, it will uniquely identify those tools.
        If providing a service's concept ID here, it will uniquely identify those services.

        :param IDs: concept ID(s) to search by. Can be provided as a string or list of strings.
        :returns: self
        """

        if isinstance(IDs, str):
            IDs = [IDs]

        # verify we weren't provided any granule concept IDs
        for ID in IDs:
            if ID.strip()[0] not in self.concept_id_chars:
                raise ValueError(
                    f"Only concept IDs that begin with '{self.concept_id_chars}' can be provided: {ID}"
                )

        self.params["concept_id"] = IDs

        return self

    def provider(self, provider: str) -> Self:
        """
        Filter by provider.

        :param provider: provider of tool.
        :returns: self
        """

        if not provider:
            return self

        self.params['provider'] = provider
        return self

    @abstractmethod
    def _valid_state(self) -> bool:
        """
        Determines if the Query is in a valid state based on the parameters and options
        that have been set. This should be implemented by the subclasses.

        :returns: True if the state is valid, otherwise False
        """

        raise NotImplementedError()

    def mode(self, mode: str = CMR_OPS) -> Self:
        """
        Sets the mode of the api target to the given URL
        CMR_OPS, CMR_UAT, CMR_SIT are provided as class variables

        :param mode: Mode to set the query to target
        :returns: self
        :raises: Will raise if provided None
        """
        if mode is None:
            raise ValueError("Please provide a valid mode (CMR_OPS, CMR_UAT, CMR_SIT)")

        self._base_url = mode + self._route
        return self

    def token(self, token: str) -> Self:
        """
        Add token into authorization headers.

        :param token: Token from EDL Echo-Token or NASA Launchpad token.
        :returns: self
        """

        if not token:
            return self

        self.headers = {'Authorization': token}

        return self

    def bearer_token(self, bearer_token: str) -> Self:
        """
        Add token into authorization headers.

        :param token: Token from EDL token.
        :returns: self
        """

        if not bearer_token:
            return self

        self.headers = {'Authorization': f'Bearer {bearer_token}'}

        return self


class GranuleCollectionBaseQuery(Query):
    """
    Base class for Granule and Collection CMR queries.
    """

    def online_only(self, online_only: bool = True) -> Self:
        """
        Only match granules that are listed online and not available for download.
        The opposite of this method is downloadable().

        :param online_only: True to require granules only be online
        :returns: self
        """

        if not isinstance(online_only, bool):
            raise TypeError("Online_only must be of type bool")

        # remove the inverse flag so CMR doesn't crash
        if "downloadable" in self.params:
            del self.params["downloadable"]

        self.params['online_only'] = online_only

        return self

    def temporal(
        self,
        date_from: Optional[DateLike],
        date_to: Optional[DateLike],
        exclude_boundary: bool = False,
    ) -> Self:
        """
        Filter by an open or closed date range.

        Dates can be provided as native date objects or ISO 8601 formatted strings. Multiple
        ranges can be provided by successive calls to this method before calling execute().

        :param date_from: earliest date of temporal range
        :param date_to: latest date of temporal range
        :param exclude_boundary: whether or not to exclude the date_from/to in the matched range
        :returns: GranueQuery instance
        """

        iso_8601 = "%Y-%m-%dT%H:%M:%SZ"

        # process each date into a datetime object
        def convert_to_string(date: Optional[DateLike], default: datetime) -> str:
            """
            Returns the argument as an ISO 8601 or empty string.
            """

            if not date:
                return ""

            # handle str, date-like objects without time, and datetime objects
            if isinstance(date, str):
                # handle string by parsing with default
                date = dateutil_parse(date, default=default)
            elif not isinstance(date, datetime):
                # handle (naive by definition) date by converting to utc datetime
                try:
                    date = datetime.combine(date, default.time())
                except TypeError:
                    raise TypeError(
                        f"Date must be a date object or ISO 8601 string, not {date.__class__.__name__}."
                    ) from None
                date = date.replace(tzinfo=timezone.utc)
            else:
                # pass aware datetime and handle naive datetime by assuming utc
                date = date if date.tzinfo else date.replace(tzinfo=timezone.utc)

            # convert aware datetime to utc datetime
            date = date.astimezone(timezone.utc)

            return date.strftime(iso_8601)

        date_from = convert_to_string(date_from, datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc))
        date_to = convert_to_string(date_to, datetime(1, 12, 31, 23, 59, 59, tzinfo=timezone.utc))

        # if we have both dates, make sure from isn't later than to
        if date_from and date_to and date_from > date_to:
            raise ValueError("date_from must be earlier than date_to.")

        # good to go, make sure we have a param list
        if "temporal" not in self.params:
            self.params["temporal"] = []

        self.params["temporal"].append(f"{date_from},{date_to}")

        if exclude_boundary:
            self.options["temporal"] = {
                "exclude_boundary": True
            }

        return self

    def short_name(self, short_name: str) -> Self:
        """
        Filter by short name (aka product or collection name).

        :param short_name: name of collection
        :returns: self
        """

        if not short_name:
            return self

        self.params['short_name'] = short_name
        return self

    def version(self, version: str) -> Self:
        """
        Filter by version. Note that CMR defines this as a string. For example,
        MODIS version 6 products must be searched for with "006".

        :param version: version string
        :returns: self
        """

        if not version:
            return self

        self.params['version'] = version
        return self

    def point(self, lon: FloatLike, lat: FloatLike) -> Self:
        """
        Filter by granules that include a geographic point.

        :param lon: longitude of geographic point
        :param lat: latitude of geographic point
        :returns: self
        """

        # coordinates must be a float
        lon = float(lon)
        lat = float(lat)

        self.params['point'] = f"{lon},{lat}"

        return self

    def circle(self, lon: FloatLike, lat: FloatLike, dist: FloatLike) -> Self:
        """Filter by granules within the circle around lat/lon

        :param lon: longitude of geographic point
        :param lat: latitude of geographic point
        :param dist: distance in meters around waypoint (lat,lon)
        :returns: self
        """
        self.params['circle'] = f"{lon},{lat},{dist}"

        return self

    def polygon(self, coordinates: Sequence[PointLike]) -> Self:
        """
        Filter by granules that overlap a polygonal area. Must be used in combination with a
        collection filtering parameter such as short_name or entry_title.

        :param coordinates: list of (lon, lat) tuples
        :returns: self
        """

        if not coordinates:
            return self

        # make sure we were passed something iterable
        try:
            iter(coordinates)
        except TypeError:
            raise TypeError(
                f"A line must be an iterable of coordinate tuples. Ex: [(90,90), (91, 90), ...]; got {type(coordinates)}."
            ) from None

        # polygon requires at least 4 pairs of coordinates
        if len(coordinates) < 4:
            raise ValueError(
                f"A polygon requires at least 4 pairs of coordinates; got {len(coordinates)}."
            )

        # convert to floats
        as_floats = []
        for lon, lat in coordinates:
            as_floats.extend([float(lon), float(lat)])

        # last point must match first point to complete polygon
        if as_floats[0] != as_floats[-2] or as_floats[1] != as_floats[-1]:
            raise ValueError(
                f"Coordinates of the last pair must match the first pair: {coordinates[0]} != {coordinates[-1]}"
            )

        # convert to strings
        as_strs = [str(val) for val in as_floats]

        self.params["polygon"] = ",".join(as_strs)

        return self

    def bounding_box(
        self,
        lower_left_lon: FloatLike,
        lower_left_lat: FloatLike,
        upper_right_lon: FloatLike,
        upper_right_lat: FloatLike,
    ) -> Self:
        """
        Filter by granules that overlap a bounding box. Must be used in combination with
        a collection filtering parameter such as short_name or entry_title.

        :param lower_left_lon: lower left longitude of the box
        :param lower_left_lat: lower left latitude of the box
        :param upper_right_lon: upper right longitude of the box
        :param upper_right_lat: upper right latitude of the box
        :returns: self
        """

        self.params["bounding_box"] = (
            f"{float(lower_left_lon)},{float(lower_left_lat)},{float(upper_right_lon)},{float(upper_right_lat)}"
        )

        return self

    def line(self, coordinates: Sequence[PointLike]) -> Self:
        """
        Filter by granules that overlap a series of connected points. Must be used in combination
        with a collection filtering parameter such as short_name or entry_title.

        :param coordinates: a list of (lon, lat) tuples
        :returns: self
        """

        if not coordinates:
            return self

        # make sure we were passed something iterable
        try:
            iter(coordinates)
        except TypeError:
            raise TypeError(
                f"A line must be an iterable of coordinate tuples. Ex: [(90,90), (91, 90), ...]; got {type(coordinates)}."
            ) from None

        # need at least 2 pairs of coordinates
        if len(coordinates) < 2:
            raise ValueError(
                f"A line requires at least 2 pairs of coordinates; got {len(coordinates)}."
            )

        # make sure they're all floats
        as_floats = []
        for lon, lat in coordinates:
            as_floats.extend([float(lon), float(lat)])

        # cast back to string for join
        as_strs = [str(val) for val in as_floats]

        self.params["line"] = ",".join(as_strs)

        return self

    def downloadable(self, downloadable: bool = True) -> Self:
        """
        Only match granules that are available for download. The opposite of this
        method is online_only().

        :param downloadable: True to require granules be downloadable
        :returns: self
        """

        if not isinstance(downloadable, bool):
            raise TypeError("Downloadable must be of type bool")

        # remove the inverse flag so CMR doesn't crash
        if "online_only" in self.params:
            del self.params["online_only"]

        self.params['downloadable'] = downloadable

        return self

    def entry_title(self, entry_title: str) -> Self:
        """
        Filter by the collection entry title.

        :param entry_title: Entry title of the collection
        :returns: self
        """

        entry_title = quote(entry_title)

        self.params['entry_title'] = entry_title

        return self


class GranuleQuery(GranuleCollectionBaseQuery):
    """
    Class for querying granules from the CMR.
    """

    def __init__(self, mode: str = CMR_OPS):
        Query.__init__(self, "granules", mode)
        self.concept_id_chars = {"G", "C"}

    def orbit_number(
        self, orbit1: FloatLike, orbit2: Optional[FloatLike] = None
    ) -> Self:
        """ "
        Filter by the orbit number the granule was acquired during. Either a single
        orbit can be targeted or a range of orbits.

        :param orbit1: orbit to target (lower limit of range when orbit2 is provided)
        :param orbit2: upper limit of range
        :returns: self
        """

        if orbit2:
            self.params['orbit_number'] = quote(f'{str(orbit1)},{str(orbit2)}')
        else:
            self.params['orbit_number'] = orbit1

        return self

    def day_night_flag(self, day_night_flag: DayNightFlag) -> Self:
        """
        Filter by period of the day the granule was collected during.

        :param day_night_flag: "day", "night", or "unspecified"
        :returns: self
        """

        if not isinstance(day_night_flag, str):
            raise TypeError("day_night_flag must be of type str.")

        if day_night_flag.lower() not in ["day", "night", "unspecified"]:
            raise ValueError(
                "day_night_flag must be 'day', 'night', or 'unspecified': "
                f"{day_night_flag!r}."
            )

        self.params["day_night_flag"] = day_night_flag.lower()
        return self

    def cloud_cover(self, min_cover: FloatLike = 0, max_cover: FloatLike = 100) -> Self:
        """
        Filter by the percentage of cloud cover present in the granule.

        :param min_cover: minimum percentage of cloud cover
        :param max_cover: maximum percentage of cloud cover
        :returns: self
        """

        if not min_cover and not max_cover:
            raise ValueError("Please provide at least min_cover, max_cover or both")

        if min_cover and max_cover:
            try:
                minimum = float(min_cover)
                maxiumum = float(max_cover)

                if minimum > maxiumum:
                    raise ValueError(
                        "Please ensure min cloud cover is less than max cloud cover"
                    )
            except ValueError:
                raise ValueError(
                    "Please ensure min_cover and max_cover are both floats"
                ) from None
            except TypeError:
                raise TypeError(
                    "Please ensure min_cover and max_cover are both convertible to floats"
                ) from None

        self.params['cloud_cover'] = f"{min_cover},{max_cover}"
        return self

    def instrument(self, instrument: str) -> Self:
        """
        Filter by the instrument associated with the granule.

        :param instrument: name of the instrument
        :returns: self
        """

        if not instrument:
            raise ValueError("Please provide a value for instrument")

        self.params['instrument'] = instrument
        return self

    def platform(self, platform: str) -> Self:
        """
        Filter by the satellite platform the granule came from.

        :param platform: name of the satellite
        :returns: self
        """

        if not platform:
            raise ValueError("Please provide a value for platform")

        self.params['platform'] = platform
        return self

    def sort_key(self, sort_key: str) -> Self:
        """
        See
        https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html#sorting-granule-results
        for valid granule sort_keys

        Filter some defined sort_key;
        use negative (-) for start_date and end_date to sort by ascending

        :param sort_key: name of the sort key
        :returns: self
        """

        valid_sort_keys = {
            'campaign',
            'entry_title',
            'dataset_id',
            'data_size',
            'end_date',
            'granule_ur',
            'producer_granule_id',
            'project',
            'provider',
            'readable_granule_name',
            'short_name',
            'start_date',
            'version',
            'platform',
            'instrument',
            'sensor',
            'day_night_flag',
            'online_only',
            'browsable',
            'browse_only',
            'cloud_cover',
            'revision_date',
        }

        # also covers if empty string and allows for '-' prefix (for descending order)
        if not isinstance(sort_key, str) or sort_key.lstrip('-') not in valid_sort_keys:
            raise ValueError(
                "Please provide a valid sort key for granules query.  See"
                " https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html#sorting-granule-results"
                " for valid sort keys."
            )

        self.params['sort_key'] = sort_key
        return self

    def granule_ur(self, granule_ur: str) -> Self:
        """
        Filter by the granules unique ID. Note this will result in at most one granule
        being returned.

        :param granule_ur: UUID of a granule
        :returns: self
        """

        if not granule_ur:
            raise ValueError("Please provide a value for platform")

        self.params['granule_ur'] = granule_ur
        return self

    def readable_granule_name(
        self, readable_granule_name: Union[str, Sequence[str]]
    ) -> Self:
        """
        Filter by the readable granule name (producer_granule_id if present, otherwise producer_granule_id).

        Can use wildcards for substring matching:

        asterisk (*) will match any number of characters.
        question mark (?) will match exactly one character.

        :param readable_granule_name: granule name or substring
        :returns: self
        """

        if isinstance(readable_granule_name, str):
            readable_granule_name = [readable_granule_name]

        self.params["readable_granule_name"] = readable_granule_name
        self.options["readable_granule_name"] = {"pattern": True}

        return self

    @override
    def _valid_state(self) -> bool:

        # spatial params must be paired with a collection limiting parameter
        spatial_keys = ["point", "polygon", "bounding_box", "line"]
        collection_keys = ["short_name", "entry_title"]

        if any(key in self.params for key in spatial_keys):
            if not any(key in self.params for key in collection_keys):
                return False

        # all good then
        return True


class CollectionQuery(GranuleCollectionBaseQuery):
    """
    Class for querying collections from the CMR.
    """

    def __init__(self, mode: str = CMR_OPS):
        Query.__init__(self, "collections", mode)
        self.concept_id_chars = {"C"}
        self._valid_formats_regex.extend([
            "dif", "dif10", "opendata", "umm_json", "umm_json_v[0-9]_[0-9]"
        ])

    def archive_center(self, center: str) -> Self:
        """
        Filter by the archive center that maintains the collection.

        :param archive_center: name of center as a string
        :returns: self
        """

        if center:
            self.params['archive_center'] = center

        return self

    def keyword(self, text: str) -> Self:
        """
        Case insentive and wildcard (*) search through over two dozen fields in
        a CMR collection record. This allows for searching against fields like
        summary and science keywords.

        :param text: text to search for
        :returns: self
        """

        if text:
            self.params['keyword'] = text

        return self

    def native_id(self, native_ids: Union[str, Sequence[str]]) -> Self:
        """
        Filter by native id.

        :param native_id: native id for collection
        :returns: self
        """

        if isinstance(native_ids, str):
            native_ids = [native_ids]

        self.params["native_id"] = native_ids

        return self

    def tool_concept_id(self, IDs: Union[str, Sequence[str]]) -> Self:
        """
        Filter collections associated with tool concept ID (ex: TL2092786348-POCLOUD)

        Collections are associated with this tool ID.

        :param IDs: tool concept ID(s) to search by. Can be provided as a string or list of strings.
        :returns: self
        """

        if isinstance(IDs, str):
            IDs = [IDs]

        # verify we provided with tool concept IDs
        for ID in IDs:
            if ID.strip()[0] != "T":
                raise ValueError(f"Only tool concept ID's can be provided (begin with 'T'): {ID}")

        self.params["tool_concept_id"] = IDs

        return self

    def service_concept_id(self, IDs: Union[str, Sequence[str]]) -> Self:
        """
        Filter collections associated with service ID (ex: S1962070864-POCLOUD)

        Collections are associated with this service ID.

        :param IDs: service concept ID(s) to search by. Can be provided as a string or list of strings.
        :returns: self
        """

        if isinstance(IDs, str):
            IDs = [IDs]

        # verify we provided with service concept IDs
        for ID in IDs:
            if ID.strip()[0] != "S":
                raise ValueError(
                    f"Only service concept IDs can be provided (begin with 'S'): {ID}"
                )

        self.params["service_concept_id"] = IDs

        return self

    @override
    def _valid_state(self) -> bool:
        return True


class ToolServiceVariableBaseQuery(Query):
    """
    Base class for Tool and Service CMR queries.
    """

    def get(self, limit: int = 2000) -> Sequence[Any]:
        """
        Get all results up to some limit, even if spanning multiple pages.

        :limit: The number of results to return
        :returns: query results as a list
        """

        page_size = min(limit, 2000)
        url = self._build_url()

        results: List[Any] = []
        page = 1
        while len(results) < limit:

            response = requests.get(
                url, params={"page_size": page_size, "page_num": page}
            )
            response.raise_for_status()

            if self._format == "json":
                latest = response.json()['items']
            else:
                latest = [response.text]

            if len(latest) == 0:
                break

            results.extend(latest)
            page += 1

        return results

    def native_id(self, native_ids: Union[str, Sequence[str]]) -> Self:
        """
        Filter by native id.

        :param native_id: native id for tool or service
        :returns: self
        """

        if isinstance(native_ids, str):
            native_ids = [native_ids]

        self.params["native_id"] = native_ids

        return self

    def name(self, name: str) -> Self:
        """
        Filter by name.

        :param name: name of service or tool.
        :returns: self
        """

        if not name:
            return self

        self.params['name'] = name
        return self


class ToolQuery(ToolServiceVariableBaseQuery):
    """
    Class for querying tools from the CMR.
    """

    def __init__(self, mode: str = CMR_OPS):
        Query.__init__(self, "tools", mode)
        self.concept_id_chars = {"T"}
        self._valid_formats_regex.extend([
            "dif", "dif10", "opendata", "umm_json", "umm_json_v[0-9]_[0-9]"
        ])

    @override
    def _valid_state(self) -> bool:
        return True


class ServiceQuery(ToolServiceVariableBaseQuery):
    """
    Class for querying services from the CMR.
    """

    def __init__(self, mode: str = CMR_OPS):
        Query.__init__(self, "services", mode)
        self.concept_id_chars = {"S"}
        self._valid_formats_regex.extend([
            "dif", "dif10", "opendata", "umm_json", "umm_json_v[0-9]_[0-9]"
        ])

    @override
    def _valid_state(self) -> bool:
        return True


class VariableQuery(ToolServiceVariableBaseQuery):

    def __init__(self, mode: str = CMR_OPS):
        Query.__init__(self, "variables", mode)
        self.concept_id_chars = {"V"}
        self._valid_formats_regex.extend([
            "dif", "dif10", "opendata", "umm_json", "umm_json_v[0-9]_[0-9]"
        ])

    @override
    def _valid_state(self) -> bool:
        return True
