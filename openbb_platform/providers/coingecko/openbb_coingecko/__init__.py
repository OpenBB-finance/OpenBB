"""CoinGecko Provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_coingecko.models.crypto_historical import CoinGeckoCryptoHistoricalFetcher

coingecko_provider = Provider(
    name="coingecko",
    website="https://www.coingecko.com",
    description="Provider for CoinGecko.",
    fetcher_dict={
        "CryptoHistorical": CoinGeckoCryptoHistoricalFetcher,
    },
)
