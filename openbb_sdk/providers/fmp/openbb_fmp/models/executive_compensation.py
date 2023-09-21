"""FMP Executive Compensation Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.executive_compensation import (
    ExecutiveCompensationData,
    ExecutiveCompensationQueryParams,
)
from pydantic import validator

# This endpoint is only provided by FMP and not by the other providers for now.


class FMPExecutiveCompensationQueryParams(ExecutiveCompensationQueryParams):
    """FMP Executive Compensation Query.

    Source: https://site.financialmodelingprep.com/developer/docs/executive-compensation-api/
    """


class FMPExecutiveCompensationData(ExecutiveCompensationData):
    """FMP Executive Compensation Data."""

    @validator("filingDate", pre=True, check_fields=False)
    def filing_date_validate(cls, v):  # pylint: disable=E0213
        """Return the filing date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")

    @validator("acceptedDate", pre=True, check_fields=False)
    def accepted_date_validate(cls, v):  # pylint: disable=E0213
        """Return the accepted date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class FMPExecutiveCompensationFetcher(
    Fetcher[  # type: ignore
        FMPExecutiveCompensationQueryParams,
        List[FMPExecutiveCompensationData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPExecutiveCompensationQueryParams:
        """Transform the query params."""
        return FMPExecutiveCompensationQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPExecutiveCompensationQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "governance/executive_compensation", api_key, query)

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPExecutiveCompensationData]:
        """Return the transformed data."""
        return [FMPExecutiveCompensationData.parse_obj(d) for d in data]
