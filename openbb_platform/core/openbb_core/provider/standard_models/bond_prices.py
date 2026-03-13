"""Bond Prices Standard Model."""

from datetime import (
    date as dateType,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class BondPricesQueryParams(QueryParams):
    """Bond Prices Query."""

    country: str | None = Field(
        default=None,
        description="The country to get data. Matches partial name.",
    )
    issuer_name: str | None = Field(
        default=None,
        description="Name of the issuer.  Returns partial matches and is case insensitive.",
    )
    isin: list | str | None = Field(
        default=None,
        description="International Securities Identification Number(s) of the bond(s).",
    )
    lei: str | None = Field(
        default=None,
        description="Legal Entity Identifier of the issuing entity.",
    )
    currency: list | str | None = Field(
        default=None,
        description="Currency of the bond. Formatted as the 3-letter ISO 4217 code (e.g. GBP, EUR, USD).",
    )
    coupon_min: float | None = Field(
        default=None,
        description="Minimum coupon rate of the bond.",
    )
    coupon_max: float | None = Field(
        default=None,
        description="Maximum coupon rate of the bond.",
    )
    issued_amount_min: int | None = Field(
        default=None,
        description="Minimum issued amount of the bond.",
    )
    issued_amount_max: str | None = Field(
        default=None,
        description="Maximum issued amount of the bond.",
    )
    maturity_date_min: dateType | None = Field(
        default=None,
        description="Minimum maturity date of the bond.",
    )
    maturity_date_max: dateType | None = Field(
        default=None,
        description="Maximum maturity date of the bond.",
    )
    ytm_max: float | None = Field(
        default=None,
        description="Maximum yield to maturity of the bond.",
    )
    ytm_min: float | None = Field(
        default=None,
        description="Minimum yield to maturity of the bond.",
    )


class BondPricesData(Data):
    """Bond Prices Data."""

    isin: str | None = Field(
        default=None,
        description="International Securities Identification Number of the bond.",
    )
    lei: str | None = Field(
        default=None,
        description="Legal Entity Identifier of the issuing entity.",
    )
    figi: str | None = Field(default=None, description="FIGI of the bond.")
    cusip: str | None = Field(
        default=None,
        description="CUSIP of the bond.",
    )
    coupon_rate: float | None = Field(
        default=None,
        description="Coupon rate of the bond.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    price: float | None = Field(
        default=None,
        description="Price of the bond.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    current_yield: float | None = Field(
        default=None,
        description="Current yield of the bond.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ytm: float | None = Field(
        default=None,
        description="Yield to maturity of the bond.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ytw: float | None = Field(
        default=None,
        description="Yield to worst of the bond.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    duration: float | None = Field(
        default=None,
        description="Duration of the bond.",
    )
    maturity_date: dateType | None = Field(
        default=None,
        description="Maturity date of the bond.",
    )
    call_date: dateType | None = Field(
        default=None,
        description="The nearest call date of the bond.",
    )
