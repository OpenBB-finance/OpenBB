"""Historical Employees data model."""


from datetime import date, datetime

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


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

    @validator("acceptance_time", pre=True, check_fields=False)
    def acceptance_time_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")

    @validator("period_of_report", pre=True, check_fields=False)
    def period_of_report_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")

    @validator("filing_date", pre=True, check_fields=False)
    def filing_date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")
