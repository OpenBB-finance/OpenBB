import pytest
from openbb_core.app.service.user_service import UserService
from openbb_finra.models.equity_short_interest import FinraShortInterestFetcher
from openbb_finra.models.otc_aggregate import FinraOTCAggregateFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.mark.record_http
def test_finra_otc_aggregate_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL", "tier": "T1", "is_ats": True}

    fetcher = FinraOTCAggregateFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.freeze_time("2021-10-21")
@pytest.mark.record_http
def test_finra_short_interest_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = FinraShortInterestFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
