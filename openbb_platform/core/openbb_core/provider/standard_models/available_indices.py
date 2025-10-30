"""Available Indices Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
)
from pydantic import Field


class AvailableIndicesQueryParams(QueryParams):
    """Available Indices Query."""


class AvailableIndicesData(Data):
    """Available Indices Data.

    Returns the list of available indices from a provider.
    """

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("name", "")
    )
    exchange: str | None = Field(
        default=None, description="Stock exchange where the index is listed."
    )
    currency: str | None = Field(
        default=None, description="Currency the index is traded in."
    )
