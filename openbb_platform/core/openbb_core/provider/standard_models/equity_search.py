"""Equity Search Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class EquitySearchQueryParams(QueryParams):
    """Equity Search Query."""

    query: str = Field(description="Search query.", default="")
    is_symbol: bool = Field(
        description="Whether to search by ticker symbol.", default=False
    )


class EquitySearchData(Data):
    """Equity Search Data."""

    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    name: str | None = Field(default=None, description="Name of the company.")
