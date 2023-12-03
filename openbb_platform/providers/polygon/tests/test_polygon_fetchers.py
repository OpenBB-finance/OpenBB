from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_polygon.models.balance_sheet import PolygonBalanceSheetFetcher
from openbb_polygon.models.cash_flow import PolygonCashFlowStatementFetcher
from openbb_polygon.models.company_news import PolygonCompanyNewsFetcher
from openbb_polygon.models.crypto_historical import PolygonCryptoHistoricalFetcher
from openbb_polygon.models.currency_historical import PolygonCurrencyHistoricalFetcher
from openbb_polygon.models.currency_pairs import PolygonCurrencyPairsFetcher
from openbb_polygon.models.equity_historical import PolygonEquityHistoricalFetcher
from openbb_polygon.models.equity_nbbo import PolygonEquityNBBOFetcher
from openbb_polygon.models.income_statement import PolygonIncomeStatementFetcher
from openbb_polygon.models.market_indices import (
    PolygonMarketIndicesFetcher,
)
from openbb_polygon.models.market_snapshots import PolygonMarketSnapshotsFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apiKey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_polygon_equity_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "AAPL",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
        "interval": "1d",
    }

    fetcher = PolygonEquityHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_market_indices_fetcher(credentials=test_credentials):
    params = {
        "symbol": "NDX",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 5, 10),
    }

    fetcher = PolygonMarketIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_company_news_fetcher(credentials=test_credentials):
    params = {"symbols": "AAPL"}

    fetcher = PolygonCompanyNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_balance_sheet_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = PolygonBalanceSheetFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_income_statement_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = PolygonIncomeStatementFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_cash_flow_statement_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = PolygonCashFlowStatementFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_crypto_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "BTCUSD",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = PolygonCryptoHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_currency_historical_fetcher(credentials=test_credentials):
    params = {
        "symbol": "EURUSD",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 1, 10),
    }

    fetcher = PolygonCurrencyHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_currency_pairs_fetcher(credentials=test_credentials):
    params = {"date": date(2023, 1, 1)}

    fetcher = PolygonCurrencyPairsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_equity_nbbo_fetcher(credentials=test_credentials):
    params = {"symbol": "SPY", "limit": 1000}

    fetcher = PolygonEquityNBBOFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_market_snapshots_fetcher(credentials=test_credentials):
    params = {}

    fetcher = PolygonMarketSnapshotsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
