"""Historical Employees data model."""


from datetime import date, datetime

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.models.base import BaseSymbol

from pydantic import Field


class HistoricalEmployeesQueryParams(QueryParams, BaseSymbol):
    """Historical Employees Query."""


class HistoricalEmployeesData(Data, BaseSymbol):
    """Historical Employees Data."""

    cik: int = Field(
        description="The CIK of the company to retrieve the historical employees of."
    )
    acceptance_time: datetime = Field(
        description="The time of acceptance of the company employee."
    )
    period_of_report: date = Field(
        description="The date of reporting of the company employee."
    )
    company_name: str = Field(
        description="The registered name of the company to retrieve the historical employees of."
    )
    form_type: str = Field(description="The form type of the company employee.")
    filing_date: date = Field(description="The filing date of the company employee")
    employee_count: int = Field(description="The count of employees of the company.")
    source: str = Field(
        description="The source URL which retrieves this data for the company."
    )
