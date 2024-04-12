"""Available Indicators Standard Model."""

from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams


class AvailableIndicesQueryParams(QueryParams):
    """Available Indicators Query."""


class AvailableIndicatorsData(Data):
    """Available Indicators Data.

    Returns the list of available economic indicators from a provider.
    """

    indicator_symbol: Optional[str] = Field(
        default=None, description="The root symbol representing the indicator."
    )
    symbol: Optional[str] = Field(
        default=None, description="The root symbol with additional codes."
    )
    country: Optional[str] = Field(
        default=None,
        description="The name of the country, region, or entity represented by the symbol.",
    )
    iso: Optional[str] = Field(
        default=None,
        description="The ISO code of the country, region, or entity represented by the symbol.",
    )
    description: Optional[str] = Field(
        default=None, description="The description of the indicator."
    )
    frequency: Optional[str] = Field(
        default=None, description="The frequency of the indicator data."
    )
