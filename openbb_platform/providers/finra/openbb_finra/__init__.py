"""FINRA provider module."""
from openbb_finra.models.otc_aggregate import FinraOTCAggregateFetcher
from openbb_provider.abstract.provider import Provider

finra_provider = Provider(
    name="finra",
    website="https://finra.org",
    description="Financial Industry Regulatory Authority.",
    required_credentials=None,
    fetcher_dict={"OTCAggregate": FinraOTCAggregateFetcher},
)
