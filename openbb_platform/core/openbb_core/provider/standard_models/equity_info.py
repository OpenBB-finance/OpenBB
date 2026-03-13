"""Equity Info Standard Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EquityInfoQueryParams(QueryParams):
    """Equity Info Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class EquityInfoData(Data):
    """Equity Info Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(default=None, description="Common name of the company.")
    cik: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("cik", ""),
    )
    cusip: str | None = Field(
        default=None, description="CUSIP identifier for the company."
    )
    isin: str | None = Field(
        default=None, description="International Securities Identification Number."
    )
    lei: str | None = Field(
        default=None, description="Legal Entity Identifier assigned to the company."
    )
    legal_name: str | None = Field(
        default=None, description="Official legal name of the company."
    )
    stock_exchange: str | None = Field(
        default=None, description="Stock exchange where the company is traded."
    )
    sic: int | None = Field(
        default=None,
        description="Standard Industrial Classification code for the company.",
    )
    short_description: str | None = Field(
        default=None, description="Short description of the company."
    )
    long_description: str | None = Field(
        default=None, description="Long description of the company."
    )
    ceo: str | None = Field(
        default=None, description="Chief Executive Officer of the company."
    )
    company_url: str | None = Field(
        default=None, description="URL of the company's website."
    )
    business_address: str | None = Field(
        default=None, description="Address of the company's headquarters."
    )
    mailing_address: str | None = Field(
        default=None, description="Mailing address of the company."
    )
    business_phone_no: str | None = Field(
        default=None, description="Phone number of the company's headquarters."
    )
    hq_address1: str | None = Field(
        default=None, description="Address of the company's headquarters."
    )
    hq_address2: str | None = Field(
        default=None, description="Address of the company's headquarters."
    )
    hq_address_city: str | None = Field(
        default=None, description="City of the company's headquarters."
    )
    hq_address_postal_code: str | None = Field(
        default=None, description="Zip code of the company's headquarters."
    )
    hq_state: str | None = Field(
        default=None, description="State of the company's headquarters."
    )
    hq_country: str | None = Field(
        default=None, description="Country of the company's headquarters."
    )
    inc_state: str | None = Field(
        default=None, description="State in which the company is incorporated."
    )
    inc_country: str | None = Field(
        default=None, description="Country in which the company is incorporated."
    )
    employees: int | None = Field(
        default=None, description="Number of employees working for the company."
    )
    entity_legal_form: str | None = Field(
        default=None, description="Legal form of the company."
    )
    entity_status: str | None = Field(
        default=None, description="Status of the company."
    )
    latest_filing_date: dateType | None = Field(
        default=None, description="Date of the company's latest filing."
    )
    irs_number: str | None = Field(
        default=None, description="IRS number assigned to the company."
    )
    sector: str | None = Field(
        default=None, description="Sector in which the company operates."
    )
    industry_category: str | None = Field(
        default=None, description="Category of industry in which the company operates."
    )
    industry_group: str | None = Field(
        default=None, description="Group of industry in which the company operates."
    )
    template: str | None = Field(
        default=None,
        description="Template used to standardize the company's financial statements.",
    )
    standardized_active: bool | None = Field(
        default=None, description="Whether the company is active or not."
    )
    first_fundamental_date: dateType | None = Field(
        default=None, description="Date of the company's first fundamental."
    )
    last_fundamental_date: dateType | None = Field(
        default=None, description="Date of the company's last fundamental."
    )
    first_stock_price_date: dateType | None = Field(
        default=None, description="Date of the company's first stock price."
    )
    last_stock_price_date: dateType | None = Field(
        default=None, description="Date of the company's last stock price."
    )
