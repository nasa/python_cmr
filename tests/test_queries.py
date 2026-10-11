import pytest

from cmr import Query


class MockQuery(Query):

    def __init__(self) -> None:
        super().__init__("/foo")

    def _valid_state(self) -> bool:
        return True


def test_query_headers_initially_empty():
    query = MockQuery()
    assert query.headers == {}


def test_bearer_token_adds_header():
    query = MockQuery()
    query.headers["foo"] = "bar"
    query.bearer_token("bearertoken")

    assert query.headers["foo"] == "bar"


def test_bearer_token_does_not_clobber_other_headers():
    query = MockQuery()
    query.bearer_token("bearertoken")

    assert query.headers["Authorization"] == "Bearer bearertoken"


def test_bearer_token_replaces_existing_auth_header():
    query = MockQuery()
    query.token("token")
    query.bearer_token("bearertoken")

    assert query.headers["Authorization"] == "Bearer bearertoken"


def test_token_adds_header():
    query = MockQuery()
    query.token("token")

    assert query.headers["Authorization"] == "token"


def test_token_does_not_clobber_other_headers():
    query = MockQuery()
    query.headers["foo"] = "bar"
    query.token("token")

    assert query.headers["foo"] == "bar"


def test_token_replaces_existing_auth_header():
    query = MockQuery()
    query.bearer_token("bearertoken")
    query.token("token")

    assert query.headers["Authorization"] == "token"


def test_singular_unknown_parameter():
    query = MockQuery().parameters(unknown_parameter="foo")

    assert query.params["unknown_parameter"] == "foo"


def test_plural_unknown_parameter():
    query = MockQuery().parameters(unknown_parameter=["foo", "bar"])

    assert query.params["unknown_parameter[]"] == ("foo", "bar")


def test_remove_missing_option():
    query = MockQuery()

    assert query.option("short_name", "ignore_case", None) is query
    assert query.options == {}


def test_remove_missing_option_preserves_other_options():
    query = MockQuery().option("short_name", "ignore_case", True)

    query.option("short_name", "or", None)

    assert query.options == {"short_name": {"ignore_case": True}}


def test_remove_option_twice():
    query = MockQuery().option("short_name", "ignore_case", True)

    query.option("short_name", "ignore_case", None)
    query.option("short_name", "ignore_case", None)

    assert "ignore_case" not in query.options["short_name"]


@pytest.mark.parametrize("parameter,key", [("", "ignore_case"), ("short_name", "")])
def test_remove_option_with_empty_name_does_nothing(parameter, key):
    query = MockQuery().option("short_name", "ignore_case", True)

    assert query.option(parameter, key, None) is query
    assert query.options == {"short_name": {"ignore_case": True}}
