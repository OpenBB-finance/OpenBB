"""FMP Revenue Business Line Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.revenue_business_line import (
    RevenueBusinessLineData,
    RevenueBusinessLineQueryParams,
)
from pydantic import validator

from openbb_fmp.utils.helpers import create_url, get_data


class FMPRevenueBusinessLineQueryParams(RevenueBusinessLineQueryParams):
    """FMP Revenue Business Line Query.

    Source: https://site.financialmodelingprep.com/developer/docs/sales-revenue-by-segments-api/
    """


class FMPRevenueBusinessLineData(RevenueBusinessLineData):
    """FMP Revenue Business Line Data."""

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class FMPRevenueBusinessLineFetcher(
    Fetcher[  # type: ignore
        RevenueBusinessLineQueryParams,
        RevenueBusinessLineData,
        FMPRevenueBusinessLineQueryParams,
        FMPRevenueBusinessLineData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPRevenueBusinessLineQueryParams:
        return FMPRevenueBusinessLineQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPRevenueBusinessLineQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPRevenueBusinessLineData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        query.period = "annual" if query.period == "annually" else "quarter"

        url = create_url(4, "revenue-product-segmentation", api_key, query)
        data = get_data(url)

        if isinstance(data, dict):
            raise ValueError("Expected list of dicts, got dict")

        data = [
            {"date": list(d.keys())[0], "business_line": list(d.values())[0]}
            for d in data
        ]

        return [FMPRevenueBusinessLineData(**d) for d in data]

    @staticmethod
    def transform_data(
        data: List[FMPRevenueBusinessLineData],
    ) -> List[FMPRevenueBusinessLineData]:
        return data
