import datetime

import pytest
from openbb_core.app.service.user_service import UserService

from openbb_ecb.models.available_indicators import ECBAvailableIndicatorsFetcher
from openbb_ecb.models.balance_of_payments import ECBBalanceOfPaymentsFetcher
from openbb_ecb.models.currency_historical import ECBCurrencyHistoricalFetcher
from openbb_ecb.models.currency_reference_rates import ECBCurrencyReferenceRatesFetcher
from openbb_ecb.models.ecb_interest_rates import ECBInterestRatesFetcher
from openbb_ecb.models.economic_calendar import ECBEconomicCalendarFetcher
from openbb_ecb.models.economic_indicators import ECBEconomicIndicatorsFetcher
from openbb_ecb.models.euro_short_term_rate import ECBEuroShortTermRateFetcher
from openbb_ecb.models.mfi_interest_rates import ECBMfiInterestRatesFetcher
from openbb_ecb.models.yield_curve import ECBYieldCurveFetcher

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
def test_ecb_available_indicators_fetcher(credentials=test_credentials):
    params = {
        "dataflow": "EXR",
        "frequency": "A",
        "reference_area": "USD",
        "limit": 50,
    }

    fetcher = ECBAvailableIndicatorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_ecb_currency_reference_rates_fetcher(credentials=test_credentials):
    params = {}

    fetcher = ECBCurrencyReferenceRatesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_ecb_currency_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "EURUSD",
        "start_date": datetime.date(2024, 6, 3),
        "end_date": datetime.date(2024, 6, 7),
        "use_cache": False,
    }

    fetcher = ECBCurrencyHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_ecb_economic_indicators_fetcher(credentials=test_credentials):
    params = {
        "symbol": "EXR::D.USD.EUR.SP00.A",
        "start_date": datetime.date(2024, 6, 3),
        "end_date": datetime.date(2024, 6, 7),
        "use_cache": False,
    }

    fetcher = ECBEconomicIndicatorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_ecb_interest_rates_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2025, 1, 1),
        "end_date": datetime.date(2025, 1, 10),
        "use_cache": False,
    }

    fetcher = ECBInterestRatesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_ecb_euro_short_term_rate_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2025, 1, 2),
        "end_date": datetime.date(2025, 1, 10),
        "use_cache": False,
    }

    fetcher = ECBEuroShortTermRateFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_ecb_mfi_interest_rates_fetcher(credentials=test_credentials):
    params = {
        "symbol": "household_loans_for_house_purchase",
        "start_date": datetime.date(2025, 1, 1),
        "end_date": datetime.date(2025, 3, 1),
        "use_cache": False,
    }

    fetcher = ECBMfiInterestRatesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_ecb_balance_of_payments_fetcher(credentials=test_credentials):
    params = {
        "report_type": "main",
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 30),
        "use_cache": False,
    }

    fetcher = ECBBalanceOfPaymentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_ecb_yield_curve_fetcher(credentials=test_credentials):
    params = {"date": "2023-11-20", "use_cache": False}

    fetcher = ECBYieldCurveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_ecb_economic_calendar_fetcher(credentials=test_credentials):
    params = {}

    fetcher = ECBEconomicCalendarFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
