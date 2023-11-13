"""Currency available pairs data model."""


from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class CurrencyPairsQueryParams(QueryParams):
    """Currency available pairs Query."""


class CurrencyPairsData(Data):
    """Currency available pairs Data."""

    name: str = Field(description="Name of the currency pair.")
