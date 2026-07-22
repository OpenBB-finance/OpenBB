"""CoinGecko provider module."""

from openbb_coingecko.models.crypto_historical import CoinGeckoCryptoHistoricalFetcher
from openbb_core.provider.abstract.provider import Provider

coingecko_provider = Provider(
    name="coingecko",
    website="https://www.coingecko.com/en/api",
    description="""CoinGecko provides cryptocurrency market data APIs for price,
market cap, and OHLCV datasets across centralized and decentralized markets.""",
    credentials=["api_key"],
    fetcher_dict={
        "CryptoHistorical": CoinGeckoCryptoHistoricalFetcher,
    },
    repr_name="CoinGecko Pro",
    instructions='Go to: https://www.coingecko.com/en/api/pricing\n\nCreate a CoinGecko account, subscribe to a paid API plan, and copy the API key from the dashboard. Configure it as "coingecko_api_key" in OpenBB credentials.',  # noqa: E501  pylint: disable=line-too-long
)

