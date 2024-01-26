"""FINRA provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_finra.models.equity_short_interest import FinraShortInterestFetcher
from openbb_finra.models.otc_aggregate import FinraOTCAggregateFetcher

finra_provider = Provider(
    name="finra",
    website="https://finra.org",
    description="Financial Industry Regulatory Authority.",
    credentials=None,
    fetcher_dict={
        "OTCAggregate": FinraOTCAggregateFetcher,
        "EquityShortInterest": FinraShortInterestFetcher,
    },
)
