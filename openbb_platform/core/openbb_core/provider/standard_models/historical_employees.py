"""Historical Employees Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class HistoricalEmployeesQueryParams(QueryParams):
    """Historical Employees Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class HistoricalEmployeesData(Data):
    """Historical Employees Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    cik: Optional[Union[str, int]] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("cik", "")
    )
    filing_date: Optional[dateType] = Field(
        default=None, description="Filing date of the company employee"
    )
    acceptance_time: Optional[datetime] = Field(
        default=None, description="Time of acceptance of the company employee."
    )
    period_of_report: Optional[dateType] = Field(
        default=None, description="Date of reporting of the company employee."
    )
    company_name: Optional[str] = Field(
        default=None,
        description="Registered name of the company to retrieve the historical employees of.",
    )
    form_type: Optional[str] = Field(
        default=None, description="Form type of the company employee."
    )
    employee_count: int = Field(description="Count of employees of the company.")
    source: Optional[str] = Field(
        default=None,
        description="Source URL which retrieves this data for the company.",
    )

    @field_validator(
        "acceptance_time",
        "period_of_report",
        "filing_date",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_date(cls, v):  # pylint: disable=E0213
        """Validate acceptance time."""
        if v:
            try:
                return datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return None
