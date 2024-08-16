import pytest

from cmr import CollectionQuery, Query


class MockQuery(Query):
    def _valid_state(self) -> bool:
        return True


def test_query_headers_initially_empty():
    query = MockQuery("/foo")
    assert query.headers == {}


def test_bearer_token_adds_header():
    query = MockQuery("/foo")
    query.headers["foo"] = "bar"
    query.bearer_token("bearertoken")

    assert query.headers["foo"] == "bar"


def test_bearer_token_does_not_clobber_other_headers():
    query = MockQuery("/foo")
    query.bearer_token("bearertoken")

    assert query.headers["Authorization"] == "Bearer bearertoken"


def test_bearer_token_replaces_existing_auth_header():
    query = MockQuery("/foo")
    query.token("token")
    query.bearer_token("bearertoken")

    assert query.headers["Authorization"] == "Bearer bearertoken"


def test_token_adds_header():
    query = MockQuery("/foo")
    query.token("token")

    assert query.headers["Authorization"] == "token"


def test_token_does_not_clobber_other_headers():
    query = MockQuery("/foo")
    query.headers["foo"] = "bar"
    query.token("token")

    assert query.headers["foo"] == "bar"


def test_token_replaces_existing_auth_header():
    query = MockQuery("/foo")
    query.bearer_token("bearertoken")
    query.token("token")

    assert query.headers["Authorization"] == "token"


def test_option_or_empty_parameter():
    query = CollectionQuery()
    query.option_or("")

    assert query.options == {}


def test_option_or_valid_parameter_on():
    query = CollectionQuery()
    query.option_or("revision_date")

    assert query.options["revision_date"]["or"] is True


def test_option_or_valid_parameter_off():
    query = CollectionQuery()
    query.option_or("revision_date", False)

    assert query.options["revision_date"]["or"] is False


def test_option_or_invalid_parameter():
    query = CollectionQuery()

    with pytest.raises(ValueError):
        query.option_or("no_such_parameter")

    assert "no_such_parameter" not in query.options


def test_option_and_valid_parameter_on():
    query = CollectionQuery()
    query.option_and("revision_date")

    assert query.options["revision_date"]["and"] is True


def test_option_and_empty_parameter():
    query = CollectionQuery()
    query.option_and("")

    assert query.options == {}


def test_option_and_valid_parameter_off():
    query = CollectionQuery()
    query.option_and("revision_date", False)

    assert query.options["revision_date"]["and"] is False


def test_option_and_invalid_parameter():
    query = CollectionQuery()

    with pytest.raises(ValueError):
        query.option_and("no_such_parameter")

    assert "no_such_parameter" not in query.options


def test_option_ignore_case_empty_parameter():
    query = CollectionQuery()
    query.option_ignore_case("")

    assert query.options == {}


def test_option_ignore_case_valid_parameter_on():
    query = CollectionQuery()
    query.option_ignore_case("revision_date")

    assert query.options["revision_date"]["ignore_case"] is True


def test_option_ignore_case_valid_parameter_off():
    query = CollectionQuery()
    query.option_ignore_case("revision_date", False)

    assert query.options["revision_date"]["ignore_case"] is False


def test_option_ignore_case_invalid_parameter():
    query = CollectionQuery()

    with pytest.raises(ValueError):
        query.option_ignore_case("no_such_parameter")

    assert "no_such_parameter" not in query.options


def test_option_pattern_empty_parameter():
    query = CollectionQuery()
    query.option_pattern("")

    assert query.options == {}


def test_option_pattern_valid_parameter_on():
    query = CollectionQuery()
    query.option_pattern("revision_date")

    assert query.options["revision_date"]["pattern"] is True


def test_option_pattern_valid_parameter_off():
    query = CollectionQuery()
    query.option_pattern("revision_date", False)

    assert query.options["revision_date"]["pattern"] is False


def test_option_pattern_invalid_parameter():
    query = CollectionQuery()

    with pytest.raises(ValueError):
        query.option_pattern("no_such_parameter")

    assert "no_such_parameter" not in query.options
