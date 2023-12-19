from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_yfinance.models.active import YFActiveFetcher
from openbb_yfinance.models.aggressive_small_caps import YFAggressiveSmallCapsFetcher
from openbb_yfinance.models.available_indices import YFinanceAvailableIndicesFetcher
from openbb_yfinance.models.balance_sheet import YFinanceBalanceSheetFetcher
from openbb_yfinance.models.cash_flow import YFinanceCashFlowStatementFetcher
from openbb_yfinance.models.company_news import YFinanceCompanyNewsFetcher
from openbb_yfinance.models.crypto_historical import YFinanceCryptoHistoricalFetcher
from openbb_yfinance.models.currency_historical import YFinanceCurrencyHistoricalFetcher
from openbb_yfinance.models.equity_historical import YFinanceEquityHistoricalFetcher
from openbb_yfinance.models.etf_historical import YFinanceEtfHistoricalFetcher
from openbb_yfinance.models.futures_curve import YFinanceFuturesCurveFetcher
from openbb_yfinance.models.futures_historical import YFinanceFuturesHistoricalFetcher
from openbb_yfinance.models.gainers import YFGainersFetcher
from openbb_yfinance.models.growth_tech_equities import YFGrowthTechEquitiesFetcher
from openbb_yfinance.models.income_statement import YFinanceIncomeStatementFetcher
from openbb_yfinance.models.losers import YFLosersFetcher
from openbb_yfinance.models.market_indices import (
    YFinanceMarketIndicesFetcher,
)
from openbb_yfinance.models.undervalued_growth_equities import (
    YFUndervaluedGrowthEquitiesFetcher,
)
from openbb_yfinance.models.undervalued_large_caps import YFUndervaluedLargeCapsFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("Cookie", "MOCK_COOKIE"),
        ],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("crumb", "MOCK_CRUMB"),
        ],
    }


@pytest.mark.record_http
def test_y_finance_market_indices_fetcher(credentials=test_credentials):
    params = {
        "symbol": "^GSPC",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = YFinanceMarketIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_y_finance_crypto_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "BTCUSD",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = YFinanceCryptoHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_y_finance_equity_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "AAPL",
    }

    fetcher = YFinanceEquityHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_y_finance_currency_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "EURUSD",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = YFinanceCurrencyHistoricalFetcher()
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
def test_y_finance_futures_curve_fetcher(credentials=test_credentials):
    params = {"symbol": "ES"}

    fetcher = YFinanceFuturesCurveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_y_finance_company_news_fetcher(credentials=test_credentials):
    params = {"symbols": "AAPL,MSFT"}

    fetcher = YFinanceCompanyNewsFetcher()
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


def test_y_finance_available_fetcher(credentials=test_credentials):
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


@pytest.mark.record_http
def test_yf_undervalued_large_caps_fetcher(credentials=test_credentials):
    params = {}

    fetcher = YFUndervaluedLargeCapsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_yf_undervalued_growth_equities_fetcher(credentials=test_credentials):
    params = {}

    fetcher = YFUndervaluedGrowthEquitiesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_yf_aggressive_small_caps_fetcher(credentials=test_credentials):
    params = {}

    fetcher = YFAggressiveSmallCapsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_yf_growth_tech_equities_fetcher(credentials=test_credentials):
    params = {}

    fetcher = YFGrowthTechEquitiesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
