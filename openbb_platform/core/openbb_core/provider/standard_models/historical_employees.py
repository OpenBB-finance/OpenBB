"""Historical Employees Standard Model."""

from datetime import date, datetime
from typing import List, Set, Union

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class HistoricalEmployeesQueryParams(QueryParams):
    """Historical Employees Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class HistoricalEmployeesData(Data):
    """Historical Employees Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    cik: int = Field(description=DATA_DESCRIPTIONS.get("cik", ""))
    acceptance_time: datetime = Field(
        description="Time of acceptance of the company employee."
    )
    period_of_report: date = Field(
        description="Date of reporting of the company employee."
    )
    company_name: str = Field(
        description="Registered name of the company to retrieve the historical employees of."
    )
    form_type: str = Field(description="Form type of the company employee.")
    filing_date: date = Field(description="Filing date of the company employee")
    employee_count: int = Field(description="Count of employees of the company.")
    source: str = Field(
        description="Source URL which retrieves this data for the company."
    )

    @field_validator("acceptance_time", mode="before", check_fields=False)
    @classmethod
    def acceptance_time_validate(cls, v):  # pylint: disable=E0213
        """Validate acceptance time."""
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")

    @field_validator("period_of_report", mode="before", check_fields=False)
    @classmethod
    def period_of_report_validate(cls, v):  # pylint: disable=E0213
        """Validate period of report."""
        return datetime.strptime(v, "%Y-%m-%d")

    @field_validator("filing_date", mode="before", check_fields=False)
    @classmethod
    def filing_date_validate(cls, v):  # pylint: disable=E0213
        """Validate filing date."""
        return datetime.strptime(v, "%Y-%m-%d")

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: Union[str, List[str], Set[str]]):
        """Convert field to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
