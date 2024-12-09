"""Equity Info Standard Model."""

from datetime import date as dateType
from typing import Optional

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
    name: Optional[str] = Field(default=None, description="Common name of the company.")
    cik: Optional[str] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("cik", ""),
    )
    cusip: Optional[str] = Field(
        default=None, description="CUSIP identifier for the company."
    )
    isin: Optional[str] = Field(
        default=None, description="International Securities Identification Number."
    )
    lei: Optional[str] = Field(
        default=None, description="Legal Entity Identifier assigned to the company."
    )
    legal_name: Optional[str] = Field(
        default=None, description="Official legal name of the company."
    )
    stock_exchange: Optional[str] = Field(
        default=None, description="Stock exchange where the company is traded."
    )
    sic: Optional[int] = Field(
        default=None,
        description="Standard Industrial Classification code for the company.",
    )
    short_description: Optional[str] = Field(
        default=None, description="Short description of the company."
    )
    long_description: Optional[str] = Field(
        default=None, description="Long description of the company."
    )
    ceo: Optional[str] = Field(
        default=None, description="Chief Executive Officer of the company."
    )
    company_url: Optional[str] = Field(
        default=None, description="URL of the company's website."
    )
    business_address: Optional[str] = Field(
        default=None, description="Address of the company's headquarters."
    )
    mailing_address: Optional[str] = Field(
        default=None, description="Mailing address of the company."
    )
    business_phone_no: Optional[str] = Field(
        default=None, description="Phone number of the company's headquarters."
    )
    hq_address1: Optional[str] = Field(
        default=None, description="Address of the company's headquarters."
    )
    hq_address2: Optional[str] = Field(
        default=None, description="Address of the company's headquarters."
    )
    hq_address_city: Optional[str] = Field(
        default=None, description="City of the company's headquarters."
    )
    hq_address_postal_code: Optional[str] = Field(
        default=None, description="Zip code of the company's headquarters."
    )
    hq_state: Optional[str] = Field(
        default=None, description="State of the company's headquarters."
    )
    hq_country: Optional[str] = Field(
        default=None, description="Country of the company's headquarters."
    )
    inc_state: Optional[str] = Field(
        default=None, description="State in which the company is incorporated."
    )
    inc_country: Optional[str] = Field(
        default=None, description="Country in which the company is incorporated."
    )
    employees: Optional[int] = Field(
        default=None, description="Number of employees working for the company."
    )
    entity_legal_form: Optional[str] = Field(
        default=None, description="Legal form of the company."
    )
    entity_status: Optional[str] = Field(
        default=None, description="Status of the company."
    )
    latest_filing_date: Optional[dateType] = Field(
        default=None, description="Date of the company's latest filing."
    )
    irs_number: Optional[str] = Field(
        default=None, description="IRS number assigned to the company."
    )
    sector: Optional[str] = Field(
        default=None, description="Sector in which the company operates."
    )
    industry_category: Optional[str] = Field(
        default=None, description="Category of industry in which the company operates."
    )
    industry_group: Optional[str] = Field(
        default=None, description="Group of industry in which the company operates."
    )
    template: Optional[str] = Field(
        default=None,
        description="Template used to standardize the company's financial statements.",
    )
    standardized_active: Optional[bool] = Field(
        default=None, description="Whether the company is active or not."
    )
    first_fundamental_date: Optional[dateType] = Field(
        default=None, description="Date of the company's first fundamental."
    )
    last_fundamental_date: Optional[dateType] = Field(
        default=None, description="Date of the company's last fundamental."
    )
    first_stock_price_date: Optional[dateType] = Field(
        default=None, description="Date of the company's first stock price."
    )
    last_stock_price_date: Optional[dateType] = Field(
        default=None, description="Date of the company's last stock price."
    )
