"""FMP Revenue Business Line Fetcher."""

# IMPORT STANDARD
from datetime import datetime
from typing import Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer

# IMPORT INTERNAL
from openbb_provider.models.revenue_business_line import (
    RevenueBusinessLineData,
    RevenueBusinessLineQueryParams,
)

# IMPORT THIRD-PARTY
from pydantic import validator

from .helpers import create_url, get_data

# This part is only provided by FMP and not by the other providers for now.


class FMPRevenueBusinessLineQueryParams(RevenueBusinessLineQueryParams):
    """FMP Revenue Business Line QueryParams.

    Source: https://site.financialmodelingprep.com/developer/docs/sales-revenue-by-segments-api/

    Parameter
    ---------
    symbol : Optional[str]
        The symbol of the company if no CIK is provided.
    period : Literal["annual", "quarterly"]
        The period of the income statement. Default is "annual".
    structure : Literal["hierarchical", "flat"]
        The structure of the revenue business line. Default is "flat".
    """


class FMPRevenueBusinessLineData(RevenueBusinessLineData):
    @validator("date", pre=True)
    def time_validate(cls, v):  # pylint: disable=E0213
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
    def transform_query(
        query: RevenueBusinessLineQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPRevenueBusinessLineQueryParams:
        return FMPRevenueBusinessLineQueryParams.parse_obj(query)

    @staticmethod
    def extract_data(
        query: FMPRevenueBusinessLineQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPRevenueBusinessLineData]:
        if credentials:
            api_key = credentials.get("FMP_API_KEY")

        # Type has to be ignored below because we are using something different than the literal type
        query.period = "quarter" if query.period == "quarterly" else "annual"  # type: ignore
        url = create_url(4, "revenue-product-segmentation", api_key, query)
        data = get_data(url)
        if isinstance(data, dict):
            raise ValueError("Expected list of dicts, got dict")

        data = [
            {
                "date": list(d.keys())[0],
                "data_and_service": list(d.values())[0],
            }
            for d in data
        ]

        return [FMPRevenueBusinessLineData(**d) for d in data]

    @staticmethod
    def transform_data(
        data: List[FMPRevenueBusinessLineData],
    ) -> List[RevenueBusinessLineData]:
        return data_transformer(data, RevenueBusinessLineData)
