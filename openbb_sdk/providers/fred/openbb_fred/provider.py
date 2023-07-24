"""FRED provider module."""

# IMPORT STANDARD
# IMPORT THIRD-PARTY
# IMPORT INTERNAL
from openbb_provider.abstract.provider import Provider

from openbb_fred.cpi import FREDCPIFetcher

# mypy: disable-error-code="list-item"

fred_provider = Provider(
    name="fred",
    description="Provider for FRED.",
    required_credentials=["api_key"],
    fetcher_list=[FREDCPIFetcher],
)
