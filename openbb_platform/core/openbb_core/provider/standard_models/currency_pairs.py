"""Currency Available Pairs Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class CurrencyPairsQueryParams(QueryParams):
    """Currency Available Pairs Query."""

    query: str | None = Field(
        default=None, description="Query to search for currency pairs."
    )


class CurrencyPairsData(Data):
    """Currency Available Pairs Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(default=None, description="Name of the currency pair.")
