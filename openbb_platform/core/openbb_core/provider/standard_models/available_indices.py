"""Available Indices Standard Model."""

from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class AvailableIndicesQueryParams(QueryParams):
    """Available Indices Query."""


class AvailableIndicesData(Data):
    """Available Indices Data.

    Returns the list of available indices from a provider.
    """

    symbol: str = Field(description="Ticker symbol of the index.")
    name: Optional[str] = Field(default=None, description="Name of the index.")
    exchange: Optional[str] = Field(
        default=None, description="Stock exchange where the index is listed."
    )
    currency: Optional[str] = Field(
        default=None, description="Currency the index is traded in."
    )
