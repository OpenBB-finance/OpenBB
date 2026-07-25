"""CryptoCompare provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_cryptocompare.models.crypto_quote import CryptoCompareCryptoQuoteFetcher
from openbb_cryptocompare.models.crypto_historical import (
    CryptoCompareCryptoHistoricalFetcher,
)
from openbb_cryptocompare.models.crypto_search import (
    CryptoCompareCryptoSearchFetcher,
)

cryptocompare_provider = Provider(
    name="cryptocompare",
    website="https://www.cryptocompare.com",
    description="CryptoCompare provides real-time and historical cryptocurrency market data.",
    credentials=["api_key"],
    fetcher_dict={
        "CryptoQuote": CryptoCompareCryptoQuoteFetcher,
        "CryptoHistorical": CryptoCompareCryptoHistoricalFetcher,
        "CryptoSearch": CryptoCompareCryptoSearchFetcher,
    },
)
