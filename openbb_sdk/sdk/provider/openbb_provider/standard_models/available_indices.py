"""Available Indices data model."""


from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class AvailableIndicesQueryParams(QueryParams):
    """Available Indices Query."""


class AvailableIndicesData(Data):
    """Available Indices Data.

    Returns the list of available indices from a provider.
    """

    name: Optional[str] = Field(description="Name of the index.")
    currency: Optional[str] = Field(description="Currency the index is traded in.")
