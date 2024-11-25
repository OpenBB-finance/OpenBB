"""Bond Trades Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Literal, Optional, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class BondTradesQueryParams(QueryParams):
    """Bond Trades Query."""

    country: Optional[str] = Field(
        default=None,
        description="The country to get data. Matches partial name.",
    )
    isin: Optional[str] = Field(
        default=None,
        description="ISIN of the bond.",
    )
    issuer_type: Optional[Literal["government", "corporate", "municipal"]] = Field(
        default=None,
        description="Type of bond issuer.",
    )
    notional_currency: Optional[str] = Field(
        default=None,
        description="""
            Currency of the bond, which might differ from the currency of the trade.
            Formatted as the 3-letter ISO 4217 code (e.g. GBP, EUR, USD).
        """,
    )
    start_date: Optional[Union[dateType, str]] = Field(
        default=None,
        description=(
            QUERY_DESCRIPTIONS.get("start_date", "")
            + " YYYY-MM-DD or  ISO-8601 format. E.g. 2023-01-14T10:55:00Z"
        ),
    )
    end_date: Optional[Union[dateType, str]] = Field(
        default=None,
        description=(
            QUERY_DESCRIPTIONS.get("end_date", "")
            + " YYYY-MM-DD or  ISO-8601 format. E.g. 2023-01-14T10:55:00Z"
        ),
    )

    @field_validator("isin", "notional_currency", mode="before", check_fields=False)
    @classmethod
    def validate_upper_case(cls, v):
        """Enforce upper case for fields."""
        return v.upper() if v else None


class BondTradesData(Data):
    """Bond Trades Data."""

    trade_date: Optional[Union[dateType, datetime]] = Field(
        default=None,
        description="Date of the transaction.",
    )
    isin: Optional[str] = Field(
        default=None,
        description="ISIN of the bond.",
    )
    figi: Optional[str] = Field(default=None, description="FIGI of the bond.")
    cusip: Optional[str] = Field(
        default=None,
        description="CUSIP of the bond.",
    )
    price: Optional[float] = Field(
        default=None,
        description="Price of the bond.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    current_yield: Optional[float] = Field(
        default=None,
        description="Current yield of the bond.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    coupon_rate: Optional[float] = Field(
        default=None,
        description="Coupon rate of the bond.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume: Optional[int] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("volume", ""),
    )
