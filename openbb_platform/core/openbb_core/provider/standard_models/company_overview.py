"""Company Overview Standard Model."""

from datetime import date
from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data, ForceInt
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class CompanyOverviewQueryParams(QueryParams):
    """Company Overview Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class CompanyOverviewData(Data):
    """Company Overview Data.

    Returns the profile of a given company.
    """

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    price: Optional[float] = Field(default=None, description="Price of the company.")
    beta: Optional[float] = Field(default=None, description="Beta of the company.")
    vol_avg: Optional[ForceInt] = Field(
        default=None, description="Volume average of the company."
    )
    mkt_cap: Optional[ForceInt] = Field(
        default=None, description="Market capitalization of the company."
    )
    last_div: Optional[float] = Field(
        default=None, description="Last dividend of the company."
    )
    range: Optional[str] = Field(default=None, description="Range of the company.")
    changes: Optional[float] = Field(
        default=None, description="Changes of the company."
    )
    company_name: Optional[str] = Field(
        default=None, description="Company name of the company."
    )
    currency: Optional[str] = Field(
        default=None, description="Currency of the company."
    )
    cik: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("cik", "")
    )
    isin: Optional[str] = Field(default=None, description="ISIN of the company.")
    cusip: Optional[str] = Field(default=None, description="CUSIP of the company.")
    exchange: Optional[str] = Field(
        default=None, description="Exchange of the company."
    )
    exchange_short_name: Optional[str] = Field(
        default=None, description="Exchange short name of the company."
    )
    industry: Optional[str] = Field(
        default=None, description="Industry of the company."
    )
    website: Optional[str] = Field(default=None, description="Website of the company.")
    description: Optional[str] = Field(
        default=None, description="Description of the company."
    )
    ceo: Optional[str] = Field(default=None, description="CEO of the company.")
    sector: Optional[str] = Field(default=None, description="Sector of the company.")
    country: Optional[str] = Field(default=None, description="Country of the company.")
    full_time_employees: Optional[str] = Field(
        default=None, description="Full time employees of the company."
    )
    phone: Optional[str] = Field(default=None, description="Phone of the company.")
    address: Optional[str] = Field(default=None, description="Address of the company.")
    city: Optional[str] = Field(default=None, description="City of the company.")
    state: Optional[str] = Field(default=None, description="State of the company.")
    zip: Optional[str] = Field(default=None, description="Zip of the company.")
    dcf_diff: Optional[float] = Field(
        default=None, description="Discounted cash flow difference of the company."
    )
    dcf: Optional[float] = Field(
        default=None, description="Discounted cash flow of the company."
    )
    image: Optional[str] = Field(default=None, description="Image of the company.")
    ipo_date: Optional[date] = Field(
        default=None, description="IPO date of the company."
    )
    default_image: bool = Field(description="If the image is the default image.")
    is_etf: bool = Field(description="If the company is an ETF.")
    is_actively_trading: bool = Field(description="If the company is actively trading.")
    is_adr: bool = Field(description="If the company is an ADR.")
    is_fund: bool = Field(description="If the company is a fund.")

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: Union[str, List[str], Set[str]]):
        """Convert field to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
