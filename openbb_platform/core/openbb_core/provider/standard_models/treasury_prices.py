"""Treasury Prices Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class TreasuryPricesQueryParams(QueryParams):
    """Treasury Prices Query."""

    date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " No date will return the current posted data.",
        default=None,
    )


class TreasuryPricesData(Data):
    """Treasury Prices Data."""

    issuer_name: Optional[str] = Field(
        default=None,
        description="Name of the issuing entity.",
    )
    cusip: Optional[str] = Field(
        default=None,
        description="CUSIP of the security.",
    )
    isin: Optional[str] = Field(
        default=None,
        description="ISIN of the security.",
    )
    security_type: Optional[str] = Field(
        default=None,
        description="The type of Treasury security - i.e., Bill, Note, Bond, TIPS, FRN.",
    )
    issue_date: Optional[dateType] = Field(
        default=None,
        description="The original issue date of the security.",
    )
    maturity_date: Optional[dateType] = Field(
        default=None,
        description="The maturity date of the security.",
    )
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
    last_traded_date: Optional[dateType] = Field(
        description="The last trade date of the security.", default=None
    )
    total_trades: Optional[int] = Field(
        default=None,
        description="Total number of trades on the last traded date.",
    )
    last_price: Optional[float] = Field(
        description="The last price of the security.", default=None
    )
    highest_price: Optional[float] = Field(
        default=None,
        description="The highest price for the bond on the last traded date.",
    )
    lowest_price: Optional[float] = Field(
        default=None,
        description="The lowest price for the bond on the last traded date.",
    )
    rate: Optional[float] = Field(
        description="The annualized interest rate or coupon of the security.",
        default=None,
    )
    ytm: Optional[float] = Field(
        default=None,
        description="Yield to maturity (YTM) is the rate of return anticipated on a bond"
        + " if it is held until the maturity date. It takes into account"
        + " the current market price, par value, coupon rate and time to maturity. It is assumed that all"
        + " coupons are reinvested at the same rate.",
    )
