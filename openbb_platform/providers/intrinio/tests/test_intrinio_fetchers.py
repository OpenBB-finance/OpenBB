from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_intrinio.models.balance_sheet import IntrinioBalanceSheetFetcher
from openbb_intrinio.models.cash_flow import IntrinioCashFlowStatementFetcher
from openbb_intrinio.models.forex_pairs import IntrinioForexPairsFetcher
from openbb_intrinio.models.fred_historical import IntrinioFredHistoricalFetcher
from openbb_intrinio.models.global_news import IntrinioGlobalNewsFetcher
from openbb_intrinio.models.income_statement import IntrinioIncomeStatementFetcher
from openbb_intrinio.models.options_chains import IntrinioOptionsChainsFetcher
from openbb_intrinio.models.stock_historical import IntrinioStockHistoricalFetcher
from openbb_intrinio.models.stock_news import IntrinioStockNewsFetcher
from openbb_intrinio.models.stock_quote import IntrinioStockQuoteFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_intrinio_stock_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "AAPL",
        "start_date": date(2023, 1, 23),
        "end_date": date(2023, 5, 23),
    }

    fetcher = IntrinioStockHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_forex_pairs_fetcher(credentials=test_credentials):
    params = {}

    fetcher = IntrinioForexPairsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_stock_news_fetcher(credentials=test_credentials):
    params = {"symbols": "AAPL"}

    fetcher = IntrinioStockNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_global_news_fetcher(credentials=test_credentials):
    params = {}

    fetcher = IntrinioGlobalNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_stock_quote_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = IntrinioStockQuoteFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_options_chains_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL", "date": "2023-09-15"}

    fetcher = IntrinioOptionsChainsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_balance_sheet_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = IntrinioBalanceSheetFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_cash_flow_statement_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = IntrinioCashFlowStatementFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_income_statement_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = IntrinioIncomeStatementFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_fred_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "GDP",
        "start_date": date(2022, 9, 20),
        "end_date": date(2023, 9, 20),
    }

    fetcher = IntrinioFredHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
