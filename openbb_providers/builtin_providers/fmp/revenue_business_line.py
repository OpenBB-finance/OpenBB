"""FMP Revenue Business Line Fetcher."""

# IMPORT STANDARD
from datetime import datetime
from typing import Dict, List, Optional

# IMPORT THIRD-PARTY
from pydantic import validator

from builtin_providers.fmp.helpers import create_url, get_data

# IMPORT INTERNAL
from openbb_provider.model.data.revenue_business_line import (
    RevenueBusinessLineData,
    RevenueBusinessLineQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer

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

    __name__ = "FMPRevenueBusinessLineQueryParams"


class FMPRevenueBusinessLineData(RevenueBusinessLineData):
    __name__ = "FMPRevenueBusinessLineData"

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
        query: FMPRevenueBusinessLineQueryParams, api_key: str
    ) -> List[FMPRevenueBusinessLineData]:
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
