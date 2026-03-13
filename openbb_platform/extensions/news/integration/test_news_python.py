"""Test news extension."""

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):  # pylint: disable=inconsistent-return-statements
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


# pylint: disable=redefined-outer-name


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "display": "full",
                "date": None,
                "start_date": "2023-05-01",
                "end_date": "2023-05-31",
                "updated_since": None,
                "published_since": None,
                "sort": "created",
                "order": "asc",
                "isin": None,
                "cusip": None,
                "channels": "General",
                "topics": "car",
                "authors": None,
                "content_types": "Car",
                "provider": "benzinga",
                "limit": 20,
            }
        ),
        (
            {
                "provider": "fmp",
                "limit": 20,
                "start_date": None,
                "end_date": None,
                "page": 0,
                "topic": "general",
            }
        ),
        (
            {
                "provider": "intrinio",
                "limit": 20,
                "start_date": "2024-01-02",
                "end_date": "2024-01-03",
                "source": "yahoo",
                "topic": None,
                "is_spam": False,
                "sentiment": None,
                "language": None,
                "word_count_greater_than": None,
                "word_count_less_than": None,
                "business_relevance_greater_than": None,
                "business_relevance_less_than": None,
            }
        ),
        (
            {
                "provider": "biztoc",
                "source": None,
                "term": "microsoft",
                "start_date": None,
                "end_date": None,
            }
        ),
        (
            {
                "provider": "tiingo",
                "limit": 30,
                "source": "bloomberg.com",
                "start_date": None,
                "end_date": None,
                "offset": 0,
            }
        ),
    ],
)
@pytest.mark.integration
def test_news_world(params, obb):
    """Test the news world endpoint."""
    result = obb.news.world(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "display": "full",
                "date": None,
                "start_date": None,
                "end_date": None,
                "updated_since": None,
                "published_since": None,
                "sort": "created",
                "order": "desc",
                "isin": None,
                "cusip": None,
                "channels": "General",
                "topics": "earnings",
                "authors": None,
                "content_types": "headline",
                "provider": "benzinga",
                "symbol": "AAPL,MSFT",
                "limit": 20,
            }
        ),
        (
            {
                "provider": "fmp",
                "symbol": "AAPL",
                "limit": 20,
                "page": 1,
                "start_date": None,
                "end_date": None,
                "press_release": False,
            }
        ),
        (
            {
                "provider": "yfinance",
                "symbol": "AAPL",
                "limit": 20,
                "start_date": None,
                "end_date": None,
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "limit": 20,
                "start_date": "2024-01-02",
                "end_date": "2024-01-03",
                "source": "yahoo",
                "topic": None,
                "is_spam": False,
                "sentiment": None,
                "language": None,
                "word_count_greater_than": None,
                "word_count_less_than": None,
                "business_relevance_greater_than": None,
                "business_relevance_less_than": None,
            }
        ),
        (
            {
                "provider": "tiingo",
                "symbol": "AAPL",
                "limit": 20,
                "source": "bloomberg.com",
                "start_date": None,
                "end_date": None,
                "offset": None,
            }
        ),
        (
            {
                "provider": "tmx",
                "symbol": "RBC",
                "limit": 20,
                "page": 1,
            }
        ),
    ],
)
@pytest.mark.integration
def test_news_company(params, obb):
    """Test the news company endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.news.company(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
