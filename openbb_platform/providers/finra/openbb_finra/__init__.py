"""FINRA provider module."""
from openbb_finra.models.equity_short_interest import FinraShortInterestFetcher
from openbb_finra.models.otc_aggregate import FinraOTCAggregateFetcher
from openbb_provider.abstract.provider import Provider

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
