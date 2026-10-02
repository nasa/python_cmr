from unittest.mock import Mock

import pytest

from cmr.queries import CollectionQuery, ServiceQuery, ToolQuery, VariableQuery


@pytest.mark.parametrize("query_type", [CollectionQuery, ServiceQuery, ToolQuery, VariableQuery])
@pytest.mark.parametrize("output_format", ["umm_json", "umm_json_v1_9"])
@pytest.mark.parametrize("method", ["get", "results"])
def test_umm_results_are_individual_items(monkeypatch, query_type, output_format, method):
    items = [{"meta": {"concept-id": "C1"}, "umm": {"ShortName": "first"}},
             {"meta": {"concept-id": "C2"}, "umm": {"ShortName": "second"}}]
    pages = [Mock(headers={"cmr-search-after": "next"}, text="first page"),
             Mock(headers={}, text="second page"), Mock(headers={}, text="empty page")]
    for page, records in zip(pages, [[items[0]], [items[1]], []]):
        page.json.return_value = {"items": records}
    request = Mock(side_effect=pages)
    monkeypatch.setattr("cmr.queries.requests.get", request)
    query = query_type().format(output_format)

    if method == "results":
        actual = list(query.results(page_size=1))
    else:
        actual = query.get(limit=2001 if query_type is CollectionQuery else 2)

    assert actual == items
    assert request.call_count == 2


def test_xml_results_remain_unparsed(monkeypatch):
    response = Mock(headers={}, text="<results/>")
    monkeypatch.setattr("cmr.queries.requests.get", Mock(return_value=response))
    assert list(CollectionQuery().format("xml").results()) == ["<results/>"]
