This repository is a copy of [jddeal/python_cmr](https://github.com/jddeal/python-cmr/tree/ef0f9e7d67ce99d342a568bd6a098c3462df16d2) which is no longer maintained. It has been copied here with the permission of the original author for the purpose of continuing to develop a python library that can be used for CMR access.

----

Python CMR
==========

[![CodeQL](https://github.com/nasa/python_cmr/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/nasa/python_cmr/actions/workflows/codeql-analysis.yml)

Python CMR is an easy to use wrapper to the NASA EOSDIS [Common Metadata Repository API](https://cmr.earthdata.nasa.gov/search/). This package aims to make querying the API intuitive and less error-prone by providing methods that will preemptively check for invalid input and handle the URL encoding the CMR API expects.

Getting access to NASA's earth science metadata is as simple as this:

    >>> from cmr import CollectionQuery, GranuleQuery

    >>> api = CollectionQuery()
    >>> collections = api.archive_center("LP DAAC").keyword("AST_L1*").get(5)

    >>> for collection in collections:
    >>>   print(collection["short_name"])
    AST_L1A
    AST_L1AE
    AST_L1T

    >>> api = GranuleQuery()
    >>> granules = api.short_name("AST_L1T").point(-112.73, 42.5).get(3)

    >>> for granule in granules:
    >>>   print(granule["title"])
    SC:AST_L1T.003:2149105822
    SC:AST_L1T.003:2149105820
    SC:AST_L1T.003:2149155037

Installation
============

To install from pypi:

    $ pip install python-cmr

To install from github, perhaps to try out the dev branch:

    $ git clone https://github.com/jddeal/python-cmr
    $ cd python-cmr
    $ pip install .

Examples
========

This library is broken into two classes, CollectionQuery and GranuleQuery. Each of these classes provide a large set of methods used to build a query for CMR. Not all parameters provided by the CMR API are covered by this version of python-cmr.

The following methods are available to both collecton and granule queries:

    # search for granules matching a specific product/short_name
    >>> api.short_name("AST_L1T")

    # search for granules matching a specific version
    >>> api.version("006")

    # search for granules at a specific longitude and latitude
    >>> api.point(-112.73, 42.5)

    # search for granules in an area bound by a box (lower left lon/lat, upper right lon/lat)
    >>> api.bounding_box(-112.70, 42.5, -110, 44.5)

    # search for granules in a polygon (these need to be in counter clockwise order and the
    # last coordinate must match the first in order to close the polygon)
    >>> api.polygon([(-100, 40), (-110, 40), (-105, 38), (-100, 40)])

    # search for granules in a line
    >>> api.line([(-100, 40), (-90, 40), (-95, 38)])

    # search for granules in an open or closed date range
    >>> api.temporal("2016-10-10T01:02:00Z", "2016-10-12T00:00:30Z")
    >>> api.temporal("2016-10-10T01:02:00Z", None)
    >>> api.temporal(datetime(2016, 10, 10, 1, 2, 0), datetime.now())

    # only include granules available for download
    >>> api.downloadable()

    # only include granules that are unavailable for download
    >>> api.online_only()

    # search for collections/granules associated with or identified by concept IDs
    # note: often the ECHO collection ID can be used here as well
    # note: when using CollectionQuery, only collection concept IDs can be passed
    # note: when uses GranuleQuery, passing a collection's concept ID will filter by granules associated
    #       with that particular collection.
    >>> api.concept_id("C1299783579-LPDAAC_ECS")
    >>> api.concept_id(["G1327299284-LPDAAC_ECS", "G1326330014-LPDAAC_ECS"])

    # search by provider
    >>> api.provider('POCLOUD')

Granule searches support these methods (in addition to the shared methods above):

    # search for a granule by its unique ID
    >>> api.granule_ur("SC:AST_L1T.003:2150315169")
    # search for granules from a specific orbit
    >>> api.orbit_number(5000)

    # filter by the day/night flag
    >>> api.day_night_flag("day")

    # filter by cloud cover percentage range
    >>> api.cloud_cover(25, 75)

    # filter by specific instrument or platform
    >>> api.instrument("MODIS")
    >>> api.platform("Terra")

Collection searches support these methods (in addition to the shared methods above):

    # search for collections from a specific archive center
    >>> api.archive_center("LP DAAC")

    # case insensitive, wildcard enabled text search through most collection fields
    >>> api.keyword("M*D09")

    # search by native_id
    >>> api.native_id('native_id')

    # filter by tool concept id
    >>> api.tool_concept_id('TL2092786348-POCLOUD')

    # filter by service concept id
    >>> api.service_concept_id('S1962070864-POCLOUD')

Service searches support the following methods

    # Search via provider
    >>> api = ServiceQuery()
    >>> api.provider('POCLOUD')
    
    # Search via native_id
    >>> api.native_id('POCLOUD_podaac_l2_cloud_subsetter')

    # Search via name
    >>> api.name('PODAAC L2 Cloud Subsetter')

Tool searches support the following methods

    # Search via provider
    >>> api = ToolQuery()
    >>> api.provider('POCLOUD')

    # Search via native_id
    >>> api.native_id('POCLOUD_hitide')

    # Search via name
    >>> api.name('hitide')

As an alternative to chaining methods together to set the parameters of your query, a method exists to allow you to pass your parameters as keyword arguments:

    # search for AST_L1T version 003 granules at latitude 42, longitude -100
    >>> api.parameters(
        short_name="AST_L1T",
        version="003",
        point=(-100, 42)
    )

Note: the kwarg key should match the name of a method from the above examples, and the value should be a tuple if it's a parameter that requires multiple values.

To inspect and retreive results from the API, the following methods are available:

    # inspect the number of results the query will return without downloading the results
    >>> print(api.hits())

    # retrieve 100 granules
    >>> granules = api.get(100)

    # retrieve 25,000 granules
    >>> granules = api.get(25000)

    # retrieve all the granules possible for the query
    >>> granules = api.get_all()  # this is a shortcut for api.get(api.hits())

By default the responses will return as json and be accessible as a list of python dictionaries. Other formats can be specified before making the request:

    >>> granules = api.format("echo10").get(100)

The following formats are supported for both granule and collection queries:

-   json (default)
-   xml
-   echo10
-   iso
-   iso19115
-   csv
-   atom
-   kml
-   native

Collection queries also support the following formats:

-   dif
-   dif10
-   opendata
-   umm\_json
-   umm\_json\_vX\_Y (ex: umm\_json\_v1\_9)
