"""Forex available pairs data model."""


from pydantic import Field

from openbb_provider.abstract.data import Data, QueryParams


class ForexPairsQueryParams(QueryParams):
    """Forex available pairs Query."""


class ForexPairsData(Data):
    """Forex available pairs Data."""

    name: str = Field(description="The name of the currency pair.")
