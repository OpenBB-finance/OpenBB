"""Headless Oracle provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_headless_oracle.models.market_state import HeadlessOracleMarketStateFetcher

headless_oracle_provider = Provider(
    name="headless_oracle",
    website="https://headlessoracle.com",
    description="Signed market-state receipts for exchange-open verification.",
    credentials=[],
    fetcher_dict={
        "MarketState": HeadlessOracleMarketStateFetcher,
    },
    repr_name="Headless Oracle",
)
