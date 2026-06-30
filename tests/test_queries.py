import pytest

from cmr import Query
from cmr.queries import _format_float


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


@pytest.mark.parametrize("value,expected", [
    (1.5,    "1.5"),       # normal float — no change
    (10,     "10"),        # integer — no change
    ("1.5",  "1.5"),       # string — passed through as-is
    (0.0,    "0.0"),       # zero — no scientific notation
    (1e-5,   "0.00001"),   # small float Python renders as "1e-05"
    (1e-8,   "0.00000001"),
    (-1e-5,  "-0.00001"),  # negative scientific notation
    (1.23e-5, "0.0000123"),
])
def test_format_float(value, expected):
    assert _format_float(value) == expected
