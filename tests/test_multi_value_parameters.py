"""Exercise repeated query parameters through URL construction and requests."""

import json
from urllib.parse import parse_qs, urlsplit

import pytest
import requests

from cmr import (
    CollectionQuery, GranuleQuery, ServiceQuery, ToolQuery, VariableQuery,
)


@pytest.mark.parametrize("query_type", [
    CollectionQuery, GranuleQuery, ServiceQuery, ToolQuery, VariableQuery,
])
def test_unchecked_values_are_individual_query_parameters(query_type):
    query = query_type().parameters(data_center=["FIRST", "SECOND"])
    original = dict(query.params)
    assert parse_qs(urlsplit(query._build_url()).query) == {
        "data_center[]": ["FIRST", "SECOND"],
    }
    assert query.params == original
    assert query.params["data_center[]"] == ("FIRST", "SECOND")


@pytest.mark.parametrize("factory", [list, tuple, iter, set])
def test_unchecked_iterables_retain_values_on_repeated_builds(factory):
    query = CollectionQuery().parameters(data_center=factory(["A", "B"]))
    first = query._build_url()
    assert query._build_url() == first
    assert sorted(parse_qs(urlsplit(first).query)["data_center[]"]) == [
        "A", "B",
    ]


@pytest.mark.parametrize("values,expected", [
    ([], {}),
    (["A"], {"data_center[]": ["A"]}),
    (["A", "A"], {"data_center[]": ["A", "A"]}),
    (range(2), {"data_center[]": ["0", "1"]}),
])
def test_empty_singleton_duplicate_and_numeric_values(values, expected):
    query = CollectionQuery().parameters(data_center=values)
    assert parse_qs(urlsplit(query._build_url()).query) == expected


@pytest.mark.parametrize("values", [["one", "two"], ("one", "two")])
def test_declared_sequence_parameter_keeps_one_array_suffix(values):
    query = VariableQuery().instance_format(values)
    assert parse_qs(urlsplit(query._build_url()).query) == {
        "instance_format[]": ["one", "two"],
    }


def test_scalar_parameters_and_tuple_method_arguments_are_unchanged():
    query = GranuleQuery().parameters(
        short_name="EXAMPLE", point=(-100, 42),
        custom_enabled=True, custom_limit=0,
    )
    assert parse_qs(urlsplit(query._build_url()).query) == {
        "short_name": ["EXAMPLE"], "point[]": ["-100.0,42.0"],
        "custom_enabled": ["true"], "custom_limit": ["0"],
    }


@pytest.mark.parametrize("operation", ["results", "get", "hits"])
def test_repeated_values_reach_the_http_request(monkeypatch, operation):
    sent = []

    def send(session, request, **kwargs):
        sent.append(request)
        response = requests.Response()
        response.status_code = 200
        response.request = request
        response.headers["CMR-Hits"] = "2"
        response._content = json.dumps({
            "feed": {"entry": [{"id": len(sent)}]},
        }).encode()
        if len(sent) == 1:
            response.headers["cmr-search-after"] = "next-page"
        return response

    monkeypatch.setattr(requests.Session, "send", send)
    query = CollectionQuery().parameters(data_center=["FIRST", "SECOND"])
    query.headers["Client-Id"] = "local-test"
    original_headers = dict(query.headers)
    if operation == "results":
        assert list(query.results(page_size=1)) == [{"id": 1}, {"id": 2}]
    elif operation == "get":
        with pytest.warns(DeprecationWarning):
            assert query.get(1) == [{"id": 1}]
    else:
        assert query.hits() == 2
    for request in sent:
        params = parse_qs(urlsplit(request.url).query)
        assert params["data_center[]"] == ["FIRST", "SECOND"]
        assert params["page_size"] == (["0"] if operation == "hits" else ["1"])
        assert "data_center[][]" not in params
        assert request.headers["Client-Id"] == "local-test"
    if operation == "results":
        assert len(sent) == 2
        assert "cmr-search-after" not in sent[0].headers
        assert sent[1].headers["cmr-search-after"] == "next-page"
    assert query.headers == original_headers
