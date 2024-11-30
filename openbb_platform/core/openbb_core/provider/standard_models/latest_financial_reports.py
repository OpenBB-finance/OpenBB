"""Latest Financial Reports Standard Model."""

from datetime import date as dateType
from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class LatestFinancialReportsQueryParams(QueryParams):
    """Latest Financial Reports Query."""


class LatestFinancialReportsData(Data):
    """Latest Financial Reports Data."""

    filing_date: dateType = Field(description="The date of the filing.")
    period_ending: Optional[dateType] = Field(
        default=None, description="Report for the period ending."
    )
    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol")
    )
    name: Optional[str] = Field(default=None, description="Name of the company.")
    cik: Optional[str] = Field(default=None, description=DATA_DESCRIPTIONS.get("cik"))
    sic: Optional[str] = Field(
        default=None, description="Standard Industrial Classification code."
    )
    report_type: Optional[str] = Field(default=None, description="Type of filing.")
    description: Optional[str] = Field(
        default=None, description="Description of the report."
    )
    url: str = Field(description="URL to the filing page.")
