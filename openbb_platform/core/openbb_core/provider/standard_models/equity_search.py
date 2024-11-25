"""Equity Search Standard Model."""

from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS


class EquitySearchQueryParams(QueryParams):
    """Equity Search Query."""

    query: str = Field(description="Search query.", default="")
    is_symbol: bool = Field(
        description="Whether to search by ticker symbol.", default=False
    )


class EquitySearchData(Data):
    """Equity Search Data."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    name: Optional[str] = Field(default=None, description="Name of the company.")
