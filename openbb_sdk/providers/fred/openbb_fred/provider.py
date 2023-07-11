"""FRED provider module."""

# IMPORT STANDARD
# IMPORT THIRD-PARTY
# IMPORT INTERNAL
from builtin_providers.fred.cpi import FREDCPIFetcher
from openbb_provider.provider.abstract.provider import Provider, ProviderNameType

# mypy: disable-error-code="list-item"

fred_provider = Provider(
    name=ProviderNameType("fred"),
    description="Provider for FRED.",
    fetcher_list=[FREDCPIFetcher],
)
