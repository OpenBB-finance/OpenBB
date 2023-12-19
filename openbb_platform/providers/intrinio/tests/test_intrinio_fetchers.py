from datetime import date
from unittest import mock

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_intrinio.models.balance_sheet import IntrinioBalanceSheetFetcher
from openbb_intrinio.models.calendar_ipo import IntrinioCalendarIpoFetcher
from openbb_intrinio.models.cash_flow import IntrinioCashFlowStatementFetcher
from openbb_intrinio.models.company_filings import IntrinioCompanyFilingsFetcher
from openbb_intrinio.models.company_news import IntrinioCompanyNewsFetcher
from openbb_intrinio.models.currency_pairs import IntrinioCurrencyPairsFetcher
from openbb_intrinio.models.equity_historical import IntrinioEquityHistoricalFetcher
from openbb_intrinio.models.equity_info import IntrinioEquityInfoFetcher
from openbb_intrinio.models.equity_quote import IntrinioEquityQuoteFetcher
from openbb_intrinio.models.equity_search import IntrinioEquitySearchFetcher
from openbb_intrinio.models.fred_series import IntrinioFredSeriesFetcher
from openbb_intrinio.models.historical_attributes import (
    IntrinioHistoricalAttributesFetcher,
)
from openbb_intrinio.models.historical_dividends import (
    IntrinioHistoricalDividendsFetcher,
)
from openbb_intrinio.models.income_statement import IntrinioIncomeStatementFetcher
from openbb_intrinio.models.insider_trading import IntrinioInsiderTradingFetcher
from openbb_intrinio.models.institutional_ownership import (
    IntrinioInstitutionalOwnershipFetcher,
)
from openbb_intrinio.models.key_metrics import IntrinioKeyMetricsFetcher
from openbb_intrinio.models.latest_attributes import IntrinioLatestAttributesFetcher
from openbb_intrinio.models.market_indices import IntrinioMarketIndicesFetcher
from openbb_intrinio.models.options_chains import IntrinioOptionsChainsFetcher
from openbb_intrinio.models.options_unusual import IntrinioOptionsUnusualFetcher
from openbb_intrinio.models.search_attributes import (
    IntrinioSearchAttributesFetcher,
)
from openbb_intrinio.models.share_statistics import IntrinioShareStatisticsFetcher
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
def test_intrinio_fred_series_fetcher(credentials=test_credentials):
    params = {
        "symbol": "$GDP",
        "start_date": date(2022, 9, 20),
        "end_date": date(2023, 9, 20),
    }

    fetcher = IntrinioFredSeriesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_calendar_ipo_fetcher(credentials=test_credentials):
    params = {"status": "upcoming"}

    fetcher = IntrinioCalendarIpoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_search_attributes(credentials=test_credentials):
    params = {"query": "ebit"}

    fetcher = IntrinioSearchAttributesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_historical_attributes(credentials=test_credentials):
    params = {
        "provider": "intrinio",
        "symbol": "AAPL",
        "tag": "ebit",
        "frequency": "yearly",
        "limit": 1000,
        "type": None,
        "start_date": date(2013, 1, 1),
        "end_date": date(2023, 1, 1),
        "sort": "desc",
    }

    fetcher = IntrinioHistoricalAttributesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_latest_attributes(credentials=test_credentials):
    params = {
        "provider": "intrinio",
        "symbol": "AAPL",
        "tag": "ceo",
    }

    fetcher = IntrinioLatestAttributesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_equity_info_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = IntrinioEquityInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_market_indices_fetcher(credentials=test_credentials):
    params = {
        "symbol": "$DJI",
        "tag": "level",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 6, 6),
    }

    fetcher = IntrinioMarketIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_historical_dividends_fetcher(credentials=test_credentials):
    params = {
        "symbol": "AAPL",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 6, 6),
    }

    fetcher = IntrinioHistoricalDividendsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_company_filings_fetcher(credentials=test_credentials):
    params = {
        "symbol": "AAPL",
        "form_type": None,
        "limit": 100,
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 6, 6),
    }

    fetcher = IntrinioCompanyFilingsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_insider_trading_fetcher(credentials=test_credentials):
    params = {
        "symbol": "AAPL",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 6, 6),
    }

    fetcher = IntrinioInsiderTradingFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_institutional_ownership_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = IntrinioInstitutionalOwnershipFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_key_metrics_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = IntrinioKeyMetricsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_share_statistics_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = IntrinioShareStatisticsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_intrinio_equity_search_fetcher(credentials=test_credentials):
    params = {"query": "gold", "limit": 100}

    fetcher = IntrinioEquitySearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
