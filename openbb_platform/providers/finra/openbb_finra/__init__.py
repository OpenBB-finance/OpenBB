"""FINRA provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_finra.models.equity_short_interest import FinraShortInterestFetcher
from openbb_finra.models.otc_aggregate import FinraOTCAggregateFetcher

finra_provider = Provider(
    name="finra",
    website="https://www.finra.org/finra-data",
    description="""FINRA Data provides centralized access to the abundance of data FINRA
makes available to the public, media, researchers and member firms.""",
    credentials=None,
    fetcher_dict={
        "OTCAggregate": FinraOTCAggregateFetcher,
        "EquityShortInterest": FinraShortInterestFetcher,
    },
    repr_name="Financial Industry Regulatory Authority (FINRA)",
)
