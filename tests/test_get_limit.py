from unittest.mock import Mock, patch

import pytest

from cmr import ServiceQuery, ToolQuery, VariableQuery


@pytest.mark.parametrize("query_class", [ToolQuery, ServiceQuery, VariableQuery])
@pytest.mark.parametrize("limit", [0, 2001, 4000, 4001, 5000])
def test_get_respects_limit_across_pages(query_class, limit):
    records = [{"id": index} for index in range(4500)]
    pages = []

    def get_page(url, params):
        page_size = params["page_size"]
        page = params["page_num"]
        pages.append((page, page_size))
        start = (page - 1) * page_size
        response = Mock()
        response.json.return_value = {"items": records[start:start + page_size]}
        return response

    with patch("cmr.queries.requests.get", side_effect=get_page):
        results = query_class().get(limit)

    assert results == records[:limit]
    if limit:
        # Changing page_size between page numbers would skip or repeat records.
        assert all(page_size == 2000 for _, page_size in pages)
        assert [page for page, _ in pages] == list(range(1, len(pages) + 1))
    else:
        assert pages == []
