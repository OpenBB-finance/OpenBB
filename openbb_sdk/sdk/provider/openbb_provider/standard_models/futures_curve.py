"""Futures aggregate end of day price data model."""


from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS


class FuturesCurveQueryParams(QueryParams, BaseSymbol):
    """Futures curve Query."""

    date: Optional[dateType] = Field(
        default=None,
        description="Historical date to search curve for.",
    )


class FuturesCurveData(Data):
    """Futures curve Data."""

    expiration: str = Field(description="Futures expiration month.")
    price: float = Field(description=DATA_DESCRIPTIONS.get("close", ""))
