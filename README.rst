Python CMR
==========

.. image:: https://travis-ci.org/jddeal/python-cmr.svg?branch=master
    :target: https://travis-ci.org/jddeal/python-cmr

Python CMR is an easy to use wrapper to the NASA EOSDIS
`Common Metadata Repository API <https://cmr.earthdata.nasa.gov/search/>`_. This package aims to make
querying the API intuitive and less error-prone by providing methods that will preemptively check
for invalid input and handle the URL encoding the CMR API expects.

Getting access to NASA's earth science data is as simple as this:

.. code-block:: python

    >>> from cmr import GranuleQuery

    >>> api = GranuleQuery()

    >>> granules = api.short_name("AST_L1T").point(42.5, -112.73).query()

    >>> for granule in granules:
    >>>   print(granule["entry_title"])
    SC:AST_L1T.003:2149105822
    SC:AST_L1T.003:2149105820
    SC:AST_L1T.003:2149155037
    SC:AST_L1T.003:2149469555
    SC:AST_L1T.003:2149469571
    SC:AST_L1T.003:2149789318
    SC:AST_L1T.003:2149962675
    SC:AST_L1T.003:2150165250
    SC:AST_L1T.003:2150261715
    SC:AST_L1T.003:2150315169


Examples
========

The CMR API provides many parameters, but not all of them are covered by this version of
the wrapper. The following shows the possible parameters supported by the wrapper:

.. code-block:: python

    >>> from cmr import GranuleQuery

    # search for granules matching a specific product/short_name
    >>> api.short_name("AST_L1T")

    # search for granules matching a specific version
    >>> api.version("006")

    # search for granules at a specific longitude and latitude
    >>> api.point(-112.73, 42.5)

    # search for granules in an area bound by a box (lower left lon/lat, upper right lon/lat)
    >>> api.bounding_box(-112.70, 42.5, -110, 44.5)

    # search for granules in a polygon
    >>> api.polygon((-100, 40), (-90, 40), (-95, 38), (-100, 40))

    # search for granules in a line
    >>> api.line((-100, 40), (-90, 40), (-95, 38))

    # search for granules in an open or closed date range
    >>> api.temporal("2016-10-10T01:02:00Z", "2016-10-12T00:00:30Z")
    >>> api.temporal("2016-10-10T01:02:00Z", None)
    >>> api.temporal(datetime("2016-10-10T01:02:00Z"), datetime.now())

    # search for a granule by its unique ID
    >>> api.granule_ur("SC:AST_L1T.003:2150315169")

    # only include granules available for download
    >>> api.downloadable()

    # only include granules that are unavailable for download
    >>> api.online_only()

    # search for granules from a specific orbit
    >>> api.orbit_number(5000)

    # filter by the day/night flag
    >>> api.day_night_flag("day")

    # filter by cloud cover percentage range
    >>> api.cloud_cover(25, 75)

    # filter by specific instrument or platform
    >>> api.instrument("MODIS")
    >>> api.platform("Terra")


Installation
============

Simply clone and install via pip.

.. code-block:: bash

    $ git clone https://github.com/jddeal/python-cmr
    $ cd python-cmr
    $ pip install .

