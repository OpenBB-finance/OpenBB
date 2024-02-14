"""FMP Executive Compensation Model."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.executive_compensation import (
    ExecutiveCompensationData,
    ExecutiveCompensationQueryParams,
)
from openbb_core.provider.utils.helpers import amake_requests
from openbb_fmp.utils.helpers import response_callback
from pydantic import field_validator


class FMPExecutiveCompensationQueryParams(ExecutiveCompensationQueryParams):
    """FMP Executive Compensation Query.

    Source: https://site.financialmodelingprep.com/developer/docs/executive-compensation-api/
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


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
        transformed_params = params
        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - timedelta(days=10 * 365)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FMPExecutiveCompensationQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: FMPExecutiveCompensationQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        base_url = "https://financialmodelingprep.com/api/v4/"
        urls = [
            f"{base_url}/governance/executive_compensation?symbol={s.strip()}&apikey={api_key}"
            for s in query.symbol.split(",")
        ]
        return await amake_requests(urls, response_callback, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPExecutiveCompensationQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPExecutiveCompensationData]:
        """Return the transformed data."""
        result = []
        for d in data:
            if "year" in d:
                if (
                    d["year"] >= query.start_date.year
                    and d["year"] <= query.end_date.year
                ):
                    result.append(FMPExecutiveCompensationData(**d))
            else:
                result.append(FMPExecutiveCompensationData(**d))
        return result
