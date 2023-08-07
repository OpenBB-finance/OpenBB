"""Company Search  data model."""

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class CompanySearchQueryParams(QueryParams):
    """Company Search Query Params"""

    query: str = Field(description="The search query.", default="")
    ticker: bool = Field(
        description="Whether to search by ticker symbol.", default=False
    )


class CompanySearchData(Data):
    """Company Search Data."""

    symbol: str = Field(description="The ticker symbol of the company.")
    name: str = Field(description="The name of the company.")
