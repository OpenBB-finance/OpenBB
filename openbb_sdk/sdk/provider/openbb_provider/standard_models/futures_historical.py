"""Futures aggregate end of day price data model."""


from datetime import date, datetime
from typing import List, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class FuturesHistoricalQueryParams(QueryParams):
    """Futures end of day Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    start_date: Optional[date] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[date] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    expiration: Optional[str] = Field(
        default=None,
        description="Future expiry date with format YYYY-MM",
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class FuturesHistoricalData(Data):
    """Futures end of day price Data."""

    date: datetime = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    open: float = Field(description=DATA_DESCRIPTIONS.get("open", ""))
    high: float = Field(description=DATA_DESCRIPTIONS.get("high", ""))
    low: float = Field(description=DATA_DESCRIPTIONS.get("low", ""))
    close: float = Field(description=DATA_DESCRIPTIONS.get("close", ""))
    volume: float = Field(description=DATA_DESCRIPTIONS.get("volume", ""))
