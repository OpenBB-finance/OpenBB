"""Index Historical Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Literal, Optional, Union

from dateutil import parser
from pydantic import Field, PositiveInt, StrictFloat, field_validator

from openbb_core.provider.abstract.data import Data, ForceInt
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class IndexHistoricalQueryParams(QueryParams):
    """Index Historical Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    start_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )
    interval: Optional[str] = Field(
        default="1d",
        description=QUERY_DESCRIPTIONS.get("interval", ""),
    )
    limit: Optional[PositiveInt] = Field(
        default=10000,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )
    sort: Optional[Literal["asc", "desc"]] = Field(
        default="asc",
        description="Sort the data in ascending or descending order.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: str) -> str:
        """Convert symbol to uppercase."""
        return v.upper()


class IndexHistoricalData(Data):
    """Index Historical Data."""

    date: Union[dateType, datetime] = Field(
        description=DATA_DESCRIPTIONS.get("date", "")
    )
    open: Optional[StrictFloat] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("open", "")
    )
    high: Optional[StrictFloat] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("high", "")
    )
    low: Optional[StrictFloat] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("low", "")
    )
    close: Optional[StrictFloat] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("close", "")
    )
    volume: Optional[ForceInt] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return formatted datetime."""
        if ":" in str(v):
            return parser.isoparse(str(v))
        return parser.parse(str(v)).date()
