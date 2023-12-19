"""Equity Quote Standard Model."""

from datetime import datetime
from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class EquityQuoteQueryParams(QueryParams):
    """Equity Quote Query."""

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " In this case, the comma separated list of symbols."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class EquityQuoteData(Data):
    """Equity Quote Data."""

    day_low: Optional[float] = Field(
        default=None,
        description="Lowest price of the stock in the current trading day.",
    )
    day_high: Optional[float] = Field(
        default=None,
        description="Highest price of the stock in the current trading day.",
    )
    date: Optional[datetime] = Field(
        description=DATA_DESCRIPTIONS.get("date", ""), default=None
    )
