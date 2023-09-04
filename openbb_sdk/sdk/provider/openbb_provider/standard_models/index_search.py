"""Index Search  data model."""

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class IndexSearchQueryParams(QueryParams):
    """Index Search Query Params"""

    query: str = Field(description="Search query.", default="")
    symbol: bool = Field(
        description="Whether to search by ticker symbol.", default=False
    )


class IndexSearchData(Data):
    """Company Search Data."""

    symbol: str = Field(description="Symbol of the index.")
    name: str = Field(description="Name of the index.")
