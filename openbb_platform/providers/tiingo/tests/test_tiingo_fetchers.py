"""Test Tiingo fetchers."""

import time
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_tiingo.models.company_news import TiingoCompanyNewsFetcher
from openbb_tiingo.models.crypto_historical import TiingoCryptoHistoricalFetcher
from openbb_tiingo.models.currency_historical import TiingoCurrencyHistoricalFetcher
from openbb_tiingo.models.equity_historical import TiingoEquityHistoricalFetcher
from openbb_tiingo.models.trailing_dividend_yield import TiingoTrailingDivYieldFetcher
from openbb_tiingo.models.websocket_connection import (
    TiingoWebSocketConnection,
    TiingoWebSocketData,
    TiingoWebSocketFetcher,
)
from openbb_tiingo.models.world_news import TiingoWorldNewsFetcher
from openbb_websockets.client import WebSocketClient

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)

MOCK_WEBSOCKET_DATA = [
    {
        "date": "2024-12-12 16:57:50.164993-0500",
        "symbol": "BTCUSD",
        "type": "trade",
        "exchange": "gdax",
        "last_price": 99818.08814355676,
        "last_size": 0.01445296,
    },
    {
        "date": "2024-12-12 16:57:50.697317-0500",
        "symbol": "BTCUSD",
        "type": "trade",
        "exchange": "kraken",
        "last_price": 99810.1,
        "last_size": 6.856e-05,
    },
    {
        "date": "2024-12-12 16:57:51.119000-0500",
        "symbol": "BTCUSD",
        "type": "trade",
        "exchange": "gemini",
        "last_price": 99827.02771283902,
        "last_size": 0.19860106,
    },
    {
        "date": "2024-12-12 16:57:52.573000-0500",
        "symbol": "BTCUSD",
        "type": "trade",
        "exchange": "bitfinex",
        "last_price": 99780.0,
        "last_size": 8.6e-05,
    },
    {
        "date": "2024-12-12 16:57:55.187865-0500",
        "symbol": "BTCUSD",
        "type": "trade",
        "exchange": "gdax",
        "last_price": 99837.23198173672,
        "last_size": 1.50565886,
    },
    {
        "date": "2024-12-12 16:57:55-0500",
        "symbol": "BTCUSD",
        "type": "trade",
        "exchange": "bitstamp",
        "last_price": 99862.0,
        "last_size": 0.00212959,
    },
    {
        "date": "2024-12-12 16:57:57.647609-0500",
        "symbol": "BTCUSD",
        "type": "trade",
        "exchange": "kraken",
        "last_price": 99819.24927536234,
        "last_size": 0.00207,
    },
    {
        "date": "2024-12-12 16:58:00.009694-0500",
        "symbol": "BTCUSD",
        "type": "trade",
        "exchange": "gdax",
        "last_price": 99838.34191368945,
        "last_size": 0.037644090000000005,
    },
]


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.fixture
def mock_websocket_connection():
    """Mock websocket client."""

    mock_connection = TiingoWebSocketConnection(
        client=MagicMock(
            spec=WebSocketClient(
                name="tiingo_test",
                module="openbb_tiingo.utils.websocket_client",
                symbol="btcusd",
                limit=10,
                data_model=TiingoWebSocketData,
                url="wss://mock.tiingo.com/iex",
                api_key="MOCK_TOKEN",
            )
        )
    )
    mock_connection.client.is_running = False
    mock_results = []

    def mock_connect():
        mock_connection.client.is_running = True
        for data in MOCK_WEBSOCKET_DATA:
            mock_results.append(TiingoWebSocketData(**data))
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
    fetcher = TiingoWebSocketFetcher()
    params = {
        "symbol": "btcusd",
        "name": "tiingo_test",
        "limit": 10,
        "asset_type": "crypto",
    }

    with patch.object(fetcher, "fetch_data", return_value=mock_websocket_connection):
        result = await fetcher.fetch_data(params, credentials)

        # Ensure the client is not running initially
        assert not result.client.is_running
        assert result.client.results() == []
        result.client.connect()
        assert result.client.is_running
        assert len(result.client.results()) == len(MOCK_WEBSOCKET_DATA)
        assert result.client.results()[0] == TiingoWebSocketData(
            **MOCK_WEBSOCKET_DATA[0]
        )


@pytest.mark.record_http
def test_tiingo_equity_historical_fetcher(credentials=test_credentials):
    """Test Tiingo equity historical fetcher."""
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
    """Test Tiingo company news fetcher."""
    params = {"symbol": "AAPL,MSFT"}

    fetcher = TiingoCompanyNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tiingo_world_news_fetcher(credentials=test_credentials):
    """Test Tiingo world news fetcher."""
    params = {"limit": 20}

    fetcher = TiingoWorldNewsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_tiingo_crypto_historical_fetcher(credentials=test_credentials):
    """Test Tiingo crypto historical fetcher."""
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
    """Test Tiingo currency historical fetcher."""
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
    """Test Tiingo trailing dividend yield fetcher."""
    params = {"symbol": "SCHD"}

    fetcher = TiingoTrailingDivYieldFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
