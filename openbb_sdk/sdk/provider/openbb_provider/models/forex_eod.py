"""Forex aggregate end of day price data model."""


from datetime import date
from typing import Optional

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.models.base import BaseSymbol
from openbb_provider.metadata import QUERY_DESCRIPTIONS, DATA_DESCRIPTIONS

from pydantic import Field, NonNegativeFloat, PositiveFloat


class ForexEODQueryParams(QueryParams, BaseSymbol):
    """Forex end of day Query."""

    start_date: Optional[date] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[date] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class ForexEODData(Data):
    """Forex end of day price Data."""

    open: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("open", ""))
    high: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("high", ""))
    low: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("low", ""))
    close: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("close", ""))
    volume: NonNegativeFloat = Field(description=DATA_DESCRIPTIONS.get("volume", ""))
