import pytest

from cmr.queries import CollectionQuery, GranuleQuery, ServiceQuery, ToolQuery, VariableQuery


@pytest.mark.parametrize("query_type", [CollectionQuery, GranuleQuery, ServiceQuery, ToolQuery, VariableQuery])
@pytest.mark.parametrize("output_format", ["jsonn", "not-json", "iso19116", "umm_json_v1_9suffix"])
def test_rejects_partial_format_matches(query_type, output_format):
    query = query_type()
    with pytest.raises(ValueError, match="Unsupported format"):
        query.format(output_format)
    assert query._format == "json"


@pytest.mark.parametrize("output_format", ["umm_json", "umm_json_v1_9", "umm_json_v1_18"])
def test_accepts_complete_umm_versions(output_format):
    query = CollectionQuery().format(output_format)
    assert query._format == output_format
