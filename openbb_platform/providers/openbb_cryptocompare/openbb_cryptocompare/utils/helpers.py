"""Helper utilities for the CryptoCompare provider."""

from typing import Any


def build_price_request_url(symbols: str, currency: str = "USD") -> str:
    """Build the pricemultifull request URL."""
    return f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={symbols}&tsyms={currency}"


def build_historical_request_url(
    symbol: str, currency: str = "USD", limit: int = 100, aggregate: int = 1
) -> str:
    """Build the histoday request URL."""
    return (
        f"https://min-api.cryptocompare.com/data/v2/histoday"
        f"?fsym={symbol}&tsym={currency}&limit={limit}&aggregate={aggregate}"
    )


def build_search_request_url() -> str:
    """Build the coin list request URL."""
    return "https://min-api.cryptocompare.com/data/blockchain/list"
