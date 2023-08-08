"""Company Overview Data Model."""


from datetime import date
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class CompanyOverviewQueryParams(QueryParams, BaseSymbol):
    """Company overview Query."""


class CompanyOverviewData(Data, BaseSymbol):
    """Company Overview Data.

    Returns the profile of a given company.
    """

    price: float = Field(description="The price of the company.")
    beta: float = Field(description="The beta of the company.")
    vol_avg: int = Field(description="The volume average of the company.")
    mkt_cap: int = Field(description="The market capitalization of the company.")
    last_div: float = Field(description="The last dividend of the company.")
    range: str = Field(description="The range of the company.")
    changes: float = Field(description="The changes of the company.")
    company_name: str = Field(description="The company name of the company.")
    currency: str = Field(description="The currency of the company.")
    cik: Optional[str] = Field(description="The CIK of the company.")
    isin: Optional[str] = Field(description="The ISIN of the company.")
    cusip: Optional[str] = Field(description="The CUSIP of the company.")
    exchange: str = Field(description="The exchange of the company.")
    exchange_short_name: str = Field(
        description="The exchange short name of the company."
    )
    industry: str = Field(description="The industry of the company.")
    website: str = Field(description="The website of the company.")
    description: str = Field(description="The description of the company.")
    ceo: str = Field(description="The CEO of the company.")
    sector: str = Field(description="The sector of the company.")
    country: str = Field(description="The country of the company.")
    full_time_employees: str = Field(
        description="The full time employees of the company."
    )
    phone: str = Field(description="The phone of the company.")
    address: str = Field(description="The address of the company.")
    city: str = Field(description="The city of the company.")
    state: str = Field(description="The state of the company.")
    zip: str = Field(description="The zip of the company.")
    dcf_diff: float = Field(
        description="The discounted cash flow difference of the company."
    )
    dcf: float = Field(description="The discounted cash flow of the company.")
    image: str = Field(description="The image of the company.")
    ipo_date: date = Field(description="The IPO date of the company.")
    default_image: bool = Field(description="If the image is the default image.")
    is_etf: bool = Field(description="If the company is an ETF.")
    is_actively_trading: bool = Field(description="If the company is actively trading.")
    is_adr: bool = Field(description="If the company is an ADR.")
    is_fund: bool = Field(description="If the company is a fund.")
