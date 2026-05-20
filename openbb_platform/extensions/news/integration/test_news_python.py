"""Python interface integration tests."""

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb
    return None


@pytest.mark.integration
def test_rss_python_fetches_articles(obb):
    out = obb.news.rss(source="bbc_world", limit=3, fetch_body=False)
    assert isinstance(out, OBBject)
    assert 1 <= len(out.results) <= 3
    first = out.results[0]
    assert first.title
    assert first.date
    assert first.author
    assert hasattr(first, "url")
    assert hasattr(first, "excerpt")
    assert hasattr(first, "body")
