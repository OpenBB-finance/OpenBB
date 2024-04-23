"""EconDB provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_econdb.models.available_indicators import EconDbAvailableIndicatorsFetcher
from openbb_econdb.models.country_profile import EconDbCountryProfileFetcher
from openbb_econdb.models.economic_indicators import EconDbEconomicIndicatorsFetcher

econdb_provider = Provider(
    name="EconDB",
    website="https://econdb.com/",
    description="""EconDB is a provider of data.""",
    credentials=[
        "api_key"
    ],  # Can be left as None, an attempt to use a temporaray token will be made.
    fetcher_dict={
        "AvailableIndicators": EconDbAvailableIndicatorsFetcher,
        "CountryProfile": EconDbCountryProfileFetcher,
        "EconomicIndicators": EconDbEconomicIndicatorsFetcher,
    },
)
