"""Test the CryptoCompare fetchers."""

from datetime import datetime

import pytest
from openbb_core.app.service.user_service import UserService

from openbb_cryptocompare.models.crypto_quote import (
    CryptoCompareCryptoQuoteData,
    CryptoCompareCryptoQuoteFetcher,
    CryptoCompareCryptoQuoteQueryParams,
)
from openbb_cryptocompare.models.crypto_historical import (
    CryptoCompareCryptoHistoricalData,
    CryptoCompareCryptoHistoricalFetcher,
    CryptoCompareCryptoHistoricalQueryParams,
)
from openbb_cryptocompare.models.crypto_search import (
    CryptoCompareCryptoSearchData,
    CryptoCompareCryptoSearchFetcher,
    CryptoCompareCryptoSearchQueryParams,
)


test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


# ── Unit Tests (no API key required) ──────────────────────────────────────


class TestCryptoQuoteTransform:
    """Test the CryptoQuote transform_data logic with mock API responses."""

    def test_transform_quote_single_coin(self):
        """Test parsing a single coin from the pricemultifull response."""
        mock_response = {
            "RAW": {
                "BTC": {
                    "USD": {
                        "PRICE": 50000.0,
                        "CHANGE24HOUR": 100.0,
                        "CHANGEPCT24HOUR": 0.5,
                        "OPEN24HOUR": 49900.0,
                        "HIGH24HOUR": 50200.0,
                        "LOW24HOUR": 49800.0,
                        "VOLUME24HOUR": 100000.0,
                        "VOLUME24HOURTO": 95000.0,
                        "MKTCAP": 1000000000.0,
                        "SUPPLY": 19000000.0,
                        "TOTALSUPPLY": 21000000.0,
                        "LASTUPDATE": 1700000000,
                    }
                }
            }
        }
        query = CryptoCompareCryptoQuoteQueryParams(symbol="BTC")
        results = CryptoCompareCryptoQuoteFetcher.transform_data(
            query=query, data=mock_response
        )
        assert len(results) == 1
        assert results[0].symbol == "BTC"
        assert results[0].price == 50000.0
        assert results[0].change == 100.0
        assert results[0].change_percent == 0.005
        assert results[0].volume_24h == 100000.0
        assert results[0].market_cap == 1000000000.0
        assert results[0].last_timestamp == datetime.fromtimestamp(1700000000)

    def test_transform_quote_multiple_coins(self):
        """Test parsing multiple coins."""
        mock_response = {
            "RAW": {
                "BTC": {"USD": {"PRICE": 50000.0, "CHANGE24HOUR": 100.0}},
                "ETH": {"USD": {"PRICE": 3000.0, "CHANGE24HOUR": 20.0}},
                "SOL": {"USD": {"PRICE": 150.0, "CHANGE24HOUR": 5.0}},
            }
        }
        query = CryptoCompareCryptoQuoteQueryParams(symbol="BTC,ETH,SOL")
        results = CryptoCompareCryptoQuoteFetcher.transform_data(
            query=query, data=mock_response
        )
        assert len(results) == 3

    def test_transform_quote_custom_currency(self):
        """Test parsing with a custom currency."""
        mock_response = {
            "RAW": {"BTC": {"EUR": {"PRICE": 46000.0, "CHANGE24HOUR": 90.0}}}
        }
        query = CryptoCompareCryptoQuoteQueryParams(symbol="BTC", currency="EUR")
        results = CryptoCompareCryptoQuoteFetcher.transform_data(
            query=query, data=mock_response
        )
        assert len(results) == 1
        assert results[0].price == 46000.0
        assert results[0].currency == "EUR"

    def test_transform_quote_empty_coins(self):
        """Test that coins not in the response are skipped."""
        mock_response = {"RAW": {}}
        query = CryptoCompareCryptoQuoteQueryParams(symbol="DOGE")
        results = CryptoCompareCryptoQuoteFetcher.transform_data(
            query=query, data=mock_response
        )
        assert len(results) == 0

    def test_transform_quote_error_response(self):
        """Test error handling."""
        mock_response = {"Err": {"type": 2, "message": "API key required"}}
        query = CryptoCompareCryptoQuoteQueryParams(symbol="BTC")
        with pytest.raises(RuntimeError, match="API key required"):
            CryptoCompareCryptoQuoteFetcher.transform_data(
                query=query, data=mock_response
            )

    def test_missing_coin_data(self):
        """Test that a coin with no price data is skipped."""
        mock_response = {"RAW": {"BTC": {"USD": {"PRICE": 50000.0}}, "ETH": {"USD": {}}}}
        query = CryptoCompareCryptoQuoteQueryParams(symbol="BTC,ETH")
        results = CryptoCompareCryptoQuoteFetcher.transform_data(
            query=query, data=mock_response
        )
        assert len(results) == 1
        assert results[0].symbol == "BTC"


class TestCryptoHistoricalTransform:
    """Test the CryptoHistorical transform_data logic."""

    def test_transform_historical_data(self):
        """Test parsing historical OHLCV data."""
        mock_response = {
            "Data": {
                "Data": [
                    {"time": 1700000000, "open": 49000.0, "high": 50200.0, "low": 48800.0, "close": 50000.0, "volumefrom": 10000.0, "volumeto": 500000000.0},
                    {"time": 1700086400, "open": 50000.0, "high": 51000.0, "low": 49800.0, "close": 50500.0, "volumefrom": 12000.0, "volumeto": 600000000.0},
                    {"time": 1700172800, "open": 50500.0, "high": 51500.0, "low": 50300.0, "close": 51000.0, "volumefrom": 8000.0, "volumeto": 400000000.0},
                ]
            }
        }
        query = CryptoCompareCryptoHistoricalQueryParams(symbol="BTC", limit=3)
        results = CryptoCompareCryptoHistoricalFetcher.transform_data(
            query=query, data=mock_response
        )
        assert len(results) == 3
        assert results[0].open == 49000.0
        assert results[0].close == 50000.0
        assert results[0].volume == 500000000.0

    def test_transform_historical_empty(self):
        """Test empty historical data."""
        mock_response = {"Data": {"Data": []}}
        query = CryptoCompareCryptoHistoricalQueryParams(symbol="BTC")
        results = CryptoCompareCryptoHistoricalFetcher.transform_data(
            query=query, data=mock_response
        )
        assert len(results) == 0

    def test_transform_historical_error(self):
        """Test error handling."""
        mock_response = {"Err": {"type": 1, "message": "Invalid symbol"}}
        query = CryptoCompareCryptoHistoricalQueryParams(symbol="INVALID")
        with pytest.raises(RuntimeError, match="Invalid symbol"):
            CryptoCompareCryptoHistoricalFetcher.transform_data(
                query=query, data=mock_response
            )


class TestCryptoSearchTransform:
    """Test the CryptoSearch transform_data logic."""

    def test_transform_search_results(self):
        """Test parsing the coin list."""
        mock_response = {
            "Data": {
                "BTC": {"symbol": "BTC", "coin_name": "Bitcoin", "rank": 1},
                "ETH": {"symbol": "ETH", "coin_name": "Ethereum", "rank": 2},
                "SOL": {"symbol": "SOL", "coin_name": "Solana", "rank": 5},
            }
        }
        query = CryptoCompareCryptoSearchQueryParams(query="BTC")
        results = CryptoCompareCryptoSearchFetcher.transform_data(
            query=query, data=mock_response
        )
        assert len(results) == 1
        assert results[0].symbol == "BTC"
        assert results[0].name == "Bitcoin"
        assert results[0].market_cap_rank == 1

    def test_transform_search_no_query(self):
        """Test without filtering."""
        mock_response = {
            "Data": {
                "BTC": {"symbol": "BTC", "coin_name": "Bitcoin"},
                "ETH": {"symbol": "ETH", "coin_name": "Ethereum"},
            }
        }
        query = CryptoCompareCryptoSearchQueryParams(query=None)
        results = CryptoCompareCryptoSearchFetcher.transform_data(
            query=query, data=mock_response
        )
        assert len(results) == 2

    def test_transform_search_error(self):
        """Test error handling."""
        mock_response = {"Err": {"type": 2, "message": "API key required"}}
        query = CryptoCompareCryptoSearchQueryParams(query="BTC")
        with pytest.raises(RuntimeError, match="API key required"):
            CryptoCompareCryptoSearchFetcher.transform_data(
                query=query, data=mock_response
            )


class TestCryptoQuoteQueryParams:
    """Test the CryptoQuote query params."""

    def test_symbol_uppercase(self):
        """Test that symbols are uppercased."""
        params = CryptoCompareCryptoQuoteQueryParams(symbol="btc")
        assert params.symbol == "BTC"

    def test_default_currency(self):
        """Test default currency."""
        params = CryptoCompareCryptoQuoteQueryParams(symbol="BTC")
        assert params.currency == "USD"

    def test_multiple_symbols(self):
        """Test comma-separated symbols."""
        params = CryptoCompareCryptoQuoteQueryParams(symbol="btc,eth,sol")
        assert params.symbol == "BTC,ETH,SOL"


class TestCryptoQuoteDataModel:
    """Test the CryptoQuote data model."""

    def test_change_percent_passes_through(self):
        """Test that change_percent passes through (normalized in fetcher)."""
        data = CryptoCompareCryptoQuoteData(
            symbol="BTC", price=50000.0, change_percent=2.5
        )
        assert data.change_percent == 2.5

    def test_change_percent_keeps_decimal(self):
        """Test that values already in decimal format are not modified."""
        data = CryptoCompareCryptoQuoteData(
            symbol="BTC", price=50000.0, change_percent=0.025
        )
        assert data.change_percent == 0.025


# ── Integration Tests (require API key credential for recording) ──────────

@pytest.mark.record_http
def test_cryptocompare_crypto_quote_fetcher(credentials=test_credentials):
    """Test the crypto quote fetcher."""
    creds = dict(credentials)
    params = {"symbol": "BTC", "currency": "USD"}
    fetcher = CryptoCompareCryptoQuoteFetcher()
    result = fetcher.test(params, creds)
    assert result is None


@pytest.mark.record_http
def test_cryptocompare_crypto_historical_fetcher(credentials=test_credentials):
    """Test the crypto historical fetcher."""
    creds = dict(credentials)
    params = {"symbol": "BTC", "currency": "USD", "limit": 5}
    fetcher = CryptoCompareCryptoHistoricalFetcher()
    result = fetcher.test(params, creds)
    assert result is None


@pytest.mark.record_http
def test_cryptocompare_crypto_search_fetcher(credentials=test_credentials):
    """Test the crypto search fetcher."""
    creds = dict(credentials)
    params = {"query": "BTC"}
    fetcher = CryptoCompareCryptoSearchFetcher()
    result = fetcher.test(params, creds)
    assert result is None
