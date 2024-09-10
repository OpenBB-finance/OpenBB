"""OpenBB IMF Provider Module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_imf.models.available_indicators import ImfAvailableIndicatorsFetcher
from openbb_imf.models.economic_indicators import ImfEconomicIndicatorsFetcher

imf_provider = Provider(
    name="imf",
    website="https://datahelp.imf.org/knowledgebase/articles/667681-using-json-restful-web-service",
    description="""The mission of the Commodity Futures Trading Commission (CFTC) is to promote the integrity, resilience, and vibrancy of the U.S. derivatives markets through sound regulation.""",
    fetcher_dict={
        "AvailableIndicators": ImfAvailableIndicatorsFetcher,
        "EconomicIndicators": ImfEconomicIndicatorsFetcher,
    },
    repr_name="International Monetary Fund (IMF) Public Data API",
    instructions="",
)
