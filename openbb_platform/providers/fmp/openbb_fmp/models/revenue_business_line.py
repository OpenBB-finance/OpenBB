"""FMP Revenue by Business Line Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.revenue_business_line import (
    RevenueBusinessLineData,
    RevenueBusinessLineQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data
from pydantic import field_validator


class FMPRevenueBusinessLineQueryParams(RevenueBusinessLineQueryParams):
    """FMP Revenue by Business Line Query.

    Source: https://site.financialmodelingprep.com/developer/docs/sales-revenue-by-segments-api/
    """


class FMPRevenueBusinessLineData(RevenueBusinessLineData):
    """FMP Revenue by Business Line Data."""

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")


class FMPRevenueBusinessLineFetcher(
    Fetcher[  # type: ignore
        FMPRevenueBusinessLineQueryParams,
        List[FMPRevenueBusinessLineData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPRevenueBusinessLineQueryParams:
        """Transform the query params."""
        return FMPRevenueBusinessLineQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPRevenueBusinessLineQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "revenue-product-segmentation", api_key, query)
        data = get_data(url, **kwargs)

        if isinstance(data, Dict):
            raise ValueError("Expected list of Dicts, got Dict")

        return data

    @staticmethod
    def transform_data(
        query: FMPRevenueBusinessLineQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPRevenueBusinessLineData]:
        """Return the transformed data."""
        return [
            FMPRevenueBusinessLineData(date=key, business_line=value)
            for d in data
            for key, value in d.items()
        ]
