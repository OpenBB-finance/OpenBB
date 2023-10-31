from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_yfinance.models.active import YFActiveFetcher
from openbb_yfinance.models.available_indices import YFinanceAvailableIndicesFetcher
from openbb_yfinance.models.balance_sheet import YFinanceBalanceSheetFetcher
from openbb_yfinance.models.cash_flow import YFinanceCashFlowStatementFetcher
from openbb_yfinance.models.crypto_historical import YFinanceCryptoHistoricalFetcher
from openbb_yfinance.models.etf_historical import YFinanceEtfHistoricalFetcher
from openbb_yfinance.models.forex_historical import YFinanceForexHistoricalFetcher
from openbb_yfinance.models.futures_curve import YFinanceFuturesCurveFetcher
from openbb_yfinance.models.futures_historical import YFinanceFuturesHistoricalFetcher
from openbb_yfinance.models.gainers import YFGainersFetcher
from openbb_yfinance.models.income_statement import YFinanceIncomeStatementFetcher
from openbb_yfinance.models.losers import YFLosersFetcher
from openbb_yfinance.models.major_indices_historical import (
    YFinanceMajorIndicesHistoricalFetcher,
)
from openbb_yfinance.models.stock_historical import YFinanceStockHistoricalFetcher
from openbb_yfinance.models.stock_news import YFinanceStockNewsFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
        ],
    }


@pytest.mark.record_http
def test_y_finance_crypto_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "BTC-USD",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = YFinanceCryptoHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_y_finance_forex_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "EURUSD",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = YFinanceForexHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_y_finance_major_indices_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "SPY",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = YFinanceMajorIndicesHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_y_finance_stock_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "AAPL",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
        "interval": "1d",
    }

    fetcher = YFinanceStockHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_y_finance_futures_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "ES",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = YFinanceFuturesHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
@pytest.mark.skip(reason="Blows up on download errors for specific dates.")
def test_y_finance_futures_curve_fetcher(credentials=test_credentials):
    params = {
        "symbol": "ES",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = YFinanceFuturesCurveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_y_finance_stock_news_fetcher(credentials=test_credentials):
    params = {"symbols": "AAPL,MSFT"}

    fetcher = YFinanceStockNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_y_finance_balance_sheet_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = YFinanceBalanceSheetFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_y_finance_cash_flow_statement_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = YFinanceCashFlowStatementFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_y_finance_income_statement_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = YFinanceIncomeStatementFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


def test_y_finance_available_indices_fetcher(credentials=test_credentials):
    params = {}

    fetcher = YFinanceAvailableIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_y_finance_etf_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "IOO",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 6, 6),
    }

    fetcher = YFinanceEtfHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_yf_active_fetcher(credentials=test_credentials):
    params = {}

    fetcher = YFActiveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_yf_gainers_fetcher(credentials=test_credentials):
    params = {}

    fetcher = YFGainersFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_yf_losers_fetcher(credentials=test_credentials):
    params = {}

    fetcher = YFLosersFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
