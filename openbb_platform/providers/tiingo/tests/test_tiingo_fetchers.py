from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_tiingo.models.company_news import TiingoCompanyNewsFetcher
from openbb_tiingo.models.crypto_historical import TiingoCryptoHistoricalFetcher
from openbb_tiingo.models.currency_historical import TiingoCurrencyHistoricalFetcher
from openbb_tiingo.models.equity_historical import TiingoEquityHistoricalFetcher
from openbb_tiingo.models.trailing_dividend_yield import TiingoTrailingDivYieldFetcher
from openbb_tiingo.models.world_news import TiingoWorldNewsFetcher

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
def test_tiingo_equity_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "AAPL",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 6, 6),
    }

    fetcher = TiingoEquityHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tiingo_company_news_fetcher(credentials=test_credentials):
    params = {"symbols": "AAPL,MSFT"}

    fetcher = TiingoCompanyNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tiingo_world_news_fetcher(credentials=test_credentials):
    params = {}

    fetcher = TiingoWorldNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tiingo_crypto_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "BTCUSD",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 6, 6),
    }

    fetcher = TiingoCryptoHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tiingo_currency_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "EURUSD",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 6, 6),
    }

    fetcher = TiingoCurrencyHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tiingo_trailing_div_yield_fetcher(credentials=test_credentials):
    params = {"symbol": "SCHD"}

    fetcher = TiingoTrailingDivYieldFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
