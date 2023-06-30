"""FRED provider module."""

# IMPORT STANDARD
# IMPORT THIRD-PARTY
# IMPORT INTERNAL
from builtin_providers.fred.cpi import FREDCPIFetcher
from openbb_provider.provider.abstract.provider import Provider

# mypy: disable-error-code="list-item"

# ignoring because I dont know how to type the string properly
fred_provider = Provider(
    name="fred",  # type: ignore
    description="Provider for FRED.",
    fetcher_list=[FREDCPIFetcher],
)
