"""Treasury Prices Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class USTreasuryPricesQueryParams(QueryParams):
    """US Treasury Prices Query."""

    date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " No date will return the current posted data.",
        default=None,
    )


class USTreasuryPricesData(Data):
    """US Treasury Prices Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    cusip: str = Field(description="CUSIP of the security.")
    security_type: str = Field(
        description="The type of US Treasury security. Bill, Note, Bond, TIPS, FRN."
    )
    rate: Optional[float] = Field(
        description="The annualized interest rate or coupon of the security.",
        default=None,
    )
    maturity_date: dateType = Field(description="The maturity date of the security.")
    call_date: Optional[dateType] = Field(
        description="The call date of the security.", default=None
    )
    bid: Optional[float] = Field(
        description="The bid price of the security.", default=None
    )
    offer: Optional[float] = Field(
        description="The offer price of the security.", default=None
    )
    eod_price: Optional[float] = Field(
        description="The end-of-day price of the security.", default=None
    )
