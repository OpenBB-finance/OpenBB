from datetime import date
from unittest import mock

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_intrinio.models.balance_sheet import IntrinioBalanceSheetFetcher
from openbb_intrinio.models.calendar_ipo import IntrinioCalendarIpoFetcher
from openbb_intrinio.models.cash_flow import IntrinioCashFlowStatementFetcher
from openbb_intrinio.models.company_news import IntrinioCompanyNewsFetcher
from openbb_intrinio.models.currency_pairs import IntrinioCurrencyPairsFetcher
from openbb_intrinio.models.equity_historical import IntrinioEquityHistoricalFetcher
from openbb_intrinio.models.equity_quote import IntrinioEquityQuoteFetcher
from openbb_intrinio.models.financial_attributes import (
    IntrinioFinancialAttributesFetcher,
)
from openbb_intrinio.models.fred_indices import IntrinioFredIndicesFetcher
from openbb_intrinio.models.income_statement import IntrinioIncomeStatementFetcher
from openbb_intrinio.models.options_chains import IntrinioOptionsChainsFetcher
from openbb_intrinio.models.options_unusual import IntrinioOptionsUnusualFetcher
from openbb_intrinio.models.search_financial_attributes import (
    IntrinioSearchFinancialAttributesFetcher,
)
from openbb_intrinio.models.world_news import IntrinioWorldNewsFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.fixture(autouse=True, scope="module")
def mock_cpu_count():
    with mock.patch(
        "os.cpu_count"
    ) as mock_cpu_count:  # pylint: disable=redefined-outer-name
        mock_cpu_count.return_value = -3
        yield


@pytest.mark.record_http
def test_intrinio_equity_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "AAPL",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
        "interval": "1d",
    }

    fetcher = IntrinioEquityHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_currency_pairs_fetcher(credentials=test_credentials):
    params = {}

    fetcher = IntrinioCurrencyPairsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_company_news_fetcher(credentials=test_credentials):
    params = {"symbols": "AAPL"}

    fetcher = IntrinioCompanyNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_world_news_fetcher(credentials=test_credentials):
    params = {}

    fetcher = IntrinioWorldNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_equity_quote_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = IntrinioEquityQuoteFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_options_chains_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL", "date": "2023-09-15"}

    fetcher = IntrinioOptionsChainsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_options_unusual_fetcher(credentials=test_credentials):
    params = {"source": "delayed"}

    fetcher = IntrinioOptionsUnusualFetcher()
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
def test_intrinio_fred_indices_fetcher(credentials=test_credentials):
    params = {
        "symbol": "GDP",
        "start_date": date(2022, 9, 20),
        "end_date": date(2023, 9, 20),
    }

    fetcher = IntrinioFredIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_calendar_ipo_fetcher(credentials=test_credentials):
    params = {"status": "upcoming"}

    fetcher = IntrinioCalendarIpoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_search_financial_attributes(credentials=test_credentials):
    params = {"query": "ebit"}

    fetcher = IntrinioSearchFinancialAttributesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_financial_attributes(credentials=test_credentials):
    params = {
        "provider": "intrinio",
        "symbol": "AAPL",
        "tag": "ebit",
        "period": "annual",
        "limit": 1000,
        "type": None,
        "start_date": date(2013, 1, 1),
        "end_date": date(2023, 1, 1),
        "sort": "desc",
    }

    fetcher = IntrinioFinancialAttributesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
