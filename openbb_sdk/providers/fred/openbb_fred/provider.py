"""FRED provider module."""
from openbb_provider.abstract.provider import Provider

from openbb_fred.models.cpi import FREDCPIFetcher

fred_provider = Provider(
    name="fred",
    description="Provider for FRED.",
    required_credentials=["api_key"],
    fetcher_dict={"CPI": FREDCPIFetcher},
)
