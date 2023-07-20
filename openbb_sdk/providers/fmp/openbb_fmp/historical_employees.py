"""FMP Historical Employees fetcher."""

# IMPORT STANDARD
from datetime import date, datetime
from typing import Dict, List, Optional

# IMPORT INTERNAL
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.historical_employees import (
    HistoricalEmployeesData,
    HistoricalEmployeesQueryParams,
)

# IMPORT THIRD-PARTY
from pydantic import Field, validator

from .helpers import create_url, get_data_many


class FMPHistoricalEmployeesQueryParams(HistoricalEmployeesQueryParams):
    """FMP Historical Employees query.

    Source: https://site.financialmodelingprep.com/developer/docs/historical-numer-of-employees-api/

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class FMPHistoricalEmployeesData(HistoricalEmployeesData):
    """FMP Historical Employees data."""

    symbol: str = Field(min_length=1)
    cik: int
    acceptanceTime: datetime = Field(alias="acceptance_time")
    periodOfReport: date = Field(alias="period_of_report")
    companyName: str = Field(alias="company_name")
    formType: str = Field(alias="form_type")
    filingDate: date = Field(alias="filing_date")
    employeeCount: int = Field(alias="employee_count")
    source: str

    @validator("acceptanceTime", pre=True)
    def acceptance_time_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")

    @validator("periodOfReport", pre=True)
    def period_of_report_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")

    @validator("filingDate", pre=True)
    def filing_date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class FMPHistoricalEmployeesFetcher(
    Fetcher[
        HistoricalEmployeesQueryParams,
        HistoricalEmployeesData,
        FMPHistoricalEmployeesQueryParams,
        FMPHistoricalEmployeesData,
    ]
):
    @staticmethod
    def transform_query(
        query: HistoricalEmployeesQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPHistoricalEmployeesQueryParams:
        return FMPHistoricalEmployeesQueryParams(
            symbol=query.symbol, **extra_params or {}
        )

    @staticmethod
    def extract_data(
        query: FMPHistoricalEmployeesQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPHistoricalEmployeesData]:
        if credentials:
            api_key = credentials.get("FMP_API_KEY")

        url = create_url(4, "historical/employee_count", api_key, query)
        return get_data_many(url, FMPHistoricalEmployeesData)

    @staticmethod
    def transform_data(
        data: List[FMPHistoricalEmployeesData],
    ) -> List[HistoricalEmployeesData]:
        return data_transformer(data, HistoricalEmployeesData)
