""" Test ECB Fetchers. """

import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_ecb.models.balance_of_payments import ECBBalanceOfPaymentsFetcher
from openbb_ecb.models.currency_reference_rates import ECBCurrencyReferenceRatesFetcher
from openbb_ecb.models.eu_yield_curve import ECBEUYieldCurveFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR config."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.mark.record_http
def test_ecbeu_yield_curve_fetcher(credentials=test_credentials):
    """Test ECBEUYieldCurveFetcher."""
    params = {"date": datetime.date(2023, 1, 1)}

    fetcher = ECBEUYieldCurveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_ecb_currency_reference_rates_fetcher(credentials=test_credentials):
    """Test ECB Currency Reference Rates Fecher."""
    params = {}

    fetcher = ECBCurrencyReferenceRatesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_ecb_balance_of_payments_fetcher(credentials=test_credentials):
    """Test ECB Balance Of Payments Fetcher."""
    params = {"date": datetime.date(2023, 1, 1)}

    fetcher = ECBBalanceOfPaymentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
