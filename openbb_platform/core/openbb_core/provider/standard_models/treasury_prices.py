"""Treasury Prices Standard Model."""

from datetime import date as dateType
from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field


class TreasuryPricesQueryParams(QueryParams):
    """Treasury Prices Query."""

    date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " Defaults to the last business day.",
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
        default=None,
        description="The bid price of the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    offer: Optional[float] = Field(
        default=None,
        description="The offer price of the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    eod_price: Optional[float] = Field(
        default=None,
        description="The end-of-day price of the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    last_traded_date: Optional[dateType] = Field(
        description="The last trade date of the security.", default=None
    )
    total_trades: Optional[int] = Field(
        default=None,
        description="Total number of trades on the last traded date.",
    )
    last_price: Optional[float] = Field(
        default=None,
        description="The last price of the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    highest_price: Optional[float] = Field(
        default=None,
        description="The highest price for the bond on the last traded date.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    lowest_price: Optional[float] = Field(
        default=None,
        description="The lowest price for the bond on the last traded date.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    rate: Optional[float] = Field(
        description="The annualized interest rate or coupon of the security.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ytm: Optional[float] = Field(
        default=None,
        description="Yield to maturity (YTM) is the rate of return anticipated on a bond"
        + " if it is held until the maturity date. It takes into account"
        + " the current market price, par value, coupon rate and time to maturity. It is assumed that all"
        + " coupons are reinvested at the same rate.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
