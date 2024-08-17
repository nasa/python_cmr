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
