"""Dividend Calendar data model."""


from datetime import date as dateType
from typing import List, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class DividendCalendarQueryParams(QueryParams):
    """Dividend Calendar Query."""

    start_date: dateType = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class DividendCalendarData(Data):
    """Dividend Calendar Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    label: str = Field(description="Date in human readable form in the calendar.")
    adj_dividend: Optional[float] = Field(
        default=None,
        description="Adjusted dividend on a date in the calendar.",
    )
    dividend: Optional[float] = Field(
        default=None, description="Dividend amount in the calendar."
    )
    record_date: Optional[dateType] = Field(
        default=None,
        description="Record date of the dividend in the calendar.",
    )
    payment_date: Optional[dateType] = Field(
        default=None,
        description="Payment date of the dividend in the calendar.",
    )
    declaration_date: Optional[dateType] = Field(
        default=None,
        description="Declaration date of the dividend in the calendar.",
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
