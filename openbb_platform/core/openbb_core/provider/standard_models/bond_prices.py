"""Bond Prices Standard Model."""

from datetime import (
    date as dateType,
)
from typing import List, Optional, Union

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams


class BondPricesQueryParams(QueryParams):
    """Bond Prices Query."""

    country: Optional[str] = Field(
        default=None,
        description="The country to get data. Matches partial name.",
    )
    issuer_name: Optional[str] = Field(
        default=None,
        description="Name of the issuer.  Returns partial matches and is case insensitive.",
    )
    isin: Optional[Union[List, str]] = Field(
        default=None,
        description="International Securities Identification Number(s) of the bond(s).",
    )
    lei: Optional[str] = Field(
        default=None,
        description="Legal Entity Identifier of the issuing entity.",
    )
    currency: Optional[Union[List, str]] = Field(
        default=None,
        description="Currency of the bond. Formatted as the 3-letter ISO 4217 code (e.g. GBP, EUR, USD).",
    )
    coupon_min: Optional[float] = Field(
        default=None,
        description="Minimum coupon rate of the bond.",
    )
    coupon_max: Optional[float] = Field(
        default=None,
        description="Maximum coupon rate of the bond.",
    )
    issued_amount_min: Optional[int] = Field(
        default=None,
        description="Minimum issued amount of the bond.",
    )
    issued_amount_max: Optional[str] = Field(
        default=None,
        description="Maximum issued amount of the bond.",
    )
    maturity_date_min: Optional[dateType] = Field(
        default=None,
        description="Minimum maturity date of the bond.",
    )
    maturity_date_max: Optional[dateType] = Field(
        default=None,
        description="Maximum maturity date of the bond.",
    )
    ytm_max: Optional[float] = Field(
        default=None,
        description="Maximum yield to maturity of the bond.",
    )
    ytm_min: Optional[float] = Field(
        default=None,
        description="Minimum yield to maturity of the bond.",
    )


class BondPricesData(Data):
    """Bond Prices Data."""

    isin: Optional[str] = Field(
        default=None,
        description="International Securities Identification Number of the bond.",
    )
    lei: Optional[str] = Field(
        default=None,
        description="Legal Entity Identifier of the issuing entity.",
    )
    figi: Optional[str] = Field(default=None, description="FIGI of the bond.")
    cusip: Optional[str] = Field(
        default=None,
        description="CUSIP of the bond.",
    )
    coupon_rate: Optional[float] = Field(
        default=None,
        description="Coupon rate of the bond.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
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
    ytm: Optional[float] = Field(
        default=None,
        description="Yield to maturity of the bond.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ytw: Optional[float] = Field(
        default=None,
        description="Yield to worst of the bond.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    duration: Optional[float] = Field(
        default=None,
        description="Duration of the bond.",
    )
    maturity_date: Optional[dateType] = Field(
        default=None,
        description="Maturity date of the bond.",
    )
    call_date: Optional[dateType] = Field(
        default=None,
        description="The nearest call date of the bond.",
    )
