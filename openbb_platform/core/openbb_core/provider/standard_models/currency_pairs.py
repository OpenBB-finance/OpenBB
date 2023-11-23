"""Currency Available Pairs Standard Model."""


from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class CurrencyPairsQueryParams(QueryParams):
    """Currency Available Pairs Query."""


class CurrencyPairsData(Data):
    """Currency Available Pairs Data."""

    name: str = Field(description="Name of the currency pair.")
