"""Crypto aggregate end of day price data model."""


from datetime import date
from typing import Optional

from pydantic import Field, PositiveFloat

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.metadata import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS
from openbb_provider.models.base import BaseSymbol


class CryptoEODQueryParams(QueryParams, BaseSymbol):
    """Crypto end of day Query."""

    start_date: Optional[date] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[date] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class CryptoEODData(Data):
    """Crypto end of day price Data."""

    open: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("open", ""))
    high: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("high", ""))
    low: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("low", ""))
    close: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("close", ""))
    volume: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("volume", ""))
