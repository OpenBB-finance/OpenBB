import pytest
from openbb import obb
from openbb_polygon.models.balance_sheet import PolygonBalanceSheetFetcher
from openbb_polygon.models.cash_flow import PolygonCashFlowStatementFetcher
from openbb_polygon.models.crypto_historical import PolygonCryptoHistoricalFetcher
from openbb_polygon.models.forex_historical import PolygonForexHistoricalFetcher
from openbb_polygon.models.forex_pairs import PolygonForexPairsFetcher
from openbb_polygon.models.income_statement import PolygonIncomeStatementFetcher
from openbb_polygon.models.major_indices_historical import (
    PolygonMajorIndicesHistoricalFetcher,
)
from openbb_polygon.models.stock_historical import PolygonStockHistoricalFetcher
from openbb_polygon.models.stock_news import PolygonStockNewsFetcher

test_credentials = obb.user.credentials.__dict__


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apiKey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_polygon_stock_historical_fetcher(credentials=test_credentials):
    params = {"symbol": "AAPL"}

    fetcher = PolygonStockHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_major_indices_historical_fetcher(credentials=test_credentials):
    params = {"symbol": "DJI"}

    fetcher = PolygonMajorIndicesHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_stock_news_fetcher(credentials=test_credentials):
    params = {"symbols": "AAPL,MSFT"}

    fetcher = PolygonStockNewsFetcher()
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
    params = {"symbol": "BTC/USD"}

    fetcher = PolygonCryptoHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_forex_historical_fetcher(credentials=test_credentials):
    params = {"symbol": "EUR/USD"}

    fetcher = PolygonForexHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_forex_pairs_fetcher(credentials=test_credentials):
    params = {}

    fetcher = PolygonForexPairsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
