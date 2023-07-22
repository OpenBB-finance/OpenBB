"""FRED provider module."""

# IMPORT STANDARD
# IMPORT THIRD-PARTY
# IMPORT INTERNAL
from openbb_provider.abstract.provider import Provider, ProviderNameType

from openbb_fred.models.cpi import FREDCPIFetcher

# mypy: disable-error-code="list-item"

fred_provider = Provider(
    name=ProviderNameType("fred"),
    description="Provider for FRED.",
    required_credentials=["api_key"],
    fetcher_list=[FREDCPIFetcher],
)
