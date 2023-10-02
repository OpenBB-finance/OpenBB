"""Forex available pairs data model."""


from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class ForexPairsQueryParams(QueryParams):
    """Forex available pairs Query."""


class ForexPairsData(Data):
    """Forex available pairs Data."""

    name: str = Field(description="Name of the currency pair.")
