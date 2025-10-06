"""N-PORT Discolsure Standard Model."""

from typing import Optional, Union

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class NportDisclosureQueryParams(QueryParams):
    """N-PORT Disclosure Query."""

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "") + " (Fund ticker or CIK)"
    )
    year: Optional[int] = Field(
        default=None,
        description="Reporting year of the filing. Default is the year for the most recent, reported, quarter.",
    )
    quarter: Optional[int] = Field(
        default=None,
        description="Reporting quarter of the filing. Default is the most recent, reported, quarter.",
    )

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class NportDisclosureData(Data):
    """N-PORT Disclosure Data."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    name: Optional[str] = Field(
        default=None,
        description="Name of the asset.",
    )
    title: Optional[str] = Field(
        default=None,
        description="Title of the asset.",
    )
    cusip: Optional[str] = Field(
        default=None,
        description="CUSIP of the holding.",
        coerce_numbers_to_str=True,
    )
    lei: Optional[str] = Field(
        default=None,
        description="The LEI of the holding.",
        coerce_numbers_to_str=True,
    )
    isin: Optional[str] = Field(
        default=None,
        description="The ISIN of the holding.",
        coerce_numbers_to_str=True,
    )
    other_id: Optional[str] = Field(
        description="Internal identifier for the holding.", default=None
    )
    is_restricted: Optional[str] = Field(
        description="Whether the holding is restricted.",
        default=None,
    )
    fair_value_level: Optional[int] = Field(
        description="The fair value level of the holding.",
        default=None,
    )
    is_cash_collateral: Optional[str] = Field(
        description="Whether the holding is cash collateral.",
        default=None,
    )
    is_non_cash_collateral: Optional[str] = Field(
        description="Whether the holding is non-cash collateral.",
        default=None,
    )
    is_loan_by_fund: Optional[str] = Field(
        description="Whether the holding is loan by fund.",
        default=None,
    )
    loan_value: Optional[float] = Field(
        description="The loan value of the holding.",
        default=None,
    )
    issuer_conditional: Optional[str] = Field(
        description="The issuer conditions of the holding.", default=None
    )
    asset_conditional: Optional[str] = Field(
        description="The asset conditions of the holding.", default=None
    )
    payoff_profile: Optional[str] = Field(
        description="The payoff profile of the holding.",
        default=None,
    )
    asset_category: Optional[str] = Field(
        description="The asset category of the holding.", default=None
    )
    issuer_category: Optional[str] = Field(
        description="The issuer category of the holding.",
        default=None,
    )
    country: Optional[str] = Field(
        description="The country of the holding.", default=None
    )
    balance: Optional[Union[int, float]] = Field(
        description="The balance of the holding, in shares or units.", default=None
    )
    units: Optional[Union[int, float, str]] = Field(
        description="The type of units.", default=None
    )
    currency: Optional[str] = Field(
        description="The currency of the holding.", default=None
    )
    value: Optional[Union[int, float]] = Field(
        description="The value of the holding, in dollars.",
        default=None,
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    weight: Optional[float] = Field(
        description="The weight of the holding, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
