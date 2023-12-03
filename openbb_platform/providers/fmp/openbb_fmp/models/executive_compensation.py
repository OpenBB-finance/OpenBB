"""FMP Executive Compensation Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.executive_compensation import (
    ExecutiveCompensationData,
    ExecutiveCompensationQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import field_validator


class FMPExecutiveCompensationQueryParams(ExecutiveCompensationQueryParams):
    """FMP Executive Compensation Query.

    Source: https://site.financialmodelingprep.com/developer/docs/executive-compensation-api/
    """


class FMPExecutiveCompensationData(ExecutiveCompensationData):
    """FMP Executive Compensation Data."""

    @field_validator("filingDate", mode="before", check_fields=False)
    @classmethod
    def filing_date_validate(cls, v):  # pylint: disable=E0213
        """Return the filing date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")

    @field_validator("acceptedDate", mode="before", check_fields=False)
    @classmethod
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
    def transform_data(
        query: FMPExecutiveCompensationQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPExecutiveCompensationData]:
        """Return the transformed data."""
        return [FMPExecutiveCompensationData.model_validate(d) for d in data]
