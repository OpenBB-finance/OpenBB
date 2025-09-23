"""Test the Benzinga fetchers."""

import pytest
from openbb_benzinga.models.analyst_search import BenzingaAnalystSearchFetcher
from openbb_benzinga.models.company_news import BenzingaCompanyNewsFetcher
from openbb_benzinga.models.price_target import BenzingaPriceTargetFetcher
from openbb_benzinga.models.world_news import BenzingaWorldNewsFetcher
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.mark.record_http
def test_benzinga_world_news_fetcher(credentials=test_credentials):
    """Test the world news fetcher."""
    params = {"limit": 2}

    fetcher = BenzingaWorldNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_benzinga_company_news_fetcher(credentials=test_credentials):
    """Test the company news fetcher."""
    params = {"symbol": "AAPL,MSFT", "limit": 20}

    fetcher = BenzingaCompanyNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_benzinga_price_target_fetcher(credentials=test_credentials):
    """Test the price target fetcher."""
    params = {"symbol": "AAPL"}

    fetcher = BenzingaPriceTargetFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_benzinga_analyst_search_fetcher(credentials=test_credentials):
    """Test the analyst search fetcher."""
    params = {"firm_name": "Barclays"}

    fetcher = BenzingaAnalystSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
