"""Currency Available Pairs Standard Model."""

from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams


class CurrencyPairsQueryParams(QueryParams):
    """Currency Available Pairs Query."""

    query: Optional[str] = Field(
        default=None, description="Query to search for currency pairs."
    )


class CurrencyPairsData(Data):
    """Currency Available Pairs Data."""

    symbol: str = Field(description="Symbol of the currency pair.")
    name: Optional[str] = Field(default=None, description="Name of the currency pair.")
