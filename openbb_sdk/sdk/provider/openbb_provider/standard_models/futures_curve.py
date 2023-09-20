"""Futures aggregate end of day price data model."""


from datetime import date as dateType
from typing import List, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class FuturesCurveQueryParams(QueryParams):
    """Futures curve Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    date: Optional[dateType] = Field(
        default=None,
        description="Historical date to search curve for.",
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class FuturesCurveData(Data):
    """Futures curve Data."""

    expiration: str = Field(description="Futures expiration month.")
    price: Optional[float] = Field(description=DATA_DESCRIPTIONS.get("close", ""))
