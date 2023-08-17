"""Available Indices data model."""


from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class AvailableIndicesQueryParams(QueryParams):
    """Available Indices Query."""


class AvailableIndicesData(Data, BaseSymbol):
    """Available Indices Data.

    Returns the major indices from Dow Jones, Nasdaq and, S&P 500.
    """

    name: Optional[str] = Field(description="Name of the index.")
    currency: Optional[str] = Field(description="Currency the index is traded in.")
    stock_exchange: str = Field(description="Stock exchange where the index is listed.")
    exchange_short_name: str = Field(
        description="Short name of the stock exchange where the index is listed."
    )
