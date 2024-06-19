"""Tradier Provider Module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_tradier.models.equity_historical import TradierEquityHistoricalFetcher
from openbb_tradier.models.equity_quote import TradierEquityQuoteFetcher
from openbb_tradier.models.equity_search import TradierEquitySearchFetcher
from openbb_tradier.models.options_chains import TradierOptionsChainsFetcher

tradier_provider = Provider(
    name="tradier",
    website="https://tradier.com",
    description="""Tradier provides a full range of services in a scalable, secure,
and easy-to-use REST-based API for businesses and individual developers.
Fast, secure, simple. Start in minutes.
Get access to trading, account management, and market-data for
Tradier Brokerage accounts through our APIs.""",
    credentials=[
        "api_key",
        "account_type",
    ],  # account_type is either "sandbox" or "live"
    fetcher_dict={
        "EquityHistorical": TradierEquityHistoricalFetcher,
        "EtfHistorical": TradierEquityHistoricalFetcher,
        "EquityQuote": TradierEquityQuoteFetcher,
        "EquitySearch": TradierEquitySearchFetcher,
        "OptionsChains": TradierOptionsChainsFetcher,
    },
    repr_name="Tradier",
    deprecated_credentials={"API_TRADIER_TOKEN": "tradier_api_key"},
    instructions='Go to: https://documentation.tradier.com\n\n![Tradier](https://user-images.githubusercontent.com/46355364/207829178-a8bba770-f2ea-4480-b28e-efd81cf30980.png)\n\nClick on, "Open Account", to start the sign-up process. After the account has been setup, navigate to [Tradier Broker Dash](https://dash.tradier.com/login?redirect=settings.api) and create the application. Request a sandbox access token.',  # noqa: E501  pylint: disable=line-too-long
)
