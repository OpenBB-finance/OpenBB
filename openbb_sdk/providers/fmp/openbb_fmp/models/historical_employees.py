"""FMP Historical Employees fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.historical_employees import (
    HistoricalEmployeesData,
    HistoricalEmployeesQueryParams,
)
from pydantic import validator

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPHistoricalEmployeesQueryParams(HistoricalEmployeesQueryParams):
    """FMP Historical Employees query.

    Source: https://site.financialmodelingprep.com/developer/docs/historical-numer-of-employees-api/
    """


class FMPHistoricalEmployeesData(HistoricalEmployeesData):
    """FMP Historical Employees Data."""

    class Config:
        fields = {
            "acceptance_time": "acceptanceTime",
            "period_of_report": "periodOfReport",
            "company_name": "companyName",
            "form_type": "formType",
            "filing_date": "filingDate",
            "employee_count": "employeeCount",
        }

    @validator("acceptanceTime", pre=True, check_fields=False)
    def acceptance_time_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")

    @validator("periodOfReport", pre=True, check_fields=False)
    def period_of_report_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")

    @validator("filingDate", pre=True, check_fields=False)
    def filing_date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class FMPHistoricalEmployeesFetcher(
    Fetcher[
        FMPHistoricalEmployeesQueryParams,
        List[FMPHistoricalEmployeesData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPHistoricalEmployeesQueryParams:
        return FMPHistoricalEmployeesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPHistoricalEmployeesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List[FMPHistoricalEmployeesData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "historical/employee_count", api_key, query)
        return get_data_many(url, FMPHistoricalEmployeesData, **kwargs)

    @staticmethod
    def transform_data(
        data: List[FMPHistoricalEmployeesData],
    ) -> List[FMPHistoricalEmployeesData]:
        return data
