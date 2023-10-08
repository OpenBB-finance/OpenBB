"""ETF Search data model."""

from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class EtfSearchQueryParams(QueryParams):
    """ETF Search Query Params"""

    query: Optional[str] = Field(description="Search query.", default="")


class EtfSearchData(Data):
    """ETF Search Data."""

    symbol: str = Field(description="The exchange ticker symbol for the ETF.")
    name: Optional[str] = Field(description="Name of the ETF.", default=None)
