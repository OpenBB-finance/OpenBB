"""FRED Series Standard Model."""


from datetime import date as dateType
from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class SeriesQueryParams(QueryParams):
    """FRED Series Query."""

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", ""),
    )
    start_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )
    limit: Optional[int] = Field(
        description=QUERY_DESCRIPTIONS.get("limit", ""), default=100000
    )

    @field_validator("symbol", mode="before", check_fields=False)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class SeriesData(Data):
    """FRED Series Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
