"""Test the Polygon fetchers."""

import time
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_core.provider.utils.websockets.client import WebSocketClient
from openbb_polygon.models.balance_sheet import PolygonBalanceSheetFetcher
from openbb_polygon.models.cash_flow import PolygonCashFlowStatementFetcher
from openbb_polygon.models.company_news import PolygonCompanyNewsFetcher
from openbb_polygon.models.crypto_historical import PolygonCryptoHistoricalFetcher
from openbb_polygon.models.currency_historical import PolygonCurrencyHistoricalFetcher
from openbb_polygon.models.currency_pairs import PolygonCurrencyPairsFetcher
from openbb_polygon.models.currency_snapshots import PolygonCurrencySnapshotsFetcher
from openbb_polygon.models.equity_historical import PolygonEquityHistoricalFetcher
from openbb_polygon.models.equity_nbbo import PolygonEquityNBBOFetcher
from openbb_polygon.models.income_statement import PolygonIncomeStatementFetcher
from openbb_polygon.models.index_historical import (
    PolygonIndexHistoricalFetcher,
)
from openbb_polygon.models.market_snapshots import PolygonMarketSnapshotsFetcher
from openbb_polygon.models.websocket_connection import (
    PolygonWebSocketConnection,
    PolygonWebSocketData,
    PolygonWebSocketFetcher,
)

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)

MOCK_WEBSOCKET_DATA = [
    {
        "date": "2024-12-12T21:04:02-05:00",
        "symbol": "BTC-USD",
        "type": "XAS",
        "open": 99445.07,
        "high": 99445.08,
        "low": 99445.07,
        "close": 99445.08,
        "volume": 0.00188791,
        "vwap": 99445.0778,
    },
    {
        "date": "2024-12-12T21:04:03-05:00",
        "symbol": "BTC-USD",
        "type": "XAS",
        "open": 99445.07,
        "high": 99445.08,
        "low": 99445.07,
        "close": 99445.07,
        "volume": 0.00670653,
        "vwap": 99445.0702,
    },
    {
        "date": "2024-12-12T21:04:04-05:00",
        "symbol": "BTC-USD",
        "type": "XAS",
        "open": 99445.07,
        "high": 99445.07,
        "low": 99445.07,
        "close": 99445.07,
        "volume": 0.00007158,
        "vwap": 99445.07,
    },
    {
        "date": "2024-12-12T21:04:05-05:00",
        "symbol": "BTC-USD",
        "type": "XAS",
        "open": 99445.07,
        "high": 99445.07,
        "low": 99428.34,
        "close": 99428.34,
        "volume": 0.6058888,
        "vwap": 99441.6093,
    },
    {
        "date": "2024-12-12T21:04:06-05:00",
        "symbol": "BTC-USD",
        "type": "XAS",
        "open": 99428.33,
        "high": 99428.34,
        "low": 99428.33,
        "close": 99428.34,
        "volume": 0.01953452,
        "vwap": 99428.3301,
    },
    {
        "date": "2024-12-12T21:04:07-05:00",
        "symbol": "BTC-USD",
        "type": "XAS",
        "open": 99428.33,
        "high": 99428.34,
        "low": 99428.33,
        "close": 99428.33,
        "volume": 0.1214753,
        "vwap": 99428.33,
    },
    {
        "date": "2024-12-12T21:04:08-05:00",
        "symbol": "BTC-USD",
        "type": "XAS",
        "open": 99428.33,
        "high": 99435.48,
        "low": 99428.33,
        "close": 99435.48,
        "volume": 0.20089819,
        "vwap": 99429.29,
    },
    {
        "date": "2024-12-12T21:04:09-05:00",
        "symbol": "BTC-USD",
        "type": "XAS",
        "open": 99435.47,
        "high": 99435.47,
        "low": 99435.02,
        "close": 99435.02,
        "volume": 0.03098464,
        "vwap": 99435.3318,
    },
    {
        "date": "2024-12-12T21:04:10-05:00",
        "symbol": "BTC-USD",
        "type": "XAS",
        "open": 99445.08,
        "high": 99445.08,
        "low": 99445.05,
        "close": 99445.05,
        "volume": 0.00245657,
        "vwap": 99445.0502,
    },
    {
        "date": "2024-12-12T21:04:11-05:00",
        "symbol": "BTC-USD",
        "type": "XAS",
        "open": 99445.08,
        "high": 99445.08,
        "low": 99440.55,
        "close": 99440.55,
        "volume": 0.06000562,
        "vwap": 99443.6374,
    },
]


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apiKey", "MOCK_API_KEY"),
        ],
    }


@pytest.fixture
def mock_websocket_connection():
    """Mock websocket client."""

    mock_connection = PolygonWebSocketConnection(
        client=MagicMock(
            spec=WebSocketClient(
                name="polygon_test",
                module="openbb_polygon.utils.websocket_client",
                symbol="btcusd",
                limit=10,
                data_model=PolygonWebSocketData,
                url="wss://mock.polygon.com/crypto",
                api_key="MOCK_API_KEY",
            )
        )
    )
    mock_connection.client.is_running = False
    mock_results = []

    def mock_connect():
        mock_connection.client.is_running = True
        for data in MOCK_WEBSOCKET_DATA:
            mock_results.append(PolygonWebSocketData(**data))
            time.sleep(0.1)

    def mock_get_results():
        return mock_results

    mock_connection.client.connect = mock_connect
    mock_connection.client.results = mock_get_results

    return mock_connection


@pytest.mark.asyncio
async def test_websocket_fetcher(
    mock_websocket_connection, credentials=test_credentials
):
    """Test websocket fetcher."""
    fetcher = PolygonWebSocketFetcher()
    params = {
        "symbol": "btcusd",
        "name": "polygon_test",
        "limit": 10,
        "asset_type": "crypto",
        "feed": "aggs_sec",
    }

    with patch.object(fetcher, "fetch_data", return_value=mock_websocket_connection):
        result = await fetcher.fetch_data(params, credentials)

        # Ensure the client is not running initially
        assert not result.client.is_running
        assert result.client.results() == []
        result.client.connect()
        assert result.client.is_running
        assert len(result.client.results()) == len(MOCK_WEBSOCKET_DATA)
        assert result.client.results()[0] == PolygonWebSocketData(
            **MOCK_WEBSOCKET_DATA[0]
        )


@pytest.mark.record_http
def test_polygon_equity_historical_fetcher(credentials=test_credentials):
    """Test the Polygon Equity Historical fetcher."""
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
def test_polygon_index_historical_fetcher(credentials=test_credentials):
    """Test the Polygon Index Historical fetcher."""
    params = {
        "symbol": "NDX",
        "start_date": date(2023, 1, 1),
        "end_date": date(2023, 5, 10),
    }

    fetcher = PolygonIndexHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_company_news_fetcher(credentials=test_credentials):
    """Test the Polygon Company News fetcher."""
    params = {"symbol": "AAPL"}

    fetcher = PolygonCompanyNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_balance_sheet_fetcher(credentials=test_credentials):
    """Test the Polygon Balance Sheet fetcher."""
    params = {"symbol": "AAPL"}

    fetcher = PolygonBalanceSheetFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_income_statement_fetcher(credentials=test_credentials):
    """Test the Polygon Income Statement fetcher."""
    params = {"symbol": "AAPL"}

    fetcher = PolygonIncomeStatementFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_cash_flow_statement_fetcher(credentials=test_credentials):
    """Test the Polygon Cash Flow Statement fetcher."""
    params = {"symbol": "AAPL"}

    fetcher = PolygonCashFlowStatementFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_crypto_historical_fetcher(credentials=test_credentials):
    """Test the Polygon Crypto Historical fetcher."""
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
    """Test the Polygon Currency Historical fetcher."""
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
    """Test the Polygon Currency Pairs fetcher."""
    params = {}

    fetcher = PolygonCurrencyPairsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_equity_nbbo_fetcher(credentials=test_credentials):
    """Test the Polygon Equity NBBO fetcher."""
    params = {"symbol": "SPY", "limit": 1000}

    fetcher = PolygonEquityNBBOFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_market_snapshots_fetcher(credentials=test_credentials):
    """Test the Polygon Market Snapshots fetcher."""
    params = {}

    fetcher = PolygonMarketSnapshotsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_polygon_currency_snapshots_fetcher(credentials=test_credentials):
    """Test the Polygon Currency Snapshots fetcher."""
    params = {"base": "XAU"}

    fetcher = PolygonCurrencySnapshotsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
