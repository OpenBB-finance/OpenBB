"""Index Constituents data model."""

from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class IndexConstituentsQueryParams(QueryParams):
    """Index Constituents Query Params."""

    symbol: str = Field(description="The index ticker symbol.")

    @field_validator("symbol")
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class IndexConstituentsData(Data):
    """Index Constituents Data."""

    symbol: str = Field(description="The ticker symbol of the index constituent.")
    name: Optional[str] = Field(
        description="The name of the index constituent.", default=None
    )
    weight: Optional[float] = Field(
        description="The weight of the sector in the index.", default=None
    )
    value: Optional[float] = Field(
        description="The current market value of the index constituent.", default=None
    )
