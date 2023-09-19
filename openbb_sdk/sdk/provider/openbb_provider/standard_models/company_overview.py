"""Company Overview Data Model."""


from datetime import date
from typing import List, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class CompanyOverviewQueryParams(QueryParams):
    """Company overview Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class CompanyOverviewData(Data):
    """Company Overview Data.

    Returns the profile of a given company.
    """

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    price: float = Field(description="Price of the company.")
    beta: float = Field(description="Beta of the company.")
    vol_avg: int = Field(description="Volume average of the company.")
    mkt_cap: int = Field(description="Market capitalization of the company.")
    last_div: float = Field(description="Last dividend of the company.")
    range: str = Field(description="Range of the company.")
    changes: float = Field(description="Changes of the company.")
    company_name: str = Field(description="Company name of the company.")
    currency: str = Field(description="Currency of the company.")
    cik: Optional[str] = Field(description="CIK of the company.")
    isin: Optional[str] = Field(description="ISIN of the company.")
    cusip: Optional[str] = Field(description="CUSIP of the company.")
    exchange: str = Field(description="Exchange of the company.")
    exchange_short_name: str = Field(description="Exchange short name of the company.")
    industry: str = Field(description="Industry of the company.")
    website: str = Field(description="Website of the company.")
    description: Optional[str] = Field(description="Description of the company.")
    ceo: str = Field(description="CEO of the company.")
    sector: str = Field(description="Sector of the company.")
    country: str = Field(description="Country of the company.")
    full_time_employees: Optional[str] = Field(
        description="Full time employees of the company."
    )
    phone: Optional[str] = Field(description="Phone of the company.")
    address: Optional[str] = Field(description="Address of the company.")
    city: Optional[str] = Field(description="City of the company.")
    state: Optional[str] = Field(description="State of the company.")
    zip: Optional[str] = Field(description="Zip of the company.")
    dcf_diff: Optional[float] = Field(
        description="Discounted cash flow difference of the company."
    )
    dcf: float = Field(description="Discounted cash flow of the company.")
    image: str = Field(description="Image of the company.")
    ipo_date: date = Field(description="IPO date of the company.")
    default_image: bool = Field(description="If the image is the default image.")
    is_etf: bool = Field(description="If the company is an ETF.")
    is_actively_trading: bool = Field(description="If the company is actively trading.")
    is_adr: bool = Field(description="If the company is an ADR.")
    is_fund: bool = Field(description="If the company is a fund.")

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
