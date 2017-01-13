"""
Class for collections of granules
"""

from requests import get


def first_ten():
    """
    Returns the first 10 results from a basic CMR collection search.
    """

    url = "https://cmr.earthdata.nasa.gov/search/collections.json"
    response = get(url)

    collections = response.json()["feed"]["entry"]

    return collections
