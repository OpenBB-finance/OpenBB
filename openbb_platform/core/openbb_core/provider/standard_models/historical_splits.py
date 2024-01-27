"""Historical Splits Standard Model."""

from datetime import date as dateType
from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class HistoricalSplitsQueryParams(QueryParams):
    """Historical Splits Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class HistoricalSplitsData(Data):
    """Historical Splits Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", "") + " (Ex-date)")
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    numerator: Optional[float] = Field(
        default=None, description="Numerator of the stock splits."
    )
    denominator: Optional[float] = Field(
        default=None, description="Denominator of the stock splits."
    )
    factor: Optional[float] = Field(default=None, description="The split factor value.")
