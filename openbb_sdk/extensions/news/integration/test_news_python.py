"""Test news extension."""
import pytest
from openbb import obb
from openbb_core.app.model.obbject import OBBject


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
                "updated_since": 1,
                "published_since": 1,
                "sort": "created",
                "order": "desc",
                "isin": "TEST_STRING",
                "cusip": "TEST_STRING",
                "channels": "TEST_STRING",
                "topics": "TEST_STRING",
                "authors": "TEST_STRING",
                "content_types": "TEST_STRING",
                "provider": "benzinga",
                "limit": 20,
            }
        ),
    ],
)
def test_news_globalnews(params):
    result = obb.news.globalnews(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


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
                "isin": "TEST_STRING",
                "cusip": "TEST_STRING",
                "channels": "TEST_STRING",
                "topics": "TEST_STRING",
                "authors": "TEST_STRING",
                "content_types": "TEST_STRING",
                "provider": "benzinga",
                "symbols": "AAPL,MSFT",
                "limit": 20,
            }
        ),
        (
            {
                "published_utc": "TEST_STRING",
                "order": "desc",
                "provider": "polygon",
                "symbols": "AAPL,MSFT",
                "limit": 20,
            }
        ),
    ],
)
def test_stocks_news(params):
    result = obb.stocks.news(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 100}),
    ],
)
def test_stocks_multiples(params):
    result = obb.stocks.multiples(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "TEST_STRING", "ticker": True}),
    ],
)
def test_stocks_search(params):
    result = obb.stocks.search(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"source": "iex", "provider": "intrinio", "symbol": "AAPL"}),
    ],
)
def test_stocks_quote(params):
    result = obb.stocks.quote(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
    ],
)
def test_stocks_info(params):
    result = obb.stocks.info(params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
