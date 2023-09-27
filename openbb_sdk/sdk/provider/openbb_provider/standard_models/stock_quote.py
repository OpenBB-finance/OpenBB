"""Stock Quote data model."""

from datetime import datetime
from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class StockQuoteQueryParams(QueryParams):
    """Stock Quote query model."""

    symbol: str = Field(default=None, description="Comma separated list of symbols.")

    @field_validator("symbol", mode="before", check_fields=False)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class StockQuoteData(Data):
    """Stock Quote data."""

    day_low: Optional[float] = Field(
        default=None,
        description="Lowest price of the stock in the current trading day.",
    )
    day_high: Optional[float] = Field(
        default=None,
        description="Highest price of the stock in the current trading day.",
    )
    date: Optional[datetime] = Field(
        description="Timestamp of the stock quote.", default=None
    )
