"""Stock Search  data model."""

from typing import List, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class StockSearchQueryParams(QueryParams):
    """Company Search Query Params"""

    query: str = Field(description="Search query.", default="")
    ticker: bool = Field(
        description="Whether to search by ticker symbol.", default=False
    )


class StockSearchData(Data):
    """Company Search Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    name: str = Field(description="Name of the company.")

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
