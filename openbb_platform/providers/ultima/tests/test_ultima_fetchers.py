import pytest
from openbb_core.app.service.user_service import UserService

try:
    from openbb_ultima.models.company_news import UltimaCompanyNewsFetcher
    from openbb_ultima.models.sector_news import UltimaSectorNewsFetcher
except ImportError:
    pytest.skip("openbb-ultima is not installed on the CI.", allow_module_level=True)

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


test_credentials["ultima_api_key"] = "MOCK_API_KEY"  # pragma: allowlist secret


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("Authorization", "Bearer MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
@pytest.mark.skip(reason="openbb-ultima is not installed on the CI.")
def test_ultima_company_news_fetcher(credentials=test_credentials):
    params = {"symbols": "AAPL, MSFT"}

    fetcher = UltimaCompanyNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
@pytest.mark.skip(reason="openbb-ultima is not installed on the CI.")
def test_ultima_sector_news_fetcher(credentials=test_credentials):
    params = {"sectors": "Real Estate, Financial Services"}

    fetcher = UltimaSectorNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
