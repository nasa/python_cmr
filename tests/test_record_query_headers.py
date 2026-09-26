import json
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import pytest
from requests import HTTPError, Response

from cmr import ServiceQuery, ToolQuery, VariableQuery


QUERY_CLASSES = [ToolQuery, ServiceQuery, VariableQuery]


@pytest.fixture(autouse=True)
def no_netrc_credentials():
    # Do not pick up credentials from the test runner's home directory.
    with patch("requests.sessions.get_netrc_auth", return_value=None):
        yield


def make_response(content: str, status: int = 200) -> Response:
    response = Response()
    response.status_code = status
    response._content = content.encode("utf-8")
    return response


@pytest.mark.parametrize("query_class", QUERY_CLASSES)
@pytest.mark.parametrize("auth_method", [None, "token", "bearer_token"])
def test_get_sends_configured_headers_on_every_page(query_class, auth_method):
    query = query_class()
    query.headers.update(
        {"Client-Id": "test-client", "X-Test-Header": "test-value"}
    )
    if auth_method:
        getattr(query, auth_method)("test-token")
    expected_headers = dict(query.headers)
    first = {"name": "first"}
    second = {"name": "second"}

    with patch("requests.sessions.Session.send", autospec=True) as send:
        send.side_effect = [
            make_response(json.dumps({"items": [first]})),
            make_response(json.dumps({"items": [second]})),
        ]
        assert query.get(2) == [first, second]

    assert send.call_count == 2
    for page, call in enumerate(send.call_args_list, start=1):
        request = call.args[1]
        assert request.method == "GET"
        for name, value in expected_headers.items():
            assert request.headers.get(name) == value
        parameters = parse_qs(urlparse(request.url).query)
        assert parameters["page_size"] == ["2"]
        assert parameters["page_num"] == [str(page)]
    assert query.headers == expected_headers


@pytest.mark.parametrize("query_class", QUERY_CLASSES)
def test_get_unparsed_pages_sends_configured_headers(query_class):
    query = query_class().format("xml").bearer_token("test-token")
    pages = ["<items>first</items>", "<items>second</items>"]
    with patch("requests.sessions.Session.send", autospec=True) as send:
        send.side_effect = [make_response(page) for page in pages]
        assert query.get(2) == pages

    assert send.call_count == 2
    for call in send.call_args_list:
        assert call.args[1].headers.get("Authorization") == "Bearer test-token"


@pytest.mark.parametrize("query_class", QUERY_CLASSES)
def test_get_without_headers_still_accepts_empty_results(query_class):
    query = query_class()
    with patch("requests.sessions.Session.send", autospec=True) as send:
        send.return_value = make_response('{"items": []}')
        assert query.get(2) == []
    assert send.call_count == 1
    assert "Authorization" not in send.call_args.args[1].headers
    assert query.headers == {}


@pytest.mark.parametrize("query_class", QUERY_CLASSES)
def test_get_preserves_http_errors(query_class):
    response = make_response("Forbidden", status=403)
    with patch("requests.sessions.Session.send", autospec=True) as send:
        send.return_value = response
        with pytest.raises(HTTPError) as error:
            query_class().bearer_token("test-token").get(1)
    assert error.value.response is response
    assert send.call_count == 1
