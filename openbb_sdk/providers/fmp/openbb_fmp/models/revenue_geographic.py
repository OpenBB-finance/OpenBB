"""FMP Revenue Geographic Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.revenue_geographic import (
    RevenueGeographicData,
    RevenueGeographicQueryParams,
)
from pydantic import validator

from openbb_fmp.utils.helpers import create_url, get_data


class FMPRevenueGeographicQueryParams(RevenueGeographicQueryParams):
    """FMP Revenue Geographic QueryParams.

    Source: https://site.financialmodelingprep.com/developer/docs/revenue-geographic-by-segments-api/
    """


class FMPRevenueGeographicData(RevenueGeographicData):
    """FMP Revenue Geographic Data."""

    @validator("date", pre=True)
    def date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class FMPRevenueGeographicFetcher(
    Fetcher[  # type: ignore
        RevenueGeographicQueryParams,
        List[RevenueGeographicData],
        FMPRevenueGeographicQueryParams,
        List[FMPRevenueGeographicData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPRevenueGeographicQueryParams:
        return FMPRevenueGeographicQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPRevenueGeographicQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPRevenueGeographicData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        query.period = "annual" if query.period == "annually" else "quarter"

        url = create_url(4, "revenue-geographic-segmentation", api_key, query)
        data = get_data(url, **kwargs)

        if isinstance(data, dict):
            raise ValueError("Expected list of dicts, got dict")

        return [
            FMPRevenueGeographicData(
                date=key,
                geographic_segment=v,
                americas=v.get("Americas Segment", v.get("North America", None)),
                europe=v.get("Europe Segment", v.get("Europe", None)),
                greater_china=v.get(
                    "Greater China Segment", v.get("Greater China", None)
                ),
                japan=v.get("Japan Segment", v.get("Japan", v.get("J P", None))),
                rest_of_asia_pacific=v.get(
                    "Rest of Asia Pacific Segment", v.get("Asia-Pacific", None)
                ),
            )
            for d in data
            for key, v in d.items()
            if isinstance(v, dict)
        ]

    @staticmethod
    def transform_data(
        data: List[FMPRevenueGeographicData],
    ) -> List[FMPRevenueGeographicData]:
        return data
