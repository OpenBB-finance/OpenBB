"""Test News API."""

import base64

import pytest
import requests
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring


@pytest.fixture(scope="session")
def headers():
    """Generate headers for API requests with basic authentication."""
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


# pylint: disable=redefined-outer-name


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
                "limit": 20,
            }
        ),
        (
            {
                "provider": "fmp",
                "limit": 30,
                "start_date": None,
                "end_date": None,
                "topic": "general",
                "page": 1,
            }
        ),
        (
            {
                "provider": "intrinio",
                "limit": 20,
                "start_date": None,
                "end_date": None,
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
def test_news_world(params, headers):
    """Test retrieval of world news with various parameters."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/news/world?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "limit": 20,
                "provider": "benzinga",
                "date": "2023-01-01",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
        (
            {
                "display": "full",
                "date": None,
                "start_date": "2023-06-01",
                "end_date": "2023-06-06",
                "updated_since": 1,
                "published_since": 1,
                "sort": "created",
                "order": "asc",
                "isin": None,
                "cusip": None,
                "channels": None,
                "topics": "AAPL",
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
                "symbol": "AAPL,MSFT",
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
def test_news_company(params, headers):
    """Test retrieval of company-specific news with various parameters."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/news/company?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
