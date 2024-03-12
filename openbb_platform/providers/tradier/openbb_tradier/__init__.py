"""Tradier Provider Module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_tradier.models.equity_historical import TradierEquityHistoricalFetcher
from openbb_tradier.models.equity_quote import TradierEquityQuoteFetcher
from openbb_tradier.models.equity_search import TradierEquitySearchFetcher
from openbb_tradier.models.options_chains import TradierOptionsChainsFetcher

tradier_provider = Provider(
    name="tradier",
    website="https://tradier.com",
    description="Tradier provides a full range of services in a scalable, secure,"
    + " and easy-to-use REST-based API for businesses and individual developers."
    + " Fast, secure, simple. Start in minutes."
    + " Get access to trading, account management, and market-data for"
    + " Tradier Brokerage accounts through our APIs.",
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
)
