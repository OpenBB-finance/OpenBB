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


@pytest.mark.integration
def test_rss_python_drugs_com_fetches_full_body(obb):
    out = obb.news.rss(source="drugs_com_medical_news", limit=3, fetch_body=True)
    assert isinstance(out, OBBject)
    assert 1 <= len(out.results) <= 3
    for article in out.results:
        assert article.url.startswith("https://www.drugs.com/")
        assert len(article.body) > len(article.excerpt)
        assert "Whatever your topic of interest" not in article.body


@pytest.mark.integration
def test_rss_python_brutalist_topic_default(obb):
    out = obb.news.rss(outlet="brutalist_business", limit=2, fetch_body=False)
    assert isinstance(out, OBBject)
    assert 1 <= len(out.results) <= 2
    assert out.results[0].title
