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
        ({"limit": 20}),
        (
            {
                "display": "full",
                "date": "2023-01-01",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "updated_since": 900000,
                "published_since": 900000,
                "sort": "created",
                "order": "desc",
                "isin": "US0378331005",
                "cusip": "037833100",
                "channels": "General",
                "topics": "car",
                "authors": "Benzinga Insights",
                "content_types": "Car",
                "provider": "benzinga",
                "limit": 20,
            }
        ),
        (
            {
                "provider": "fmp",
                "limit": 20,
            }
        ),
        (
            {
                "provider": "intrinio",
                "limit": 20,
            }
        ),
        (
            {
                "provider": "biztoc",
                "filter": "tag",
                "tag": "federalreserve",
                "source": "bloomberg",
                "term": "MSFT",
            }
        ),
        (
            {
                "provider": "tiingo",
                "limit": 30,
                "source": "bloomberg.com",
            }
        ),
    ],
)
@pytest.mark.integration
def test_news_world(params, obb):
    result = obb.news.world(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        ({"symbols": "AAPL,MSFT", "limit": 20}),
        (
            {
                "display": "full",
                "date": "2023-01-01",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "updated_since": 1,
                "published_since": 1,
                "sort": "created",
                "order": "desc",
                "isin": "US0378331005",
                "cusip": "037833100",
                "channels": "General",
                "topics": "AAPL",
                "authors": "Benzinga Insights",
                "content_types": "headline",
                "provider": "benzinga",
                "symbols": "AAPL,MSFT",
                "limit": 20,
            }
        ),
        (
            {
                "published_utc": "2023-01-10",
                "order": "desc",
                "provider": "polygon",
                "symbols": "AAPL",
                "limit": 20,
            }
        ),
        (
            {
                "provider": "fmp",
                "symbols": "AAPL",
                "limit": 20,
                "page": 1,
            }
        ),
        (
            {
                "provider": "yfinance",
                "symbols": "AAPL",
                "limit": 20,
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbols": "AAPL",
                "limit": 20,
            }
        ),
        (
            {
                "provider": "ultima",
                "symbols": "AAPL,MSFT",
            }
        ),
        (
            {
                "provider": "tiingo",
                "symbols": "AAPL,MSFT",
                "limit": 20,
                "source": "bloomberg.com",
            }
        ),
    ],
)
@pytest.mark.integration
def test_news_company(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.news.company(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
