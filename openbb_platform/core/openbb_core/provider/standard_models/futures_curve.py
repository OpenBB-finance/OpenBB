"""Futures Curve Standard Model."""


from datetime import date as dateType
from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class FuturesCurveQueryParams(QueryParams):
    """Futures Curve Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", ""),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class FuturesCurveData(Data):
    """Futures Curve Data."""

    expiration: str = Field(description="Futures expiration month.")
    price: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("close", "")
    )
