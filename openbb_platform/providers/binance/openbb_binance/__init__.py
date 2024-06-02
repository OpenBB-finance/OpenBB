"""Binance provider module."""

from openbb_core.provider.abstract.provider import Provider

from providers.binance.openbb_binance.models.crypto_historical import (
    BinanceCryptoHistoricalFetcher,
)

binance_provider = Provider(
    name="binance",
    website="https://api.binance.com",
    description="""Binance is a cryptocurrency exchange that provides a platform for trading various cryptocurrencies.

    The Binance API features both REST and WebSocket endpoints for accessing historical and real-time data.
    """,
    # credentials=["api_key"],
    fetcher_dict={
        "CryptoLive": BinanceCryptoHistoricalFetcher,
    },
    repr_name="Binance",
    instructions="",
)
