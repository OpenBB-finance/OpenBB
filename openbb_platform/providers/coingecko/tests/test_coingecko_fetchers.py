"""Tests for CoinGecko fetchers."""

from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_coingecko.models.crypto_historical import (
    CoinGeckoCryptoHistoricalFetcher,
)
from openbb_coingecko.utils.helpers import split_crypto_symbol

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)
test_credentials = (
    test_credentials
    if test_credentials and test_credentials.get("coingecko_api_key")
    else {"coingecko_api_key": "MOCK_API_KEY"}
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [
            ("x-cg-pro-api-key", "MOCK_API_KEY"),
            ("User-Agent", None),
        ],
    }


def test_split_crypto_symbol_variants():
    """Normalize different pair syntaxes."""
    assert split_crypto_symbol("btcusd") == ("BTC", "USD")
    assert split_crypto_symbol("eth-usd") == ("ETH", "USD")
    assert split_crypto_symbol("SOL/USDT") == ("SOL", "USDT")


def test_coingecko_crypto_historical_transform_query_defaults():
    """Default to a one-year trailing window."""
    query = CoinGeckoCryptoHistoricalFetcher.transform_query({"symbol": "BTCUSD"})

    assert query.end_date == date.today()
    assert query.start_date is not None
    assert 364 <= (query.end_date - query.start_date).days <= 366


def test_coingecko_crypto_historical_transform_data():
    """Map OHLCV arrays into OpenBB's standard fields."""
    query = CoinGeckoCryptoHistoricalFetcher.transform_query(
        {
            "symbol": "BTCUSD",
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 1, 2),
            "interval": "1d",
        }
    )
    data = [
        {
            "symbol": "BTCUSD",
            "coin_id": "bitcoin",
            "ohlcv": [
                [1704067200000, 42000.0, 43000.0, 41000.0, 42500.0, 1000.0],
                [1704153600000, 42500.0, 43500.0, 42000.0, 43300.0, 1100.0],
            ],
        }
    ]

    transformed = CoinGeckoCryptoHistoricalFetcher.transform_data(query, data)

    assert len(transformed) == 2
    assert transformed[0].date == date(2024, 1, 1)
    assert transformed[0].open == 42000.0
    assert transformed[0].high == 43000.0
    assert transformed[0].low == 41000.0
    assert transformed[0].close == 42500.0
    assert transformed[0].volume == 1000.0
    assert transformed[0].symbol == "BTCUSD"
    assert transformed[0].coin_id == "bitcoin"


@pytest.mark.record_http
def test_coingecko_crypto_historical_fetcher(credentials=test_credentials):
    """Test CoinGecko crypto historical fetcher with recorded HTTP."""
    params = {
        "symbol": "BTCUSD",
        "start_date": date(2024, 1, 1),
        "end_date": date(2024, 1, 7),
        "interval": "1d",
    }

    fetcher = CoinGeckoCryptoHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_coingecko_crypto_historical_fetcher_pair_format(credentials=test_credentials):
    """Test CoinGecko historical fetcher with separator-based pair notation."""
    params = {
        "symbol": "ETH-USD",
        "start_date": date(2024, 1, 1),
        "end_date": date(2024, 1, 7),
        "interval": "1d",
    }

    fetcher = CoinGeckoCryptoHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
