"""Futures term structure data model."""


from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class FuturesTermStructureQueryParams(QueryParams, BaseSymbol):
    """Futures end of day Query."""

    date: Optional[dateType] = Field(
        default=None,
        description="The date for the settlement prices.",
    )


class FuturesTermStructureData(Data):
    """Futures end of day price Data."""

    expiration: dateType = Field(description="The expiration date of the contract.")
    price: float = Field(description="The settlement price of the tenor.")
