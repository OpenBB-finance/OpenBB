"""Stock Search  data model."""

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class StockSearchQueryParams(QueryParams):
    """Company Search Query Params"""

    query: str = Field(description="Search query.", default="")
    ticker: bool = Field(
        description="Whether to search by ticker symbol.", default=False
    )


class StockSearchData(Data, BaseSymbol):
    """Company Search Data."""

    name: str = Field(description="Name of the company.")
